from multiprocessing import Process, Queue

def f():
    # q.put([42, None, 'hello'])
	a=100

if __name__ == '__main__':
    # q = Queue()
    # p = Process(target=f, args=(q,))
    # p.start()
    # info=q.get()
    # print info[0]    # prints "[42, None, 'hello']"
    # p.join()
	global a
	f()
	print(a)