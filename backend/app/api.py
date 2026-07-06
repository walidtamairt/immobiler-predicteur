import json
import time
from pathlib import Path
from statistics import median

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.auth import AuthenticatedPrincipal, require_api_key
from backend.app.chat_service import call_gemini_chat
from backend.app.database import get_db
from backend.app.models import (
    BatchPrediction,
    ExternalContextSummary,
    ExternalMarketContext,
    ModelMetric,
    PropertyTrain,
    ScrapedMarketTrend,
    UserPrediction,
)
from backend.app.schemas import ModelMetricsHistoryResponse, ModelMetricsResponse
from backend.config.settings import get_settings
from backend.ml.predict_batch import load_model
from backend.ml.train_model import FEATURES

router = APIRouter(prefix="/api")
settings = get_settings()
MARKET_SUMMARY_CACHE: dict[str, object] = {"value": None, "expires_at": 0.0}
MARKET_SUMMARY_TTL_SECONDS = 300


def build_filtered_query(
    db: Session,
    neighborhood: str | None = None,
    house_style: str | None = None,
    overall_qual: int | None = None,
    bedroom_abv_gr: int | None = None,
    full_bath: int | None = None,
    sale_month: int | None = None,
    property_age_min: int | None = None,
    property_age_max: int | None = None,
):
    query = db.query(PropertyTrain)
    if neighborhood:
        query = query.filter(PropertyTrain.neighborhood == neighborhood)
    if house_style:
        query = query.filter(PropertyTrain.house_style == house_style)
    if overall_qual is not None:
        query = query.filter(PropertyTrain.overall_qual == overall_qual)
    if bedroom_abv_gr is not None:
        query = query.filter(PropertyTrain.bedroom_abv_gr == bedroom_abv_gr)
    if full_bath is not None:
        query = query.filter(PropertyTrain.full_bath == full_bath)
    if sale_month is not None:
        query = query.filter(PropertyTrain.sale_month == sale_month)
    if property_age_min is not None:
        query = query.filter(PropertyTrain.property_age >= property_age_min)
    if property_age_max is not None:
        query = query.filter(PropertyTrain.property_age <= property_age_max)
    return query


def serialize_property(row: PropertyTrain) -> dict:
    return {
        "id": row.id,
        "gr_liv_area": row.gr_liv_area,
        "lot_area": row.lot_area,
        "overall_qual": row.overall_qual,
        "overall_cond": row.overall_cond,
        "bedroom_abv_gr": row.bedroom_abv_gr,
        "full_bath": row.full_bath,
        "garage_cars": row.garage_cars,
        "garage_area": row.garage_area,
        "neighborhood": row.neighborhood,
        "house_style": row.house_style,
        "sale_month": row.sale_month,
        "property_age": row.property_age,
        "sale_price": row.sale_price,
    }


def build_market_summary(db: Session) -> str:
    now = time.time()
    cached_value = MARKET_SUMMARY_CACHE.get("value")
    cached_expires_at = float(MARKET_SUMMARY_CACHE.get("expires_at") or 0)
    if cached_value and cached_expires_at > now:
        return str(cached_value)

    properties = db.query(PropertyTrain).all()
    if not properties:
        return "Aucune donnee de marche n'est disponible dans Neon pour le moment."

    prices = [row.sale_price for row in properties if row.sale_price is not None]
    surfaces = [row.gr_liv_area for row in properties if row.gr_liv_area is not None]
    avg_price = sum(prices) / len(prices) if prices else 0
    median_price = median(prices) if prices else 0
    avg_surface = sum(surfaces) / len(surfaces) if surfaces else 0

    neighborhoods = db.query(
        PropertyTrain.neighborhood,
        func.avg(PropertyTrain.sale_price),
        func.count(PropertyTrain.id),
    ).group_by(PropertyTrain.neighborhood).having(func.count(PropertyTrain.id) >= 10).order_by(
        func.avg(PropertyTrain.sale_price).desc()
    ).limit(5).all()

    styles = db.query(
        PropertyTrain.house_style,
        func.avg(PropertyTrain.sale_price),
    ).group_by(PropertyTrain.house_style).order_by(func.avg(PropertyTrain.sale_price).desc()).limit(5).all()

    qualities = db.query(
        PropertyTrain.overall_qual,
        func.avg(PropertyTrain.sale_price),
    ).group_by(PropertyTrain.overall_qual).order_by(PropertyTrain.overall_qual).limit(5).all()

    months = db.query(
        PropertyTrain.sale_month,
        func.avg(PropertyTrain.sale_price),
    ).group_by(PropertyTrain.sale_month).order_by(PropertyTrain.sale_month).limit(6).all()
    external_indicators = (
        db.query(ExternalMarketContext)
        .order_by(ExternalMarketContext.year.desc(), ExternalMarketContext.id.desc())
        .limit(3)
        .all()
    )

    lines = [
        "Indicateurs globaux :",
        f"- Nombre de biens : {len(properties)}",
        f"- Prix moyen : {avg_price:.2f}",
        f"- Prix median : {median_price:.2f}",
        f"- Surface moyenne : {avg_surface:.2f}",
        "",
        "Top quartiers par prix moyen :",
    ]
    for neighborhood, neighborhood_price, total in neighborhoods:
        lines.append(f"- {neighborhood} : {float(neighborhood_price or 0):.2f} sur {total} biens")

    lines.append("")
    lines.append("Prix moyen par type de bien :")
    for style, style_price in styles:
        lines.append(f"- {style} : {float(style_price or 0):.2f}")

    lines.append("")
    lines.append("Prix moyen par qualite :")
    for quality, quality_price in qualities:
        lines.append(f"- Qualite {quality} : {float(quality_price or 0):.2f}")

    lines.append("")
    lines.append("Saisonnalite moyenne :")
    for month, month_price in months:
        lines.append(f"- Mois {month} : {float(month_price or 0):.2f}")

    if external_indicators:
        lines.append("")
        lines.append("Indicateurs externes charges dans Neon :")
        for row in external_indicators:
            lines.append(f"- {row.indicator} ({row.year}) : {float(row.value or 0):.2f}")

    external_context = load_external_summary_text(db)
    if external_context:
        lines.append("")
        lines.append("Contexte externe :")
        lines.append(f"- {external_context}")

    scraped_examples = db.query(ScrapedMarketTrend).order_by(ScrapedMarketTrend.created_at.desc()).limit(3).all()
    if scraped_examples:
        lines.append("")
        lines.append("Tendances scrappees :")
        for row in scraped_examples:
            description = row.description or row.trend or "Signal HTML"
            lines.append(f"- {row.city or 'Unknown'} : {description}")

    summary = "\n".join(lines)
    MARKET_SUMMARY_CACHE["value"] = summary
    MARKET_SUMMARY_CACHE["expires_at"] = now + MARKET_SUMMARY_TTL_SECONDS
    return summary


def load_external_summary_text(db: Session) -> str | None:
    summaries = (
        db.query(ExternalContextSummary)
        .order_by(ExternalContextSummary.created_at.desc())
        .all()
    )
    if summaries:
        texts = [summary.summary_text for summary in summaries if summary.summary_text]
        if texts:
            return " ".join(texts)

    external_summary_path = Path("data/external/external_market_summary.json")
    if external_summary_path.exists():
        try:
            external_summary = json.loads(external_summary_path.read_text(encoding="utf-8"))
            return external_summary.get("summary_text")
        except json.JSONDecodeError:
            return None
    return None


def build_market_analysis(rows: list[PropertyTrain], price_per_m2: list[float], external_context: str | None) -> dict:
    if not rows:
        return {
            "title": "Analyse du marche",
            "summary": "Aucune donnee ne correspond aux filtres selectionnes pour le moment.",
            "highlights": [],
            "externalContext": external_context,
        }

    avg_price = sum(float(row.sale_price or 0) for row in rows) / len(rows)
    avg_surface = sum(float(row.gr_liv_area or 0) for row in rows if row.gr_liv_area is not None) / max(
        len([row for row in rows if row.gr_liv_area is not None]),
        1,
    )

    top_neighborhoods = {}
    for row in rows:
        if not row.neighborhood or row.sale_price is None:
            continue
        top_neighborhood = top_neighborhoods.setdefault(row.neighborhood, {"total_price": 0.0, "count": 0})
        top_neighborhood["total_price"] += float(row.sale_price)
        top_neighborhood["count"] += 1

    best_neighborhood = None
    if top_neighborhoods:
        best_neighborhood = max(
            (
                {
                    "name": key,
                    "avg_price": value["total_price"] / value["count"],
                    "count": value["count"],
                }
                for key, value in top_neighborhoods.items()
            ),
            key=lambda item: item["avg_price"],
        )

    month_map = {}
    for row in rows:
        if row.sale_month is None or row.sale_price is None:
            continue
        month_data = month_map.setdefault(row.sale_month, {"total_price": 0.0, "count": 0})
        month_data["total_price"] += float(row.sale_price)
        month_data["count"] += 1

    best_month = None
    if month_map:
        best_month = min(
            (
                {
                    "month": key,
                    "avg_price": value["total_price"] / value["count"],
                    "count": value["count"],
                }
                for key, value in month_map.items()
            ),
            key=lambda item: item["avg_price"],
        )

    highlights = [
        f"Echantillon actif : {len(rows)} biens pour un prix moyen de {round(avg_price):,} EUR.".replace(",", " "),
        f"Surface moyenne observee : {round(avg_surface)} sqft et prix moyen au m2 de {round(sum(price_per_m2) / len(price_per_m2)) if price_per_m2 else 0} EUR.".replace(",", " "),
    ]

    if best_neighborhood:
        highlights.append(
            f"Quartier le plus valorise dans la selection : {best_neighborhood['name']} avec un prix moyen de {round(best_neighborhood['avg_price']):,} EUR.".replace(
                ",",
                " ",
            )
        )

    if best_month:
        highlights.append(
            f"Mois le plus accessible dans la selection : {best_month['month']} avec un prix moyen de {round(best_month['avg_price']):,} EUR.".replace(
                ",",
                " ",
            )
        )

    summary = "Le marche filtre reste dynamique et les dashboards montrent les segments les plus tendus ou accessibles de la selection courante."
    if best_neighborhood and best_month:
        summary = (
            f"Sur la selection courante, {best_neighborhood['name']} ressort comme le secteur le plus cher, "
            f"alors que le mois {best_month['month']} semble offrir le point d'entree moyen le plus bas."
        )

    return {
        "title": "Analyse du marche",
        "summary": summary,
        "highlights": highlights,
        "externalContext": external_context,
    }


def validate_prediction_payload(payload: dict) -> dict:
    missing = [feature for feature in FEATURES if feature not in payload]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing features: {missing}")

    numeric_features = {
        "GrLivArea",
        "LotArea",
        "OverallQual",
        "OverallCond",
        "BedroomAbvGr",
        "FullBath",
        "GarageCars",
        "GarageArea",
        "MoSold",
        "property_age",
    }

    validated = {}
    invalid_numeric = []
    for feature in FEATURES:
        value = payload.get(feature)
        if feature in numeric_features:
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                invalid_numeric.append(feature)
                continue
            if numeric_value < 0:
                invalid_numeric.append(feature)
                continue
            validated[feature] = numeric_value
        else:
            if not isinstance(value, str) or not value.strip():
                raise HTTPException(status_code=422, detail=f"Invalid categorical feature: {feature}")
            validated[feature] = value.strip()

    if invalid_numeric:
        raise HTTPException(status_code=422, detail=f"Invalid numeric features: {invalid_numeric}")

    return validated


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.get("/")
def root() -> dict:
    return {"message": "Real Estate AI API is running"}


@router.get("/market-data")
def market_data(
    db: Session = Depends(get_db),
    _: AuthenticatedPrincipal = Security(require_api_key),
) -> list[dict]:
    rows = db.query(PropertyTrain).all()
    return [serialize_property(row) for row in rows]


@router.get("/market-dashboard")
def market_dashboard(
    neighborhood: str | None = Query(default=None),
    house_style: str | None = Query(default=None),
    overall_qual: int | None = Query(default=None),
    bedroom_abv_gr: int | None = Query(default=None),
    full_bath: int | None = Query(default=None),
    sale_month: int | None = Query(default=None),
    property_age_min: int | None = Query(default=None),
    property_age_max: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    external_context = load_external_summary_text(db)
    rows = build_filtered_query(
        db,
        neighborhood=neighborhood,
        house_style=house_style,
        overall_qual=overall_qual,
        bedroom_abv_gr=bedroom_abv_gr,
        full_bath=full_bath,
        sale_month=sale_month,
        property_age_min=property_age_min,
        property_age_max=property_age_max,
    ).all()

    prices = [float(row.sale_price) for row in rows if row.sale_price is not None]
    surfaces = [float(row.gr_liv_area) for row in rows if row.gr_liv_area is not None]
    price_per_m2 = [
        float(row.sale_price) / float(row.gr_liv_area)
        for row in rows
        if row.sale_price is not None and row.gr_liv_area not in (None, 0)
    ]
    analysis = build_market_analysis(rows, price_per_m2, external_context)

    by_neighborhood_map = {}
    by_quality_map = {}
    by_month_map = {}
    scatter = []

    for row in rows:
        neighborhood_key = row.neighborhood or "Unknown"
        quality_key = row.overall_qual if row.overall_qual is not None else "Unknown"
        month_key = row.sale_month if row.sale_month is not None else "Unknown"
        price_value = float(row.sale_price or 0)

        by_neighborhood = by_neighborhood_map.setdefault(neighborhood_key, {"total_price": 0.0, "count": 0})
        by_neighborhood["total_price"] += price_value
        by_neighborhood["count"] += 1

        by_quality = by_quality_map.setdefault(quality_key, {"total_price": 0.0, "count": 0})
        by_quality["total_price"] += price_value
        by_quality["count"] += 1

        by_month = by_month_map.setdefault(month_key, {"total_price": 0.0, "count": 0})
        by_month["total_price"] += price_value
        by_month["count"] += 1

        if row.gr_liv_area is not None and row.sale_price is not None:
            scatter.append(
                {
                    "gr_liv_area": float(row.gr_liv_area),
                    "sale_price": float(row.sale_price),
                    "neighborhood": row.neighborhood or "Unknown",
                }
            )

    distribution = []
    if prices:
        min_price = min(prices)
        max_price = max(prices)
        bin_count = 8
        step = max((max_price - min_price) / bin_count, 1)
        distribution = [
            {
                "bucket": f"{round(min_price + index * step)}-{round(min_price + (index + 1) * step)}",
                "count": 0,
            }
            for index in range(bin_count)
        ]
        for price in prices:
            index = min(int((price - min_price) / step), bin_count - 1)
            distribution[index]["count"] += 1

    return {
        "kpis": {
            "totalProperties": len(rows),
            "averagePrice": round(sum(prices) / len(prices), 2) if prices else 0,
            "medianPrice": round(median(prices), 2) if prices else 0,
            "averageSurface": round(sum(surfaces) / len(surfaces), 2) if surfaces else 0,
            "averagePricePerM2": round(sum(price_per_m2) / len(price_per_m2), 2) if price_per_m2 else 0,
        },
        "byNeighborhood": sorted(
            [
                {
                    "neighborhood": key,
                    "avg_price": round(value["total_price"] / value["count"], 2),
                    "count": value["count"],
                }
                for key, value in by_neighborhood_map.items()
            ],
            key=lambda item: item["avg_price"],
            reverse=True,
        ),
        "priceVsSurface": scatter,
        "byQuality": sorted(
            [
                {
                    "overall_qual": key,
                    "avg_price": round(value["total_price"] / value["count"], 2),
                    "count": value["count"],
                }
                for key, value in by_quality_map.items()
            ],
            key=lambda item: (999 if item["overall_qual"] == "Unknown" else item["overall_qual"]),
        ),
        "priceDistribution": distribution,
        "seasonality": sorted(
            [
                {
                    "sale_month": key,
                    "avg_price": round(value["total_price"] / value["count"], 2),
                    "count": value["count"],
                }
                for key, value in by_month_map.items()
            ],
            key=lambda item: (999 if item["sale_month"] == "Unknown" else item["sale_month"]),
        ),
        "analysis": analysis,
    }


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    avg_price, median_proxy, avg_price_per_m2, total = db.query(
        func.avg(PropertyTrain.sale_price),
        func.avg(PropertyTrain.sale_price),
        func.avg(PropertyTrain.sale_price / func.nullif(PropertyTrain.gr_liv_area, 0)),
        func.count(PropertyTrain.id),
    ).one()
    avg_surface = db.query(func.avg(PropertyTrain.gr_liv_area)).scalar()
    return {
        "average_price": round(avg_price or 0, 2),
        "median_price": round(median_proxy or 0, 2),
        "average_price_per_m2": round(avg_price_per_m2 or 0, 2),
        "average_surface": round(avg_surface or 0, 2),
        "total_properties": total or 0,
    }


@router.get("/filters")
def filters(db: Session = Depends(get_db)) -> dict:
    neighborhoods = [row[0] for row in db.query(PropertyTrain.neighborhood).distinct().order_by(PropertyTrain.neighborhood).all() if row[0]]
    house_styles = [row[0] for row in db.query(PropertyTrain.house_style).distinct().order_by(PropertyTrain.house_style).all() if row[0]]
    qualities = [row[0] for row in db.query(PropertyTrain.overall_qual).distinct().order_by(PropertyTrain.overall_qual).all() if row[0] is not None]
    bedrooms = [row[0] for row in db.query(PropertyTrain.bedroom_abv_gr).distinct().order_by(PropertyTrain.bedroom_abv_gr).all() if row[0] is not None]
    baths = [row[0] for row in db.query(PropertyTrain.full_bath).distinct().order_by(PropertyTrain.full_bath).all() if row[0] is not None]
    months = [row[0] for row in db.query(PropertyTrain.sale_month).distinct().order_by(PropertyTrain.sale_month).all() if row[0] is not None]
    min_age = db.query(func.min(PropertyTrain.property_age)).scalar() or 0
    max_age = db.query(func.max(PropertyTrain.property_age)).scalar() or 0
    return {
        "neighborhoods": neighborhoods,
        "house_styles": house_styles,
        "overall_qual": qualities,
        "bedroom_abv_gr": bedrooms,
        "full_bath": baths,
        "sale_month": months,
        "property_age_range": {"min": int(min_age), "max": int(max_age)},
    }


@router.get("/price-analysis")
def price_analysis(db: Session = Depends(get_db)) -> dict:
    by_neighborhood = [
        {"neighborhood": neighborhood, "avg_price": round(avg_price or 0, 2), "count": count}
        for neighborhood, avg_price, count in db.query(
            PropertyTrain.neighborhood, func.avg(PropertyTrain.sale_price), func.count(PropertyTrain.id)
        ).group_by(PropertyTrain.neighborhood).all()
    ]
    by_style = [
        {"house_style": style, "avg_price": round(avg_price or 0, 2), "count": count}
        for style, avg_price, count in db.query(
            PropertyTrain.house_style, func.avg(PropertyTrain.sale_price), func.count(PropertyTrain.id)
        ).group_by(PropertyTrain.house_style).all()
    ]
    by_surface = [
        {"gr_liv_area": row.gr_liv_area, "sale_price": row.sale_price}
        for row in db.query(PropertyTrain.gr_liv_area, PropertyTrain.sale_price).limit(250).all()
    ]
    return {"by_neighborhood": by_neighborhood, "by_style": by_style, "by_surface": by_surface}


@router.get("/location-analysis")
def location_analysis(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(PropertyTrain.gr_liv_area, PropertyTrain.lot_area, PropertyTrain.sale_price).all()
    return [{"gr_liv_area": row[0], "lot_area": row[1], "sale_price": row[2]} for row in rows]


@router.get("/batch-predictions")
def batch_predictions(
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.query(BatchPrediction).order_by(BatchPrediction.id.desc()).limit(200).all()
    return [
        {
            "source_row_id": row.source_row_id,
            "gr_liv_area": row.gr_liv_area,
            "lot_area": row.lot_area,
            "overall_qual": row.overall_qual,
            "overall_cond": row.overall_cond,
            "bedroom_abv_gr": row.bedroom_abv_gr,
            "full_bath": row.full_bath,
            "garage_cars": row.garage_cars,
            "garage_area": row.garage_area,
            "neighborhood": row.neighborhood,
            "house_style": row.house_style,
            "sale_month": row.sale_month,
            "property_age": row.property_age,
            "predicted_price": row.predicted_price,
            "model_version": row.model_version,
        }
        for row in rows
    ]


@router.get("/prediction-history")
def prediction_history(
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = db.query(UserPrediction).order_by(UserPrediction.created_at.desc()).limit(20).all()
    return [
        {
            "id": row.id,
            "gr_liv_area": row.gr_liv_area,
            "lot_area": row.lot_area,
            "overall_qual": row.overall_qual,
            "overall_cond": row.overall_cond,
            "bedroom_abv_gr": row.bedroom_abv_gr,
            "full_bath": row.full_bath,
            "garage_cars": row.garage_cars,
            "garage_area": row.garage_area,
            "neighborhood": row.neighborhood,
            "house_style": row.house_style,
            "sale_month": row.sale_month,
            "property_age": row.property_age,
            "predicted_price": row.predicted_price,
            "lower_bound": row.lower_bound,
            "upper_bound": row.upper_bound,
            "model_version": row.model_version,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]


@router.get("/model-metrics/latest", response_model=ModelMetricsResponse)
def latest_model_metrics(
    db: Session = Depends(get_db),
) -> ModelMetricsResponse:
    row = db.query(ModelMetric).order_by(ModelMetric.created_at.desc()).first()
    if not row:
        raise HTTPException(status_code=404, detail="No model metrics found")
    return ModelMetricsResponse(
        model_name=row.model_name,
        model_version=row.model_version,
        mae=row.mae,
        rmse=row.rmse,
        r2=row.r2,
        train_rows=row.train_rows,
        feature_count=row.feature_count,
        created_at=row.created_at,
    )


@router.get("/model-metrics/history", response_model=ModelMetricsHistoryResponse)
def model_metrics_history(
    db: Session = Depends(get_db),
) -> ModelMetricsHistoryResponse:
    rows = db.query(ModelMetric).order_by(ModelMetric.created_at.asc()).all()
    return ModelMetricsHistoryResponse(
        items=[
            ModelMetricsResponse(
                model_name=row.model_name,
                model_version=row.model_version,
                mae=row.mae,
                rmse=row.rmse,
                r2=row.r2,
                train_rows=row.train_rows,
                feature_count=row.feature_count,
                created_at=row.created_at,
            )
            for row in rows
        ]
    )


@router.post("/predict")
def predict(
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    bundle = load_model()
    model = bundle["model"]
    validated_payload = validate_prediction_payload(payload)

    predicted_price = float(model.predict(pd.DataFrame([validated_payload])[FEATURES])[0])
    response = {
        "predicted_price": round(predicted_price, 2),
        "lower_bound": round(predicted_price * 0.9, 2),
        "upper_bound": round(predicted_price * 1.1, 2),
        "model_version": bundle.get("model_version"),
    }
    db.add(
        UserPrediction(
            gr_liv_area=validated_payload.get("GrLivArea"),
            lot_area=validated_payload.get("LotArea"),
            overall_qual=validated_payload.get("OverallQual"),
            overall_cond=validated_payload.get("OverallCond"),
            bedroom_abv_gr=validated_payload.get("BedroomAbvGr"),
            full_bath=validated_payload.get("FullBath"),
            garage_cars=validated_payload.get("GarageCars"),
            garage_area=validated_payload.get("GarageArea"),
            neighborhood=validated_payload.get("Neighborhood"),
            house_style=validated_payload.get("HouseStyle"),
            sale_month=validated_payload.get("MoSold"),
            property_age=validated_payload.get("property_age"),
            predicted_price=response["predicted_price"],
            lower_bound=response["lower_bound"],
            upper_bound=response["upper_bound"],
            model_version=response["model_version"],
        )
    )
    db.commit()
    return response


@router.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db)) -> dict:
    messages = payload.get("messages", [])
    if not messages:
        raise HTTPException(status_code=422, detail="messages is required")

    trimmed_messages = messages[-8:]
    user_messages = [message for message in trimmed_messages if message.get("role") == "user"]
    if not user_messages:
        raise HTTPException(status_code=422, detail="At least one user message is required")

    market_context = build_market_summary(db)
    system_prompt = (
        "Tu es un assistant d'analyse du marche immobilier.\n"
        "Reponds d'abord a partir du contexte fourni.\n"
        "Si une information manque, dis-le clairement.\n"
        "N'invente jamais de chiffres.\n"
        "Sois clair, concis et utile.\n\n"
        f"CONTEXTE MARCHE :\n{market_context}"
    )
    model_messages = [{"role": "system", "content": system_prompt}]
    model_messages.extend(
        {"role": message["role"], "content": message["content"]}
        for message in trimmed_messages
        if message.get("role") in {"user", "assistant"} and message.get("content")
    )

    try:
        answer = call_gemini_chat(model_messages, market_context)
        return {"answer": answer, "mode": "gemini"}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur Gemini: {exc}") from exc
