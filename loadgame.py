import tanks, agent
import multiprocessing as mp

game=tanks.Game()
tanks.castle=tanks.Castle()
class LoadGame():
	def __init(self):
		self.stage=0

	def autorun(self, stage=0, num=1):
		game.stage=stage
		game.nr_of_players=num
		print("stage %s starts, %s players"%(game.stage, game.nr_of_players))
		game.nextLevel()

	def getData(self):
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

		return d

	def start(self, stage, num):
		ag = agent.Agent()

		# p = threading.Thread(target=ai1.operations)
		self.autorun(stage, num)
		p = mp.process(target=ag.getAction())
		p.start()

if __name__ == "__main__":
	autostart=LoadGame()
	autostart.start(0,1)
