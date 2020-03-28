import pyautogui
import  math, heapq, tanks, pygame, time, os
import multiprocessing as mp
from multiprocessing import Manager
# pyautogui.press('enter')
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)


class LoadGame(tanks.Game):
	def __init__(self):
		tanks.Game.__init__(self)
		self.map_height=13
		self.map_width=13
		#               up right down left
		self.dir_top =  [-1, 0,  1,   0]
		self.dir_left = [0,  1,  0,  -1]


	def encodeMap(self, d):
		result=[['_' for x in range(self.map_width)] for y in range(self.map_height)]

		for player in d["players"]:
			p_left=player[0].left
			p_top=player[0].top
			result[p_left//32][p_top//32]="p"
		for enemy in d["enemies"]:
			e_left=enemy[0].left
			e_top=enemy[0].top
			result[e_left//32][e_top//32]="e"

		for bullet in d["bullets"]:
			b_left=bullet[0].left//32
			b_top=bullet[0].top//32
			if (b_left>=0 and b_left<13 and b_top>=0 and b_top<13):
				result[b_left][b_top]='b'
			b_right=(bullet[0].left+bullet[0].width)//32
			b_bottom=(bullet[0].top+bullet[0].height)//32
			if (b_right>=0 and b_right<13 and b_bottom>=0 and b_bottom<13):
				result[b_right][b_bottom]='b'

		for bonus in d["bonuses"]:
			bo_left=bonus[0].left//32
			bo_top=bonus[0].top//32
			result[bo_left][bo_top]="bo"

		for tile in	self.level.mapr:
			t_left=tile.left//32
			t_top=tile.top//32
			if tile.type != TILE_GRASS and tile.type != TILE_FROZE:
				result[t_left][t_top]="t"
		return result

	def dodge_bullets(self, player):
		bullets=self.d["bullets"]
		range = 100
		player_top=player[0].top
		player_left=player[0].left
		for bullet in bullets:
			bullet_top = bullet[0].top
			bullet_left = bullet[0].left
			bullet_bottom = bullet_top + bullet[0].height
			bullet_right = bullet_left + bullet[0].width
			# bullet_h_mid = (bullet_top + bullet_bottom) / 2
			# bullet_v_mid = (bullet_left + bullet_right) / 2
			bullet_dir = bullet[1]
			# top part of player tank
			if (bullet_bottom > player_top and bullet_bottom <= player_top + 10):
					# or (bullet_h_mid > player_top and bullet_h_mid <= player_top + 10)):
				if ((player_left < bullet_left and player_left + range > bullet_left and bullet_dir == 3) or (player_left > bullet_left and player_left - range < bullet_left and  bullet_dir == 1)):
					return 2
			# bottom part of player tank
			if (bullet_top > player_top + 16 and bullet_top <= player_top + 26):
			# or (bullet_h_mid > player_top + 16 and bullet_h_mid <= player_top + 26)):
				if ((player_left < bullet_left and player_left + range > bullet_left and bullet_dir == 3) or (player_left > bullet_left and player_left - range < bullet_left and bullet_dir == 1)):
					return 0
			# left part of player tank
			if (bullet_right > player_left and bullet_right <= player_left + 10):
			# or (bullet_v_mid > player_left and bullet_v_mid <= player_left + 10)):
				if ((player_top < bullet_top and player_top + range > bullet_top and bullet_dir == 0) or (player_top > bullet_top and player_top - range < bullet_top and bullet_dir == 2)):
					return 1
			# right part of player tank
			if bullet_left > player_left + 16 and bullet_left <= player_left + 26:
			# or (bullet_v_mid > player_left + 16 and bullet_v_mid <= player_left + 26)):
				if ((player_top < bullet_top and player_top + range > bullet_top and bullet_dir == 0) or (player_top > bullet_top and player_top - range < bullet_top and bullet_dir == 2)):
					return 3

		return -1

	def check_bullets(self,player):

		bullets=self.d["bullets"]
		encoded_player_left=player[0].left//32
		encoded_player_top=player[0].top//32
		for bullet in bullets:
			encoded_bullet_left = bullet[0][0] / 32
			encoded_bullet_top = bullet[0][1] / 32
			bullet_dir = bullet[1]

			if (encoded_bullet_left == encoded_player_left):
				if (encoded_bullet_top < encoded_player_top and bullet_dir == 2):
					return 0
				elif (encoded_bullet_top > encoded_player_top and bullet_dir == 0):
					return 2

			if (encoded_bullet_top == encoded_player_top):
				if (encoded_bullet_left < encoded_player_left and bullet_dir == 1):
					return 3
				elif (encoded_bullet_left > encoded_player_left and bullet_dir == 3):
					return 1

		return -1

	def check_tanks(self, player):
		encoded_player_left=player[0].left//32
		encoded_player_top=player[0].top//32
		for i in range(4):
			current_left = encoded_player_left
			current_top = encoded_player_top
			for j in range(5):
				current_left = current_left + self.dir_left[i]
				current_top = current_top + self.dir_top[i]
				if (current_left < 0 or current_left >= 13 or current_top < 0 or current_top >= 13 or self.encoded_map[current_top][current_left] == '@'):
					break
				if (self.encoded_map[current_top][current_left] == 'E'):
					return i

		return -1


	# def getAction(self,arr,lock,d):
	def getAction(self,control, d, v):
		self.d=d
		isSecondPlayer=False
		# array=[0]*4
		self.encoded_map=self.encodeMap(d)

		for player in d["players"]:

			if len(d["bullets"])!=0:
				direction=self.dodge_bullets(player)
				if (direction != -1):
					print "Dodge Bullet"
					self.UpdateStrategy(control, direction, 0)
					continue

			adjust_top = player[0].top//32 * 32
			adjust_left = player[0].left//32 * 32

			# 1. check if the position of player's tank is on the multiplier of 32
			if (player[1] == 1 or player[1] == 3):
				if (player[0].top - adjust_top > 5):
					# print "adjust left"
					self.UpdateStrategy(control, 0, 0)
					continue

			elif (player[1] == 0 or player[1] == 2):
				if (player[0].left - adjust_left > 5):
					# print "adjust left"
					self.UpdateStrategy(control, 3, 0)
					continue

			# 2. check nearest 5 blocks in every direction ( bullet, tank )
			# check for bullets
			if len(d["bullets"])!=0:
				direction = self.check_bullets(player)
				if (direction != -1):
					print "fire enemy's bullet"
					self.UpdateStrategy(control, direction, 1)
					continue


			# check for tanks
			# move = self.check_tanks(player)
			# if (move != -1):
			# 	# print "Found Tank"
			# 	self.UpdateStrategy(control, move, 1)
			# 	continue


			if len(d["bonuses"])!=0:
				direction=self.getPath(player[0],d["bonuses"][0][0], player[2])
				if direction!=-1:
					self.UpdateStrategy(control,direction, 0)
					continue
					# array[int(isSecondPlayer)]=cmd

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

				astar_direction = self.getPath(player[0], enemy[0], player[2])
				inline_direction = self.inline_with_enemy(player[0], enemy[0])
				if inline_direction!=-1:
					self.UpdateStrategy(control, inline_direction, 1)
				else:
					if astar_direction:
						self.UpdateStrategy(control,astar_direction, 0)





	def inline_with_enemy(self, player_rect, enemy_rect):
		# vertical inline
		if enemy_rect.left <= player_rect.centerx <= enemy_rect.right:
				# and abs(player_rect.top - enemy_rect.bottom) <= 151:
			# enemy on top
			if enemy_rect.bottom <= player_rect.top:
				print('enemy on top')
				return 0
			# enemy on bottom
			elif player_rect.bottom <= enemy_rect.top:
				print('enemy on bottom')
				return 2
		# horizontal inline
		if enemy_rect.top <= player_rect.centery <= enemy_rect.bottom:
				# and abs(player_rect.left - enemy_rect.right) <= 151:
			# enemy on left
			if enemy_rect.right <= player_rect.left:
				print('enemy on left')
				return 3
			# enemy on right
			elif player_rect.right <= enemy_rect.left:
				print('enemy on right')
				return 1
		return -1


	def getPath(self, origin, destination, speed):
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
		path=[]
		while len(openSet)!=0:
			current=heapq.heappop(openSet)
			current_cor=(current.left,current.top)
			if self.isDestination(current_cor,destination_cor):
				path=self.reconstructPath(cameFrom,current_cor)
				break
			# openSet.remove(current)
			for point_cor in self.neighbour(current, destination, speed):
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
			# print("path calculated")
			next=path[1]
			next_left, next_top = next
			current_left, current_top = origin_cor
			dir_cmd=False

			# up
			if current_top > next_top:
				dir_cmd = 0
			# down
			elif current_top < next_top:
				dir_cmd = 1
			# left
			elif current_left > next_left:
				dir_cmd = 2
			# right
			elif current_left < next_left:
				dir_cmd = 3
			return dir_cmd
		else:
			return -1

	def reconstructPath(self, cameFrom, current):
		totalPath = [current]
		while current in cameFrom.keys():
			current = cameFrom[current]
			totalPath.insert(0, current)
		return totalPath

	def neighbour(self, current, destination, speed):


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
			for enemy in self.d["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_up = False
						break

			# check collision with bullet
			for bullet in self.d["bullets"]:
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
			for enemy in self.d["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_right = False
						break

			# check collision with bullet
			for bullet in self.d["bullets"]:
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
			for enemy in self.d["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_down = False
						break

			# check collision with bullet
			for bullet in self.d["bullets"]:
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
			for enemy in self.d["enemies"]:
				if not enemy[0].colliderect(destination):
					if temp_rect.colliderect(enemy[0]):
						move_left = False
						break

			# check collision with bullet
			for bullet in self.d["bullets"]:
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
		self.showMenu(auto, bothplayers)

		# pyautogui.press("enter")
		# arr = mp.Array('i', [0,0,0,0])
		# lock = mp.Lock()
		# q=mp.Queue()
		if not auto:
			self.nextLevel1()
			self.nextLevel2(None,None,None)
		else:
			while True:
				self.nextLevel1()
				control = mp.Queue()
				manager=mp.Manager()
				d=manager.dict()
				d["players"]=[]
				d["enemies"]=[]
				d["bonuses"]=[]
				d["bullets"]=[]
				v = mp.Value('i', 1)
				# process = mp.Process(target=self.nextLevel2, args=(arr, lock,d,v))
				process = mp.Process(target=self.nextLevel2, args=(control,d,v))
				process.start()
				# self.nextLevel()
				while True:
					# with lock:
					if v.value==0:
						# self.kill_ai_process(process)
						break
					# self.getAction(arr,lock,d)
					self.getAction(control, d,v)

	def kill_ai_process(self,p):
		#p.terminate()
		os.kill(p.pid,9)
		print "kill ai_process!!"

	def UpdateStrategy(self, control, direction, fire):
		if control.empty()==True:
			control.put([direction, fire])
			return True
		else:
			return False


if __name__=='__main__':
	autogame=LoadGame()
	tanks.castle=tanks.Castle()
	autogame.run(auto=False,bothplayers=False)

