from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Property


def get_overview(db: Session) -> dict:
    avg_price, median_proxy, avg_price_per_m2, total = db.query(
        func.avg(Property.price),
        func.avg(Property.price),
        func.avg(Property.price / func.nullif(Property.surface, 0)),
        func.count(Property.id),
    ).one()
    return {
        "average_price": round(avg_price or 0, 2),
        "median_price": round(median_proxy or 0, 2),
        "average_price_per_m2": round(avg_price_per_m2 or 0, 2),
        "total_properties": total or 0,
    }


def get_price_analysis(db: Session) -> dict:
    by_city = [
        {"city": city, "avg_price": round(avg_price or 0, 2), "count": count}
        for city, avg_price, count in db.query(
            Property.city, func.avg(Property.price), func.count(Property.id)
        ).group_by(Property.city).all()
    ]
    by_type = [
        {"property_type": ptype, "avg_price": round(avg_price or 0, 2), "count": count}
        for ptype, avg_price, count in db.query(
            Property.property_type, func.avg(Property.price), func.count(Property.id)
        ).group_by(Property.property_type).all()
    ]
    by_surface = [
        {"surface_bucket": bucket, "avg_price": round(avg_price or 0, 2), "count": count}
        for bucket, avg_price, count in db.query(
            (func.floor(Property.surface / 25) * 25).label("bucket"),
            func.avg(Property.price),
            func.count(Property.id),
        ).group_by("bucket").order_by("bucket").all()
    ]
    return {"by_city": by_city, "by_type": by_type, "by_surface": by_surface}


def get_location_analysis(db: Session) -> list[dict]:
    rows = db.query(Property.latitude, Property.longitude, Property.price).filter(
        Property.latitude.isnot(None), Property.longitude.isnot(None)
    ).all()
    return [{"latitude": lat, "longitude": lon, "price": price} for lat, lon, price in rows]


def get_filters(db: Session) -> dict:
    cities = [row[0] for row in db.query(Property.city).distinct().order_by(Property.city).all() if row[0]]
    property_types = [
        row[0] for row in db.query(Property.property_type).distinct().order_by(Property.property_type).all() if row[0]
    ]
    energy_ratings = [
        row[0] for row in db.query(Property.energy_rating).distinct().order_by(Property.energy_rating).all() if row[0]
    ]
    return {
        "cities": cities,
        "property_types": property_types,
        "energy_ratings": energy_ratings,
    }
