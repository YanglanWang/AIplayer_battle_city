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


	def encodeMap(self, d):
		result=[['_' for x in range(self.map_width)] for y in range(self.map_height)]

		for player in d["players"]:
			p_left=player[0].left//32
			p_top=player[0].top//32
			result[p_top][p_left]="p"
		for enemy in d["enemies"]:
			e_left=enemy[0].left//32
			e_top=enemy[0].top//32
			result[e_top][e_left]="e"

		for bullet in d["bullets"]:
			b_left=bullet[0].left//32
			b_top=bullet[0].top//32
			if (b_left>=0 and b_left<self.map_width and b_top>=0 and b_top<self.map_height):
				result[b_top][b_left]="b"
			b_right=(bullet[0].left+bullet[0].width)//32
			b_bottom=(bullet[0].top+bullet[0].height)//32
			if (b_right>=0 and b_right<self.map_width and b_bottom>=0 and b_bottom<self.map_height):
				result[b_bottom][b_right]="b"

		for bonus in d["bonuses"]:
			bo_left=bonus[0].left//32
			bo_top=bonus[0].top//32
			result[bo_top][bo_left]="bo"

		for tile in	self.level.mapr:
			t_left=tile.left//32
			t_top=tile.top//32
			if tile.type != TILE_GRASS and tile.type != TILE_FROZE:
				result[t_top][t_left]="t"
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
				if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height or self.encoded_map[current_top][current_left] == "t"):
					break
				if (self.encoded_map[current_top][current_left] == "e"):
					return i

		return -1


	def bfs(self, player):
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

		result_move = -1

		while not q.empty():
			temp = q.get()
			current_top = temp[0]
			current_left = temp[1]
			direction = temp[2]
			visited[current_top][current_left] = True

			if (self.encoded_map[current_top][current_left] == "e"):
				print "found enemy"
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
			direction = self.check_tanks(player)
			if (direction != -1):
				print "Found Tank, direction %s"%direction
				self.UpdateStrategy(control, direction, 1)
				continue

			# 3. BFS
			self.generate_dangerous_map(d["bullets"], d["enemies"])
			direction = self.bfs(player)
			if (direction == -1):
				# move = random.randint(0,4)
				# print("no movement")
				self.UpdateStrategy(control,4, 0)
			else:
				print("trace tank")
				self.UpdateStrategy(control, direction, 0)


	def generate_dangerous_map(self, bullets, enemies):
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
				if (
						current_right >= 0 and current_right < self.map_width and current_bottom >= 0 and current_bottom < self.map_height):
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
	autogame.run(auto=True,bothplayers=False)

