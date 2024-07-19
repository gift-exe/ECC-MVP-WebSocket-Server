FROM python:3.10-slim

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

RUN mkdir app

RUN cd app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80


CMD bash -c "supervisord -c supervisord.conf"