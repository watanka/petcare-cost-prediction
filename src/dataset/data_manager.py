import pymysql
import pandas as pd



def get_connection(db_host, db_user, db_password, db_name, db_port):
    return pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, port = db_port)
    
    
    
def load_data(conn, sql_command):
    cur = conn.cursor()
    sql = 'select pet_breed_id, birth, gender, neuter_yn, weight_kg, claim_price, pi.created_at, pi.updated_at from pet as p left join pet_insurance_claim as pi on pi.pet_id=p.id where type_of_claims="치료비" and status="접수";' 

    cur.execute(sql_command)

    return pd.DataFrame(cur.fetchall())


def save_df_to_csv(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index = False)