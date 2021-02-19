"""
    多进程
"""

import time
import multiprocessing


def task(i):
    for j in range(5):
        print(f'这是进程{i}')
        print(j)
        time.sleep(100)


if __name__ == '__main__':
    for i in range(10):
        p = multiprocessing.Process(target=task, args=(i, ))
        p.start()
