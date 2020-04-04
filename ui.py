from Tkinter import *
import loadgame,threading, time, tanks
# if __name__ == "__main__":

def clicked():
	stage = int(txt_stage.get())-1
	num = int(txt_num.get())
	c = loadgame.Combine(stage, num)
	c.start()

window=Tk()
window.geometry('600x200')
window.title("AI battle city")

lbl0=Label(window, text="Please input the stage(1~35) and \nthe number of players(1 or 2), and then enter play")
lbl0.grid(column=1, row=0)

lbl_stage=Label(window,text="stage:")
lbl_stage.grid(column=1, row=1)

txt_stage=Entry(window,width=10)
txt_stage.grid(column=1,row=2)

lbl_num=Label(window, text="num of players: ")
lbl_num.grid(column=1,row=3)

txt_num=Entry(window,width=10)
txt_num.grid(column=1,row=4)

btn=Button(window,text="play", command=clicked)
btn.grid(column=1, row=5)

lbl_live_title=Label(window,text="live ")
lbl_live_title.grid(column=1,row=6)

lbl_pos_title=Label(window,text="position ")
lbl_pos_title.grid(column=2,row=6)

lbl_player1=Label(window,text="PLAYER 1")
lbl_player1.grid(column=0, row=7)

live_1=StringVar()
lbl_live1 = Label(window, textvariable=live_1)
lbl_live1.grid(column=1, row=7 )

pos_1=StringVar()
lbl_pos1 = Label(window, textvariable=pos_1)
lbl_pos1.grid(column=2, row=7 )




def update():
	if len(tanks.players)==2:
		lbl_player2 = Label(window, text="PLAYER 2")
		lbl_player2.grid(column=0, row=8)

		live_2 = StringVar()
		lbl_live2 = Label(window, textvariable=live_2)
		lbl_live2.grid(column=1, row=8)

		pos_2 = StringVar()
		lbl_pos2 = Label(window, textvariable=pos_2)
		lbl_pos2.grid(column=2, row=8)

		live_2.set(tanks.players[1].lives)
		pos_2.set(tanks.players[1].rect.topleft)
		live_1.set(tanks.players[0].lives)
		pos_1.set(tanks.players[0].rect.topleft)
	if len(tanks.players)==1:
		live_1.set(tanks.players[0].lives)
		pos_1.set(tanks.players[0].rect.topleft)

	window.after(200,update)
update()




# p=threading.Thread(target=update,)
# p.start()


window.mainloop()
