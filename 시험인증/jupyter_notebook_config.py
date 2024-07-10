# jupyter_notebook_config.py

c.NotebookApp.token = ''  # 빈 문자열로 설정하여 토큰을 사용하지 않음
c.NotebookApp.password = ''  # 비밀번호를 설정하지 않음 (optional)
c.NotebookApp.allow_origin = '*'  # 모든 원본에서 접속을 허용 (optional)
c.NotebookApp.open_browser = False  # 브라우저 자동 열기 비활성화 (optional)
c.NotebookApp.ip = '0.0.0.0'  # 모든 IP에서 접속 허용