from .redis import redis

def fail(message: str, status_code: int = 400):
    return ({
        "code":"-1",
        "data":{},
        "msg": message
    }, status_code)


def ok(data= None, status_code = 200):
    return ({
        "code": 0 ,
        "data": data if data else {},
        "msg": "ojbk"
    }, status_code)