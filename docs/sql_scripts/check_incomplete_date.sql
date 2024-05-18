SELECT Count(cd.datetime)
FROM AIStockPicker.CLEAN_DATA cd
JOIN (
    SELECT DATE(`datetime`) AS date, stock_index
    FROM AIStockPicker.CLEAN_DATA
    GROUP BY DATE(`datetime`), stock_index
    HAVING COUNT(*) <> 26
) subquery
ON DATE(cd.`datetime`) = subquery.date AND cd.stock_index = subquery.stock_index;