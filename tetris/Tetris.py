from math import sqrt
import pygame
from random import choice


# Draw text
def draw_text(screen, text, font_name, size, color, position, coordinates):
    
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(str(text), True, color)
    
    text_rect = text_surface.get_rect()
    setattr(text_rect, position, coordinates)
    screen.blit(text_surface, text_rect)

    return

#Draw tetrominos
def draw_tetrominos(tetromino_list,screen, BLOCK_SIZE,rainbow_img):

    for x,y,color in tetromino_list:
        
        x1 = x*BLOCK_SIZE+1
        y1 = y*BLOCK_SIZE+1
        x2 = BLOCK_SIZE-1
        y2 = BLOCK_SIZE-1

        if color == "white":
            test = pygame.draw.rect(screen, (0,0,0,0), (x1,y1,x2,y2))
            screen.blit(pygame.transform.scale(rainbow_img, (50, 50)), test)
            continue


        pygame.draw.rect(screen, color, (x1,y1,x2,y2))

        color_code = pygame.Color(color)

        highlight = tuple(min(c+50,255) for c in color_code)

        pygame.draw.line(
                screen, highlight,
                (x1 + 3, y1 + 3),
                (x1 + 50 - 4, y1 + 3),
                3
            )

        pygame.draw.line(
            screen, highlight,
            (x1 + 3, y1 + 3),
            (x1 + 3, y1 + 50 - 4),
            3
        )
    return


def draw_grid(screen, WIDTH, HEIGHT, BLOCK_SIZE, powerbar_width):
    for x in range(0, WIDTH  - powerbar_width, BLOCK_SIZE):
        pygame.draw.line(screen, "grey50", (x,0),(x,HEIGHT))

    for y in range(0, HEIGHT , BLOCK_SIZE):
        pygame.draw.line(screen, "grey50", (0,y),(WIDTH- powerbar_width,y))

    return


def draw_hud(screen,next_symbol,score,rows_destroyed_total, WIDTH, HEIGHT, BLOCK_SIZE, gravity_ms,ppnt):
    
    #Draw Powerbar
    pygame.draw.rect(screen, "lawngreen", (WIDTH-100, HEIGHT-ppnt, 100, ppnt))
    
    #Draw HUD
    pygame.draw.rect(screen, "indianred1", (0,0,WIDTH,BLOCK_SIZE*2))

    draw_text(screen, f"Score: {score}", "unispacebold", 20, "black", "topleft",(10, 20))
    draw_text(screen, f"Rows: {rows_destroyed_total}", "unispacebold", 20, "black", "topleft",(10, 60))

    draw_text(screen, f"Tetris", "unispacebold", 50, "black", "center", (WIDTH/2-10, 50))
    draw_text(screen, f"Tetris", "unispacebold", 46, "white", "center", (WIDTH/2-10, 50))

    draw_text(screen, f"Next Tetromino:", "unispacebold", 15, "black", "topright",(WIDTH-20, 10))
    draw_text(screen, f"{gravity_ms}", "unispacebold", 15, "white", "center",(WIDTH-50, 120))

    for x,y in next_symbol:
            
            x1 = x*15 + WIDTH-100
            y1 = y*15 + 50
            x2 = 14
            y2 = 14

            pygame.draw.rect(screen, "black", (x1+1,y1+1,x2+1,y2+1))
            pygame.draw.rect(screen, "green", (x1,y1,x2,y2))


#moves symbol to position and adds color to touple
def move_symbol(symbol, width, height, color):
    
    moved = []
    for x,y in symbol:
        moved.append((x + width, y + height, color))

    return moved


# rotates the symbol by 90 degress 
def rotate_by_origin(symbol):

    if symbol == [(0,0),(0,1),(1,0),(1,1)]:
        return symbol
    
    for i, (x, y) in enumerate(symbol):
        symbol[i] = (y, -x)

    return symbol


#predict if a move is legal
def this_move_legal(symbol, x_pos, y_pos, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):

    moved_symbol = move_symbol(symbol, x_pos, y_pos, "")



    for x, y, c in moved_symbol:

        # Left/right walls
        if x < 0 or x > BLOCK_WIDTH-1:
            return False

        #Bottom wall
        if y > BLOCK_HEIGHT-1:
            return False

        # Existing blocks
        if any((x, y) == (bx, by) for bx, by, bc in set_blocks):
            return False

    return True


#checks if bottom or the other symbols are reached
def reached_bottom(symbol, set_blocks, BLOCK_HEIGHT):

    for x,y,c in symbol:
        if y == BLOCK_HEIGHT-1:
            return True

        for dx,dy, dc in set_blocks:
            if dy - y == 1 and x == dx:
                return True

    return False

#Looks for full rows and deletes them while shifting all above down
def seek_and_destroy(set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):

    tracker = [0 for _ in range(BLOCK_HEIGHT)]
    indexes = []

    for x,y,c in set_blocks:
        tracker[y] +=1

        if tracker[y] == BLOCK_WIDTH:
            indexes.append(y)


    if not indexes:
        return set_blocks, []
    indexes.sort()

    for value in indexes:

        new_list = []
        for x,y,c in set_blocks:

            if y < value:
                new_list.append((x,y+1,c))

            elif y > value:
                new_list.append((x,y,c))
        set_blocks = new_list


    return set_blocks, indexes


class Button():
    def __init__(self, image, x, y, scale, hover_scale=1.3):
        w, h = image.get_size()
        self.normal = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
        self.hover = pygame.transform.scale(image, (int(w * scale * hover_scale), int(h * scale * hover_scale)))
        self.rect = self.normal.get_rect(topleft=(x, y))
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(pos)

        if hovering:
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        if hovering:
            rect = self.hover.get_rect(center=self.rect.center)
            surface.blit(self.hover, rect)
        else:
            surface.blit(self.normal, self.rect)

        return action


def fluid_movement(set_blocks, fluid_blocks, height):
    
    def select_above(fluid_blocks, x, y, c):
        for bx, by, bc in fluid_blocks:
            if bx == x and by == y - 1:
                return [(x, y, c)] + select_above(fluid_blocks, x, y - 1, bc)
        return [(x, y, c)]

    gap_column = []
    to_remove = []
    for x,y,c in fluid_blocks:

        if (x,y,c) in to_remove:
            continue

        elif any(bx == x and by == y + 1 and (bx, by, bc) not in fluid_blocks
            for bx, by, bc in set_blocks):
                to_remove += select_above(fluid_blocks, x, y, c)
                continue

        elif any(bx == x and by == y + 1 for bx, by, _ in fluid_blocks):
            continue

        elif y == height-1:
            to_remove += select_above(fluid_blocks,x,y,c)

        else:
            gap_column += select_above(fluid_blocks,x,y,c)
        
    for (x,y,c) in gap_column:
        indx = set_blocks.index((x,y,c))
        set_blocks[indx] = (x,y+1,c)
        indx = fluid_blocks.index((x,y,c))
        fluid_blocks[indx] = (x,y+1,c)


    if to_remove:
        for item in to_remove:
            fluid_blocks.remove(item)

    return set_blocks, fluid_blocks




def main():

    print(pygame.Color("white"))
    # pygame setup
    pygame.init()
    pygame.display.set_caption('Tetris EXTREME')

    #Game size
    BLOCK_SIZE = 51
    BLOCK_WIDTH = 10
    BLOCK_HEIGHT = 20
    powerbar_width = 100
    HEIGHT = BLOCK_SIZE * BLOCK_HEIGHT +1
    WIDTH = BLOCK_SIZE * BLOCK_WIDTH + powerbar_width +1 

    #Tetris blocks and color palette
    tetris_colors = ["blue","chartreuse3","darkgoldenrod1","darkorchid2","turquoise1","crimson"]
    symbols = [[(0,0),(0,1),(0,2),(-1,0)], # L
            [(0,0),(0,1),(0,2),(1,0)],  # L reverse
            [(0,0),(0,1),(1,0),(1,1)],  # Cube
            [(-1,0),(0,0),(1,0),(0,1)], # T
            [(-1,0),(0,0),(1,0),(2,0)], # Straight
            [(-1,1),(0,1),(0,0),(1,0)], # Z
            [(1,1),(0,1),(0,0),(-1,0)]] # Z


    #Initialize Screen and Clock
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True


    #Icons
    expansion_img = pygame.image.load('expansion.png').convert_alpha()
    expansion_button = Button(expansion_img,  WIDTH - powerbar_width +25, 150, 2.5)
    bomb_img = pygame.image.load('bomb.png').convert_alpha()
    bomb_button = Button(bomb_img,  WIDTH - powerbar_width +25, 250, 2.5)
    water_img = pygame.image.load('water.png').convert_alpha()
    water_button = Button(water_img,  WIDTH - powerbar_width +25, 350, 2.5)
    rainbow_img = pygame.image.load('rainbow.png').convert_alpha()
    rainbow_button = Button(rainbow_img,  WIDTH - powerbar_width +25, 450, 2.5)
    nuke_img = pygame.image.load('nuke.png').convert_alpha()
    nuke_button = Button(nuke_img,  WIDTH - powerbar_width +25, 550, 2.5)
    stopwatch_img = pygame.image.load('stopwatch.png').convert_alpha()
    stopwatch_button = Button(stopwatch_img,  WIDTH - powerbar_width +25, 650, 2.5)
    bonus_img = pygame.image.load('bonus.png').convert_alpha()
    bonus_button = Button(bonus_img,  WIDTH - powerbar_width +25, 750, 2.5)
    multiplier_img = pygame.image.load('multiplier.png').convert_alpha()
    multiplier_button = Button(multiplier_img,  WIDTH - powerbar_width +25, 850, 2.5)
    reroll_img = pygame.image.load('reroll.png').convert_alpha()
    reroll_button = Button(reroll_img,  WIDTH - powerbar_width +25, 950, 2.5)
     

    #Symbol start values
    current_color = choice(tetris_colors)
    current_symbol = choice(symbols).copy()
    next_symbol = choice(symbols).copy()
    x_pos = BLOCK_WIDTH // 2
    y_pos = 0

    #Gravity timer
    GRAVITY_EVENT = pygame.USEREVENT + 1
    gravity_ms = 500  
    pygame.time.set_timer(GRAVITY_EVENT, gravity_ms)

    #Multiplier timer
    multiplier_end = 0
    multiplier_length = 15000

    #Fluid feature setup
    fluid_state = False
    fluid_blocks = []

    #Select block
    find_field = False
    bomb = False
    special = False

    #Score and dead symbols
    set_blocks = []
    score = 0 
    rows_destroyed_total = 0
    power_points = 0


    while running:

        multiplier = 2 if multiplier_end > pygame.time.get_ticks() else 1

        #Check for input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == GRAVITY_EVENT:
                if this_move_legal(current_symbol, x_pos, y_pos + 1, set_blocks,BLOCK_WIDTH, BLOCK_HEIGHT):
                    y_pos += 1
                if fluid_blocks:
                    set_blocks, fluid_blocks = fluid_movement(set_blocks, fluid_blocks,BLOCK_HEIGHT)

            if event.type == pygame.KEYDOWN:           
                if event.key == pygame.K_w: 
                    if this_move_legal(rotate_by_origin(current_symbol.copy()),x_pos,y_pos, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):
                        current_symbol  = rotate_by_origin(current_symbol)

                if event.key == pygame.K_s: 
                    if this_move_legal(current_symbol,x_pos,y_pos+1, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):
                        y_pos += 1
                        score += 1 * multiplier
                
                if event.key == pygame.K_a: 
                    if this_move_legal(current_symbol,x_pos-1,y_pos, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):
                        x_pos -= 1
            
                if event.key == pygame.K_d: 
                    if this_move_legal(current_symbol,x_pos+1,y_pos, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):
                        x_pos += 1


        moved_symbol = move_symbol(current_symbol,x_pos,y_pos,current_color)

        if reached_bottom(moved_symbol, set_blocks, BLOCK_HEIGHT):
            if fluid_state:
                fluid_blocks += moved_symbol
                fluid_state = False

            set_blocks += moved_symbol
            current_symbol = next_symbol.copy()
            next_symbol = choice(symbols).copy()
            current_color = choice(tetris_colors)
            x_pos = BLOCK_WIDTH // 2
            y_pos = 0


        #Remove full rows and show short animation
        old_set = set_blocks
        set_blocks, destroyed_index = seek_and_destroy(set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT)

        if destroyed_index:
            gravity_ms = max(200,gravity_ms - len(destroyed_index) * 10)
            pygame.time.set_timer(GRAVITY_EVENT, gravity_ms)

            rows_destroyed_total += len(destroyed_index)
            score += (len(destroyed_index) ** 2) * 100 * multiplier
            power_points += (len(destroyed_index) ** 2) * 100

            #Flash white
            screen.fill("black")
            draw_grid(screen, WIDTH, HEIGHT, BLOCK_SIZE, powerbar_width)

            draw_tetrominos(old_set + moved_symbol,screen, BLOCK_SIZE, rainbow_img)

            for x,y,color in [t for t in old_set if t[1]  in destroyed_index ] + [t for t in moved_symbol if t[1]  in destroyed_index ]:
                    
                x1 = x*BLOCK_SIZE+1
                y1 = y*BLOCK_SIZE+1
                x2 = BLOCK_SIZE-1
                y2 = BLOCK_SIZE-1
                    
                pygame.draw.rect(screen, "white", (x1,y1,x2,y2))

            draw_hud(screen,next_symbol,score,rows_destroyed_total, WIDTH, HEIGHT, BLOCK_SIZE, gravity_ms, power_points)

            pygame.display.flip()
            pygame.time.wait(50)

            #Draw GAP
            screen.fill("black")
            draw_grid(screen, WIDTH, HEIGHT, BLOCK_SIZE, powerbar_width)
            draw_tetrominos([t for t in old_set if t[1] not in destroyed_index ] + 
                            [t for t in moved_symbol if t[1] not in destroyed_index ],
                            screen, BLOCK_SIZE,rainbow_img)
            
            draw_hud(screen,next_symbol,score,rows_destroyed_total, WIDTH, HEIGHT, BLOCK_SIZE, gravity_ms,power_points)

            pygame.display.flip()
            pygame.time.wait(150)


        #Draw Grid, Tetrominos, HUD
        screen.fill("black")
        draw_grid(screen, WIDTH, HEIGHT, BLOCK_SIZE, powerbar_width)
        draw_tetrominos(set_blocks + moved_symbol,screen, BLOCK_SIZE,rainbow_img)
        draw_hud(screen,next_symbol,score,rows_destroyed_total, WIDTH, HEIGHT, BLOCK_SIZE, gravity_ms,power_points)
        

        if find_field:
            pos = pygame.mouse.get_pos()

            x1 = int(pos[0] / BLOCK_SIZE)*BLOCK_SIZE+1
            y1 = int(pos[1] / BLOCK_SIZE)*BLOCK_SIZE+1
            x2 = y2 = 50

            if pos[1] > BLOCK_SIZE*2 and pos[0] < WIDTH - powerbar_width:
                pygame.draw.rect(screen, "yellow", (x1,y1,x2,y2),3)

                if pygame.mouse.get_pressed()[0]:
                    x = int(pos[0] / BLOCK_SIZE) 
                    y = int(pos[1] / BLOCK_SIZE)

                    if special:
                        set_blocks.append((x,y,"white"))
                        special = False
                    if bomb:
                        to_clear = {(i,j)  for i in range(x-1,x+2) for j in range(y-1,y+2)}
                        set_blocks = [b for b in set_blocks if (b[0],b[1]) not in to_clear]
                        bomb = False
                    
                    find_field = False

        #Special abilities check
        if bomb_button.draw(screen):
            find_field = True
            bomb = True
            print("bomb")

        if water_button.draw(screen):
            fluid_state = True
            print("water")

        if rainbow_button.draw(screen):
            find_field = True
            special = True
            print("rainbow")

        if nuke_button.draw(screen):
            set_blocks = []
            print("nuke")

        if stopwatch_button.draw(screen):
            gravity_ms += 50
            pygame.time.set_timer(GRAVITY_EVENT, gravity_ms)
            print("stopwatch")

        if bonus_button.draw(screen):
            score += 500
            print("bonus")

        if multiplier_button.draw(screen):
            multiplier_end = pygame.time.get_ticks() + multiplier_length
            print("multiplier")

        if reroll_button.draw(screen):
            current_symbol = choice(symbols).copy()
            current_color = choice(tetris_colors)
            x_pos = BLOCK_WIDTH // 2
            y_pos = 0
            print("reroll")

        if expansion_button.draw(screen):
            BLOCK_HEIGHT += 1
            HEIGHT = BLOCK_SIZE * BLOCK_HEIGHT + 1
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            set_blocks = [(x,y+1,c) for x,y,c in set_blocks]
            print("expansion")



        #Check if the game should end
        if not this_move_legal(current_symbol,x_pos,y_pos, set_blocks, BLOCK_WIDTH, BLOCK_HEIGHT):
            draw_text(screen, "Game Over!", "unispacebold", 48, "fuchsia", "center", (WIDTH/2, HEIGHT/2))
            draw_text(screen, "Game Over!", "unispacebold", 46, "white", "center", (WIDTH/2, HEIGHT/2))
            pygame.display.flip()
            pygame.time.wait(4000)
            running = False

        # flip() the display to put your work on screen
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()