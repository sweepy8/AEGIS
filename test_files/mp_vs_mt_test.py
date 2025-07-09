# Testing the cpu utilization and speed difference between
# true multiprocessing and fake GIL-limited multithreading

import multiprocessing
import threading
from time import sleep, time
from datetime import datetime

def A():
    while True:
        start = time()
        a = 0
        for x in range(0,10**8):
            a += x
        print(datetime.now().time(), ": A took", round(time() - start, 6), "s") 
        

def B():
    while True:
        start = time()
        b = 0
        for x in range(0, 10**8):
            b += x
        print(datetime.now().time(), ": B took", round(time() - start, 6), "s") 


def threading_test():
    ta = threading.Thread(target=A, daemon=True)
    tb = threading.Thread(target=B, daemon=True)

    ta.start()
    tb.start()

    ta.join()
    tb.join()

def mp_test():
    mpa = multiprocessing.Process(target=A)
    mpb = multiprocessing.Process(target=B)

    mpa.start()
    mpb.start()

    mpa.join()
    mpb.join()

if __name__ == "__main__":
    #threading_test()
    mp_test()