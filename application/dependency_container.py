from dependency_injector import containers, providers

from src.appservices.stock_service import StockService
from src.interfaceadapters.controllers.stock_controller import StockController
from src.interfaceadapters.repositories.constants_repo import ConstantsRepo
from src.interfaceadapters.repositories.mlflow_repo import MLFlowRepo
from src.interfaceadapters.repositories.stock_repo import StockRepo


def setup_dependency_container(app, modules=None, packages=None):
    container = DependencyContainer()
    app.container = container
    app.container.wire(modules=modules, packages=packages)
    return app


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration()

    constants_repo = providers.Factory(ConstantsRepo)

    stock_repo = providers.Factory(StockRepo)
    mlflow_repo = providers.Factory(MLFlowRepo)
    stock_service = providers.Factory(StockService, constants_repo=constants_repo, stock_repo=stock_repo, mlflow_repo=mlflow_repo)
    stock_controller = providers.Factory(StockController, stock_service=stock_service)
