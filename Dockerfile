FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install django-redis
RUN pip install -r requirements.txt

RUN pip install daphne channels channels-redis aiohttp

EXPOSE 8000