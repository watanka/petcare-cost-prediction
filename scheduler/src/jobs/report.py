from dataclasses import dataclass
from datetime import datetime


class Reporter:        
    
    def generate_report(self, exception: Exception)-> dict:
        
        when = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        
        
        subject = f'[양육비 예측 파이프라인 오류 발생 알림({when})]'
        content = f'''
            에러 발생 시간: {when},
            에러 타입: {type(exception).__name__},
            에러 메세지: {str(exception)}
            에러 Traceback: {exception.__traceback__}
        '''
        
        return {'subject': subject, 'content' : content}
                
        