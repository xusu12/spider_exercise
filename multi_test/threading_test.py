"""
    多线程测试
"""

import threading
import time


def task(i):
    for j in range(5):
        print(f'这是线程{i}')
        print(j)
        time.sleep(1)


for i in range(20):
    t = threading.Thread(target=task, args=(i, ))
    # t.setDaemon(True)
    t.start()
# t.join()


