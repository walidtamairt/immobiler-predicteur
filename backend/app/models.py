from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class PropertyTrain(Base):
    __tablename__ = "properties_train"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gr_liv_area: Mapped[float | None] = mapped_column(Float)
    lot_area: Mapped[float | None] = mapped_column(Float)
    overall_qual: Mapped[int | None] = mapped_column(Integer)
    overall_cond: Mapped[int | None] = mapped_column(Integer)
    bedroom_abv_gr: Mapped[int | None] = mapped_column(Integer)
    full_bath: Mapped[int | None] = mapped_column(Integer)
    garage_cars: Mapped[float | None] = mapped_column(Float)
    garage_area: Mapped[float | None] = mapped_column(Float)
    neighborhood: Mapped[str | None] = mapped_column(Text)
    house_style: Mapped[str | None] = mapped_column(Text)
    sale_month: Mapped[int | None] = mapped_column(Integer)
    property_age: Mapped[int | None] = mapped_column(Integer)
    sale_price: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str | None] = mapped_column(Text)
    mae: Mapped[float | None] = mapped_column(Float)
    rmse: Mapped[float | None] = mapped_column(Float)
    r2: Mapped[float | None] = mapped_column(Float)
    train_rows: Mapped[int | None] = mapped_column(Integer)
    feature_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class BatchPrediction(Base):
    __tablename__ = "batch_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_row_id: Mapped[int | None] = mapped_column(Integer)
    gr_liv_area: Mapped[float | None] = mapped_column(Float)
    lot_area: Mapped[float | None] = mapped_column(Float)
    overall_qual: Mapped[int | None] = mapped_column(Integer)
    overall_cond: Mapped[int | None] = mapped_column(Integer)
    bedroom_abv_gr: Mapped[int | None] = mapped_column(Integer)
    full_bath: Mapped[int | None] = mapped_column(Integer)
    garage_cars: Mapped[float | None] = mapped_column(Float)
    garage_area: Mapped[float | None] = mapped_column(Float)
    neighborhood: Mapped[str | None] = mapped_column(Text)
    house_style: Mapped[str | None] = mapped_column(Text)
    sale_month: Mapped[int | None] = mapped_column(Integer)
    property_age: Mapped[int | None] = mapped_column(Integer)
    predicted_price: Mapped[float | None] = mapped_column(Float)
    model_version: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class UserPrediction(Base):
    __tablename__ = "user_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gr_liv_area: Mapped[float | None] = mapped_column(Float)
    lot_area: Mapped[float | None] = mapped_column(Float)
    overall_qual: Mapped[int | None] = mapped_column(Integer)
    overall_cond: Mapped[int | None] = mapped_column(Integer)
    bedroom_abv_gr: Mapped[int | None] = mapped_column(Integer)
    full_bath: Mapped[int | None] = mapped_column(Integer)
    garage_cars: Mapped[float | None] = mapped_column(Float)
    garage_area: Mapped[float | None] = mapped_column(Float)
    neighborhood: Mapped[str | None] = mapped_column(Text)
    house_style: Mapped[str | None] = mapped_column(Text)
    sale_month: Mapped[int | None] = mapped_column(Integer)
    property_age: Mapped[int | None] = mapped_column(Integer)
    predicted_price: Mapped[float | None] = mapped_column(Float)
    lower_bound: Mapped[float | None] = mapped_column(Float)
    upper_bound: Mapped[float | None] = mapped_column(Float)
    model_version: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
