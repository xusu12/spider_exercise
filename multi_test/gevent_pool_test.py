"""
    协程池
"""
from gevent import monkey
# 打猴子补丁, 让程序在sleep,socket等一些耗时任务的时候, 自动切换
monkey.patch_all()
from gevent.pool import Pool
import time

# 创建协程池对象
p = Pool()


# 定义一个执行任务的方法
def func(msg):
    for i in range(0, 10):
        print(msg)
        time.sleep(1)
        print(i)


# 协程池执行异步任务
for i in range(10):
    p.apply_async(func, (f"协程{i}",))

# 将协程任务加入到主线线程, 让主线程等待协程任务完成
p.join()