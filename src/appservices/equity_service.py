from src.dtos.iequity_mapper import IEquityMapper
from src.domain.aggregates.equity import Equity
from src.appservices.irepositories.iequity_repo import IEquityRepo
from src.appservices.iservices.iequity_service import IEquityService


class EquityService(IEquityService):

    def __init__(self, equityrepo:IEquityRepo, equitymapper: IEquityMapper):
        self.equityrepo = equityrepo
        self.equitymapper = equitymapper

    def refresh_data(self):
        # map each equity in the repo.get_all() to dto list
        equity_dto_list = []
        for equity in self.equityrepo.get_all():
            equity_dto_list.append(self.equitymapper.map_equity_to_dto(equity))
        
        return equity_dto_list
    """
     def get_equity(self, equity_id):
        return self.equity_repository.get_equity_by_id(equity_id)

    def get_equities(self):
        return self.equity_repository.get_equities()

    def create_equity(self, equity):
        return self.equity_repository.create_equity(equity)

    def update_equity(self, equity_id, equity):
        return self.equity_repository.update_equity(equity_id, equity)

    def delete_equity(self, equity_id):
        return self.equity_repository.delete_equity(equity_id)
    """ 
    