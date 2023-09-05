import json

from flask import Response

from src.serializers.equity import EquityJsonEnconder
from src.appservices.iservices.iequity_service import IEquityService
from src.interfaceadapters.controllers.icontrollers.iequity_controller import IEquityController

    
class EquityController(IEquityController):
    

    def __init__(self, equityservice:IEquityService) -> None:
        self.equityservice = equityservice

    def equity_list(self):
        result = self.equityservice.list()
        return Response(
            json.dumps(result, cls=EquityJsonEnconder),
            mimetype="application/json",
            status=200
            )