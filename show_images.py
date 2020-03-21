# import pygame
# pygame.init()
#
# X,Y=400,400
# display_surface=pygame.display.set_mode((X,Y))
# sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])
# shield_images = [
# 			sprites.subsurface(0, 48*2, 16*2, 16*2),
# 			sprites.subsurface(16*2, 48*2, 16*2, 16*2)
# 		]
# image=shield_images[0]
# while True:
#     display_surface.fill((0,0,0))
#     display_surface.blit(image,(0,0))
#     for event in pygame.event.get():
#         if event.type==pygame.QUIT:
#             pygame.quit()
#             quit()
#         pygame.display.update()


def f(a,b,c=0):
    return a+b+c

if  __name__=="__main__":
    d=2
    l=f(1,2,d==2)
    print(l)