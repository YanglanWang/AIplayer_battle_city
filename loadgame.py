import tanks, agent, threading, os, logging, thread, time, Queue, pygame
import multiprocessing as mp

game = tanks.Game()
tanks.castle = tanks.Castle()
lock=threading.Lock()

class Combine():
	def __init__(self, stage, num):
		self.stage=stage
		self.num=num

	def loadtanks(self):
		game.stage=self.stage
		game.nr_of_players=self.num
	# print("stage %s starts, %s players"%(game.stage, game.nr_of_players))
		logging.info("stage %s starts, %s players"%(game.stage, game.nr_of_players))
		game.nextLevel()
		while not game.running:
			game.stage-=1
			for player in tanks.players:
				player.lives=3
			time.sleep(3)
			game.nextLevel()
			if hasattr(game, "stage") and game.stage>=35:
				os._exit(0)

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
		p2=threading.Thread(target=self.loadtanks)
		p1=threading.Thread(target=ag.run, args=(p2,))
		# p3=threading.Thread(target=self.game_over,)
		p1.start()
		# p2=threading.Thread(target=game_over)
		p2.start()
		# p3.start()
		# self.loadtanks()
			# time.sleep(0.1)

	def kill_process(self, p):
		#p.terminate()
		os.kill(p.pid,9)
		print "kill ai_process!!"

if __name__ == "__main__":
	stage=0
	num=1
	c=Combine(stage,num)
	c.start()
