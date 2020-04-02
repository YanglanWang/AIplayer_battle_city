import random, logging, threading, time, Queue

SENTINEL = object()

def producer(queue, event):
    """Pretend we're getting a message from the network."""
    while not event.is_set():
        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        queue.put(message)
    logging.info("Producer received EXIT event. Exiting")

def consumer(queue, event):
    """Pretend we're saving a number in the database."""

    while not event.is_set() or not queue.empty():
        message = queue.get()
        logging.info("Consumer storing message: %s  (queue size=%s)", message,
                     queue.qsize(),)
    logging.info("Consumer received EXIT event. Exiting")

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # logging.getLogger().setLevel(logging.DEBUG)
    event=threading.Event()
    queue=Queue.Queue(maxsize=10)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    #     executor.submit(producer, pipeline)
    #     executor.submit(consumer, pipeline)
    p1=threading.Thread(target=producer, args=(queue,event))
    p2=threading.Thread(target=consumer, args=(queue,event))
    p1.start()
    p2.start()
    time.sleep(0.1)
    logging.info("Main: about to set event")
    event.set()

