import pygame,math


def euclidean_distance(x, y):
	return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


d=dict()
a=pygame.Rect(51,135,26,26)
b=pygame.Rect(289, 198, 26, 26)
d["enemies"]=[[a, 0], [b, 2]]
player=(12,4)
UNIT_LENGTH=32
enemies_sorted=sorted(d["enemies"], key=lambda enemy:euclidean_distance((enemy[0].top//UNIT_LENGTH,enemy[0].left//UNIT_LENGTH),player))
print("")


