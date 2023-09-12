from src.appservices.iservices.iconstants_service import IConstantsService
from src.dtos.istock_mapper import IStockMapper
from src.domain.aggregates.stock import Stock
from src.appservices.irepositories.istock_repo import IStockRepo
from src.appservices.iservices.istock_service import IStockService


class StockService(IStockService):

    def __init__(self, constants_service: IConstantsService, stock_repo:IStockRepo, stock_mapper: IStockMapper):
        self.constants_service = constants_service
        self.stock_repo = stock_repo
        self.stock_mapper = stock_mapper

    def refresh_data(self):
        
        #retrieve stock indices from constants_service
        stock_indices=self.constants_service.stocks_indices()
        
        # map each stock in the repo.get_all() to dto list
        stock_dto_list = list(map(self.stock_mapper.map_stock_to_dto, self.stock_repo.get_all()))
            
        #self.perform_refresh(stock_indices, stock_dto_list)
        
        return stock_dto_list
    
    #def perform_refresh(self,stock_indices, stock_dto_list):
    #    for stock_index in stock_indices:
    #        if stock_index not in stock_dto_list:
    #            self.stock_repo.call_stock_data(stock_index)
    #        else:
    #            self.update_stock(stock_index)
    #    pass

    """
     def get_stock(self, stock_id):
        return self.stock_repository.get_stock_by_id(stock_id)

    def get_equities(self):
        return self.stock_repository.get_equities()

    def create_stock(self, stock):
        return self.stock_repository.create_stock(stock)

    def update_stock(self, stock_id, stock):
        return self.stock_repository.update_stock(stock_id, stock)

    def delete_stock(self, stock_id):
        return self.stock_repository.delete_stock(stock_id)
    """ 
    