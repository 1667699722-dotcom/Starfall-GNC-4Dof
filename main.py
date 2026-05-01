from link import clink
import pygame
import sys
pygame.init()
W, H = 1280, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("mini_starship")
clock = pygame.time.Clock()

# 方块参数
block_w = 2
block_h = 16
x = W // 2 - block_w // 2
y = H/4
speed = 3
# 初始化
arr=[0,0,0,0]
a=clink(arr)
arr=[1,0,0.1,10]
a=clink(arr)

landed = False

while True:
    # 退出
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    arr=[2,0,0,0]
    a=clink(arr)
    result=[a[i] for i in range(3)]
    #print(result,y)

    # 下落
    if not landed:
       y=H/4-result[2]*1
       if y>=H-block_h:
            y=H-block_h
            landed = True
    # 绘制
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 255), (x,y, block_w, block_h))
    
    pygame.display.update()
    
    clock.tick(60)
# 游戏结束
# 游戏结束时，显示游戏结束界面