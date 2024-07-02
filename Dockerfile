FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install djangorestframework
RUN pip install drf-yasg
RUN pip install -r requirements.txt
RUN pip install cryptography

EXPOSE 8000