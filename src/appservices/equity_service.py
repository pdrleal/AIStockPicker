from src.appservices.irepositories.iequity_repo import IEquityRepo
from src.appservices.iservices.iequity_service import IEquityService


class EquityService(IEquityService):

    def __init__(self, equityrepo:IEquityRepo) -> None:
        self.equityrepo = equityrepo

    def list(self):
        return self.equityrepo.list()