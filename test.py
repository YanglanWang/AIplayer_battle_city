from pykeyboard import PyKeyboard
from pymouse import PyMouse
import tanks

game = tanks.Game()
castle = tanks.Castle()
game.showMenu()

m=PyMouse()
k=PyKeyboard()




x_dim,y_dim=m.screen_size()
m.click(x_dim/2,y_dim/2,1)
k.type_string('hello world!')