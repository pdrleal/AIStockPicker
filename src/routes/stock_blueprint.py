from flask import Blueprint
from dependency_injector.wiring import inject, Provide
from application.dependency_container import DependencyContainer
from src.interfaceadapters.controllers.icontrollers.istock_controller import IStockController

blueprint = Blueprint('refresh', __name__)


@blueprint.route("/refresh", methods=["GET"])
@inject
def refresh_stock_blueprint(controller: IStockController=Provide[DependencyContainer.stock_controller]):
    response = controller.refresh_data()
    return response