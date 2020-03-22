import pyautogui
import tanks, math, heapq, pygame

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
			playerSurroundingInfo["myself"]=[player.rect,player.direction,player.speed]
			if len(players) == 1:
				playerSurroundingInfo["otherplayers"]=[]
			else:
				for others in players:
					if player!=others:
						playerSurroundingInfo["otherplayers"]=[others.rect,others.direction,others.speed]

			playerSurroundingInfo["enemies"]=[]
			for enemy in enemies:
				playerSurroundingInfo["enemies"].append([enemy.rect,enemy.direction,enemy.speed,enemy.paused])

			playerSurroundingInfo["bullets"]=[]
			for bullet in bullets:
				playerSurroundingInfo["bullets"].append([bullet.rect,bullet.direction,bullet.speed])

			playerSurroundingInfo["tiles"]=[]
			for tile in self.level.mapr:
				playerSurroundingInfo["tiles"].append([tile.rect,tile.type])

			playerSurroundingInfo["bonuses"]=bonuses

			if playerSurroundingInfo["bonuses"]!=None:
				cmd=self.getPath(player.rect.topleft,bonuses[0].rect.topleft, playerSurroundingInfo)

				if not cmd:
					pyautogui.press(cmd)
			else:
				sortedEnemies=sorted(playerSurroundingInfo["enemies"],key=lambda x:self.euclidean_distance((x[0].left,
						x[0].top), (player[0].left, player[0].top)))
				if len(sortedEnemies)!=0:
					enemy=sortedEnemies[0]
					inline_direction = self.inline_with_enemy(player.rect, enemy.rect)

					astar_direction = self.getPath(player.rect.topleft, enemy.rect.topleft, playerSurroundingInfo)
					

					# perform bullet avoidance
					shoot, direction = self.bullet_avoidance(self.mapinfo[3][0], 6, self.mapinfo[0], astar_direction,
															 inline_direction)


	def inline_with_enemy(self, player_rect, enemy_rect):
		# vertical inline
		if enemy_rect.left <= player_rect.centerx <= enemy_rect.right and abs(
				player_rect.top - enemy_rect.bottom) <= 151:
			# enemy on top
			if enemy_rect.bottom <= player_rect.top:
				print('enemy on top')
				return 0
			# enemy on bottom
			elif player_rect.bottom <= enemy_rect.top:
				print('enemy on bottom')
				return 2
		# horizontal inline
		if enemy_rect.top <= player_rect.centery <= enemy_rect.bottom and abs(
				player_rect.left - enemy_rect.right) <= 151:
			# enemy on left
			if enemy_rect.right <= player_rect.left:
				print('enemy on left')
				return 3
			# enemy on right
			elif player_rect.right <= enemy_rect.left:
				print('enemy on right')
				return 1
		return False


	def getPath(self, origin, destination, info):
		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

		openSet=[]
		cameFrom=dict()
		gScore=dict()
		gScore[origin]=0
		fScore=dict()
		fScore[origin]=self.euclidean_distance(origin,destination)
		heapq.heappush(openSet,origin)
		while len(openSet)!=0:
			current=heapq.heappop(openSet)
			if self.isDestination(current,destination):
				path=self.reconstructPath(cameFrom,current)
				break
			openSet.remove(current)
			speed=info["myself"][2]
			for point in self.neighbor(current, speed, destination):
				tentatice_gScore=gScore[current]+speed
				if point not in gScore.keys() or (tentatice_gScore<gScore[point])
					cameFrom[point]=current
					gScore[point]=tentatice_gScore
					fScore[point]=gScore[point]+self.euclidean_distance(point,destination)
					if point not in openSet:
						openSet.append(point)

		if len(path)>0:
			next=path[0]
			next_left, next_top = next
			current_left, current_top = current
			# up
			if current_top > next_top:
				dir_cmd = 'up'
			# down
			elif current_top < next_top:
				dir_cmd = 'down'
			# left
			elif current_left > next_left:
				dir_cmd = 'left'
			# right
			elif current_left < next_left:
				dir_cmd = 'right'
			return dir_cmd
		else:
			return False

	def neighbour(self, current, speed, destination):
		top, left = current
		# Rect(left, top, width, height)
		allowable_move = []

		# move up
		new_top = top - speed
		new_left = left
		if not (new_top < 0):
			move_up = True
			temp_rect = pygame.Rect(new_left, new_top, 26, 26)

			# check collision with enemy except goal
			for enemy in self.mapinfo[1]:
				if enemy[0] is not destination:
					if temp_rect.colliderect(enemy[0]):
						move_up = False
						break

			# check collision with tile
			if move_up:
				for tile in self.mapinfo[2]:
					# not a grass tile
					if tile[1] != 4:
						if temp_rect.colliderect(tile[0]):
							move_up = False
							break

			if move_up:
				allowable_move.append((new_left, new_top))

		# move right
		new_top = top
		new_left = left + speed
		if not (new_left > (416 - 26)):
			move_right = True
			temp_rect = pygame.Rect(new_left, new_top, 26, 26)

			# check collision with enemy except goal
			for enemy in self.mapinfo[1]:
				if enemy[0] is not destination:
					if temp_rect.colliderect(enemy[0]):
						move_right = False
						break

			# check collision with tile
			if move_right:
				for tile in self.mapinfo[2]:
					# not a grass tile
					if tile[1] != 4:
						if temp_rect.colliderect(tile[0]):
							move_right = False
							break

			if move_right:
				allowable_move.append((new_left, new_top))

		# move down
		new_top = top + speed
		new_left = left
		if not (new_top > (416 - 26)):
			move_down = True
			temp_rect = pygame.Rect(new_left, new_top, 26, 26)

			# check collision with enemy except goal
			for enemy in self.mapinfo[1]:
				if enemy[0] is not destination:
					if temp_rect.colliderect(enemy[0]):
						move_down = False
						break

			# check collision with
			if move_down:
				for tile in self.mapinfo[2]:
					# not a grass tile
					if tile[1] != 4:
						if temp_rect.colliderect(tile[0]):
							move_down = False
							break

			if move_down:
				allowable_move.append((new_left, new_top))

		# move left
		new_top = top
		new_left = left - speed
		if not (new_left < 0):
			move_left = True
			temp_rect = pygame.Rect(new_left, new_top, 26, 26)

			# check collision with enemy except goal
			for enemy in self.mapinfo[1]:
				if enemy[0] is not destination:
					if temp_rect.colliderect(enemy[0]):
						move_left = False
						break

			# check collision with tile
			if move_left:
				for tile in self.mapinfo[2]:
					# not a grass tile
					if tile[1] != 4:
						if temp_rect.colliderect(tile[0]):
							move_left = False
							break

			if move_left:
				allowable_move.append((new_left, new_top))

		return allowable_move

	def reconstructPath(self, cameFrom, current):
		totalPath=[current]
		while current in cameFrom.keys:
			current=cameFrom[current]
			totalPath.insert(0,current)
		return totalPath


	def isDestination(self, current, destination):
		center_x1, center_y1 = current
		center_x2, center_y2 = destination
		if abs(center_x1 - center_x2) <= 7 and abs(center_y1 - center_y2) <= 7:
			return True
		else:
			return False


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