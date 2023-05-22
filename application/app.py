from flask import Flask
from concurrent.futures import ThreadPoolExecutor
import time
import logging
import sys
import os
import signal

app = Flask(__name__)
my_array = []
is_allocating = False
thread_pool = ThreadPoolExecutor(max_workers=1)
logger = logging.getLogger(__name__)

def allocate_memory():
    global my_array, is_allocating
    while is_allocating:
        my_array += [0] * (1<<20)
        array_size = len(my_array)
        logger.info(f"Array size: {sys.getsizeof(my_array) >> 20 } MB")
        time.sleep(1)  # Sleep for 1 second

def shutdown_handler(signum, frame):
    global my_array, is_allocating
    is_allocating = False
    my_array = []
    thread_pool.shutdown(wait=False)
    logger.info(f"received signal {signum}, shutting down...")
    sys.exit(0)

@app.route('/health')
def health():
    logger.debug("Health OK")
    return 'OK', 200

@app.route('/up')
def up():
    global is_allocating
    logger.info("Received up command")
    if not is_allocating:
        is_allocating = True
        thread_pool.submit(allocate_memory)
        return 'Memory allocation started', 200
    return 'Already allocating', 200

@app.route('/down')
def down():
    global is_allocating, my_array
    logger.info("Received down command")
    is_allocating = False
    my_array = []
    return 'Memory allocation stopped', 200

if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get('PYTHON_LOGLEVEL', 'INFO').upper())
    logging.getLogger('werkzeug').setLevel("ERROR")

    init_mem_size=int(os.environ.get('INIT_MEM_SIZE', '0')) // 8 # each int takes 8 bytes
    dummy_array = [0] * init_mem_size

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host='0.0.0.0')


