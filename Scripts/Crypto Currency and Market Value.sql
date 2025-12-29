WITH te AS (
  SELECT
    coin_name AS metric,
    price,
    created_at AS "time",
    AVG(price) OVER (PARTITION BY coin_name) as avg_price,
    LAST_VALUE(price) OVER (
      PARTITION BY coin_name 
      ORDER BY created_at 
      RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_price
  FROM crypto_prices
  WHERE created_at > now() - interval '2 hour'
)

SELECT 
  metric, 
  MAX(time) as time,
  last_price as "last price",
  CASE
    WHEN last_price > avg_price THEN '🔺' 
    WHEN last_price < avg_price THEN '🔻' 
    ELSE '───'
  END AS trend
FROM te
GROUP BY metric, last_price, avg_price
ORDER BY 2;
