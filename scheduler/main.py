import os
from omegaconf import DictConfig
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from src.jobs.retrieve import Retriever
from src.jobs.monitor import Monitor, DataAmountAlertPolicy
from src.jobs.notify import Notifier, EmailSender, HttpRequestSender, Receiver
from src.jobs.report import Reporter
from src.middleware.db_client import DBClient


DB_URL = os.getenv('DB_URL')
PORT = os.getenv('DB_PORT')
USER_NAME = os.getenv('USER_NAME')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD =  os.getenv("EMAIL_PASSWORD")

SEND_EMAIL_ADDRESS = os.getenv("SEND_EMAIL_ADDRESS")
SEND_EMAIL_PASSWORD = os.getenv("SEND_EMAIL_PASSWORD")
RECEIVE_EMAIL_ADDRESS= os.getenv("RECEIVE_EMAIL_ADDRESS")

MODEL_SERVER_URL=os.getenv("MODEL_SERVER_URL")
RECORD_SAVE_PATH = os.getenv("RECORD_SAVE_PATH")

MONITORING_INTERVAL_HOURS = os.getenv("MONITORING_INTERVAL_HOURS")

cfg = DictConfig(
    {
        "url": DB_URL,
        "port": int(PORT),
        "user": USER_NAME,
        "password": DB_PASSWORD,
        "name": DB_NAME,
    }
)

email_sender = EmailSender('smtp.naver.com', 587, SEND_EMAIL_ADDRESS, SEND_EMAIL_PASSWORD)
server_request_sender = HttpRequestSender()

email_receiver = Receiver(email = RECEIVE_EMAIL_ADDRESS)
server = Receiver(http_server = MODEL_SERVER_URL) # TODO: receiver가 서버 주소를 갖고 있는 건 조금 이상하다.. 이메일 수신 리시버와 학습요청을 받는 서버가 같은 리시버 클래스를 갖기 때문에 혼동이 생긴다.

notifier = Notifier()

policy = DataAmountAlertPolicy()
monitor = Monitor(RECORD_SAVE_PATH, policy)
reporter = Reporter()

db_client = DBClient(cfg)
retriever = Retriever(db_client)

def db_monitoring():
    sql = """
    SELECT pet_breed_id, birth, age, gender, neuter_yn, weight_kg, claim_price, disease_name
    FROM pet_insurance_claim_ml_fake_data;
    """
    retrieved_data = retriever.retrieve_dataset(sql)#date_from="2021-01-01", date_to=datetime.now().strftime("%Y-%m-%d"))
    monitor.update_record(retrieved_data)
    
    
    try:
        # 데이터를 확인하고 필요시 재학습을 요청한다.
        alert = monitor.alert(retrieved_data)
        if alert:
            notifier.send(server_request_sender, None, server)
            
    except Exception as e: 
        report = reporter.generate_report(e)
        notifier.send(email_sender, report, email_receiver)



if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(db_monitoring, 'interval', hours=MONITORING_INTERVAL_HOURS)
    

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass