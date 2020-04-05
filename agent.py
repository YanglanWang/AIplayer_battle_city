import pyautogui
import  math, heapq, tanks, pygame, time, os, Queue, loadgame, logging,random
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
			if tile.type == TILE_BRICK:
				if "r" not in result[t_top][t_left]:
					result[t_top][t_left]+="r"
			if tile.type ==TILE_STEEL:
				if "s" not in result[t_top][t_left]:
					result[t_top][t_left]+="s"
			if tile.type==TILE_WATER:
				if "w" not in result[t_top][t_left]:
					result[t_top][t_left]+="w"
		return result


	def dodge_bullets_enemies(self, player):
		bullets = self.d["bullets"]
		tanks=self.d["enemies"]

		encoded_player_left=player[0].left//32
		encoded_player_top=player[0].top//32
		# player_bottom=player_top+player[0].height
		# player_right=player_left+player[0].width
		for object in [bullets, tanks]:
			for bullet in object:
				encoded_bullet_left = bullet[0].left / 32
				encoded_bullet_top = bullet[0].top / 32
				bullet_dir = bullet[1]

				# bullet is in the top of player
				if (encoded_player_top-encoded_bullet_top>0 and encoded_player_top-encoded_bullet_top<4 and player[1]==0):
					if ((encoded_bullet_left-encoded_player_left>0 and encoded_bullet_left-encoded_player_left<4 and bullet_dir == 3) or
							(encoded_player_left-encoded_bullet_left>0 and encoded_player_left-encoded_bullet_left<4 and  bullet_dir == 1)):
						# print("stop to dodge bullet in the top")
						logging.info("stop to dodge bullets or enemies in the top")
						return 4
				# bullet is in below the player
				if (encoded_bullet_top-encoded_player_top>0 and encoded_bullet_top-encoded_player_top<4 and player[1]==2):
					if ((encoded_bullet_left-encoded_player_left>0 and encoded_bullet_left-encoded_player_left<4 and bullet_dir == 3) or
							(encoded_player_left-encoded_bullet_left>0 and encoded_player_left-encoded_bullet_left<4 and  bullet_dir == 1)):
						# print("dodge bullet in the bottom")
						logging.info("dodge bullets or enemies in the bottom")
						return 4
				# bullet is in the left part of player
				if (encoded_player_left-encoded_bullet_left>0 and encoded_player_left-encoded_bullet_left<4 and  player[1] == 3):
					if ((encoded_bullet_top - encoded_player_top > 0 and encoded_bullet_top - encoded_player_top <4 and bullet_dir==0) or
						(encoded_player_top-encoded_bullet_top>0 and encoded_player_top-encoded_bullet_top<4 and bullet_dir==2)):
						# print("dodge bullet in the left")
						logging.info("dodge bullets or enemies in the left")
						return 4
				# bullet is in the right part of player
				if (encoded_bullet_left-encoded_player_left>0 and encoded_bullet_left-encoded_player_left<4 and  player[1] == 1):
					if ((encoded_bullet_top - encoded_player_top > 0 and encoded_bullet_top - encoded_player_top <4 and bullet_dir==0) or
						(encoded_player_top-encoded_bullet_top>0 and encoded_player_top-encoded_bullet_top<4 and bullet_dir==2)):
						# print("dodge bullet in the right")
						logging.info("dodge bullets or enemies in the right")
						return 4

		return -1

	def check_bullets(self,player,i):
		if len(self.d["players"])>1:
			other_player=self.d["players"][1-i]
			other_encoded_player_left = other_player[0].left
			other_encoded_player_top = other_player[0].top

		bullets=self.d["bullets"]
		encoded_player_left=player[0].left
		encoded_player_top=player[0].top

		for bullet in bullets:
			encoded_bullet_left = bullet[0][0]
			encoded_bullet_top = bullet[0][1]
			bullet_dir = bullet[1]

			# in the same vertical side
			if (encoded_bullet_left == encoded_player_left):
				if (len(self.d["players"])>1 and other_encoded_player_left==encoded_player_left and
					encoded_player_top - encoded_bullet_top>0 and bullet_dir == 2 and other_encoded_player_top>encoded_player_top):
						return 0
				elif (len(self.d["players"])==1 and encoded_player_top - encoded_bullet_top>0 and bullet_dir == 2 ):
						return 0

				elif (len(self.d["players"])>1 and other_encoded_player_left==encoded_player_left and
				      encoded_player_top - encoded_bullet_top<0 and bullet_dir == 0 and other_encoded_player_top<encoded_player_top):
						return 2
				elif (len(self.d["players"])==1 and encoded_player_top - encoded_bullet_top<0 and bullet_dir == 0 ):
						return 2


			# in the same horizontal side
			if (encoded_bullet_top == encoded_player_top):
				if (len(self.d["players"])>1 and other_encoded_player_top==encoded_player_top and
					encoded_player_left - encoded_bullet_left>0 and bullet_dir == 1 and encoded_player_left<other_encoded_player_left):
						return 3
				elif (encoded_player_left - encoded_bullet_left>0 and bullet_dir == 1):
						return 3

				elif (len(self.d["players"])>1 and other_encoded_player_top==encoded_player_top and
				      encoded_bullet_left - encoded_player_left>0 and bullet_dir == 3 and other_encoded_player_left<encoded_player_left):
						return 1
				elif (encoded_bullet_left - encoded_player_left>0 and bullet_dir == 3):
						return 1

		return -1

	def check_tanks(self, player, i, i_player):
		encoded_player_left=player[0].left//UNIT_LENGTH
		encoded_player_top=player[0].top//UNIT_LENGTH
		# current_left=encoded_player_left
		# current_top=encoded_player_top

		for j in range(14):
			current_left = encoded_player_left + self.dir_left[i]*j
			current_top = encoded_player_top + self.dir_top[i]*j
			if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height
					or "s" in self.encoded_map[current_top][current_left] or "r" in self.encoded_map[current_top][current_left])\
					or "w" in self.encoded_map[current_top][current_left]:
				break
			if ("e" in self.encoded_map[current_top][current_left]):
				if len(self.d["players"])>1:
					other_encoded_player_left = self.d["players"][1-i_player][0].left // UNIT_LENGTH
					other_encoded_player_top = self.d["players"][1-i_player][0].top // UNIT_LENGTH
					if (encoded_player_left<=other_encoded_player_left<=current_left and
							encoded_player_top<=other_encoded_player_top<=current_top):
						break
					else:
						return i,j
				else:
					return i,j
				logging.info("the position of origin (%s, %s), the position of enemy (%s, %s)"%(encoded_player_top,
				                                    encoded_player_left, current_top, current_left))
		return -1,-1

	def check_bonus(self, player, i,i_player):
		encoded_player_left=player[0].left//UNIT_LENGTH
		encoded_player_top=player[0].top//UNIT_LENGTH
		for j in range(14):
			current_left = encoded_player_left + self.dir_left[i]*j
			current_top = encoded_player_top + self.dir_top[i]*j
			if (current_left < 0 or current_left >= self.map_width or current_top < 0 or current_top >= self.map_height) or \
				"s" in self.encoded_map[current_top][current_left] 	or "w" in self.encoded_map[current_top][current_left]:
				break
			if ("o" in self.encoded_map[current_top][current_left] ):
				if len(self.d["players"]) > 1:
					other_encoded_player_left = self.d["players"][1 - i_player][0].left // UNIT_LENGTH
					other_encoded_player_top = self.d["players"][1 - i_player][0].top // UNIT_LENGTH
					if (encoded_player_left <= other_encoded_player_left <= current_left and
							encoded_player_top <= other_encoded_player_top <= current_top):
						break
					else:
						return i
				logging.info("the position of origin (%s, %s), the position of bonus (%s, %s)"%(encoded_player_top,
				                                    encoded_player_left, current_top, current_left))
				return i
		return -1


	def getAction(self, i_player):
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
		player = self.d["players"][i_player]
		unicode_player_top=player[0].top//UNIT_LENGTH
		unicode_player_left=player[0].left//UNIT_LENGTH
		player_cor=(unicode_player_top,unicode_player_left)


		# fire to bullets in the same vertical or horizontal direction
		if len(self.d["bullets"]) != 0:
			direction = self.check_bullets(player,i_player)
			if (direction != -1):
				print "find bullet running to the player, fire to %s" % (direction)
				logging.info("find bullet running to the player, fire to %s" % (direction))
				self.UpdateStrategy(direction, 1)
				return

		# adjust position and check for tanks and bonus in this direction
		if player[1] == 0:
			direction1,dis1 = self.check_tanks(player, 0, i_player)
			direction2, dis2 = self.check_tanks(player, 2, i_player)
			if direction1 != -1 and direction2!=-1:
				if(dis1<dis2):
					self.UpdateStrategy(direction1, 1)
					logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
				else:
					self.UpdateStrategy(direction2, 1)
					logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
			elif direction1 != -1:
				self.UpdateStrategy(direction1, 1)
				logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			elif direction2!=-1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction1 = self.check_bonus(player, 0, i_player)
			if direction1 != -1:
				self.UpdateStrategy(direction1, 1)
				logging.info("move up to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction2 = self.check_bonus(player, 2, i_player)
			if direction2 != -1:
				self.UpdateStrategy(direction, 1)
				logging.info("move down to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return


			if player[0].top % UNIT_LENGTH > 3:
				if "r" in self.encoded_map[unicode_player_top][unicode_player_left]:
					logging.info("move up to adjust position, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(0, 1)
					return
				elif "w" not in self.encoded_map[unicode_player_top][unicode_player_left] and \
						"s" not in self.encoded_map[unicode_player_top][unicode_player_left]:
					logging.info("move up to adjust position, player position: (%s, %s, %s, %s), no fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(0, 0)
					return

		if player[1] == 2:
			direction1, dis1 = self.check_tanks(player, 2, i_player)
			direction2,dis2 = self.check_tanks(player, 0, i_player)
			if (direction1!=-1 and direction2!=-1):
				if(dis1<dis2):
					logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(direction1, 1)
					return
				else:
					logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(direction2, 1)
					return
			elif direction1!=-1:
				logging.info("move down to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction1, 1)
				return
			elif direction2!=-1:
				logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction2, 1)
				return

			direction2 = self.check_bonus(player, 2, i_player)
			if direction2 != -1:
				logging.info("move down to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction2, 1)
				return

			direction2 = self.check_bonus(player, 0, i_player)
			if direction2 != -1:
				logging.info("move up to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				self.UpdateStrategy(direction2, 1)
				return

			if player[0].top % UNIT_LENGTH > 3:
				if "r" in self.encoded_map[unicode_player_top + 1][unicode_player_left]:
					logging.info("move down to adjust position, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(2, 1)
					return
				elif "w" not in self.encoded_map[unicode_player_top + 1][unicode_player_left] and \
						"s" not in self.encoded_map[unicode_player_top + 1][unicode_player_left]:
					logging.info("move down to adjust position, player position: (%s, %s, %s, %s), no fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					self.UpdateStrategy(2, 0)
					return

		if player[1] == 1:
			direction1,dis1 = self.check_tanks(player, 1, i_player)
			direction2,dis2 = self.check_tanks(player, 3, i_player)
			if (direction1 != -1 and direction2!=-1):
				if(dis1<dis2):
					self.UpdateStrategy(direction1, 1)
					logging.info("move right to attack enemey, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
				else:
					self.UpdateStrategy(direction2, 1)
					logging.info("move left to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
			elif direction1 != -1:
				self.UpdateStrategy(direction1, 1)
				logging.info("move right to attack enemey, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			elif direction2!=-1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move left to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return


			direction2 = self.check_bonus(player, 1, i_player)
			if direction2 != -1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move right to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction2 = self.check_bonus(player, 3, i_player)
			if direction2 != -1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move left to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			if player[0].left % UNIT_LENGTH > 3:
				if "r" in self.encoded_map[unicode_player_top][unicode_player_left + 1]:
					self.UpdateStrategy(1, 1)
					logging.info("move right to adjust position, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
				elif ("w" not in self.encoded_map[unicode_player_top][unicode_player_left + 1] and \
				      "s" not in self.encoded_map[unicode_player_top][unicode_player_left + 1]):
					self.UpdateStrategy(1, 0)
					logging.info("move right to adjust position, player position: (%s, %s, %s, %s), no fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return

		if player[1] == 3:
			direction1,dis1 = self.check_tanks(player, 3, i_player)
			direction2,dis2 = self.check_tanks(player, 1, i_player)
			if (direction1 != -1 and direction2!=-1):
				if(dis1<dis2):
					self.UpdateStrategy(direction1, 1)
					logging.info("move left to attack enemy, player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
				else:
					self.UpdateStrategy(direction2, 1)
					logging.info("move right to attack enemy , player position: (%s, %s, %s, %s), fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
			elif direction1 != -1:
				self.UpdateStrategy(direction1, 1)
				logging.info("move left to attack enemy, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return
			elif direction2!=-1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move right to attack enemy , player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction2 = self.check_bonus(player, 3, i_player)
			if direction2 != -1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move left to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			direction2 = self.check_bonus(player, 1, i_player)
			if direction2 != -1:
				self.UpdateStrategy(direction2, 1)
				logging.info("move right to attack bonus's tile, player position: (%s, %s, %s, %s), fire" % (
					player[0].top, player[0].left, player[0].bottom, player[0].right))
				return

			if player[0].left % UNIT_LENGTH > 3:
				if "r" in self.encoded_map[unicode_player_top][unicode_player_left]:
					self.UpdateStrategy(3, 1)
					logging.info("move left to adjust position, player position: (%s, %s, %s, %s),fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return
				elif "w" not in self.encoded_map[unicode_player_top][unicode_player_left] and \
						"s" not in self.encoded_map[unicode_player_top][unicode_player_left]:
					self.UpdateStrategy(3, 0)
					logging.info("move left to adjust position, player position: (%s, %s, %s, %s), no fire" % (
						player[0].top, player[0].left, player[0].bottom, player[0].right))
					return

		# dodge the bullets and enemies
		if len(self.d["bullets"]) != 0 or len(self.d["enemies"])!=0:
			direction = self.dodge_bullets_enemies(player)
			if (direction != -1):
				logging.info("Dodge bullets or enemies")
				self.UpdateStrategy(direction, 0)
				return


		# ensure the safety of castle
		if len(self.d["enemies"]) != 0:
			enemies_sorted_castle = sorted(self.d["enemies"], key=lambda enemy:
			self.euclidean_distance((enemy[0].top // UNIT_LENGTH, enemy[0].left // UNIT_LENGTH), (12, 6.5)))

			# for enemy in enemies_sorted:
			enemy = enemies_sorted_castle[0]
			if enemy[0].top // UNIT_LENGTH >= 7:
				player_left = player[0].left // UNIT_LENGTH
				player_top = player[0].top // UNIT_LENGTH
				player_cor = (player_top, player_left)
				enemy_left = enemy[0].left // UNIT_LENGTH
				enemy_top = enemy[0].top // UNIT_LENGTH
				enemy_cor = (enemy_top, enemy_left)


				direction, dir_fire = self.pathToDestination(player_cor, enemy_cor)
				if (direction != -1):
					logging.info("ensure the safety of castle, the position of dangerous enemy (%s,%s),"
					             "the position of player (%s, %s), move to %s" % (enemy[0].top,enemy[0].left,
						player[0].top, player[0].left, direction))
					self.UpdateStrategy(direction, dir_fire)
					return


		# check for tanks in the four directions
		if len(self.d["enemies"]) != 0:
			for i in range(4):
				direction,dis = self.check_tanks(player, i,i_player)
				if (direction != -1):
					# print "find tank, fire to direction %s" % direction
					self.UpdateStrategy(direction, 1)
					logging.info("find tank, fire to direction %s" % direction)
					return

		# search for bonuses
		if len(self.d["bonuses"]) != 0:
			dest=self.d["bonuses"][0]
			dest_left = dest[0].left // UNIT_LENGTH
			dest_top = dest[0].top // UNIT_LENGTH
			dest_cor = (dest_top, dest_left)
			player_left = player[0].left // UNIT_LENGTH
			player_top = player[0].top // UNIT_LENGTH
			player_cor = (player_top, player_left)
			if "s" in self.encoded_map[dest_top][dest_left] or "w" in self.encoded_map[dest_top][dest_left]:
				return
			if "r" in self.encoded_map[dest_top][dest_left]:
				direction,dir_fire=self.pathToDestination(player_cor,dest_cor)
				if (direction == -1):
					logging.info("no movement in search of bonus")
				else:
					logging.info("move to " + str(direction) + " in search of bonus")
					self.UpdateStrategy(direction, dir_fire)
					return

		if i_player==1:
			if player_cor==(12,8):
				return
			else:
				direction, dir_fire=self.pathToDestination(player_cor,(12, 8))
				if (direction == -1):
					logging.info("no movement to return to castle")
				else:
					logging.info("move to " + str(direction) + " to return to castle")
					self.UpdateStrategy(direction, dir_fire)
					return

		# find path to one enemy
		if len(self.d["enemies"]) != 0:
			enemies_sorted_player = sorted(self.d["enemies"], key=lambda enemy:
			self.euclidean_distance((enemy[0].top // UNIT_LENGTH, enemy[0].left // UNIT_LENGTH),
			                        (player[0].top // UNIT_LENGTH,
			                         player[0].left // UNIT_LENGTH)))

			# for enemy in enemies_sorted:
			enemy = enemies_sorted_player[0]
			player_left = player[0].left // UNIT_LENGTH
			player_top = player[0].top // UNIT_LENGTH
			player_cor = (player_top, player_left)

			enemy_left = enemy[0].left // UNIT_LENGTH
			enemy_top = enemy[0].top // UNIT_LENGTH
			enemy_cor = (enemy_top, enemy_left)

			direction, dir_fire = self.pathToDestination(player_cor, enemy_cor)
			if (direction != -1):
				logging.info("move to %s to find enemy, the position of player (%s, %s), the position of enemy (%s, %s)"
				             % (direction, player[0].top // UNIT_LENGTH, player[0].left // UNIT_LENGTH,
				                enemy[0].top // UNIT_LENGTH,
				                enemy[0].left // UNIT_LENGTH))
				self.UpdateStrategy(direction, dir_fire)
				return

		if unicode_player_top==0 and unicode_player_left==0 and "e" not in self.encoded_map[0][0]:
			self.UpdateStrategy(1,0)
			return

		if unicode_player_top==0 and unicode_player_left==6 and "e" not in self.encoded_map[0][6]:
			self.UpdateStrategy(1,0)
			return

		if unicode_player_top==0 and unicode_player_left==5 and "e" not in self.encoded_map[0][6]:
			self.UpdateStrategy(3,0)
			return

		if unicode_player_top==0 and (unicode_player_left==12 or unicode_player_left==11) and "e" not in self.encoded_map[0][12]:
			self.UpdateStrategy(3,0)
			return
	# def nearestP(self, point):
	# 	q=Queue.Queue()
	# 	q.put(point)
	# 	cameFrom=dict()
	# 	cameFrom[point]=None
	# 	while q.qsize()>0:
	# 		current=q.get()
	# 		for i in range(4):
	# 			new_top=current[0]+self.dir_top[i]
	# 			new_left=current[1]+self.dir_left[i]
	# 			if new_top>=0 and new_top<13 and new_left>=0 and new_left<13:
	# 				if "r" in self.encoded_map[new_top][new_left]:
	# 					if (new_top,new_left) not in cameFrom.keys():
	# 						q.put((new_top,new_left))
	# 						cameFrom[(new_top,new_left)]=current
	# 				elif "s" not in self.encoded_map[new_top][new_left] and "w" not in self.encoded_map[new_top][new_left]:
	# 					return (new_top,new_left)
	# 	return -1





	def pathToDestination(self, player_cor, dest_cor):
		player_left = player_cor[1]
		player_top = player_cor[0]

		dest_left=dest_cor[1]
		dest_top=dest_cor[0]

		# if "t" in self.encoded_map[dest_top][dest_left]:
		# 	return -1

		openSet = []
		cameFrom = dict()
		isfire=dict()
		gScore = dict()
		gScore[player_cor] = 0
		fScore = dict()
		fScore[player_cor] = self.euclidean_distance(player_cor, dest_cor)
		heapq.heappush(openSet, player_cor)
		path = []
		while len(openSet) != 0:
			current = heapq.heappop(openSet)
			if self.isDestination(current, dest_cor):
				path, whetherfire= self.reconstructPath(cameFrom,isfire, current)
				break
			# openSet.remove(current)
			for point_cor,fire in self.neighbour(current):
				tentatice_gScore = gScore[current] + 1
				# point_cor=(point.left,point.top)
				if point_cor not in gScore.keys() or (tentatice_gScore < gScore[point_cor]):
					cameFrom[point_cor] = current
					isfire[point_cor]=fire
					gScore[point_cor] = tentatice_gScore
					fScore[point_cor] = gScore[point_cor] + self.euclidean_distance(point_cor, dest_cor)
					if point_cor not in openSet:
						openSet.append(point_cor)

		if len(path) > 1:
			# print("path calculated")
			next = path[1]
			next_top, next_left = next
			dir_cmd = False
			dir_fire=whetherfire[0]

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
			return dir_cmd, dir_fire
		else:
			return -1,-1

	def euclidean_distance(self,x,y):
		return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

	def isDestination(self, current_cor, point_cor):
		return (current_cor[0]==point_cor[0]) and (current_cor[1]==point_cor[1])

	def reconstructPath(self, cameFrom, isfire, current):
		totalPath = [current]
		whetherfire=[]
		while current in cameFrom.keys():
			whetherfire.insert(0,isfire[current])
			current = cameFrom[current]
			totalPath.insert(0, current)
		return totalPath, whetherfire

	def neighbour(self, current):
		allowable_move = []
		current_top,current_left=current


		# move down
		new_top=current_top+1
		new_left=current_left
		if new_top>=self.map_height or ("s" in self.encoded_map[new_top][new_left]) or ("w" in self.encoded_map[new_top][new_left])\
				or (11<=new_top<=12 and 5<=new_left<=7):
			pass
		elif "r" in self.encoded_map[new_top][new_left]:
			allowable_move.append([(new_top,new_left),1])
		else:
			allowable_move.append([(new_top,new_left),0])

		# move right
		new_top = current_top
		new_left = current_left + 1
		if new_left >= self.map_width or ("s" in self.encoded_map[new_top][new_left]) or ("w" in self.encoded_map[new_top][new_left])\
				or (11 <= new_top <= 12 and 5 <= new_left <= 7):
			pass
		elif "r" in self.encoded_map[new_top][new_left]:
			allowable_move.append([(new_top, new_left),1])
		else:
			allowable_move.append([(new_top, new_left),0])


		# move left
		new_top = current_top
		new_left = current_left - 1
		if new_left < 0 or ("s" in self.encoded_map[new_top][new_left]) or ("w" in self.encoded_map[new_top][new_left]) \
			or (11<=new_top<=12 and 5<=new_left<=7):
			pass
		elif "r" in self.encoded_map[new_top][new_left]:
			allowable_move.append([(new_top, new_left),1])
		else:
			allowable_move.append([(new_top, new_left),0])


		# move up
		new_top = current_top - 1
		new_left = current_left
		if new_top < 0 or ("s" in self.encoded_map[new_top][new_left]) or ("w" in self.encoded_map[new_top][new_left]) \
				or (11<=new_top<=12 and 5<=new_left<=7):
			pass
		elif "r" in self.encoded_map[new_top][new_left]:
			allowable_move.append([(new_top, new_left),1])
		else:
			allowable_move.append([(new_top, new_left),0])


		return allowable_move

	def run(self, p):
		while True:
			logging.info("game_over check")
			if hasattr(loadgame.game, "game_over") and loadgame.game.game_over:
				logging.info("game fail")
				loadgame.game.running=False
			if hasattr(loadgame.game, "active") and (not loadgame.game.active) and hasattr(loadgame.game, "stage") \
					and loadgame.game.stage >= 35:
				loadgame.game.running=False
				os._exit(0)


			for i in range(len(tanks.players)):
				if len(tanks.players)==1:
					time_passed = self.clock.tick(50)
				else:
					time_passed=self.clock.tick(100)
				self.getAction(i)
				self.applyAction(i)
				if tanks.players[i].paralised:
					tanks.players[i].paralised=False


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
						logging.info("fire")
					else:
						logging.info("cannot fire")
				if operations[0] < 4:
					player.pressed[operations[0]] = True
					logging.info("player 's position before movement(%s,%s)"%(player.rect.top,player.rect.left))
				elif operations[0]==4:
					logging.info("no movement")
				if player.pressed[0] == True:
					player.move(DIR_UP)
					logging.info("move up")
				elif player.pressed[1] == True:
					player.move(DIR_RIGHT)
					logging.info("move right")
				elif player.pressed[2] == True:
					player.move(DIR_DOWN)
					logging.info("move down")
				elif player.pressed[3] == True:
					player.move(DIR_LEFT)
					logging.info("move left")
				if operations[0] < 4:
					player.pressed[operations[0]] = False
					logging.info("press false")
				logging.info("player 's position after movement (%s,%s)" % (player.rect.top, player.rect.left))



	def UpdateStrategy(self, direction, fire):
		if self.control.empty()==True:
			self.control.put([direction, fire])
			return True
		else:
			print("self.control is not empty")
			return False

