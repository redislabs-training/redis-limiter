""" User API token rate limiter

"""

import redis
from redis import RedisError
import sys
import signal
import argparse
import random
import string
import time
import threading
import datetime
from random import randint
from time import sleep

ARGS=None
STOP=False
conn=None


def main(argv):
    global conn
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='redistroy, Provision random data and do things')
    parser.add_argument('--host', default="127.0.0.1", help='Host (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', type=int, default=6379, help='Port (default: 6379)')
    parser.add_argument('-u', '--user', required=False, help='User')
    parser.add_argument('-P', '--password', required=False, help='Password')
    parser.add_argument('-c', '--concurrency', type=int, required=True, help='Concurrency')
    parser.add_argument('-i', '--iterations', type=int, default=1000, required=False, help='Iterations')
    parser.add_argument('-t', '--threshold', type=int, required=True, help='Allowed operations per minute')
    args = parser.parse_args()
    global ARGS
    ARGS=args

    pool = redis.ConnectionPool(host=ARGS.host, port=ARGS.port, db=0, decode_responses=True)
    conn = redis.Redis(connection_pool=pool)

    threads = []
    for x in range(0, ARGS.concurrency):
        processThread = threading.Thread(target=api_call)
        threads.append(processThread)
        processThread.start()

    start = time.time()
    for x in threads:
        x.join()

    end = time.time()
    print("Duration: " + str(format(round(end-start, 2))))
    sys.exit()


def api_call():
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    print("initializing API " + token)
    for x in range(ARGS.iterations):
        if not limiter(token, ARGS.threshold):
            print(token + ' is exceeding the threshold')
        else:
            print(token + ' ok')
        sleep(randint(0,100)/1000)


def limiter(token, threshold):
    token_minute = "api:" + token + ":" + str(datetime.datetime.now().minute)
    ops = conn.get(token_minute)
    if (ops is not None) and (int(ops) > threshold):
        return False
    p = conn.pipeline(transaction=True)
    p.incr(token_minute)
    p.expire(token_minute, 59)
    p.execute()
    return True


def signal_handler(sig, frame):
    print("Simulation stopped")
    global STOP
    STOP=True    


if __name__ == "__main__":
   main(sys.argv[1:])