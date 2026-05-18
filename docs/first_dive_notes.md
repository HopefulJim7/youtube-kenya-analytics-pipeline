# First Dive Notes

## Goal

Validate that the project can connect to the YouTube Data API and identify target Kenyan channels.

## First Milestone

Successfully search for `Citizen TV Kenya` and print possible channel matches with their channel IDs.

## Why This Matters

Before building daily snapshots, dbt models, Airflow DAGs, or dashboards, we need reliable channel identifiers. YouTube channel names and handles can change, but channel IDs are stable.

## Next Step After This

Once the API test works, update `config/channels.yml` with confirmed `channel_id` values.