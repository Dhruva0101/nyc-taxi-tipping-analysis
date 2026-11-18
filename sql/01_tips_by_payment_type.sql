-- Step 0: first look at tipping by payment type (paste into the BigQuery console).
-- payment_type codes (NYC TLC): 1 = credit card, 2 = cash, 3 = no charge, 4 = dispute.
-- Note: cash tips are usually NOT recorded, so cash shows ~0% tips.
SELECT
  payment_type,
  COUNT(*)                                             AS trips,
  ROUND(AVG(SAFE_DIVIDE(tip_amount, fare_amount)) * 100, 2) AS avg_tip_pct,
  ROUND(APPROX_QUANTILES(SAFE_DIVIDE(tip_amount, fare_amount), 100)[OFFSET(50)] * 100, 2) AS median_tip_pct
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022`
WHERE fare_amount > 0
GROUP BY payment_type
ORDER BY trips DESC;
