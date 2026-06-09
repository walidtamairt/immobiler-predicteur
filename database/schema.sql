CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    price DOUBLE PRECISION NOT NULL,
    surface DOUBLE PRECISION NOT NULL,
    rooms INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    city VARCHAR(120),
    zipcode VARCHAR(20),
    property_type VARCHAR(50),
    year_built INTEGER,
    property_age INTEGER,
    energy_rating VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    sale_month INTEGER
);

CREATE TABLE IF NOT EXISTS prediction_logs (
    id SERIAL PRIMARY KEY,
    input_payload JSONB NOT NULL,
    predicted_price DOUBLE PRECISION NOT NULL,
    lower_bound DOUBLE PRECISION NOT NULL,
    upper_bound DOUBLE PRECISION NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    mae DOUBLE PRECISION NOT NULL,
    rmse DOUBLE PRECISION NOT NULL,
    r2 DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
