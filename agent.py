import pyautogui
import  math, heapq, tanks, pygame, time, os, Queue, loadgame, logging
import multiprocessing as mp
# pyautogui.press('enter')
format = "%(asctime)s: %(message)s"
# logging.basicConfig(format=format,level=logging.INFO, datefmt="%H:%M:%S")
logging.basicConfig(format=format, filename='test.log',level=logging.INFO, datefmt="%H:%M:%S")

(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)
UNIT_LENGTH=32

class Agent():
	def __init__(self,num):
		self.num=num
		self.control=mp.Queue()
		self.map_height=13
		self.map_width=13
		self.clock = pygame.time.Clock()
		#               up right down left
		self.dir_top =  [-1, 0,  1,   0]
		self.dir_left = [0,  1,  0,  -1]


	def encodeMap(self):
		result=[['' for x in range(self.map_width)] for y in range(self.map_height)]

		for player in self.d["players"]:
			p_left=player[0].left//UNIT_LENGTH
			p_top=player[0].top//UNIT_LENGTH
			if "p" not in result[p_top][p_left]:
				result[p_top][p_left]+="p"
		for enemy in self.d["enemies"]:
			e_left=enemy[0].left//UNIT_LENGTH
			e_top=enemy[0].top//UNIT_LENGTH
			if "e" not in result[e_top][e_left]:
				result[e_top][e_left]+="e"

		for bullet in self.d["bullets"]:
			b_left=bullet[0].left//32
			b_top=bullet[0].top//32
			if (b_left>=0 and b_left<self.map_width and b_top>=0 and b_top<self.map_height):
				if "b" not in result[b_top][b_left]:
					result[b_top][b_left]+="b"
			b_right=(bullet[0].left+bullet[0].width)//32
			b_bottom=(bullet[0].top+bullet[0].height)//32
			if (b_right>=0 and b_right<self.map_width and b_bottom>=0 and b_bottom<self.map_height):
				if "b" not in result[b_top][b_left]:
					result[b_bottom][b_right]+="b"

		for bonus in self.d["bonuses"]:
			bo_left=bonus[0].left//32
			bo_top=bonus[0].top//32
			if "o" not in result[bo_top][bo_left]:
				result[bo_top][bo_left]+="o"

		for tile in	self.d["tiles"]:
			t_left=tile.left//32
			t_top=tile.top//32
			if tile.type != TILE_GRASS and tile.type != TILE_FROZE:
				if "t" not in result[t_top][t_left]:
					result[t_top][t_left]+="t"
		return result

	# def enemeyDirection(self):
	# 	result = [[10 for x in range(self.map_width)] for y in range(self.map_height)]
	# 	for enemy in self.d["enemies"]:
	# 		e_left=enemy[0].left//UNIT_LENGTH
	# 		e_top=enemy[0].top//UNIT_LENGTH
	# 		result[e_top][e_left]=enemy[1]
	# 	return result



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
					# print("stop to dodge bullet in the top")
					logging.info("stop to dodge bullet in the top")
					return 4
			# bullet is in below the player
			if (encoded_bullet_top-encoded_player_top>1 and encoded_bullet_top-encoded_player_top<=2 and player[1]==2):
				if ((encoded_bullet_left-encoded_player_left>1 and encoded_bullet_left-encoded_player_left<=2 and bullet_dir == 3) or
						(encoded_player_left-encoded_bullet_left>1 and encoded_player_left-encoded_bullet_left<=2 and  bullet_dir == 1)):
					# print("dodge bullet in the bottom")
					logging.info("dodge bullet in the bottom")
					return 4
			# bullet is in the left part of player
			if (encoded_player_left-encoded_bullet_left>1 and encoded_player_left-encoded_bullet_left<=2 and  player[1] == 3):
				if ((encoded_bullet_top - encoded_player_top > 1 and encoded_bullet_top - encoded_player_top <= 2 and bullet_dir==0) or
					(encoded_player_top-encoded_bullet_top>1 and encoded_player_top-encoded_bullet_top<=2 and bullet_dir==2)):
					# print("dodge bullet in the left")
					logging.info("dodge bullet in the left")
					return 4
			# bullet is in the right part of player
			if (encoded_bullet_left-encoded_player_left>1 and encoded_bullet_left-encoded_player_left<=2 and  player[1] == 1):
				if ((encoded_bullet_top - encoded_player_top > 1 and encoded_bullet_top - encoded_player_top <= 2 and bullet_dir==0) or
					(encoded_player_top-encoded_bullet_top>1 and encoded_player_top-encoded_bullet_top<=2 and bullet_dir==2)):
					# print("dodge bullet in the right")
					logging.info("dodge bullet in the right")
					return 4

		return -1

	def check_bullets(self,player):

		bullets=self.d["bullets"]
		encoded_player_left=player[0].left
		encoded_player_top=player[0].top
		for bullet in bullets:
			encoded_bullet_left = bullet[0][0]
			encoded_bullet_top = bullet[0][1]
			bullet_dir = bullet[1]

			# in the same vertical side
			if (encoded_bullet_left == encoded_player_left):
				if (encoded_player_top - encoded_bullet_top>0 and bullet_dir == 2):
					return 0

				elif (encoded_bullet_top - encoded_player_top>0 and bullet_dir == 0):
					return 2

			# in the same horizontal side
			if (encoded_bullet_top == encoded_player_top):
				if (encoded_player_left - encoded_bullet_left>0 and bullet_dir == 1):
					return 3

				elif (encoded_bullet_left - encoded_player_left>0 and bullet_dir == 3):
					return 1

		return -1

	def check_tanks(self, player, i):
		encoded_player_left=player[0].left//UNIT_LENGTH
		encoded_player_top=player[0].top//UNIT_LENGTH
		current_left=encoded_player_left
		current_top=encoded_player_top

		for j in range(13):
			current_left = current_left + self.dir_left[i]
			current_top = current_top + self.dir_top[i]
			if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height
					or "t" in self.encoded_map[current_top][current_left]):
				break
			if ("e" in self.encoded_map[current_top][current_left] ):
				# print("the position of origin (%s, %s ) (%s, %s )") % (encoded_player_top, encoded_player_left, player[0].top, player[0].left)
				# print("the position of enemy (%s, %s)") % (current_top, current_left)
				logging.info("the position of origin (%s, %s), the position of enemy (%s, %s)"%(encoded_player_top,
				                                    encoded_player_left, current_top, current_left))
				# if abs(self.enemy_direction[current_top][current_left]-i)==2 or j<=3:
				# 	# if the enemy and player are in the opposite running directions, the player keeps its position; else runs to enemy
				# 	return 4
				# else:
				return i
		return -1

	def getAction(self, i):
		while True:
			if hasattr(loadgame.game, "level"):
				break
		logging.info("run getAction")

		# print("start determining actions:")
		# logging.info("start determining actions:")
		self.d = loadgame.Combine.getData()

		# array=[0]*4
		self.encoded_map = self.encodeMap()
		for row in range(len(self.encoded_map)):
			logging.info(self.encoded_map[row])

		# self.enemy_direction = self.enemeyDirection()
		# self.dangerous_map = self.generate_dangerous_map()

		# for i_th in range(len(self.d["players"])):
		player = self.d["players"][i]

		# dodge the bullets
		if len(self.d["bullets"]) != 0:
			direction = self.dodge_bullets(player)
			if (direction != -1):
				print "Dodge Bullet"
				logging.info("Dodge Bullet")
				self.UpdateStrategy(direction, 0)
				return

		# fire to bullets in the same vertical or horizontal direction
		if len(self.d["bullets"]) != 0:
			direction = self.check_bullets(player)
			if (direction != -1):
				print "find bullet running to the player, fire to %s" % (direction)
				logging.info("find bullet running to the player, fire to %s" % (direction))
				self.UpdateStrategy(direction, 1)
				return

		# ensure the safety of castle
		if len(self.d["enemies"]) != 0:
			enemies_sorted_castle = sorted(self.d["enemies"], key=lambda enemy:
			self.euclidean_distance((enemy[0].top // UNIT_LENGTH, enemy[0].left // UNIT_LENGTH), (12, 6.5)))

			# for enemy in enemies_sorted:
			enemy = enemies_sorted_castle[0]
			if enemy[0].top // UNIT_LENGTH >= 7:
				direction = self.pathToDestination(player, enemy)
				if (direction != -1):
					print("ensure the safety of castle, the position of player (%s, %s), move to %s" % (
					player[0].top, player[0].left, direction))
					logging.info("ensure the safety of castle, the position of player (%s, %s), move to %s" % (
					player[0].top, player[0].left, direction))
					self.UpdateStrategy(direction, 0)
					return

		# adjust position and check for tanks in this direction
		if player[1] == 0:
			direction = self.check_tanks(player, 0)
			if direction != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			direction = self.check_tanks(player, 2)
			if direction != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			if player[0].top % UNIT_LENGTH > 3:
				logging.info("move up to adjust position, player position: (%s, %s, %s, %s), no fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(0, 0)
				return

		if player[1] == 2:
			direction = self.check_tanks(player, 2)
			if direction != -1:
				logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction, 1)
				return
			direction = self.check_tanks(player, 0)
			if direction != -1:
				logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction, 1)
				return

			if player[0].top % UNIT_LENGTH > 3:
				logging.info("move down to adjust position, player position: (%s, %s, %s, %s), no fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(2, 0)
				return

		if player[1] == 1:
			direction = self.check_tanks(player, 1)
			if direction != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move right to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			direction=self.check_tanks(player, 3)
			if direction!=-1:
				self.UpdateStrategy(direction, 1)
				logging.info("move left to attack enemey, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			if player[0].left % UNIT_LENGTH > 3:
				self.UpdateStrategy(1, 0)
				logging.info("move right to adjust position, player position: (%s, %s, %s, %s), no fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

		if player[1] == 3:
			direction = self.check_tanks(player, 3)
			if direction != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move left to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction = self.check_tanks(player, 1)
			if direction != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move right to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			if player[0].left % UNIT_LENGTH > 3:
				self.UpdateStrategy(3, 0)
				print("move left to adjust position, player position: (%s, %s, %s, %s),no fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				logging.info("move left to adjust position, player position: (%s, %s, %s, %s),no fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

		# check for tanks in the four directions
		if len(self.d["enemies"]) != 0:
			for i in range(4):
				direction = self.check_tanks(player, i)
				if (direction != -1):
					print "find tank, fire to direction %s" % direction
					self.UpdateStrategy(direction, 1)
					logging.info("find tank, fire to direction %s" % direction)
					return

		# search for bonuses
		if len(self.d["bonuses"]) != 0:
			direction = self.pathToDestination(player, self.d["bonuses"][0])
			if (direction == -1):
				print("no movement in search of bonus")
				logging.info("no movement in search of bonus")
			else:
				print("move to " + str(direction) + " in search of bonus")
				logging.info("move to " + str(direction) + " in search of bonus")
				self.UpdateStrategy(direction, 0)
				return

		if len(self.d["enemies"]) != 0:
			enemies_sorted_player = sorted(self.d["enemies"], key=lambda enemy:
			self.euclidean_distance((enemy[0].top // UNIT_LENGTH, enemy[0].left // UNIT_LENGTH),
			                        (player[0].top // UNIT_LENGTH,
			                         player[0].left // UNIT_LENGTH)))

			# for enemy in enemies_sorted:
			enemy = enemies_sorted_player[0]
			direction = self.pathToDestination(player, enemy)
			if (direction != -1):
				print("move to %s to find enemy, the position of player (%s, %s), the position of enemy (%s, %s)"
				      % (direction, player[0].top // UNIT_LENGTH, player[0].left // UNIT_LENGTH,
				         enemy[0].top // UNIT_LENGTH,
				         enemy[0].left // UNIT_LENGTH))
				logging.info("move to %s to find enemy, the position of player (%s, %s), the position of enemy (%s, %s)"
				             % (direction, player[0].top // UNIT_LENGTH, player[0].left // UNIT_LENGTH,
				                enemy[0].top // UNIT_LENGTH,
				                enemy[0].left // UNIT_LENGTH))
				self.UpdateStrategy(direction, 0)
				return

	# def getAction(self,arr,lock,d):
	# def getAction(self,i,queue,event):
	# 	while not event.is_set():
	# 		logging.info("run getAction")
	# 		time_passed = self.clock.tick(500)
	#
	# 		while True:
	# 			if hasattr(loadgame.game, "level"):
	# 				break
	# 		# print("start determining actions:")
	# 		# logging.info("start determining actions:")
	# 		self.d=loadgame.Combine.getData()
	#
	# 		# array=[0]*4
	# 		self.encoded_map=self.encodeMap()
	# 		self.enemy_direction = self.enemeyDirection()
	# 		self.dangerous_map = self.generate_dangerous_map()
	#
	# 		# for i_th in range(len(self.d["players"])):
	# 		if len(self.d["players"])>i:
	# 			player=self.d["players"][i]
	#
	# 			# dodge the bullets
	# 			if len(self.d["bullets"])!=0:
	# 				direction=self.dodge_bullets(player)
	# 				if (direction != -1):
	# 					# print "Dodge Bullet"
	# 					logging.info("Dodge Bullet")
	# 					self.UpdateStrategy( direction, 0,queue)
	# 					return
	#
	# 			# fire to bullets in the same vertical or horizontal direction
	# 			if len(self.d["bullets"]) != 0:
	# 				direction = self.check_bullets(player)
	# 				if (direction != -1):
	# 					# print "find bullet running to the player, fire to %s"%(direction)
	# 					logging.info("find bullet running to the player, fire to %s"%(direction))
	# 					self.UpdateStrategy(direction, 1, queue)
	# 					return
	#
	# 			# adjust position and check for tanks in this direction
	# 			if player[1] == 0:
	# 				if player[0].top % UNIT_LENGTH > 3:
	#
	# 					direction=self.check_tanks(player,0)
	# 					if direction!=-1:
	# 						self.UpdateStrategy(direction, 1, queue)
	# 						# print("move up to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 						# player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move up to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 						player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 					else:
	# 						# print("move up to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 						# player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move up to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 						player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						self.UpdateStrategy(0,0, queue)
	# 					return
	#
	# 			if player[1] == 2:
	# 				if player[0].top % UNIT_LENGTH > 3:
	#
	# 					direction=self.check_tanks(player,2)
	# 					if direction!=-1:
	# 						# print("move down to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 						# player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move down to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 						player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						self.UpdateStrategy(direction, 1, queue)
	# 					else:
	# 						# print("move down to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 						# 	player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move down to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 							player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						self.UpdateStrategy(2,0,queue)
	# 					return
	#
	# 			if player[1] == 1:
	# 				if player[0].left % UNIT_LENGTH > 3:
	#
	# 					direction=self.check_tanks(player,1)
	# 					if direction!=-1:
	# 						self.UpdateStrategy(direction, 1, queue)
	# 						# print("move right to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 					# player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move right to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 					player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 					else:
	# 						self.UpdateStrategy(1,0,queue)
	# 						# print("move right to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 						# 	player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move right to adjust position, player position: (%s, %s, %s, %s), no fire" % (
	# 							player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 					return
	#
	# 			if player[1] == 3:
	# 				if player[0].left % UNIT_LENGTH > 3:
	#
	# 					direction=self.check_tanks(player,3)
	# 					if direction!=-1:
	# 						self.UpdateStrategy(direction, 1, queue)
	# 						# print("move left to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 					# player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move left to adjust position, player position: (%s, %s, %s, %s), fire" % (
	# 					player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 					else:
	# 						self.UpdateStrategy(3,0, queue)
	# 						# print("move left to adjust position, player position: (%s, %s, %s, %s),no fire" % (
	# 						# 	player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 						logging.info("move left to adjust position, player position: (%s, %s, %s, %s),no fire" % (
	# 							player[0].top, player[0].left, player[0].bottom, player[0].right))
	# 					return
	#
	# 			# ensure the safety of castle
	# 			if len(self.d["enemies"])!=0:
	# 				enemies_sorted_castle=sorted(self.d["enemies"], key=lambda enemy:
	# 				self.euclidean_distance((enemy[0].top//UNIT_LENGTH,enemy[0].left//UNIT_LENGTH),(12,6.5)))
	#
	# 				# for enemy in enemies_sorted:
	# 				enemy=enemies_sorted_castle[0]
	# 				if enemy[0].top//UNIT_LENGTH>=7:
	# 					direction=self.pathToDestination(player, enemy)
	# 					if(direction!=-1):
	# 						# print("ensure the safety of castle, the position of player (%s, %s), move to %s"%(player[0].top,player[0].left,direction))
	# 						logging.info("ensure the safety of castle, the position of player (%s, %s), move to %s"%(player[0].top,player[0].left,direction))
	# 						self.UpdateStrategy(direction, 0, queue)
	# 						return
	#
	#
	# 			# check for tanks in the four directions
	# 			if len(self.d["enemies"]) != 0:
	# 				for i in range(4):
	# 					direction = self.check_tanks(player, i)
	# 					if (direction != -1):
	# 						# print "find tank, fire to direction %s" % direction
	# 						self.UpdateStrategy(direction, 1, queue)
	# 						logging.info("find tank, fire to direction %s" % direction)
	# 						return
	#
	#
	# 			# search for bonuses
	# 			if len(self.d["bonuses"])!=0:
	# 				direction=self.pathToDestination(player,self.d["bonuses"][0])
	# 				if (direction==-1):
	# 					# print("no movement in search of bonus")
	# 					logging.info("no movement in search of bonus")
	# 					self.UpdateStrategy(4, 0 ,queue)
	# 				else:
	# 					# print("move to "+str(direction)+" in search of bonus")
	# 					logging.info("move to "+str(direction)+" in search of bonus")
	# 					self.UpdateStrategy(direction,0, queue)
	# 					return
	#
	#
	# 			if len(self.d["enemies"])!=0:
	# 				enemies_sorted_player=sorted(self.d["enemies"], key=lambda enemy:
	# 				self.euclidean_distance((enemy[0].top//UNIT_LENGTH,enemy[0].left//UNIT_LENGTH),(player[0].top//UNIT_LENGTH,
	# 				                                                                                player[0].left//UNIT_LENGTH)))
	#
	# 				# for enemy in enemies_sorted:
	# 				enemy=enemies_sorted_player[0]
	# 				direction=self.pathToDestination(player, enemy)
	# 				if(direction!=-1):
	# 					# print("move to %s to find enemy, the position of player (%s, %s), the position of enemy (%s, %s)"
	# 					#       %(direction,player[0].top//UNIT_LENGTH,player[0].left//UNIT_LENGTH,enemy[0].top//UNIT_LENGTH,
	# 					#         enemy[0].left//UNIT_LENGTH))
	# 					logging.info("move to %s to find enemy, the position of player (%s, %s), the position of enemy (%s, %s)"
	# 					      %(direction,player[0].top//UNIT_LENGTH,player[0].left//UNIT_LENGTH,enemy[0].top//UNIT_LENGTH,
	# 					        enemy[0].left//UNIT_LENGTH))
	# 					self.UpdateStrategy(direction, 0, queue)
	# 					return



					# # 3. BFS
					# self.generate_expect_enemies()
					# print("player "+str(i_th) +":")
					# direction = self.bfs(player, True)
					# if (direction == -1):
					# 	# move = random.randint(0,4)
					# 	print("no movement in search of enemy")
					# 	self.UpdateStrategy(4, 0)
					# else:
					# 	print("movement to "+str(direction)+" in search of enemy")
					# 	# print("trace tank")
					# 	self.UpdateStrategy(direction, 0)


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
		return result


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
		if "t" in self.encoded_map[dest_top][dest_left]:
			return -1

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
			next_top, next_left = next
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


		# move down
		new_top=current_top+1
		new_left=current_left
		if new_top>=self.map_height or "t" in self.encoded_map[new_top][new_left]:
			pass
		else:
			allowable_move.append((new_top,new_left))

		# move right
		new_top = current_top
		new_left = current_left + 1
		if new_left >= self.map_width or "t" in self.encoded_map[new_top][new_left] :
			pass
		else:
			allowable_move.append((new_top, new_left))

		# move left
		new_top = current_top
		new_left = current_left - 1
		if new_left < 0 or "t" in self.encoded_map[new_top][new_left]:
			pass
		else:
			allowable_move.append((new_top, new_left))

		# move up
		new_top = current_top - 1
		new_left = current_left
		if new_top < 0 or "t" in self.encoded_map[new_top][new_left]:
			pass
		else:
			allowable_move.append((new_top, new_left))




		return allowable_move

	def run(self):
		while True:
			for i in range(len(tanks.players)):
				time_passed = self.clock.tick(50)
				self.getAction(i)
				self.applyAction(i)

	def applyAction(self, i):
		logging.info("run applyAction")

		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
		# if self.control.empty() is True:
		# 	# print ("self.control for player %s is empty"%(i))
		# 	# logging.info("self.control for player %s is empty"%(i))
		# 	return 0
		# else:
		logging.info("the self.control.size: " + str(self.control.qsize()))
		while self.control.qsize()>0:
			operations = self.control.get()
			logging.info("the operations are "+str(operations))
			# for player in tanks.players:
			player = tanks.players[i]
			if player.state == player.STATE_ALIVE and not loadgame.game.game_over and loadgame.game.active:
				if operations[1] == 1:
					if player.fire() and tanks.play_sounds:
						tanks.sounds["fire"].play()
						print("fire")
						logging.info("fire")
					else:
						logging.info("cannot fire")
				if operations[0] < 4:
					player.pressed[operations[0]] = True
					logging.info("player 's position before movement(%s,%s)"%(player.rect.top,player.rect.left))
				if player.pressed[0] == True:
					player.move(DIR_UP)
					logging.info("move up")
				elif player.pressed[1] == True:
					player.move(DIR_RIGHT)
					print("move right")
					logging.info("move right")
				elif player.pressed[2] == True:
					player.move(DIR_DOWN)
					print("move down")
					logging.info("move down")
				elif player.pressed[3] == True:
					player.move(DIR_LEFT)
					print("move left")
					logging.info("move left")
				if operations[0] < 4:
					player.pressed[operations[0]] = False
				print("press false")
				logging.info("player 's position after movement (%s,%s)" % (player.rect.top, player.rect.left))
				logging.info("press false")
			before_update = (player.rect.top, player.rect.left)
			if before_update == (player.rect.top, player.rect.left):
				print("the player' s position after movement: (%s, %s)" % (player.rect.top, player.rect.left))

	# def applyAction(self,i,queue,event):
	# 	while not event.is_set() or not queue.empty():
	# 		logging.info("run apply action")
	# 		(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
	# 		# if self.control.empty() is True:
	# 		# 	# print ("self.control for player %s is empty"%(i))
	# 		# 	# logging.info("self.control for player %s is empty"%(i))
	# 		# 	return 0
	# 		# else:
	# 		# print("the self.control.size: "+str(self.control.qsize()))
	# 		logging.info("the queue.size: "+str(queue.qsize()))
	# 		# operations = self.control.get()
	# 		operations=queue.get()
	# 		logging.info("apply operations: "+str(operations))
	# 		# for player in tanks.players:
	# 		player=tanks.players[i]
	# 		if player.state == player.STATE_ALIVE and not loadgame.game.game_over and loadgame.game.active:
	# 			if operations[1]==1:
	# 				if player.fire() and tanks.play_sounds:
	# 					tanks.sounds["fire"].play()
	# 					# print("fire")
	# 					logging.info("fire")
	# 			if operations[0]<4:
	# 				player.pressed[operations[0]] = True
	# 			if player.pressed[0] == True:
	# 				logging.info("the player' s position (%s, %s)"%(player.rect.top,player.rect.left))
	# 				player.move(DIR_UP)
	# 				logging.info("move up")
	# 			elif player.pressed[1] == True:
	# 				logging.info("the player' s position (%s, %s)"%(player.rect.top,player.rect.left))
	# 				player.move(DIR_RIGHT)
	# 				# print("move right")
	# 				logging.info("move right")
	# 			elif player.pressed[2] == True:
	# 				logging.info("the player' s position (%s, %s)"%(player.rect.top,player.rect.left))
	# 				player.move(DIR_DOWN)
	# 				# print("move down")
	# 				logging.info("move down")
	# 			elif player.pressed[3] == True:
	# 				logging.info("the player' s position (%s, %s)"%(player.rect.top,player.rect.left))
	# 				player.move(DIR_LEFT)
	# 				# print("move left")
	# 				logging.info("move left")
	# 			if operations[0]<4:
	# 				player.pressed[operations[0]] = False
	# 			# print("press false")
	# 			logging.info("press false")
	# 		before_update=(player.rect.top,player.rect.left)
	# 		logging.info("the player' s position after movement: (%s, %s)" % (player.rect.top, player.rect.left))

	def kill_ai_process(self,p):
		p.terminate()
		os.kill(p.pid,9)
		print "kill process!!"
		logging.info("kill process!")

	def clear_queue(self,queue):
		if queue.empty()!=True:
			try:
				queue.get(False)
				print "clear queue!!"
				logging.info("clear queue")
			except Queue.Empty:
				print "Queue already is empty!!"
				logging.info("Queue already is empty")

	# def UpdateStrategy(self, direction, fire,queue):
	# 	# if self.control.empty()==True:
	# 	# 	self.control.put([direction, fire])
	# 	# 	return True
	# 	# else:
	# 	# 	print("self.control is not empty")
	# 	# 	logging.info("self.control is not empty")
	# 	# 	return False
	# 	queue.put([direction,fire])


	def UpdateStrategy(self, direction, fire):
		if self.control.empty()==True:
			self.control.put([direction, fire])
			return True
		else:
			print("self.control is not empty")
			return False

