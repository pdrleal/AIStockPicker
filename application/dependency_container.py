from dependency_injector import containers, providers
from src.appservices.constants_service import ConstantsService
from src.interfaceadapters.repositories.constants_repo import ConstantsRepo
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
    
    constants_repo= providers.Factory(ConstantsRepo)
    constants_service = providers.Factory(ConstantsService,constants_repo=constants_repo)
    
    equity_repo= providers.Factory(EquityRepo)
    equity_mapper= providers.Factory(EquityMapper)
    equity_service = providers.Factory(EquityService,constants_service= constants_service, equity_repo=equity_repo,equity_mapper=equity_mapper)
    equity_controller = providers.Factory(EquityController,equity_service=equity_service)