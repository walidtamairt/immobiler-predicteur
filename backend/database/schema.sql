CREATE TABLE IF NOT EXISTS properties_train (
    id SERIAL PRIMARY KEY,
    gr_liv_area FLOAT,
    lot_area FLOAT,
    overall_qual INT,
    overall_cond INT,
    bedroom_abv_gr INT,
    full_bath INT,
    garage_cars FLOAT,
    garage_area FLOAT,
    neighborhood TEXT,
    house_style TEXT,
    sale_month INT,
    property_age INT,
    sale_price FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name TEXT,
    model_version TEXT,
    mae FLOAT,
    rmse FLOAT,
    r2 FLOAT,
    train_rows INT,
    feature_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS batch_predictions (
    id SERIAL PRIMARY KEY,
    source_row_id INT NULL,
    gr_liv_area FLOAT,
    lot_area FLOAT,
    overall_qual INT,
    overall_cond INT,
    bedroom_abv_gr INT,
    full_bath INT,
    garage_cars FLOAT,
    garage_area FLOAT,
    neighborhood TEXT,
    house_style TEXT,
    sale_month INT,
    property_age INT,
    predicted_price FLOAT,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_predictions (
    id SERIAL PRIMARY KEY,
    gr_liv_area FLOAT,
    lot_area FLOAT,
    overall_qual INT,
    overall_cond INT,
    bedroom_abv_gr INT,
    full_bath INT,
    garage_cars FLOAT,
    garage_area FLOAT,
    neighborhood TEXT,
    house_style TEXT,
    sale_month INT,
    property_age INT,
    predicted_price FLOAT,
    lower_bound FLOAT,
    upper_bound FLOAT,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS external_market_context (
    id SERIAL PRIMARY KEY,
    source TEXT,
    country TEXT,
    indicator TEXT,
    year INT,
    value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scraped_market_trends (
    id SERIAL PRIMARY KEY,
    city TEXT,
    average_price FLOAT,
    trend TEXT,
    description TEXT,
    source_url TEXT,
    source_title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS external_context_summaries (
    id SERIAL PRIMARY KEY,
    summary_kind TEXT,
    source TEXT,
    summary_text TEXT,
    rows_collected INT,
    average_indicator_value FLOAT,
    payload_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
