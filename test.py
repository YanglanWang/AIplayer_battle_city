import pyautogui
import  math, heapq, tanks, pygame
import multiprocessing as mp
from multiprocessing import Manager
# pyautogui.press('enter')

class LoadGame(tanks.Game):
	def __init__(self):
		tanks.Game.__init__(self)



	def getAction(self,arr,lock,d):
	# def getAction(self):
	# 	info=q.get()

		isSecondPlayer=False
		# keyboard={1:['up','w'],2:['right','d'],3:['down','s'],4:['left','a'],5:['enter','f']}
		array=[0]*4

		for player in d["players"]:


			if len(d["bonuses"])!=0:

				cmd=self.getPath(d["players"][int(isSecondPlayer)][0],d["bonuses"][0], d, isSecondPlayer)

				if cmd:
					array[int(isSecondPlayer)]=cmd
			else:

				# sortedEnemies=sorted(d["enemies"],key=lambda x: self.euclidean_distance(x[0].topleft, d["players"][int(isSecondPlayer)][0].topleft))


				if len(d["enemies"])!=0:
					min_dict=float("inf")
					min_index=len(d["enemies"])
					for i in range(len(d["enemies"])):
						tmp_dis=self.euclidean_distance(d["enemies"][i][0].topleft, d["players"][int(isSecondPlayer)][0].topleft)
						if min_dict>tmp_dis:
							min_dict=tmp_dis
							min_index=i
					enemy=d["enemies"][min_index]

					astar_direction = self.getPath(d["players"][int(isSecondPlayer)][0], enemy[0], d, isSecondPlayer)
					inline_direction = self.inline_with_enemy(player[0], enemy[0])
					if inline_direction:
						array[int(isSecondPlayer)]=inline_direction
						array[int(isSecondPlayer)+1]=1
					else:
						if astar_direction:
							array[int(isSecondPlayer)] = astar_direction
						array[int(isSecondPlayer) + 1] = 0
			isSecondPlayer=not isSecondPlayer
		with lock:
			for i in range(len(arr)):
				arr[i]=array[i]




	def inline_with_enemy(self, player_rect, enemy_rect):
		# vertical inline
		if enemy_rect.left <= player_rect.centerx <= enemy_rect.right:
				# and abs(player_rect.top - enemy_rect.bottom) <= 151:
			# enemy on top
			if enemy_rect.bottom <= player_rect.top:
				print('enemy on top')
				return 1
			# enemy on bottom
			elif player_rect.bottom <= enemy_rect.top:
				print('enemy on bottom')
				return 3
		# horizontal inline
		if enemy_rect.top <= player_rect.centery <= enemy_rect.bottom:
				# and abs(player_rect.left - enemy_rect.right) <= 151:
			# enemy on left
			if enemy_rect.right <= player_rect.left:
				print('enemy on left')
				return 4
			# enemy on right
			elif player_rect.right <= enemy_rect.left:
				print('enemy on right')
				return 2
		return False


	def getPath(self, origin, destination, info,isFirstPlayer):
		# (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
		origin_cor=(origin.left,origin.top)
		destination_cor=(destination.left,destination.top)

		openSet=[]
		cameFrom=dict()
		gScore=dict()
		gScore[origin_cor]=0
		fScore=dict()
		fScore[origin_cor]=self.euclidean_distance(origin_cor,destination_cor)
		heapq.heappush(openSet,origin)
		speed = info["players"][int(isFirstPlayer)][2]
		path=[]
		while len(openSet)!=0:
			current=heapq.heappop(openSet)
			current_cor=(current.left,current.top)
			if self.isDestination(current_cor,destination_cor):
				path=self.reconstructPath(cameFrom,current_cor)
				break
			# openSet.remove(current)
			for point_cor in self.neighbour(current, destination, speed, info):
				tentatice_gScore=gScore[current_cor]+speed
				# point_cor=(point.left,point.top)
				if point_cor not in gScore.keys() or (tentatice_gScore<gScore[point_cor]):
					cameFrom[point_cor]=current_cor
					gScore[point_cor]=tentatice_gScore
					fScore[point_cor]=gScore[point_cor]+self.euclidean_distance(point_cor,destination_cor)
					point=pygame.Rect(point_cor[0],point_cor[1],origin.width,origin.height)
					if point not in openSet:
						openSet.append(point)

		if len(path)>1:
			next=path[1]
			next_left, next_top = next
			current_left, current_top = origin_cor
			dir_cmd=False

			# up
			if current_top > next_top:
				dir_cmd = 1
			# down
			elif current_top < next_top:
				dir_cmd = 2
			# left
			elif current_left > next_left:
				dir_cmd = 3
			# right
			elif current_left < next_left:
				dir_cmd = 4
			return dir_cmd
		else:
			return False

	def reconstructPath(self, cameFrom, current):
		totalPath = [current]
		while current in cameFrom.keys():
			current = cameFrom[current]
			totalPath.insert(0, current)
		return totalPath

	def neighbour(self, current, destination, speed, info):

		(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

		left, top = current.topleft
		# Rect(left, top, width, height)
		allowable_move = []

		# move up
		new_top = top - speed
		new_left = left
		if not (new_top < 0):
			move_up = True
			temp_rect = pygame.Rect(new_left, new_top, 26, 26)

			# check collision with enemy except goal
			for enemy in info["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_up = False
						break

			# check collision with bullet
			for bullet in info["bullets"]:
				if temp_rect.colliderect(bullet[0]):
					move_up = False
					break

			# check collision with tile
			if move_up:
				for tile in self.level.mapr:
					# not a grass , frozen tile
					if tile.type != TILE_GRASS and tile.type!=TILE_FROZE:
						tile_rect=pygame.Rect(tile.left,tile.top,tile.width,tile.height)
						if temp_rect.colliderect(tile_rect):
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
			for enemy in info["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_right = False
						break

			# check collision with bullet
			for bullet in info["bullets"]:
				if temp_rect.colliderect(bullet[0]):
					move_right = False
					break

			# check collision with tile
			if move_right:
				for tile in self.level.mapr:
					# not a grass, frozen tile
					if tile.type != TILE_GRASS and tile.type!=TILE_FROZE:
						tile_rect=pygame.Rect(tile.left,tile.top,tile.width,tile.height)
						if temp_rect.colliderect(tile_rect):
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
			for enemy in info["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_down = False
						break

			# check collision with bullet
			for bullet in info["bullets"]:
				if temp_rect.colliderect(bullet[0]):
					move_down = False
					break

			# check collision with tile
			if move_down:
				for tile in self.level.mapr:
					# not a grass , frozn tile
					if tile.type != TILE_GRASS and tile.type!=TILE_FROZE:
						tile_rect=pygame.Rect(tile.left,tile.top,tile.width,tile.height)
						if temp_rect.colliderect(tile_rect):
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
			for enemy in info["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_left = False
						break

			# check collision with bullet
			for bullet in info["bullets"]:
				if temp_rect.colliderect(bullet[0]):
					move_left = False
					break

			# check collision with tile
			if move_left:
				for tile in self.level.mapr:
					# not a grass , frozn tile
					if tile.type != TILE_GRASS and tile.type!=TILE_FROZE:
						tile_rect=pygame.Rect(tile.left,tile.top,tile.width,tile.height)
						if temp_rect.colliderect(tile_rect):
							move_left = False
							break

			if move_left:
				allowable_move.append((new_left, new_top))

		return allowable_move



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



	def run(self,auto,bothplayers):
		if not auto:
			self.showMenu()
		else:

			self.showMenu1()
			if bothplayers:
				pyautogui.press("down")
			pyautogui.press("enter")
			self.showMenu2()
			v = mp.Value('i', 1)
			arr = mp.Array('i', [0,0,0,0])
			lock = mp.Lock()
			# q=mp.Queue()
			manager=mp.Manager()
			d=manager.dict()
			d["players"]=[]
			d["enemies"]=[]
			d["bonuses"]=[]
			d["bullets"]=[]
			self.nextLevel()
			process = mp.Process(target=self.nextLevel2, args=(arr, lock,d,v))
			process.start()
			# self.nextLevel()
			while True:
				with lock:
					if v.value==0:
						break
				self.getAction(arr,lock,d)



if __name__=='__main__':
	autogame=LoadGame()
	tanks.castle=tanks.Castle()
	autogame.run(auto=True,bothplayers=True)

