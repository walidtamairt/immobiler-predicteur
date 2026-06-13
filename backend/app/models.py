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


class ExternalMarketContext(Base):
    __tablename__ = "external_market_context"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(Text)
    indicator: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer)
    value: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ScrapedMarketTrend(Base):
    __tablename__ = "scraped_market_trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str | None] = mapped_column(Text)
    average_price: Mapped[float | None] = mapped_column(Float)
    trend: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    source_title: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ExternalContextSummary(Base):
    __tablename__ = "external_context_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    summary_kind: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)
    summary_text: Mapped[str | None] = mapped_column(Text)
    rows_collected: Mapped[int | None] = mapped_column(Integer)
    average_indicator_value: Mapped[float | None] = mapped_column(Float)
    payload_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
