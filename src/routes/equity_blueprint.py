from flask import Blueprint
from dependency_injector.wiring import inject, Provide
from application.dependency_container import DependencyContainer
from src.interfaceadapters.controllers.icontrollers.iequity_controller import IEquityController

blueprint = Blueprint('equity', __name__)


@blueprint.route("/equities", methods=["GET"])
@inject
def get_equities_blueprint(controller: IEquityController=Provide[DependencyContainer.equity_controller]):
    response = controller.equity_list()
    return response