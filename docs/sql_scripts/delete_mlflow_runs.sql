-- Step 1: Delete from mlflow.latest_metrics
DELETE FROM mlflow.latest_metrics WHERE run_uuid IN (
    SELECT run_uuid FROM (
        SELECT run_uuid FROM mlflow.runs ORDER BY start_time DESC LIMIT 2
    ) AS subquery
);

-- Step 2: Delete from mlflow.tags
DELETE FROM mlflow.tags WHERE run_uuid IN (
    SELECT run_uuid FROM (
        SELECT run_uuid FROM mlflow.runs ORDER BY start_time DESC LIMIT 2
    ) AS subquery
);

-- Step 3: Delete from mlflow.metrics
DELETE FROM mlflow.metrics WHERE run_uuid IN (
    SELECT run_uuid FROM (
        SELECT run_uuid FROM mlflow.runs ORDER BY start_time DESC LIMIT 2
    ) AS subquery
);

-- Step 4: Delete from mlflow.params
DELETE FROM mlflow.params WHERE run_uuid IN (
    SELECT run_uuid FROM (
        SELECT run_uuid FROM mlflow.runs ORDER BY start_time DESC LIMIT 2
    ) AS subquery
);

-- Step 5: Finally, delete from mlflow.runs
DELETE FROM mlflow.runs WHERE run_uuid IN (
    SELECT run_uuid FROM (
        SELECT run_uuid FROM mlflow.runs ORDER BY start_time DESC LIMIT 2
    ) AS subquery
);