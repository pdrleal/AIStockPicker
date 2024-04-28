import json
import re
from datetime import datetime

from flask import Response

from src.appservices.iservices.istock_service import IStockService
from src.interfaceadapters.controllers.icontrollers.istock_controller import IStockController
from src.serializers.stock import EnhancedJSONEncoder


class StockController(IStockController):

    def __init__(self, stock_service: IStockService) -> None:
        self.stock_service = stock_service

    def refresh_data(self):
        result = self.stock_service.refresh_data()
        return Response(json.dumps(result, cls=EnhancedJSONEncoder), mimetype='application/json')

    def forecast_data(self, request_args: dict):
        stock_index = request_args.get('stock_index')
        current_date = request_args.get('current_date')
        if stock_index is None:
            return "Missing 'stock_index' parameter", 400
        if current_date is None:
            current_date = datetime.now()
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", current_date) is not None:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")
        else:
            return "Invalid date parameter. Date format must be yyyy-mm-dd.", 400

        result = self.stock_service.forecast_data(stock_index, current_date)
        return Response(json.dumps(result, cls=EnhancedJSONEncoder), mimetype='application/json')

    def build_portfolio(self, request_args: dict):
        current_date = request_args.get('current_date')
        if current_date is None:
            current_date = datetime.now()
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", current_date) is not None:
            current_date = datetime.strptime(current_date, "%Y-%m-%d")
        else:
            return "Invalid date parameter. Date format must be yyyy-mm-dd.", 400

        result = self.stock_service.build_portfolio(current_date)
        return Response(json.dumps(result, cls=EnhancedJSONEncoder), mimetype='application/json')
    def test_performance(self, request_args: dict):
        start_date = request_args.get('start_date')
        end_date = request_args.get('end_date')

        if start_date is None or end_date is None:
            return "Missing 'start_date' or 'end_date' parameter", 400
        if re.match(r"^\d{4}-\d{2}-\d{2}$", start_date) is None or re.match(r"^\d{4}-\d{2}-\d{2}$", end_date) is None:
            return "Invalid date parameter. Date format must be yyyy-mm-dd.", 400
        # Convert string to datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        result = self.stock_service.test_performance(start_date, end_date)
        return Response(json.dumps(result, cls=EnhancedJSONEncoder), mimetype='application/json')

