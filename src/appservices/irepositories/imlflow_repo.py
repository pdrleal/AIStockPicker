import abc


class IMLFlowRepo(abc.ABC):

    @abc.abstractmethod
    def get_stock_mlflow_run_for_last_validation_date(self, stock_index: str, last_validation_date_str: str):
        pass
