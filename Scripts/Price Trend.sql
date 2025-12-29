SELECT
 coin_name,
 price,
 created_at
FROM
 crypto_prices 
WHERE coin_name = '$coin_name' AND $__timeFilter(created_at)
