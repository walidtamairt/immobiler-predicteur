# Database Architecture and RGPD

## Purpose of each table

| Table | Role |
| --- | --- |
| `properties_train` | Stores the cleaned training dataset used by dashboards, market analysis and model preparation. |
| `model_metrics` | Stores each training run result with version, MAE, RMSE, R2, training volume and feature count. |
| `batch_predictions` | Stores batch inferences generated from the cleaned test dataset for downstream analysis. |
| `user_predictions` | Stores user-triggered predictions from the application UI for traceability and product analytics. |

## Separation logic

### Why business data is separated from metrics

`properties_train` contains the real estate observations used as business facts. `model_metrics` contains monitoring metadata about the model itself. This separation keeps dashboards fast, avoids mixing operational facts with ML evaluation logs, and supports cloud maintenance more cleanly.

### Why batch predictions are separated from user predictions

`batch_predictions` corresponds to offline inference on a predefined test dataset. `user_predictions` captures interactive predictions made from the frontend. The two usages have different frequencies, different semantics and different query patterns, so they should not share the same table.

### Why this is adapted to a cloud application

The structure is lightweight, query-friendly and easy to evolve in Neon PostgreSQL. It minimizes storage cost, keeps requests simple for dashboards, and isolates data domains so each service can read only what it needs.

## Physical modeling logic

### Column types

- Numeric business fields use `FLOAT` or `INT` for analytics and ML compatibility.
- Categorical dimensions such as `neighborhood` and `house_style` use `TEXT`.
- Temporal tracking fields use `TIMESTAMP`.

### Primary keys

Each table uses a simple `SERIAL PRIMARY KEY`, which gives:

- a stable row identifier,
- easy pagination,
- efficient sorting for latest records,
- straightforward joins if needed later.

### Relational simplicity

The schema intentionally stays simple:

- no unnecessary join tables,
- no deeply nested structures,
- no denormalization beyond what supports analytics speed.

This is appropriate for a cloud MVP with dashboards, API access and ML tracking.

### Fast querying for dashboards

Dashboards mainly aggregate:

- average prices,
- counts,
- quality-based price levels,
- seasonality by month,
- neighborhood comparisons.

This schema supports these queries directly from `properties_train` without expensive transformations at runtime.

## RGPD and data minimization

### No personal data

The project does not store:

- names,
- emails,
- phone numbers,
- personal identifiers,
- direct user identity data.

Only technical real estate attributes are used.

### Why this is compliant in principle

The data model only retains the attributes necessary to:

- estimate a property price,
- build dashboards,
- monitor model behavior,
- support the assistant with market context.

### Data minimization

The dataset was deliberately reduced before storage:

- many noisy or low-value columns were removed,
- only the most relevant predictive features were preserved,
- the storage volume is limited,
- the injected data is capped for scalability.

This demonstrates a sobriety-by-design approach aligned with RGPD minimization principles.
