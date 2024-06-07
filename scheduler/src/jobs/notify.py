from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from email.mime.text import MIMEText
import smtplib
import ssl
import requests

     
class Sender(ABC):
    @abstractmethod
    def send(self, message: str):
        raise NotImplementedError
        


@dataclass
class Receiver:
    email: Optional[str] = None
    phone_number: Optional[str] = None
    http_server: Optional[str] = None

    def validate_necessary_info(self, sender: Sender):
        if not getattr(self, sender.type):
            raise ValueError(f"{sender.type} 정보가 없습니다.")
            
            

class Notifier:
        
    def send(self, sender: Sender, message: dict, receiver: Receiver):
        sender.send(message, receiver)



class EmailSender(Sender):
    type = 'email'
    def __init__(self, smtp_server: str, port: int, email: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.email = email
        self.password = password
        self.context = ssl.create_default_context()

    def send(self, message: dict, receiver: Receiver):
        receiver.validate_necessary_info(self)
        
        msg = MIMEText(message['content'])
        msg['Subject'] = message['subject']
        msg['From'] = self.email
        msg['To'] = receiver.email
        
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, receiver.email, msg.as_string())
    

class HttpRequestSender(Sender):
    type = 'http_server'
        
    def send(self, message: Optional[str], receiver: Receiver): 
        receiver.validate_necessary_info(self)
        try:
            response = requests.post(receiver.http_server, params=message)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"GET request failed: {e}")
            return None
        
            
