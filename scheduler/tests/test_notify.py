import pytest

import pandas as pd

from src.jobs.notify import EmailSender, Receiver
from src.jobs.monitor import DataAmountAlertPolicy, Monitor

def test_send_email(mocker):
    # smtp 서버 모킹
    mock_smtp = mocker.MagicMock(name = "src.jobs.notify.smtplib.SMTP")
    mocker.patch("src.jobs.notify.smtplib.SMTP", new = mock_smtp)

    sender = EmailSender(smtp_server = 'smtp.naver.com',
                         port = 11,
                         email = 'sample',
                         password = 'pw'
                         )
    
    
    sender.send(message = {'content': 'hi', 'subject' : 'sample_test'},
                receiver = Receiver(email = "example@naver.com"))
    
    
    assert mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 1
    
def test_alert_policy():
    '''
    재학습 요청조건 테스트
    '''
    
    minimum_num_to_trigger_retrain = 30
    
    old_row_cnt = 10000
    new_row_cnt = old_row_cnt + minimum_num_to_trigger_retrain
    
    policy = DataAmountAlertPolicy()
    trigger_on = policy.analyze(previous_df = pd.DataFrame.from_dict({'pets': [pet_id for pet_id in range(old_row_cnt)]}),
                                new_df = pd.DataFrame.from_dict({'pets': [pet_id for pet_id in range(new_row_cnt)]}),
                                )
    
    assert trigger_on
    
    
def test_monitor_keeps_record_new(mocker):
    '''
    재학습 요청조건이 발동되었을 때, 모니터에서 새로운 비교기준을 저장한다.
    '''
    
    df = pd.DataFrame.from_dict({'pets': [pet_id for pet_id in range(10)]})
    
    
    pd_to_csv_mocking = mocker.patch('pandas.DataFrame.to_csv')
    pd_read_csv_mocking = mocker.patch('pandas.read_csv')
    
    monitor = Monitor('sample.csv', DataAmountAlertPolicy())
    monitor.update_record(df)
    
    pd_to_csv_mocking.assert_called_once()
    pd_read_csv_mocking.assert_called_once()
    
    