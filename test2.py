import pyautogui

from tanks import wholemain2
import multiprocessing as mp

def main():
	v = mp.Value('i', 0)
	lock = mp.Lock()
	surrounding_info=dict()
	process = mp.Process(target=wholemain2, args=(v, lock, surrounding_info))
	process.start()
	with lock:
		v.value=0
		print("lll")
	print("hhh")

if __name__=="__main__":
	main()
