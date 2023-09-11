from flask import Blueprint
from dependency_injector.wiring import inject, Provide
from application.dependency_container import DependencyContainer
from src.interfaceadapters.controllers.icontrollers.iequity_controller import IEquityController

blueprint = Blueprint('refresh', __name__)


@blueprint.route("/refresh", methods=["GET"])
@inject
def refresh_equity_blueprint(controller: IEquityController=Provide[DependencyContainer.equity_controller]):
    response = controller.refresh_data()
    return response