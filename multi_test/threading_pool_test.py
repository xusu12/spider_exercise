import time
# 导入线程池
from multiprocessing.dummy import Pool


def get_page_data(i):
    print(f'this is {i}')
    time.sleep(1)


# while True:
pool = Pool()
for i in range(25):
    pool.apply_async(get_page_data, args=(i, ))

pool.close()
pool.join()
