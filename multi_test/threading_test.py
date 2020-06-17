"""
    多线程测试
"""

import threading
import time


def add_to_queue():
    for i in range(0, 100):
        print("存入队列: {}".format(i))
        time.sleep(1)


def get_from_queue():
    for i in range(0, 100):
        print("队列: {}".format(i))
        # q.task_done()
        time.sleep(1)

# 创建线程
t1 = threading.Thread(target=add_to_queue)
# 设置为守护线程
t1.setDaemon(True)
# 启动线程
t1.start()

t2 = threading.Thread(target=get_from_queue)
t2.setDaemon(True)
t2.start()

# 队列加入主线线程, 等待队列中任务完成为止
# q.join()
t1.join()
t2.join()