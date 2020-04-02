import tanks, agent, threading, os, logging, thread, time, Queue
import multiprocessing as mp

game = tanks.Game()
tanks.castle = tanks.Castle()
lock=threading.Lock()

class Combine():
	def __init__(self, stage, num):
		self.stage=stage
		self.num=num

	def loadtanks(self,event):
		while not event.is_set():
			game.stage=self.stage
			game.nr_of_players=self.num
		# print("stage %s starts, %s players"%(game.stage, game.nr_of_players))
			logging.info("stage %s starts, %s players"%(game.stage, game.nr_of_players))
			game.nextLevel()

	def loadtanks(self):
		# while not event.is_set():
		game.stage=self.stage
		game.nr_of_players=self.num
	# print("stage %s starts, %s players"%(game.stage, game.nr_of_players))
		logging.info("stage %s starts, %s players"%(game.stage, game.nr_of_players))
		game.nextLevel()

	def loadagent(self):
		self.agent=agent.Agent(self.num)
		return self.agent

	@staticmethod
	def getData():
		# if hasattr()
		d=dict()
		playersinfo = []
		enemiesinfo = []
		bulletsinfo = []
		bonusesinfo = []
		for player in tanks.players:
			# print("players >0")
			# logging.info("players >0")

			# playersinfo.append([player.rect, player.direction, player.speed])
			playersinfo.append([player.rect, player.direction, player.speed])
		d["players"] = playersinfo

		for enemy in tanks.enemies:
			# print("enemies>0")
			# logging.info("enemies>0")
			enemiesinfo.append([enemy.rect, enemy.direction])
		d["enemies"] = enemiesinfo

		for bullet in tanks.bullets:
			# print("bullets > 0")
			# logging.info("bullets>0")
			bulletsinfo.append([bullet.rect, bullet.direction])
		d["bullets"] = bulletsinfo

		for bonus in tanks.bonuses:
			# print("bonuses>0")
			# logging.info("bonuses>0")
			bonusesinfo.append([bonus.rect])
		d["bonuses"] = bonusesinfo

		d["tiles"]=game.level.mapr
		return d

	def start(self):

		ag=self.loadagent()
		# p1 = threading.Thread(target=ag.run)
		# event = threading.Event()
		# queue = Queue.Queue(maxsize=10)
		# p1=threading.Thread(target=ag.getAction,args=(0,queue,event))
		# p2=threading.Thread(target=ag.applyAction, args=(0,queue,event))
		# # p3=threading.Thread(target=self.loadtanks, args=(event,))
		# p1.start()
		# p2.start()
		# # p3.start()

		p1=threading.Thread(target=ag.run,)
		p1.start()
		self.loadtanks()
			# time.sleep(0.1)


		# self.loadtanks()
		# p.join()

		# p=mp.Process(target=ag.run)
		# p2=threading.Thread(target=self.loadtanks)
		# p.start()
		# p2.start()
		# if not game.running:
		# 	self.kill_process(p2)

	def kill_process(self, p):
		#p.terminate()
		os.kill(p.pid,9)
		print "kill ai_process!!"

if __name__ == "__main__":
	stage=0
	num=1
	c=Combine(stage,num)
	c.start()
