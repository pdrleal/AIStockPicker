use AIStockPicker;


-- Check if the trigger exists and drop it if it does
DROP TRIGGER IF EXISTS update_last_date_news_sentiment;
DROP TRIGGER IF EXISTS update_last_date_stock_values;
DROP TRIGGER IF EXISTS update_last_date_social_sentiment;

DELIMITER //

-- Trigger for LANDING_NEWS_SENTIMENT
CREATE TRIGGER update_last_date_news_sentiment
AFTER INSERT ON LANDING_NEWS_SENTIMENT
FOR EACH ROW
BEGIN
    UPDATE `VARIABLES`
    SET `value` = CONVERT_TZ(NOW(), 'SYSTEM', 'Europe/Lisbon') 
    WHERE `key`='Last Update Date';
END;
//

-- Trigger for LANDING_STOCK_VALUES
CREATE TRIGGER update_last_date_stock_values
AFTER INSERT ON LANDING_STOCK_VALUES
FOR EACH ROW
BEGIN
    UPDATE `VARIABLES`
    SET `value` = CONVERT_TZ(NOW(), 'SYSTEM', 'Europe/Lisbon') 
    WHERE `key`='Last Update Date';
END;
//

-- Trigger for LANDING_SOCIAL_SENTIMENT
CREATE TRIGGER update_last_date_social_sentiment
AFTER INSERT ON LANDING_SOCIAL_SENTIMENT
FOR EACH ROW
BEGIN
    UPDATE `VARIABLES`
    SET `value` = CONVERT_TZ(NOW(), 'SYSTEM', 'Europe/Lisbon') 
    WHERE `key`='Last Update Date';
END;
//

DELIMITER ;
