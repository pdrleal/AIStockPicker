CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `admin`@`%` 
    SQL SECURITY DEFINER
VIEW `mlflow`.`mlflow_log` AS
    SELECT 
        `t`.`run_uuid` AS `run_uuid`,
        `t`.`stock_index` AS `stock_index`,
        `t`.`run_timestamp` AS `run_timestamp`,
        `t`.`current_date` AS `current_date`,
        `t`.`predicted_date` AS `predicted_date`,
        `t`.`is_retrain` AS `is_retrain`,
        `t`.`used_features` AS `used_features`,
        `t`.`technical_indicators_combinations` AS `technical_indicators_combinations`,
        `t`.`used_lags` AS `used_lags`,
        `t`.`metric_optimized` AS `metric_optimized`,
        `t`.`model` AS `model`,
        `t`.`model_params` AS `model_params`,
        `t`.`predicted_signal` AS `predicted_signal`,
        `t`.`predicted_return` AS `predicted_return`,
        `t`.`predicted_close_price` AS `predicted_close_price`,
        `m`.`accuracy` AS `accuracy`,
        `m`.`f1_score` AS `f1_score`,
        `m`.`information_ratio` AS `information_ratio`,
        `m`.`mape` AS `mape`,
        `m`.`precision` AS `precision`,
        `m`.`adjusted_r2_score` AS `adjusted_r2_score`,
        `m`.`recall` AS `recall`,
        `m`.`rmse` AS `rmse`
    FROM
        (((SELECT 
            `mlflow`.`tags`.`run_uuid` AS `run_uuid`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'stock_index') THEN `mlflow`.`tags`.`value`
                END)) AS `stock_index`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'run_timestamp') THEN `mlflow`.`tags`.`value`
                END)) AS `run_timestamp`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'current_date') THEN `mlflow`.`tags`.`value`
                END)) AS `current_date`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'predicted_date') THEN `mlflow`.`tags`.`value`
                END)) AS `predicted_date`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'is_retrain') THEN `mlflow`.`tags`.`value`
                END)) AS `is_retrain`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'used_features') THEN `mlflow`.`tags`.`value`
                END)) AS `used_features`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'technical_indicators_combinations') THEN `mlflow`.`tags`.`value`
                END)) AS `technical_indicators_combinations`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'used_lags') THEN `mlflow`.`tags`.`value`
                END)) AS `used_lags`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'metric_optimized') THEN `mlflow`.`tags`.`value`
                END)) AS `metric_optimized`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'model') THEN `mlflow`.`tags`.`value`
                END)) AS `model`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'model_params') THEN `mlflow`.`tags`.`value`
                END)) AS `model_params`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'predicted_signal') THEN `mlflow`.`tags`.`value`
                END)) AS `predicted_signal`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'predicted_return') THEN `mlflow`.`tags`.`value`
                END)) AS `predicted_return`,
                MAX((CASE
                    WHEN (`mlflow`.`tags`.`key` = 'predicted_close_price') THEN `mlflow`.`tags`.`value`
                END)) AS `predicted_close_price`
        FROM
            `mlflow`.`tags`
        GROUP BY `mlflow`.`tags`.`run_uuid`)) `t`
        JOIN (SELECT 
            `mlflow`.`metrics`.`run_uuid` AS `run_uuid`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'accuracy') THEN `mlflow`.`metrics`.`value`
                END)) AS `accuracy`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'f1_score') THEN `mlflow`.`metrics`.`value`
                END)) AS `f1_score`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'information_ratio') THEN `mlflow`.`metrics`.`value`
                END)) AS `information_ratio`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'mape') THEN `mlflow`.`metrics`.`value`
                END)) AS `mape`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'precision') THEN `mlflow`.`metrics`.`value`
                END)) AS `precision`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'adjusted_r2_score') THEN `mlflow`.`metrics`.`value`
                END)) AS `adjusted_r2_score`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'recall') THEN `mlflow`.`metrics`.`value`
                END)) AS `recall`,
                MAX((CASE
                    WHEN (`mlflow`.`metrics`.`key` = 'rmse') THEN `mlflow`.`metrics`.`value`
                END)) AS `rmse`
        FROM
            `mlflow`.`metrics`
        GROUP BY `mlflow`.`metrics`.`run_uuid`) `m` ON ((`t`.`run_uuid` = `m`.`run_uuid`)))
    ORDER BY `t`.`run_timestamp` DESC