# Dockerfile

# Jupyter Notebook 이미지를 기반으로 함
FROM jupyter/minimal-notebook:latest

# 유저 설정을 변경 (root로 변경)
USER root

COPY . .

# 필요한 패키지 설치 (예: 추가적인 Python 패키지)
RUN pip install pandas matplotlib

# Jupyter Notebook 설정 파일을 복사
COPY jupyter_notebook_config.py /home/jovyan/.jupyter/

# 유저 설정을 다시 변경 (다시 jovyan 유저로 변경)
USER jovyan