import json

from flask import Response

from src.serializers.equity import EnhancedJSONEncoder
from src.appservices.iservices.iequity_service import IEquityService
from src.interfaceadapters.controllers.icontrollers.iequity_controller import IEquityController

    
class EquityController(IEquityController):
    

    def __init__(self, equity_service:IEquityService) -> None:
        self.equity_service = equity_service

    def refresh_data(self):
        result = self.equity_service.refresh_data()
        #return the response as json
        return Response(json.dumps(result,cls=EnhancedJSONEncoder), mimetype='application/json')
        

    