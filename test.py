import pyautogui
import tanks,math
pyautogui.press('enter')

class LoadGame(tanks.Game):
	def __init__(self):
		tanks.Game.__init__(self)


	def autoshowMenu(self,bothplayers):
		if bothplayers:
			pyautogui.press('down')
		pyautogui.press('enter')
		self.autonextLevel(bothplayers)


	def autonextLevel(self,bothplayers):
		global players,enemies,bullets,bonuses
		for player in players:
			playerSurroundingInfo = dict()
			playerSurroundingInfo["myself"]=[player.start_position,player.start_direction,player.speed]
			if len(players) == 1:
				playerSurroundingInfo["otherplayers"]=[]
			else:
				for others in players:
					if player!=others:
						playerSurroundingInfo["otherplayers"]=[others.start_position,others.start_direction,others.speed]

			playerSurroundingInfo["enemies"]=[]
			for enemy in enemies:
				playerSurroundingInfo["enemies"].append([enemy.rect.topleft,enemy.direction,enemy.speed,enemy.paused])

			playerSurroundingInfo["bullets"]=[]
			for bullet in bullets:
				playerSurroundingInfo["bullets"].append([bullet.rect.topleft,bullet.direction,bullet.speed])

			playerSurroundingInfo["tiles"]=[]
			for tile in self.level.mapr:
				playerSurroundingInfo["tiles"].append([tile.rect.topleft,tile.type])

			playerSurroundingInfo["bonuses"]=bonuses

			if playerSurroundingInfo["bonuses"]!=None:
				nextdirection=self.getBonus(bonuses[0], playerSurroundingInfo)
			else:
				sortedEnemies=sorted(playerSurroundingInfo["enemies"],key=lambda x:self.euclidean_distance((x[0].left,
						x[0].top), (player[0].left, player[0].top)))
				for


	def getBonus(self, destination, info):
		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

		origin=info["myself"][0]
		o_x,o_y=origin
		d_x,d_y=destination.rect.topleft
		if d_x-o_x<26 or o_x-d_x<32:
			print("d is on the same vertical road with o")
			if o_y+26<=d_y:
				print("o is on the top of d")
				return DIR_DOWN
			if d_y+30<=o_y:
				print("d is on the top of o")
				return DIR_UP
		elif d_x-o_x>=26:
			return DIR_RIGHT
		else:
			return DIR_LEFT





	def getDirection(self,destination, info, isEnemy):
		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

		origin=info["myself"][0]
		o_x,o_y=origin
		d_x,d_y=destination.rect.topleft
		if abs(d_x-o_x)<=6:
			print("d is on the same vertical road with o")
			if o_y+32<d_y:
				print("o is on the top of d")
				if isEnemy and destination.direction!=DIR_UP:
					return DIR_DOWN,True
				if not isEnemy:
					return DIR_DOWN,False
			elif d_y+32<o_y:
				print("d is on the top of o")
				if isEnemy and destination.direction!=DIR_DOWN:
					return DIR_UP,True
				if not isEnemy:
					return DIR_UP, False
			else:
				print("o and d will crack down")
		elif d_x-o_x>6:
			print("d is on the right hand of x")
		elif d_x<o_x:
			print("d is on the left hand of x")


	def euclidean_distance(self, x, y):
		return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

		if not bothplayers:

			tanks.Game.nextLevel()



	def run(self,auto,bothplayers):
		if not auto:
			tanks.Game.showMenu()
		else:
			self.autoshowMenu(bothplayers)







if __name__=='__main__':
	autogame=LoadGame()
	autogame.run(auto=True,bothplayers=False)