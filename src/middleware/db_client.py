import pymysql
from abc import ABC, abstractmethod


class AbstractDBClient(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get_connection(self):
        raise NotImplementedError
    


class DBClient(AbstractDBClient):
    def __init__(self, cfg):
        self.cfg = cfg

    def get_connection(self):
        return pymysql.connect(
            user=self.cfg.user, 
            password=self.cfg.password, 
            db=self.cfg.name, 
            port = self.cfg.port,
            host = self.cfg.url
        )