-- Step 1: cleaned, analysis-ready card trips with derived features.
-- Save the result as a table in your own dataset, e.g. `your_project.taxi.card_trips_2022`.
-- {year} is filled in by src/run_analysis.py; replace it by hand in the console.
SELECT
  t.pickup_datetime,
  EXTRACT(MONTH FROM t.pickup_datetime)      AS month,
  EXTRACT(HOUR FROM t.pickup_datetime)       AS hour,
  EXTRACT(DAYOFWEEK FROM t.pickup_datetime) IN (1, 7) AS is_weekend,  -- 1 = Sunday, 7 = Saturday
  EXTRACT(HOUR FROM t.pickup_datetime) NOT BETWEEN 6 AND 19 AS is_night,
  t.pickup_location_id IN ('132', '138')
    OR t.dropoff_location_id IN ('132', '138') AS is_airport,   -- 132 = JFK, 138 = LaGuardia
  z.borough                                  AS pickup_borough,
  t.trip_distance,
  t.fare_amount,
  t.tip_amount,
  SAFE_DIVIDE(t.tip_amount, t.fare_amount)   AS tip_pct
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_{year}` AS t
LEFT JOIN `bigquery-public-data.new_york_taxi_trips.taxi_zone_geom` AS z
  ON t.pickup_location_id = z.zone_id
WHERE t.payment_type = '1'                   -- card only: cash tips are not recorded
  AND t.fare_amount BETWEEN 2.5 AND 500      -- drop zero/negative and extreme fares
  AND t.trip_distance BETWEEN 0.1 AND 100
  AND t.tip_amount >= 0
  AND SAFE_DIVIDE(t.tip_amount, t.fare_amount) <= 1  -- tips over 100% are almost always data errors
  AND TIMESTAMP_DIFF(t.dropoff_datetime, t.pickup_datetime, MINUTE) BETWEEN 1 AND 180
