from math import sqrt
import pygame
from random import choice

def move_symbol(symbol, width, height):
    moved= []
    
    for x,y in symbol:
        moved.append((x + width, y + height))

    return moved


def rotate_by_origin(symbol):
    
    def rotate_diagonal(x,y):
        
        if (x,y) != (0,0):
            
            if x < 0 and y < 0 or x > 0 and y > 0 :
                y *= -1
                
            else:
                x *= -1
        return (x,y)
  
    def rotate_straight(x,y):
        
        if x != 0:
            return (y,-x)
        elif y != 0:
            return (y,x)
        return None

    for i, (x,y) in enumerate(symbol):
                
        if (x,y) == (0,0):
            continue
                
        if (sqrt(x ** 2 + y ** 2)) % 1 != 0:
            symbol[i] = rotate_diagonal(x,y)
        else:
            symbol[i] = rotate_straight(x,y)

    return symbol



def validity_check_side(symbol,x_pos,y_pos, dir):

    symbol_position = move_symbol(symbol, x_pos + dir ,y_pos)

    for x,y in symbol_position:
        if x < 0 or x > 9:
            return False

    return True 
    

# pygame setup
pygame.init()


block_size = 51
block_width = 10
block_height = 20

HEIGHT = block_size * block_height +1
WIDTH = block_size * block_width  +1 

symbols = [[(0,0),(0,1),(0,2),(-1,0)],
           [(0,0),(0,1),(1,0),(1,1)],
           [(-1,0),(0,0),(1,0),(0,1)],
           [(-1,0),(0,0),(1,0),(2,0)],
           [(-1,1),(0,1),(0,0),(1,0)]]


screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

current_symbol = choice(symbols)
x_pos = 5
y_pos = 5

set_blocks = {}

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_w: 
                current_symbol = rotate_by_origin(current_symbol)
            if event.key == pygame.K_s: 
                continue
            if event.key == pygame.K_a: 
                if validity_check_side(current_symbol,x_pos,y_pos, -1):
                    x_pos -= 1
            if event.key == pygame.K_d: 
                if validity_check_side(current_symbol,x_pos,y_pos, 1):
                    x_pos += 1


    screen.fill("black")

    for x in range(0,WIDTH,51):
        pygame.draw.line(screen, "grey", (x,0),(x,HEIGHT))

    for y in range(0,HEIGHT,51):
        pygame.draw.line(screen, "grey", (0,y),(WIDTH,y))

    pygame.draw.rect(screen, "red", (0,0,WIDTH,102))


    moved_symbol = move_symbol(current_symbol,x_pos,y_pos)

    for x,y in moved_symbol:
        pygame.draw.rect(screen, "green", (x*block_size+1,y*block_size+1,50,50))


    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
