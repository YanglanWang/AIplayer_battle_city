import loadgame,threading
if __name__ == "__main__":
	stage=0
	num=1
	c=loadgame.Combine(stage,num)
	c.start()
