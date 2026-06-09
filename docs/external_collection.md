# External Dynamic Collection

## Objective

The external collection complements the local Ames Housing dataset with a lightweight public economic indicator source.

## Implemented script

File:

- [backend/etl/fetch_external_context.py](/d:/Projet estate/backend/etl/fetch_external_context.py)

## Technology used

- `requests`
- `pandas`

## Source used

The script queries the World Bank API for a France economic indicator related to market context.

## What the script does

1. Calls a public API.
2. Parses the JSON payload.
3. Converts the response to a pandas DataFrame.
4. Keeps only a few useful columns.
5. Saves the result as CSV.
6. Produces a summary JSON for complementary market context.

## Output files

- `data/external/external_market_context.csv`
- `data/external/external_market_summary.json`

## Role in the project

This source does not replace the training dataset.
It acts as an external contextual layer that can enrich documentation or the assistant prompt with macro-economic market information.
