from Tkinter import *
import loadgame,threading, time
# if __name__ == "__main__":

def clicked():
	stage = int(txt1.get())-1
	num = int(txt2.get())
	c = loadgame.Combine(stage, num)
	c.start()

window=Tk()
window.geometry('300x200')
window.title("AI battle city")

lbl0=Label(window, text="Please choose the stage(1~35)\n and the number of players(1 or 2)")
lbl0.grid(column=0, row=0)

lbl1=Label(window,text="stage:")
lbl1.grid(column=0, row=1)

txt1=Entry(window,width=10)
txt1.grid(column=0,row=2)

lbl2=Label(window, text="num of players: ")
lbl2.grid(column=0,row=3)

txt2=Entry(window,width=10)
txt2.grid(column=0,row=4)

btn=Button(window,text="play", command=clicked)
btn.grid(column=0, row=5)
window.mainloop()

