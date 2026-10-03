from math import sqrt
import pygame
from random import choice

def move_symbol(symbol, width, height, color):
    
    moved= []

    for x,y in symbol:
        moved.append((x + width, y + height, color))

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

def reached_bottom(symbol, set_blocks):

    for x,y in symbol:
        if y == 19:
            return True

        for dx,dy in set_blocks:
            if abs(y-dy) == 1 and abs(x-dx) == 0:
                return True

    return False

# pygame setup
pygame.init()


block_size = 51
block_width = 10
block_height = 20

HEIGHT = block_size * block_height +1
WIDTH = block_size * block_width  +1 

tetris_colors = ["blue","green","yellow","orange","green"]
symbols = [[(0,0),(0,1),(0,2),(-1,0)],
           [(0,0),(0,1),(1,0),(1,1)],
           [(-1,0),(0,0),(1,0),(0,1)],
           [(-1,0),(0,0),(1,0),(2,0)],
           [(-1,1),(0,1),(0,0),(1,0)]]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

current_color = choice(tetris_colors)
current_symbol = choice(symbols)
x_pos = 5
y_pos = 0

set_blocks = []
score = 0 
count_frames = 0

while running:

    #Check for input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_w: 
                current_symbol = rotate_by_origin(current_symbol)
            if event.key == pygame.K_s: 
                y_pos += 1
                score += 1
            if event.key == pygame.K_a: 
                if validity_check_side(current_symbol,x_pos,y_pos, -1):
                    x_pos -= 1
            if event.key == pygame.K_d: 
                if validity_check_side(current_symbol,x_pos,y_pos, 1):
                    x_pos += 1

    
    moved_symbol = move_symbol(current_symbol,x_pos,y_pos,current_color)

    if reached_bottom(moved_symbol, set_blocks):
        set_blocks += moved_symbol
        current_symbol = choice(symbols)
        current_color = choice(tetris_colors)
        x_pos = 5
        y_pos = 0
        continue


    if count_frames % 30 == 0:
        y_pos += 1

    if reached_bottom(moved_symbol, set_blocks):
        set_blocks += moved_symbol
        current_symbol = choice(symbols)
        current_color = choice(tetris_colors)
        x_pos = 5
        y_pos = 0


    screen.fill("black")


    #Draw Grid
    for x in range(0, WIDTH, block_size):
        pygame.draw.line(screen, "grey", (x,0),(x,HEIGHT))

    for y in range(0, HEIGHT, block_size):
        pygame.draw.line(screen, "grey", (0,y),(WIDTH,y))


    #Draw Symbols
    for x,y in moved_symbol + set_blocks:
        pygame.draw.rect(screen, "green", (x*block_size+1,y*block_size+1,block_size-1,block_size-1))


    #Draw HUD
    pygame.draw.rect(screen, "red", (0,0,WIDTH,block_size*2))



    if reached_bottom (moved_symbol, set_blocks) and y_pos == 0:
        print("hey")
        font = pygame.font.SysFont("impact", 55)
        text_surface = font.render(str("You lost Fatty"), True, "green")
        text_rect = text_surface.get_rect(center=(250, 50))
        screen.blit(text_surface, text_rect)
        running = False

    # flip() the display to put your work on screen
    pygame.display.flip()

    count_frames += 1
    
    clock.tick(60)

pygame.quit()
