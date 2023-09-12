from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from src.appservices.iservices.iconstants_service import IConstantsService

class ConstantsService(IConstantsService):

    def __init__(self, constants_repo:IConstantsRepo):
        self.constants_repo = constants_repo

    def stocks_indices(self):
        return self.constants_repo.stocks_indices()
    