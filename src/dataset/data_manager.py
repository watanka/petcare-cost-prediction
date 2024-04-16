import pymysql
import pandas as pd



def get_connection(db_host, db_user, db_password, db_name, db_port):
    return pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, port = db_port)
    
    
    
def load_data(conn, sql_command, date_from, date_to):
    cursor = conn.cursor()
    with cursor as c:
        c.execute(sql_command,(date_from, date_to) )
        result = c.fetchall()
        columns = [col[0] for col in cursor.description]        
    return pd.DataFrame(result, columns = columns)


def save_df_to_csv(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index = False)