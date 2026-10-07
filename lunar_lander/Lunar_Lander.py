# Example file showing a circle moving on screen
import pygame
from random import randint
import numpy as np


def draw_text(screen, text, font_name, size, color, position, coordinates):
    
    font = pygame.font.SysFont(font_name, size)
    text_surface = font.render(str(text), True, color)
    
    text_rect = text_surface.get_rect()
    setattr(text_rect, position, coordinates)
    screen.blit(text_surface, text_rect)

    return


def draw_hud(landar_angle, landar_speed, altitude, fuel, score):

    draw_text(screen, f"Angle: {landar_angle+135}", "unispacebold", 15, "white", "topleft",(WIDTH-230, 20))
    draw_text(screen, f"Altitude: {altitude}", "unispacebold", 15, "white", "topleft",(WIDTH-230, 35))
    draw_text(screen, f"Horizontal speed: {round(landar_speed[0],0)}", "unispacebold", 15, "white", "topleft",(WIDTH-230, 50))
    draw_text(screen, f"Vertica speed: {round(landar_speed[1],0)}", "unispacebold", 15, "white", "topleft",(WIDTH-230, 65))

    draw_text(screen, f"Score: {score}", "unispacebold", 15, "white", "topleft",(20, 20))
    draw_text(screen, f"Time: {pygame.time.get_ticks()/1000}", "unispacebold", 15, "white", "topleft",(20, 35))
    draw_text(screen, f"fuel: {fuel}", "unispacebold", 15, "white", "topleft",(20, 50))


def angle_change_allowed(angle):

    if angle < MIN_ANGLE  or angle > MAX_ANGLE:
        return False
    return True

def draw_terrain(terrain_points,stars, landar_pos, zoom, thrust_strength):


    dist = (WIDTH / zoom) / 2
    dist2 = (HEIGHT / zoom) / 2
    abzug = landar_pos[0] - dist
    abzug2 = landar_pos[1] - dist2
    sx = lambda x: (x - abzug) * zoom
    sy = lambda y: (y - abzug2) * zoom/2



    for i in range(len(terrain_points)-1):
        x1,y1 = terrain_points[i] 
        x2,y2 = terrain_points[i+1]
        c = "white"
        if y1 == y2:
            mult = int((1/(x2-x1+1))*50)
            draw_text(screen, f"{mult}x", "unispacebold", 10, "white", "center",(sx((x1 + x2) / 2), sy(y1+20)))
            c = "indianred"



        pygame.draw.line(screen, c, (sx(x1),sy(y1)), (sx(x2),sy(y2)))

    for x,y in stars:

        if randint(1,300)== 9:
            pygame.draw.circle(screen, "white", (sx(x),y), 4)
        else:
            pygame.draw.circle(screen, "white", (sx(x),y), 2)

    #draw rocket
    rotated_image = pygame.transform.rotate(landar_img, landar_angle+135)
    rect = rotated_image.get_rect(center=(sx(landar_pos[0]),sy(landar_pos[1])))
    screen.blit(rotated_image, rect)

    if thrust_strength > 0: 
        draw_jet(pygame.Vector2(sx(landar_pos[0]),sy(landar_pos[1])),landar_angle, thrust_strength)

    return abzug, abzug2

def change_speed(angle, speed):

    normalized = pygame.Vector2(1,1).rotate(angle)
    normalized = pygame.math.Vector2.normalize(normalized)

    speed[0] -= normalized[0] * 0.25
    speed[1] += normalized[1] * 0.25

    return speed


def get_closest_points(point_list,position):

    for i in range(len(point_list)):
        if point_list[i][0] > position[0]:
            return point_list[i-1][0],point_list[i-1][1],point_list[i][0],point_list[i][1]
    

def get_altitude(position, point_list):

    x1,y1,x2,y2 = get_closest_points(point_list,position)

    steigung = (y2-y1)/(x2-x1)

    return round((y1 - (position[1] + steigung * (x1-position[0])) - (LANDER_SIZE/2)/zoom)-3,1)
    
def draw_jet(landar_pos,landar_angle,thrust_strength):

    pos = landar_pos.copy()
    normalized = pygame.Vector2(1,1).rotate(-landar_angle+90)
    normalized = pygame.math.Vector2.normalize(normalized)

    normalized2 = pygame.math.Vector2.normalize(pygame.Vector2(1,1).rotate(-landar_angle))

    pnt1 = pos + normalized2*6
    pnt2 = pos - normalized2*6

    pnt1 -= normalized * 10
    pnt2 -= normalized * 10

    mult = min(35,5 + thrust_strength)
    mult += randint(1,10)
    
    pos[0] -= normalized[0] * mult
    pos[1] -= normalized[1] * mult

    pygame.draw.line(screen, "white", pos, pnt1)
    pygame.draw.line(screen, "white", pos, pnt2)

    return

def get_target_zoom(altitude):
    # Zoom starts at 150 px altitude, reaches max zoom of 3x near the ground
    if altitude > 250:
        return 1.0
    t = 1 - max(altitude, 0) / 250   # 0 -> 1 as you descend
    return 1.0 + t * 3.0    


def make_sound(samples, volume=0.5):
    samples = samples / np.max(np.abs(samples))
    data = (samples * volume * 32767).astype(np.int16)
    data = np.column_stack((data, data))          # stereo
    return pygame.sndarray.make_sound(data)

def rumble(duration, smooth):
    n = int(SR * duration)
    noise = np.random.uniform(-1, 1, n)
    # pad with the opposite ends so the filter wraps around
    padded = np.concatenate((noise[-smooth:], noise, noise[:smooth]))
    kernel = np.ones(smooth) / smooth
    out = np.convolve(padded, kernel, mode="same")
    return out[smooth:-smooth]

def start_settings():
    #TERRAIN GENERATOR
    last_y = randint(300,HEIGHT)
    last_x = -800
    last_flat = False
    terrain_points = [(last_x,last_y)]

    while last_x < WIDTH:

        if randint(0,20) == 1 and not last_flat:
            new_y = last_y
            new_x = randint(last_x+10,last_x+40)
            last_flat = True
        else:
            new_y = randint(last_y-50,last_y+50)        
            new_x = randint(last_x,last_x+20)
            last_flat = False
        
        if new_y > HEIGHT-10 or new_y < 200:
            continue

        terrain_points.append((new_x,new_y))
        last_y = new_y
        last_x = new_x


    stars = [(randint(-800, WIDTH), randint(0, 200)) for _ in range(40)]
    zoom = 1.0
    landar_angle = -45
    landar_speed = pygame.Vector2(randint(50,80),randint(5,10))
    landar_pos = pygame.Vector2(0, randint(-100,0))

    return terrain_points, stars,zoom, landar_angle, landar_speed, landar_pos



# pygame setup
SR = 44100
pygame.mixer.pre_init(44100, -16, 2, 512)   # 2 = stereo
pygame.init()

WIDTH = 1280
HEIGHT = 720
LANDER_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0

# sounds (after pygame.init())
thrust_sound = make_sound(rumble(1.0, 30), 0.05)

crash = rumble(1.5, 60) * np.linspace(1, 0, int(SR * 1.5)) ** 2
crash_sound = make_sound(crash, 0.7)

t = np.linspace(0, 0.15, int(SR * 0.15), False)
beep_sound = make_sound(np.sin(2 * np.pi * 880 * t), 0.3)

thrust_channel = pygame.mixer.Channel(0)
thrust_strength = 0

terrain_points, stars,zoom, landar_angle, landar_speed, landar_pos = start_settings()

score = 0
fuel = 1000

MAX_ANGLE = -45
MIN_ANGLE = -225

landar_img = pygame.image.load("lunar_lander.png").convert_alpha()
landar_img = pygame.transform.scale(landar_img, (LANDER_SIZE,LANDER_SIZE))

while running:

    screen.fill("black") 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and fuel > 0:
        fuel -= 0.5
        landar_speed = change_speed(landar_angle,landar_speed)
        
        thrust_strength += 1
        thrust_channel.play(thrust_sound, loops=-1)

    else:
        thrust_channel.fadeout(80)
        thrust_strength = 0

    if keys[pygame.K_a]:
        if angle_change_allowed(landar_angle+1):
            landar_angle += 1
    if keys[pygame.K_d]:
        if angle_change_allowed(landar_angle-1):
            landar_angle -= 1

    
    landar_pos += landar_speed * dt
    landar_speed[1] += 8 * dt 
    altitude = get_altitude(landar_pos, terrain_points)

    zoom = max(zoom,get_target_zoom(altitude))

    #draw terrain and stars
    abzug, abzug2 = draw_terrain(terrain_points,stars, landar_pos, zoom,thrust_strength)
    sx = lambda x: (x - abzug) * zoom
    sy = lambda y: (y - abzug2) * zoom/2

    #HUD
    draw_hud(landar_angle, landar_speed, altitude, fuel, score)

    #check if game should end
    if altitude <= 0:
        x1,y1,x2,y2 =  get_closest_points(terrain_points,landar_pos)

        if abs(landar_angle+135) <= 5 and landar_speed.length() < 8 and y1 == y2:
            mult = int((1/(x2-x1+1))*50)
            score += 50 * mult
            thrust_channel.fadeout(40)
            beep_sound.play()

            draw_text(screen, f"A perfect landing!", "unispacebold", 15, "white", "center",(sx(landar_pos[0]),sy(landar_pos[1]-30)))
            draw_text(screen, f"{50 * mult} Points", "unispacebold", 15, "white", "center",(sx(landar_pos[0]),sy(landar_pos[1]-15)))
            pygame.display.flip()
            pygame.time.delay(2000)
            terrain_points, stars,zoom, landar_angle, landar_speed, landar_pos = start_settings()

        else:
            crash_sound.play()
            thrust_channel.fadeout(40)
            draw_text(screen, f"Game Over!", "unispacebold", 15, "white", "center",(sx(landar_pos[0]),sy(landar_pos[1]-30)))
            draw_text(screen, f"Final Score: {score}", "unispacebold", 15, "white", "center",(sx(landar_pos[0]),sy(landar_pos[1]-15)))
            pygame.display.flip()
            pygame.time.delay(4000)
            running = False
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()