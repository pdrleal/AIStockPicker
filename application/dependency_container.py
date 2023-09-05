from dependency_injector import containers, providers

from src.interfaceadapters.repositories.memequity_repo import MemEquityRepo
from src.appservices.equity_service import EquityService
from src.interfaceadapters.controllers.equity_controller import EquityController


def setup_dependency_container(app, modules=None, packages=None):
    container = DependencyContainer()
    app.container = container
    app.container.wire(modules=modules, packages=packages)
    return app


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration()
    equity_repo= providers.Factory(MemEquityRepo)
    equity_service = providers.Factory(EquityService,equityrepo=equity_repo)
    equity_controller = providers.Factory(EquityController,equityservice=equity_service)