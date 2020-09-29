"""
    进程池
"""


import random
import time
import requests
from multiprocessing import Pool


def get_page_data(i):
    print(f'this is {i}')
    time.sleep(1)



def main():
    while True:
        pool = Pool()
        for i in range(20):
            pool.apply_async(get_page_data, args=(i,))

        pool.close()
        pool.join()


if __name__ == '__main__':
    main()