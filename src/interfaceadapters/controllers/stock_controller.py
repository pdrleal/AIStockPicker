import json

from flask import Response

from src.serializers.stock import EnhancedJSONEncoder
from src.appservices.iservices.istock_service import IStockService
from src.interfaceadapters.controllers.icontrollers.istock_controller import IStockController

    
class StockController(IStockController):
    

    def __init__(self, stock_service:IStockService) -> None:
        self.stock_service = stock_service

    def refresh_data(self):
        result = self.stock_service.refresh_data()
        #return the response as json
        return Response(json.dumps(result,cls=EnhancedJSONEncoder), mimetype='application/json')
        

    