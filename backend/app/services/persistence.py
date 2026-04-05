import logging
from typing import Dict, List, Optional

from sqlalchemy import inspect, or_, text

from sqlmodel import Session, select

from app.core.config import get_settings
from app.db import get_engine, initialize_database, session_scope
from app.models import (
    AllergyProfileRecord,
    Ingredient,
    IngredientAlias,
    IngredientMapping,
    IngredientNutMapping,
    Product,
    ScanHistory,
)
from app.models.records import utcnow
from app.schemas.ingredients import AllergyProfile
from app.schemas.history import ScanHistoryEntry
from app.schemas.products import NormalizedProduct, SavedProductEntry
from app.services.seed_rules import SeedIngredientRule, load_seed_rule_set

logger = logging.getLogger(__name__)


def prepare_persistence() -> bool:
    if not initialize_database():
        return False

    if not ensure_scan_history_schema():
        return False

    settings = get_settings()
    if not settings.database_seed_data:
        return True

    try:
        with session_scope() as session:
            seed_rule_tables(session)
        return True
    except Exception:
        logger.exception("Database seed failed. Continuing without database-backed seed records.")
        return False


def seed_rule_tables(session: Session) -> None:
    rule_set = load_seed_rule_set()
    for rule in rule_set.rules:
        seed_rule(session, rule)
    session.commit()


def seed_rule(session: Session, rule: SeedIngredientRule) -> None:
    canonical_name = rule.aliases[0]
    ingredient = session.exec(
        select(Ingredient).where(Ingredient.normalized_name == canonical_name)
    ).first()

    if ingredient is None:
        ingredient = Ingredient(
            normalized_name=canonical_name,
            display_name=canonical_name.title(),
            source="seed",
            is_active=True,
        )
    else:
        ingredient.display_name = ingredient.display_name or canonical_name.title()
        ingredient.source = "seed"
        ingredient.is_active = True
        ingredient.updated_at = utcnow()

    session.add(ingredient)
    session.flush()

    existing_aliases = {
        alias.alias: alias
        for alias in session.exec(
            select(IngredientAlias).where(IngredientAlias.ingredient_id == ingredient.id)
        ).all()
    }
    for index, alias_name in enumerate(rule.aliases):
        alias = existing_aliases.get(alias_name)
        if alias is None:
            alias = IngredientAlias(
                ingredient_id=ingredient.id,
                alias=alias_name,
                is_primary=index == 0,
            )
        else:
            alias.is_primary = index == 0
        session.add(alias)

    mapping = session.exec(
        select(IngredientNutMapping).where(
            IngredientNutMapping.ingredient_id == ingredient.id,
            IngredientNutMapping.nut_source == rule.nut_source,
            IngredientNutMapping.source == "seed",
        )
    ).first()
    if mapping is None:
        mapping = IngredientNutMapping(
            ingredient_id=ingredient.id,
            nut_source=rule.nut_source,
            confidence=rule.confidence,
            status=rule.status,
            reason=rule.reason,
            source="seed",
            is_active=True,
        )
    else:
        mapping.confidence = rule.confidence
        mapping.status = rule.status
        mapping.reason = rule.reason
        mapping.is_active = True
        mapping.updated_at = utcnow()
    session.add(mapping)

    legacy_mapping = session.exec(
        select(IngredientMapping).where(IngredientMapping.normalized_name == canonical_name)
    ).first()
    if legacy_mapping is None:
        legacy_mapping = IngredientMapping(
            normalized_name=canonical_name,
            aliases=list(rule.aliases),
            nut_source=rule.nut_source,
            confidence=rule.confidence,
            status=rule.status,
            reason=rule.reason,
            source="seed",
            is_active=True,
        )
    else:
        legacy_mapping.aliases = list(rule.aliases)
        legacy_mapping.nut_source = rule.nut_source
        legacy_mapping.confidence = rule.confidence
        legacy_mapping.status = rule.status
        legacy_mapping.reason = rule.reason
        legacy_mapping.is_active = True
        legacy_mapping.updated_at = utcnow()
    session.add(legacy_mapping)


def get_cached_product(barcode: str) -> Optional[NormalizedProduct]:
    try:
        with session_scope() as session:
            product = session.exec(select(Product).where(Product.barcode == barcode)).first()
            if product is None:
                return None
            return product_to_schema(product)
    except Exception:
        logger.exception("Product cache lookup failed for barcode %s", barcode)
        return None


def upsert_product(product: NormalizedProduct) -> Optional[int]:
    try:
        with session_scope() as session:
            record = session.exec(select(Product).where(Product.barcode == product.barcode)).first()
            if record is None:
                record = Product(barcode=product.barcode)

            record.product_name = product.product_name
            record.brand_name = product.brand_name
            record.image_url = product.image_url
            record.ingredient_text = product.ingredient_text
            record.ingredient_coverage_status = product.ingredient_coverage_status
            record.source = product.source
            record.updated_at = utcnow()

            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id
    except Exception:
        logger.exception("Product cache write failed for barcode %s", product.barcode)
        return None


def persist_scan_result(
    ingredient_text: str,
    result: dict,
    allergy_profile: Optional[AllergyProfile] = None,
    product_id: Optional[int] = None,
    scan_type: str = "manual_ingredient_check",
    submitted_barcode: Optional[str] = None,
) -> None:
    try:
        with session_scope() as session:
            allergy_profile_id = create_allergy_profile(session, allergy_profile)
            scan_history = ScanHistory(
                scan_type=scan_type,
                product_id=product_id,
                submitted_barcode=submitted_barcode,
                allergy_profile_id=allergy_profile_id,
                submitted_ingredient_text=ingredient_text,
                result_status=result["status"],
                explanation=result.get("explanation"),
                matched_ingredients=result.get("matched_ingredients", []),
            )
            session.add(scan_history)
            session.commit()
    except Exception:
        logger.exception("Scan history persistence failed.")


def create_allergy_profile(
    session: Session, allergy_profile: Optional[AllergyProfile]
) -> Optional[int]:
    if allergy_profile is None:
        return None

    record = AllergyProfileRecord(**allergy_profile.model_dump())
    session.add(record)
    session.flush()
    return record.id


def product_to_schema(product: Product) -> NormalizedProduct:
    return NormalizedProduct(
        barcode=product.barcode or "",
        brand_name=product.brand_name,
        product_name=product.product_name,
        image_url=product.image_url,
        ingredient_text=product.ingredient_text,
        ingredient_coverage_status=product.ingredient_coverage_status,
        source=product.source,
    )


def list_recent_scan_history(limit: int = 20) -> List[ScanHistoryEntry]:
    try:
        with session_scope() as session:
            scans = session.exec(
                select(ScanHistory).order_by(ScanHistory.created_at.desc()).limit(limit)
            ).all()
            product_ids = [scan.product_id for scan in scans if scan.product_id is not None]
            products_by_id: Dict[int, Product] = {}
            if product_ids:
                products = session.exec(select(Product).where(Product.id.in_(product_ids))).all()
                products_by_id = {product.id: product for product in products if product.id is not None}

            return [
                ScanHistoryEntry(
                    scan_type=scan.scan_type,
                    barcode=products_by_id.get(scan.product_id).barcode
                    if scan.product_id is not None and products_by_id.get(scan.product_id)
                    else scan.submitted_barcode,
                    product_name=products_by_id.get(scan.product_id).product_name
                    if scan.product_id is not None and products_by_id.get(scan.product_id)
                    else None,
                    brand_name=products_by_id.get(scan.product_id).brand_name
                    if scan.product_id is not None and products_by_id.get(scan.product_id)
                    else None,
                    product_source=products_by_id.get(scan.product_id).source
                    if scan.product_id is not None and products_by_id.get(scan.product_id)
                    else None,
                    submitted_ingredient_text=scan.submitted_ingredient_text or None,
                    assessment_status=scan.result_status,
                    explanation=scan.explanation,
                    matched_ingredient_summary=build_matched_ingredient_summary(scan.matched_ingredients),
                    created_at=scan.created_at,
                )
                for scan in scans
            ]
    except Exception:
        logger.exception("Recent scan history lookup failed.")
        return []


def ensure_scan_history_schema() -> bool:
    try:
        engine = get_engine()
        inspector = inspect(engine)
        if "scan_history" not in inspector.get_table_names():
            return True

        columns = {column["name"] for column in inspector.get_columns("scan_history")}
        statements = []
        if "scan_type" not in columns:
            statements.append(
                "ALTER TABLE scan_history ADD COLUMN scan_type TEXT NOT NULL DEFAULT 'manual_ingredient_check'"
            )
        if "submitted_barcode" not in columns:
            statements.append("ALTER TABLE scan_history ADD COLUMN submitted_barcode TEXT")

        if statements:
            with engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))
                connection.execute(
                    text(
                        """
                        UPDATE scan_history
                        SET scan_type = CASE
                            WHEN product_id IS NOT NULL THEN 'barcode_lookup'
                            ELSE 'manual_ingredient_check'
                        END
                        WHERE scan_type IS NULL
                           OR scan_type = ''
                           OR scan_type = 'manual_ingredient_check'
                        """
                    )
                )
            return True

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE scan_history
                    SET scan_type = CASE
                        WHEN product_id IS NOT NULL THEN 'barcode_lookup'
                        ELSE 'manual_ingredient_check'
                    END
                    WHERE product_id IS NOT NULL
                      AND scan_type <> 'barcode_lookup'
                    """
                )
            )
        return True
    except Exception:
        logger.exception("Scan history schema update failed. Continuing without database-backed persistence.")
        return False


def build_matched_ingredient_summary(matched_ingredients: List[dict]) -> Optional[str]:
    if not matched_ingredients:
        return None

    names = []
    for item in matched_ingredients:
        name = item.get("original_text") or item.get("normalized_name")
        if name and name not in names:
            names.append(name)

    if not names:
        return None

    if len(names) == 1:
        return names[0]

    return ", ".join(names[:3])


def list_saved_products(limit: int = 20, query: Optional[str] = None) -> List[SavedProductEntry]:
    try:
        with session_scope() as session:
            statement = select(Product)
            if query:
                search_term = query.strip()
                if search_term:
                    statement = statement.where(
                        or_(
                            Product.barcode.contains(search_term),
                            Product.product_name.contains(search_term),
                            Product.brand_name.contains(search_term),
                        )
                    )

            products = session.exec(statement.order_by(Product.updated_at.desc()).limit(limit)).all()
            product_ids = [product.id for product in products if product.id is not None]

            latest_scans_by_product_id: Dict[int, ScanHistory] = {}
            if product_ids:
                scans = session.exec(
                    select(ScanHistory)
                    .where(ScanHistory.product_id.in_(product_ids))
                    .order_by(ScanHistory.created_at.desc())
                ).all()
                for scan in scans:
                    if scan.product_id is None or scan.product_id in latest_scans_by_product_id:
                        continue
                    latest_scans_by_product_id[scan.product_id] = scan

            entries = []
            for product in products:
                latest_scan = (
                    latest_scans_by_product_id.get(product.id) if product.id is not None else None
                )
                entries.append(
                    SavedProductEntry(
                        barcode=product.barcode or "",
                        product_name=product.product_name,
                        brand_name=product.brand_name,
                        image_url=product.image_url,
                        ingredient_text=product.ingredient_text,
                        ingredient_coverage_status=product.ingredient_coverage_status,
                        source=product.source,
                        created_at=product.created_at,
                        updated_at=product.updated_at,
                        latest_assessment_status=latest_scan.result_status if latest_scan else None,
                        latest_assessment_explanation=latest_scan.explanation if latest_scan else None,
                        latest_matched_ingredient_summary=build_matched_ingredient_summary(
                            latest_scan.matched_ingredients
                        )
                        if latest_scan
                        else None,
                        latest_scan_created_at=latest_scan.created_at if latest_scan else None,
                    )
                )
            return entries
    except Exception:
        logger.exception("Saved product lookup failed.")
        return []
