SELECT
  created_at AS "time",
  price AS "actual_price",
  AVG(price) OVER(ORDER BY created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) AS "moving_avg"
FROM crypto_prices
WHERE coin_name = '$coin_name' AND $__timeFilter(created_at)
ORDER BY created_at;
