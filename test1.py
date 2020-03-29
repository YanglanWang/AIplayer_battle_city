import pyautogui
import  math, heapq, tanks, pygame, time, os, Queue
import multiprocessing as mp
from multiprocessing import Manager
# pyautogui.press('enter')
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)
UNIT_LENGTH=32

class LoadGame(tanks.Game):
	def __init__(self):
		tanks.Game.__init__(self)
		self.map_height=13
		self.map_width=13
		#               up right down left
		self.dir_top =  [-1, 0,  1,   0]
		self.dir_left = [0,  1,  0,  -1]


	def encodeMap(self):
		result=[['_' for x in range(self.map_width)] for y in range(self.map_height)]

		for player in self.d["players"]:
			p_left=player[0].left//UNIT_LENGTH
			p_top=player[0].top//UNIT_LENGTH
			result[p_top][p_left]="p"
		for enemy in self.d["enemies"]:
			e_left=enemy[0].left//UNIT_LENGTH
			e_top=enemy[0].top//UNIT_LENGTH
			result[e_top][e_left]="e"

		for bullet in self.d["bullets"]:
			b_left=bullet[0].left//32
			b_top=bullet[0].top//32
			if (b_left>=0 and b_left<self.map_width and b_top>=0 and b_top<self.map_height):
				result[b_top][b_left]="b"
			b_right=(bullet[0].left+bullet[0].width)//32
			b_bottom=(bullet[0].top+bullet[0].height)//32
			if (b_right>=0 and b_right<self.map_width and b_bottom>=0 and b_bottom<self.map_height):
				result[b_bottom][b_right]="b"

		for bonus in self.d["bonuses"]:
			bo_left=bonus[0].left//32
			bo_top=bonus[0].top//32
			result[bo_top][bo_left]="bo"

		for tile in	self.level.mapr:
			t_left=tile.left//32
			t_top=tile.top//32
			if tile.type != TILE_GRASS and tile.type != TILE_FROZE:
				result[t_top][t_left]="t"
		return result

	def enemeyDirection(self):
		result = [[10 for x in range(self.map_width)] for y in range(self.map_height)]
		for enemy in self.d["enemies"]:
			e_left=enemy[0].left//UNIT_LENGTH
			e_top=enemy[0].top//UNIT_LENGTH
			result[e_top][e_left]=enemy[1]
		return result



	def dodge_bullets(self, player):
		bullets=self.d["bullets"]
		range = 100

		encoded_player_left=player[0].left//32
		encoded_player_top=player[0].top//32
		# player_bottom=player_top+player[0].height
		# player_right=player_left+player[0].width
		for bullet in bullets:
			encoded_bullet_left = bullet[0].left / 32
			encoded_bullet_top = bullet[0].top / 32
			bullet_dir = bullet[1]

			# bullet is in the top of player
			if (encoded_player_top-encoded_bullet_top>1 and encoded_player_top-encoded_bullet_top<=2 and player[1]==0):
				if ((encoded_bullet_left-encoded_player_left>1 and encoded_bullet_left-encoded_player_left<=2 and bullet_dir == 3) or
						(encoded_player_left-encoded_bullet_left>1 and encoded_player_left-encoded_bullet_left<=2 and  bullet_dir == 1)):
					print("stop to dodge bullet in the top")
					return -1
			# bullet is in below the player
			if (encoded_bullet_top-encoded_player_top>1 and encoded_bullet_top-encoded_player_top<=2 and player[1]==2):
				if ((encoded_bullet_left-encoded_player_left>1 and encoded_bullet_left-encoded_player_left<=2 and bullet_dir == 3) or
						(encoded_player_left-encoded_bullet_left>1 and encoded_player_left-encoded_bullet_left<=2 and  bullet_dir == 1)):
					print("dodge bullet in the bottom")
					return -1
			# bullet is in the left part of player
			if (encoded_player_left-encoded_bullet_left>1 and encoded_player_left-encoded_bullet_left<=2 and  player[1] == 3):
				if ((encoded_bullet_top - encoded_player_top > 1 and encoded_bullet_top - encoded_player_top <= 2 and bullet_dir==0) or
					(encoded_player_top-encoded_bullet_top>1 and encoded_player_top-encoded_bullet_top<=2 and bullet_dir==2)):
					print("dodge bullet in the left")
					return -1
			# bullet is in the right part of player
			if (encoded_bullet_left-encoded_player_left>1 and encoded_bullet_left-encoded_player_left<=2 and  player[1] == 1):
				if ((encoded_bullet_top - encoded_player_top > 1 and encoded_bullet_top - encoded_player_top <= 2 and bullet_dir==0) or
					(encoded_player_top-encoded_bullet_top>1 and encoded_player_top-encoded_bullet_top<=2 and bullet_dir==2)):
					print("dodge bullet in the right")
					return -1

		return False

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
		encoded_player_left=player[0].left//UNIT_LENGTH
		encoded_player_top=player[0].top//UNIT_LENGTH
		for i in range(4):
			current_left = encoded_player_left
			current_top = encoded_player_top
			for j in range(13):
				current_left = current_left + self.dir_left[i]
				current_top = current_top + self.dir_top[i]
				if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height
						or self.encoded_map[current_top][current_left] == "t"):
					break
				if (self.encoded_map[current_top][current_left] == "e"):
					print("the position of origin (%s, %s ) (%s, %s )") % (encoded_player_top, encoded_player_left, player[0].top, player[0].left)
					print("the position of enemy (%s, %s)") % (current_top, current_left)
					if abs(self.enemy_direction[current_top][current_left]-i)==2:
						return -1
					else:
						return i


		return -1


	def bfs(self, player, findEnemy=True):
		print("run bfs")
		q = Queue.Queue()

		player_left = player[0].left//UNIT_LENGTH
		player_top = player[0].top//UNIT_LENGTH


		# record whether the position has been visited
		visited = [[False for x in range(self.map_width)] for y in range(self.map_height)]

		visited[player_top][player_left] = True
		# put first 4 block into queue.
		for i in range(4):
			new_top = player_top + self.dir_top[i]
			new_left = player_left + self.dir_left[i]
			if (new_left < 0 or new_left >= self.map_width or new_top < 0 or new_top >= self.map_height or self.dangerous_map[new_top][
				new_left] == True):
				continue
			if (self.encoded_map[new_top][new_left] != "t"):
				q.put([new_top, new_left, i])
				visited[new_top][new_left] = True

		print("the position of origin (%s, %s ) (%s, %s)")%(player_top,player_left, player[0].top, player[0].left)

		result_move = -1

		while not q.empty():
			temp = q.get()
			current_top = temp[0]
			current_left = temp[1]
			direction = temp[2]
			visited[current_top][current_left] = True

			if findEnemy:
				goal="e"
			else:
				goal="bo"

			if (self.expected_enemies[current_top][current_left] == goal ):
				print("the position of origin (%s, %s ) (%s, %s)")%(player_top,player_left, player[0].top, player[0].left)
				print("the position of enemy (%s, %s)")%(current_top, current_left )
				print "found enemy or bonus in "+ str(direction)

				result_move = direction
				return result_move

			for i in range(4):
				new_top = current_top + self.dir_top[i]
				new_left = current_left + self.dir_left[i]
				if (new_left < 0 or new_left >= self.map_width or new_top < 0 or new_top >= self.map_height):
					continue
				if (visited[new_top][new_left] == False and self.encoded_map[new_top][new_left] != "t"):
				# if (self.encoded_map[new_top][new_left] != "t"):
					q.put([new_top, new_left, direction])

		return result_move

	# def getAction(self,arr,lock,d):
	def getAction(self,control, d, v):
		self.d=d
		isSecondPlayer=False
		# array=[0]*4
		self.encoded_map=self.encodeMap()
		self.enemy_direction=self.enemeyDirection()


		for i_th in range(len(d["players"])):
			player=d["players"][i_th]

			if len(d["bullets"])!=0:
				direction=self.dodge_bullets(player)
				if (direction != False):
					print "Dodge Bullet"
					self.UpdateStrategy(control, 4, 0)
					continue

			# 1. check if the position of player's tank is on the multiplier of 32
			# if (player[1] == 1 or player[1] == 3):
			# 	if (player[0].top - adjust_top > 5):
			# 		# print "adjust left"
			# 		self.UpdateStrategy(control, 0, 0)
			# 		continue
			#
			# elif (player[1] == 0 or player[1] == 2):
			# 	if (player[0].left - adjust_left > 5):
			# 		# print "adjust left"
			# 		self.UpdateStrategy(control, 3, 0)
			# 		continue
			# 2. check nearest 5 blocks in every direction ( bullet, tank )
			# check for bullets


			if len(d["bullets"]) != 0:
				direction = self.check_bullets(player)
				if (direction != -1):
					print "fire enemy's bullet"
					self.UpdateStrategy(control, direction, 1)
					continue

			if player[1] == 0:
				if player[0].top % UNIT_LENGTH > 3:
					print("player position: (%s, %s, %s, %s)" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(control, 0, 0)
					continue
			if player[1] == 2:
				if player[0].top % UNIT_LENGTH > 3:
					self.UpdateStrategy(control, 2, 0)
					continue
			if player[1] == 1:
				if player[0].left % UNIT_LENGTH > 3:
					self.UpdateStrategy(control, 1, 0)
					continue
			if player[1] == 3:
				if player[0].left % UNIT_LENGTH > 3:
					self.UpdateStrategy(control, 3, 0)
					continue

			# check for tanks
			if len(d["enemies"]) != 0:
				direction = self.check_tanks(player)
				if (direction != -1):
					print "Found Tank, direction %s, fire" % direction
					self.UpdateStrategy(control, direction, 1)
					continue


			# ensure the safety of castle
			if len(d["enemies"])!=0:
				for enemy in self.d["enemies"]:
					if enemy[0].top//UNIT_LENGTH>=7:
						direction=self.pathToDestination(player, enemy)
						if(direction!=-1):
							self.UpdateStrategy(control,direction, 0)




			# search for bonuses
			if len(d["bonuses"])!=0:
				direction=self.bfs(player,False)
				if (direction==-1):
					print("no movement in search of bonus")
					self.UpdateStrategy(control, 4, 0)
				else:
					print("move to "+str(direction)+" in search of bonus")
					self.UpdateStrategy(control,direction,0)


			# 3. BFS
			self.generate_dangerous_map()
			self.generate_expect_enemies()
			print("player "+str(i_th) +":")
			direction = self.bfs(player, True)
			if (direction == -1):
				# move = random.randint(0,4)
				print("no movement in search of enemy")
				self.UpdateStrategy(control,4, 0)
			else:
				print("movement to "+str(direction)+" in search of enemy")
				# print("trace tank")
				self.UpdateStrategy(control, direction, 0)


	def generate_dangerous_map(self):
		bullets=self.d["bullets"]
		enemies=self.d["enemies"]
		result = [[False for x in range(self.map_width)] for y in range(self.map_height)]

		# put positions that bullets may pass into dangerous map
		for bullet in bullets:
			b_left = bullet[0][0] / 32
			b_top = bullet[0][1] / 32
			b_right = (bullet[0][0] + bullet[0][2]) / 32
			b_bottom = (bullet[0][1] + bullet[0][3]) / 32
			b_dir = bullet[1]

			# This situation happened before, but still reason is unknown.
			if (b_left >= 0 and b_left < self.map_width and b_top >= 0 and b_top < self.map_height):
				result[b_top][b_left] = True

			current_top = b_top
			current_left = b_left
			current_bottom = b_bottom
			current_right = b_right

			# mark next 3 blocks as dangerous
			for i in range(4):
				current_top = current_top + self.dir_top[b_dir]
				current_left = current_left + self.dir_left[b_dir]
				current_bottom = current_bottom + self.dir_top[b_dir]
				current_right = current_right + self.dir_left[b_dir]
				if (current_left >= 0 and current_left < self.map_width and current_top >= 0 and current_top < self.map_height):
					result[current_top][current_left] = True
				if (current_right >= 0 and current_right < self.map_width and current_bottom >= 0 and current_bottom < self.map_height):
					result[current_bottom][current_right] = True

		# put positions that tanks may shoot into dangerous map
		for enemy in enemies:
			e_left = enemy[0][0] // UNIT_LENGTH
			e_top = enemy[0][1] // UNIT_LENGTH
			e_dir = enemy[1]

			# This situation happened before, but still reason is unknown.
			if (e_left < 0 or e_left >= self.map_width or e_top < 0 or e_top >= self.map_height):
				continue

			result[e_top][e_left] = True

			current_top = e_top
			current_left = e_left

			# mark next 2 blocks as dangerous
			for i in range(2):
				current_top = current_top + self.dir_top[e_dir]
				current_left = current_left + self.dir_left[e_dir]
				if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height):
					continue
				result[current_top][current_left] = True

		self.dangerous_map = result



	def generate_expect_enemies(self):
		enemies=self.d["enemies"]
		result = [['-' for x in range(self.map_width)] for y in range(self.map_height)]

		# put positions that tanks may shoot into dangerous map
		for enemy in enemies:
			e_left = enemy[0][0] // UNIT_LENGTH
			e_top = enemy[0][1] // UNIT_LENGTH
			e_dir = enemy[1]

			# This situation happened before, but still reason is unknown.
			if (e_left < 0 or e_left >= self.map_width or e_top < 0 or e_top >= self.map_height):
				continue

			result[e_top][e_left] = "e"

			current_top = e_top
			current_left = e_left

			# mark next 2 blocks as dangerous
			for i in range(2):
				current_top = current_top + self.dir_top[e_dir]
				current_left = current_left + self.dir_left[e_dir]
				if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height):
					continue
				result[current_top][current_left] = "e"


		for bonus in self.d["bonuses"]:
			bo_left=bonus[0].left//32
			bo_top=bonus[0].top//32
			result[bo_top][bo_left]="bo"

		self.expected_enemies = result

	def pathToDestination(self, player, dest):
		player_left = player[0].left//UNIT_LENGTH
		player_top = player[0].top//UNIT_LENGTH
		player_cor=(player_top,player_left)

		dest_left=dest[0].left//UNIT_LENGTH
		dest_top=dest[0].top//UNIT_LENGTH
		dest_cor=(dest_top, dest_left)

		openSet = []
		cameFrom = dict()
		gScore = dict()
		gScore[player_cor] = 0
		fScore = dict()
		fScore[player_cor] = self.euclidean_distance(player_cor, dest_cor)
		heapq.heappush(openSet, player_cor)
		path = []
		while len(openSet) != 0:
			current = heapq.heappop(openSet)
			if self.isDestination(current, dest_cor):
				path = self.reconstructPath(cameFrom, current)
				break
			# openSet.remove(current)
			for point_cor in self.neighbour(current):
				tentatice_gScore = gScore[current] + 1
				# point_cor=(point.left,point.top)
				if point_cor not in gScore.keys() or (tentatice_gScore < gScore[point_cor]):
					cameFrom[point_cor] = current
					gScore[point_cor] = tentatice_gScore
					fScore[point_cor] = gScore[point_cor] + self.euclidean_distance(point_cor, dest_cor)
					if point_cor not in openSet:
						openSet.append(point_cor)

		if len(path) > 1:
			# print("path calculated")
			next = path[1]
			next_left, next_top = next
			dir_cmd = False

			# up
			if player_top > next_top:
				dir_cmd = 0
			# down
			elif player_top < next_top:
				dir_cmd = 2
			# left
			elif player_left > next_left:
				dir_cmd = 3
			# right
			elif player_left < next_left:
				dir_cmd = 1
			return dir_cmd
		else:
			return -1

	def euclidean_distance(self,x,y):
		return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

	def isDestination(self, current_cor, point_cor):
		return (current_cor[0]==point_cor[0]) and (current_cor[1]==point_cor[1])

	def reconstructPath(self, cameFrom, current):
		totalPath = [current]
		while current in cameFrom.keys():
			current = cameFrom[current]
			totalPath.insert(0, current)
		return totalPath

	def neighbour(self, current):
		allowable_move = []
		current_top,current_left=current
		#move up
		new_top=current_top-1
		new_left=current_left
		if new_top<0 or self.encoded_map[new_top][new_left]=="t" or self.dangerous_map[new_top][new_left]==True:
			pass
		else:
			allowable_move.append((new_top,new_left))

		# move down
		new_top=current_top+1
		new_left=current_left
		if new_top>=self.map_height or self.encoded_map[new_top][new_left]=="t" or self.dangerous_map[new_top][new_left]==True:
			pass
		else:
			allowable_move.append((new_top,new_left))

		# move left
		new_top=current_top
		new_left=current_left-1
		if new_left<0 or self.encoded_map[new_top][new_left]=="t" or self.dangerous_map[new_top][new_left]==True:
			pass
		else:
			allowable_move.append((new_top,new_left))

		# move right
		new_top=current_top
		new_left=current_left+1
		if new_left>=self.map_width or self.encoded_map[new_top][new_left]=="t" or self.dangerous_map[new_top][new_left]==True:
			pass
		else:
			allowable_move.append((new_top,new_left))
		return allowable_move

	def run(self,auto,bothplayers):

		# pyautogui.press("enter")
		# arr = mp.Array('i', [0,0,0,0])
		# lock = mp.Lock()
		# q=mp.Queue()
		if not auto:
			self.showMenu(bothplayers, auto)
			while not self.game_over:
				self.nextLevel1()
				self.nextLevel2(None,None,None)
		else:
			self.showMenu(bothplayers, auto)
			while True:
				self.nextLevel1()

				while self.active==False:
					print("stage %s begin: "%self.stage)
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
						time_passed = self.clock.tick(100)
						# with lock:
						if v.value==0:
							# self.kill_ai_process(process)
							break
						# self.getAction(arr,lock,d)
						self.getAction(control, d,v)
				if self.stage>=35:
					print("whole stages completed")
					break


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
	autogame.run(auto=True,bothplayers=False)

