DROP procedure IF EXISTS `AIStockPicker`.`update_last_update_date`;
DELIMITER //

-- Create or replace a procedure to update the Last Update Date variable
CREATE PROCEDURE update_last_update_date()
BEGIN
    -- Update Last Update Date variable
    UPDATE AIStockPicker.VARIABLES
    SET value = CURRENT_TIMESTAMP
    WHERE `key` = 'Last Update Date';
END //

DELIMITER ;

-- Create triggers for LANDING_NEWS_SENTIMENT table
DELIMITER //
CREATE TRIGGER update_last_update_date_news_insert
AFTER INSERT ON AIStockPicker.LANDING_NEWS_SENTIMENT
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

CREATE TRIGGER update_last_update_date_news_update
AFTER UPDATE ON AIStockPicker.LANDING_NEWS_SENTIMENT
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

DELIMITER ;

-- Create triggers for LANDING_SOCIAL_SENTIMENT table
DELIMITER //
CREATE TRIGGER update_last_update_date_social_insert
AFTER INSERT ON AIStockPicker.LANDING_SOCIAL_SENTIMENT
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

CREATE TRIGGER update_last_update_date_social_update
AFTER UPDATE ON AIStockPicker.LANDING_SOCIAL_SENTIMENT
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

DELIMITER ;

-- Create triggers for LANDING_STOCK_VALUES table
DELIMITER //
CREATE TRIGGER update_last_update_date_stock_values_insert
AFTER INSERT ON AIStockPicker.LANDING_STOCK_VALUES
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

CREATE TRIGGER update_last_update_date_stock_values_update
AFTER UPDATE ON AIStockPicker.LANDING_STOCK_VALUES
FOR EACH ROW
BEGIN
    CALL update_last_update_date();
END//

DELIMITER ;


