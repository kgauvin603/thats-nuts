from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime, Text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    barcode: Optional[str] = Field(default=None, index=True, unique=True)
    product_name: Optional[str] = Field(default=None, index=True)
    brand_name: Optional[str] = Field(default=None, index=True)
    image_url: Optional[str] = Field(default=None)
    ingredient_text: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    ingredient_coverage_status: str = Field(default="unknown", index=True)
    source: str = Field(default="manual", index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    normalized_name: str = Field(index=True, unique=True)
    display_name: Optional[str] = Field(default=None, index=True)
    inci_name: Optional[str] = Field(default=None, index=True)
    source: str = Field(default="seed", index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class IngredientAlias(SQLModel, table=True):
    __tablename__ = "ingredient_aliases"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredients.id", index=True)
    alias: str = Field(index=True)
    is_primary: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class IngredientNutMapping(SQLModel, table=True):
    __tablename__ = "ingredient_nut_mappings"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredients.id", index=True)
    nut_source: str = Field(index=True)
    confidence: str = Field(index=True)
    status: str = Field(index=True)
    reason: str = Field(sa_column=Column(Text, nullable=False))
    source: str = Field(default="seed", index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class IngredientMapping(SQLModel, table=True):
    __tablename__ = "ingredient_mappings"

    id: Optional[int] = Field(default=None, primary_key=True)
    normalized_name: str = Field(index=True, unique=True)
    aliases: List[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    nut_source: str = Field(index=True)
    confidence: str = Field(index=True)
    status: str = Field(index=True)
    reason: str = Field(sa_column=Column(Text, nullable=False))
    source: str = Field(default="seed", index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class AllergyProfileRecord(SQLModel, table=True):
    __tablename__ = "allergy_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, index=True)
    peanut: bool = Field(default=False, index=True)
    tree_nuts: bool = Field(default=False, index=True)
    almond: bool = Field(default=False, index=True)
    walnut: bool = Field(default=False, index=True)
    cashew: bool = Field(default=False, index=True)
    pistachio: bool = Field(default=False, index=True)
    hazelnut: bool = Field(default=False, index=True)
    macadamia: bool = Field(default=False, index=True)
    brazil_nut: bool = Field(default=False, index=True)
    pecan: bool = Field(default=False, index=True)
    coconut: bool = Field(default=False, index=True)
    shea: bool = Field(default=False, index=True)
    argan: bool = Field(default=False, index=True)
    kukui: bool = Field(default=False, index=True)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class ScanHistory(SQLModel, table=True):
    __tablename__ = "scan_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: Optional[int] = Field(default=None, foreign_key="products.id", index=True)
    allergy_profile_id: Optional[int] = Field(
        default=None,
        foreign_key="allergy_profiles.id",
        index=True,
    )
    submitted_ingredient_text: str = Field(sa_column=Column(Text, nullable=False))
    result_status: str = Field(index=True)
    explanation: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    matched_ingredients: List[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
