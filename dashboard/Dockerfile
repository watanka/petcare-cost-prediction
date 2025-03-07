FROM python:3.10.6-slim

WORKDIR /app
RUN pip install poetry

# Poetry가 가상 환경을 생성하지 않도록 설정
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --no-interaction

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py"]