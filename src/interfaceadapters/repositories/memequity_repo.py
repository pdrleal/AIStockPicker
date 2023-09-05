from src.domain.aggregates.equity import Equity
from src.appservices.irepositories.iequity_repo import IEquityRepo

class MemEquityRepo(IEquityRepo):
        
    def list(self):
        equities = [
            {
                "code": "f853578c-fc0f-4e65-81b8-566c5dffa35a",
                "index": "AAPL",
                "price": 39
            },  
            {
                "code": "fe2c3195-aeff-487a-a08f-e0bdc0ec6e9a",
                "index": "AMZN",
                "price": 66
            }
        ]
        return [Equity.from_dict(i) for i in equities]