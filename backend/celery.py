from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 설정 파일의 경로를 환경 변수로 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Celery 앱 생성
app = Celery("backend")

# Celery 설정 로드
app.config_from_object("django.conf:settings", namespace="CELERY")

# 장고 애플리케이션을 찾아서 Celery 작업을 등록
app.autodiscover_tasks()
