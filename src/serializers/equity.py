import json

class EquityJsonEnconder(json.JSONEncoder):
    def default (self,o):
        try:
            to_serialize = {
                'code': str(o.code),
                'index': o.index,
                'price': o.price,
            }
            return to_serialize
        except AttributeError:
            return super().default(o)