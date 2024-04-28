import abc


class IMLFlowRepo(abc.ABC):

    @abc.abstractmethod
    def get_stock_mlflow_run_for_current_date(self, stock_index: str, current_date_str: str):
        pass
