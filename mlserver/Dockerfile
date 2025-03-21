FROM python:3.10-buster

WORKDIR /app

RUN apt-get -y update && \
    apt-get -y install \
    apt-utils \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY . .
RUN pip install -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]
