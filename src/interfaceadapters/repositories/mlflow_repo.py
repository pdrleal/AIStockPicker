import os

import mlflow
from dotenv import load_dotenv, find_dotenv

from src.appservices.irepositories.imlflow_repo import IMLFlowRepo


class MLFlowRepo(IMLFlowRepo):
    def __init__(self):
        load_dotenv(find_dotenv())
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        db_name = os.getenv('MYSQL_DB_NAME_MLFLOW')
        host = os.getenv('MYSQL_HOST')
        port = os.getenv('MYSQL_PORT')
        experiment_name = os.getenv('MLFLOW_EXPERIMENT')
        mlflow.set_tracking_uri(f'mysql://{user}:{password}@{host}:{port}/{db_name}')
        mlflow.set_experiment(experiment_name)

    def get_stock_mlflow_run_for_current_date(self, stock_index: str, current_date_str: str):
        runs_df = mlflow.search_runs(search_all_experiments=True,
                                     filter_string=f"tags.stock_index = '{stock_index}' "
                                                   f"AND tags.current_date = '{current_date_str}'",
                                     order_by=["tags.run_timestamp DESC"])
        if runs_df.empty:
            return None
        try:
            last_run_id = runs_df.iloc[0].run_id
        except IndexError:
            return None
        client = mlflow.tracking.MlflowClient()
        return client.get_run(run_id=last_run_id)


