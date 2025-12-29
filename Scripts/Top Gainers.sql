SELECT 
    coin_name,
    MAX(price)- MIN(price) as price_change
FROM crypto_prices
WHERE $__timeFilter(created_at)
GROUP BY coin_name
ORDER BY price_change DESC
LIMIT 5;
