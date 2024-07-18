FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install django-redis
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput

RUN pip install daphne channels channels-redis aiohttp

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]