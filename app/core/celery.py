import os
from celery import Celery

# 创建 Celery 实例
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=["app.tasks"]  # 包含任务模块
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    worker_max_tasks_per_child=200,  # 每个worker处理200个任务后重启
    worker_prefetch_multiplier=1  # 限制worker预取任务数量
)