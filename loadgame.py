import tanks, agent, threading
import multiprocessing as mp

game = tanks.Game()
tanks.castle = tanks.Castle()

class Combine():
	def __init__(self, stage, num):
		self.stage=stage
		self.num=num


	def loadtanks(self):

		game.stage=self.stage
		game.nr_of_players=self.num
		print("stage %s starts, %s players"%(game.stage, game.nr_of_players))
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
			# playersinfo.append([player.rect, player.direction, player.speed])
			playersinfo.append([player.rect, player.direction, player.speed])
		d["players"] = playersinfo

		for enemy in tanks.enemies:
			enemiesinfo.append([enemy.rect, enemy.direction])
		d["enemies"] = enemiesinfo

		for bullet in tanks.bullets:
			bulletsinfo.append([bullet.rect, bullet.direction])
		d["bullets"] = bulletsinfo

		for bonus in tanks.bonuses:
			bonusesinfo.append([bonus.rect])
		d["bonuses"] = bonusesinfo

		d["tiles"]=game.level.mapr
		return d

	def start(self):

		ag=self.loadagent()
		p = threading.Thread(target=ag.run)
		p.start()
		self.loadtanks()

if __name__ == "__main__":
	stage=0
	num=1
	c=Combine(stage,num)
	c.start()
