import pymysql
from abc import ABC, abstractmethod
import pandas as pd

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
            port=self.cfg.port,
            host=self.cfg.url,
        )



def get_connection(db_client: DBClient):
    return db_client.get_connection()


def load_data(db_client: DBClient, sql_command, params=None):
    cursor = db_client.get_connection().cursor()
    with cursor as c:
        c.execute(sql_command, params) #(date_from, date_to))
        result = c.fetchall()
        columns = [col[0] for col in c.description]
    return pd.DataFrame(result, columns=columns)


def save_df_to_csv(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index=False)
