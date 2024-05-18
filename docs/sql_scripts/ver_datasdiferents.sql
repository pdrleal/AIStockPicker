-- Ver Porque numero de datas no clean e News são diferentes

SELECT * FROM AIStockPicker.LANDING_NEWS_SENTIMENT l
left join AIStockPicker.CLEAN_DATA c on l.date=DATE(c.datetime) and c.stock_index=l.stock_index
WHERE DATE(c.datetime) IS NULL