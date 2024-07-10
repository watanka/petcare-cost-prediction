import pymysql
import pandas as pd
from src.middleware.db_client import DBClient


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
