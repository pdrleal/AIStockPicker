from dependency_injector import containers, providers
from src.dtos.equity_mapper import EquityMapper

from src.interfaceadapters.repositories.equity_repo import EquityRepo
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
    equity_repo= providers.Factory(EquityRepo)
    equity_mapper= providers.Factory(EquityMapper)
    equity_service = providers.Factory(EquityService,equityrepo=equity_repo,equitymapper=equity_mapper)
    equity_controller = providers.Factory(EquityController,equityservice=equity_service)