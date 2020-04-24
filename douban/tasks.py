import requests
from celery import Celery

# 创建celery对象
app = Celery('img_tasks', broker='redis://127.0.0.1:6379/3')

# 让celery自动发现任务
app.autodiscover_tasks(['celery_tasks.sms'])


# 定义任务函数  使用@app.task来装饰这个函数
@app.task(name='tasks')
def download_pic(image_url, image_path):
    try:
        image = requests.get(image_url, stream=True)
        with open(image_path, 'wb') as img:
            img.write(image.content)
    except Exception as e:
        print(e)
