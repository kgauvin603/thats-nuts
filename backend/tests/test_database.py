from sqlalchemy import inspect
from sqlmodel import Session, select

from app.db.session import create_db_engine, get_engine, initialize_database
from app.models import Ingredient, IngredientAlias, IngredientMapping, IngredientNutMapping
from app.services.persistence import prepare_persistence


def test_initialize_database_creates_expected_tables(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_db_engine(f"sqlite:///{database_path}")

    assert initialize_database(engine=engine) is True

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    assert {
        "products",
        "ingredients",
        "ingredient_aliases",
        "ingredient_nut_mappings",
        "ingredient_mappings",
        "allergy_profiles",
        "scan_history",
    }.issubset(table_names)


def test_prepare_persistence_seeds_normalized_rule_tables(temp_database):
    assert prepare_persistence() is True

    with Session(get_engine()) as session:
        ingredient = session.exec(
            select(Ingredient).where(Ingredient.normalized_name == "almond oil")
        ).first()
        alias = session.exec(
            select(IngredientAlias).where(IngredientAlias.alias == "sweet almond oil")
        ).first()
        nut_mapping = session.exec(
            select(IngredientNutMapping).where(IngredientNutMapping.nut_source == "almond")
        ).first()
        legacy_mapping = session.exec(
            select(IngredientMapping).where(
                IngredientMapping.normalized_name == "almond oil"
            )
        ).first()

        assert ingredient is not None
        assert alias is not None
        assert alias.ingredient_id == ingredient.id
        assert nut_mapping is not None
        assert nut_mapping.ingredient_id == ingredient.id
        assert legacy_mapping is not None
        assert "sweet almond oil" in legacy_mapping.aliases
