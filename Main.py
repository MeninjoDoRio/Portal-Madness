# Pygame Python Platformer Game
import pygame
import levels
pygame.init()
from levels import *

# ====================
# set up pygame game
# ====================
WIDTH = 1800
HEIGHT = 900
TILE_SIZE = 100 # when scaling down the WIDTH and HEIGHT, make sure to adjust TILE_SIZE accordingly
#screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Space Platformer!!')
fps = 60 
timer = pygame.time.Clock()

# ====================
# LEVEL & Game STATUS
# ====================
active_level = 0
active_phase = 3
level = levels[active_level][active_phase]


# drawing the player onto the screen
for _ in range(len(level)): 
    if 5 in level[_]:
        start_pos = (_, level[_].index(5)) # row, column

# ==============
# GAME VARIABLES
# =============
player_scale = 14 # scaling factor for player sprite
inventory = [False, False, False, False] # Inventory for blue, green, red, yellow keys

# initial player coordinates
player_x = start_pos[1] * 100
player_y = start_pos[0] * 100 - (8 * player_scale - 100) 
init_x = start_pos[1] * 100
init_y = start_pos[0] * 100 - (8 * player_scale - 100) 

counter = 0
mode = 'idle'           # idle, run, jump, fall
direction = 1           # 1 - right, -1 - left
player_speed = 10       # adjust it for difficulty purposes
colliding = False       # Collision State 
door_collisions = [False, False, False, False] # portal collision states for blue, green, red, yellow portals
gravity = 0.5
y_change = 0
jump_height = 14

# initial state of the game when booting up
in_air = False
lives = 3
enter_message = False
time = 0
win = False
lose = False

# ======================================
# load in high score upon program start
# ======================================
file = open('high_score.txt', 'r')
read = file.readlines()
if read[0] != '':
    high_score = read[0]
    high_score = int(high_score)
else:
    high_score = 0
file.close()

# ==============================
# load images in for use in game
# ==============================
bg = pygame.image.load('assets/images/space bg.png')
rock = pygame.transform.scale(pygame.image.load('assets/images/tiles/rock.png'), (TILE_SIZE, TILE_SIZE))
ground = pygame.transform.scale(pygame.image.load('assets/images/tiles/ground.png'), (TILE_SIZE, TILE_SIZE))
acid = pygame.transform.scale(pygame.image.load('assets/images/tiles/acid2.png'), (TILE_SIZE, 0.25 * TILE_SIZE))
platform = pygame.transform.scale(pygame.image.load('assets/images/tiles/platform.png'), (TILE_SIZE, 0.5 * TILE_SIZE))

# load in keys and doors
blue_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_blue.png'), (0.6 * TILE_SIZE, TILE_SIZE))
green_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_green.png'), (0.6 * TILE_SIZE, TILE_SIZE))
red_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_red.png'), (0.6 * TILE_SIZE, TILE_SIZE))
yellow_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_yellow.png'), (0.6 * TILE_SIZE, TILE_SIZE))
blue_door = pygame.transform.scale(pygame.image.load('assets/images/portals/blue.png'), (TILE_SIZE, TILE_SIZE))
green_door = pygame.transform.scale(pygame.image.load('assets/images/portals/green.png'), (TILE_SIZE, TILE_SIZE))
red_door = pygame.transform.scale(pygame.image.load('assets/images/portals/red.png'), (TILE_SIZE, TILE_SIZE))
yellow_door = pygame.transform.scale(pygame.image.load('assets/images/portals/yellow.png'), (TILE_SIZE, TILE_SIZE))
lock = pygame.transform.scale(pygame.image.load('assets/images/lock.png'), (0.6 * TILE_SIZE, 0.6 * TILE_SIZE))

# tile list for drawing
tiles = ['', rock, ground, platform, acid]
keys = [blue_key, green_key, red_key, yellow_key]
doors = [blue_door, green_door, red_door, yellow_door]
frames = []


# load in player frames for animation
for _ in range(4):
    frames.append(pygame.transform.scale(pygame.image.load(f'assets/images/astronaut/{_+1}.png'), 
                                         (5 * player_scale, 8 * player_scale)))
    

# ===============================
# load in music and sound effects
# =============================== 
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/song2.mp3')
pygame.mixer.music.set_volume(0.2) # set volume for music
pygame.mixer.music.play(-1) # play music on loop 
acid_sound =  pygame.mixer.Sound('assets/sounds/acid.mp3')
portal_sound = pygame.mixer.Sound('assets/sounds/fast woosh.mp3')
end_sound = pygame.mixer.Sound('assets/sounds/victory.mp3')
jump_sound = pygame.mixer.Sound('assets/sounds/leap.mp3')
key_sound = pygame.mixer.Sound('assets/sounds/key_acquire.mp3')


#==================
# FUNCTIONS (teleporting, drawing inventory, checking collisions)
#==================

# create teleport when going through portals
def teleport(index, current_phase):
    phase = current_phase
    coords = (0, 0)
    for i in range(len(levels[active_level])):
        for j in range(len(levels[active_level][i])):
            if index + 10 in levels[active_level][i][j] and i != current_phase: # find the door that was collided with
                y_pos = j
                x_pos = levels[active_level][i][j].index(index + 10) # find the coordinates of the door in the new phase
                coords = (x_pos, y_pos)
                phase = i # set new phase to the one where the door was found 
    return phase, coords

# draw inventory and HUD for instructions and scoring on bottom of screen
def draw_inventory():
    font = pygame.font.Font('assets/fonts/neo_sci_fi/neo_scifi.ttf', 20)
    colors = ['blue', 'green', 'red', 'yellow'] # colors of keys in inventory

    # HUD background and rectangles
    pygame.draw.rect(screen, 'black', [5, HEIGHT - 120, WIDTH - 10, 110], 0, 5) # black BG rectangle
    pygame.draw.rect(screen, 'purple', [5, HEIGHT - 120, WIDTH - 10, 110], 3, 5) # inner purple rectangle
    pygame.draw.rect(screen, 'white', [8, HEIGHT - 117, 340, 104], 3, 5) # white rectangle rest of instructions
    pygame.draw.rect(screen, 'white', [348, HEIGHT - 117, 532, 104], 3, 5) # white rectangle rest of instructions
    pygame.draw.rect(screen, 'white', [880, HEIGHT - 117, 720, 104], 3, 5) # white rectangle rest of instructions
    pygame.draw.rect(screen, 'white', [1600, HEIGHT - 117, 1920, 104], 3, 5) # white rectangle rest of instructions
    font.italic = True 

    # drawing inventory boxes and keys
    inventory_text = font.render(' I n v e n t o r y: ', True, 'white')
    screen.blit(inventory_text, (14, HEIGHT - 105))

    for i in range(4):
        pygame.draw.rect(screen, colors[i], [10 + (80 * i), HEIGHT - 88, 70, 70], 5, 5)
        if inventory[i]:
            scaled_key = pygame.transform.scale(keys[i], (40, 70))
            screen.blit(scaled_key, (25 + (80 * i), HEIGHT - 88))

    # drawing level, phase, lives, time, best time
    font = pygame.font.Font('assets/fonts/neo_sci_fi/neo_scifi.ttf', 20)
    level_text = font.render(f' Level: {active_level + 1} ', True, 'white')
    screen.blit(level_text, (344, HEIGHT - 110))
    phase_strings = ['Blue', 'Green', 'Red', 'Gold']
    phase_text = font.render(f'Phase: {phase_strings[active_phase]}', True, colors[active_phase])
    screen.blit(phase_text, (354, HEIGHT - 80))
    lives_text = font.render(f' Lives: {lives} ', True, 'green')
    screen.blit(lives_text, (344, HEIGHT - 50))
    time_text = font.render('Elapsed Time:', True, 'gray')
    time_text2 = font.render(f' {time//20} seconds', True, 'white')
    screen.blit(time_text, (700, HEIGHT - 110))
    screen.blit(time_text2, (700, HEIGHT - 89))
    best_text = font.render(f'Best Time: {high_score}', True, 'light gray')
    screen.blit(best_text, (700, HEIGHT - 50))

    # drawing instructions when colliding with a Portal to go through portal or collect keys
    if enter_message: 
        font = pygame.font.Font('assets/fonts/neo_sci_fi/neo_scifi.ttf', 20)
        enter_text1 = font.render('Press Enter to', True, 'white')
        enter_text2 = font.render('Go through Portal!', True, 'white')
        screen.blit(enter_text1, (1000, HEIGHT - 60))
        screen.blit(enter_text2, (1000, HEIGHT - 89))
    else: 
        font = pygame.font.Font('assets/fonts/neo_sci_fi/neo_scifi.ttf', 20)
        enter_text1 = font.render('Collect Keys And', True, 'white')
        enter_text2 = font.render('Get To Gold Portal!', True, 'white')
        screen.blit(enter_text1, (1000, HEIGHT - 60))
        screen.blit(enter_text2, (1000, HEIGHT - 89))    

    # draw game logo
    #logo = pygame.transform.scale(pygame.image.load('assets/images/logo.png'), (200, 120))
    #screen.blit(logo, (WIDTH -240, HEIGHT -140))


#check for vertical collisions with solid tiles
def check_verticals(y_pos):
    center_coord = int((player_x + 30) // 100)
    bot_coord = int((player_y + 110) // 100)
    if player_y + 110 > 0:
        if 0 < level[bot_coord][center_coord] < 4:
            falling = False
        else:
            falling = True
    else:
        falling = True
    if not falling:
        y_pos = (bot_coord - 1) * 100 - 10
    return falling, y_pos


#check collsions with tiles
def check_collisions():
    global level, inventory
    door_collides = [False, False, False, False]
    collide = False
    right_coord = int((player_x + 60) // 100)
    left_coord = int(player_x //100)
    top_coord = int((player_y + 30) // 100)
    bot_coord = int((player_y + 80) // 100)
    top_right = level[top_coord][right_coord]
    bot_right = level[bot_coord][right_coord]
    top_left = level[top_coord][left_coord]
    bot_left = level[bot_coord][left_coord]
    if top_coord >= 0:
        if 0 < top_right < 4 or 0 < bot_right < 4:
            collide = 1
        elif 0 < top_left < 4 or 0 < bot_left < 4:
            collide = -1
        else:
            collide = 0
    elif bot_coord >= 0:
        if 0 < bot_right < 4:
            collide = 1
        elif 0 < bot_left < 4:
            collide = -1
        else:
            collide = 0
    else:
        collide = 0

    if 6 <= top_left <= 9:
        if not inventory[top_left - 6]:
            inventory[top_left - 6] = True
            key_sound.play()
    elif 6 <= top_right <= 9:
        if not inventory[top_right - 6]:
            inventory[top_right - 6] = True
            key_sound.play()
    elif 6 <= bot_left <= 9:
        if not inventory[bot_left - 6]:
            inventory[bot_left - 6] = True
            key_sound.play()
    elif 6 <= bot_right <= 9:
        if not inventory[bot_right - 6]:
            inventory[bot_right - 6] = True
            key_sound.play()

    if 10 <= top_left <= 13:
        if  inventory[top_left - 10]:
            door_collides[top_left - 10] = True
    elif 10 <= top_right <= 13:
        if inventory[top_right - 10]:
            door_collides[top_right - 10] = True
    elif 10 <= bot_left <= 13:
        if inventory[bot_left - 10]:
            door_collides[bot_left - 10] = True
    elif 10 <= bot_right <= 13:
        if inventory[bot_right - 10]:
            door_collides[bot_right - 10] = True

    return collide, door_collides



# draw astronaut player
def draw_player(count, direc, mod):
    if mod != 'idle':
        if direc == 1: 
            screen.blit(frames[count // 5], (player_x, player_y))
        else: 
            screen.blit(pygame.transform.flip(frames[count // 5], True, False), (player_x, player_y))
    else:
        if direc == 1: 
            screen.blit(frames[0], (player_x, player_y))
        else: 
            screen.blit(pygame.transform.flip(frames[0], True, False), (player_x, player_y))



# draw all tiles based on value in level array
def draw_board(board):
    acids = []
    # 0 - empty frame, 1 - below ground rock, 2 - walkable surface, 3 - platform, 4 - acid, 5 - player spawn, 6-9 keys, 10-13 doors
    for i in range(len(board)): # getting the coordinates of each tile in the 2D array
        for j in range(len(board[i])):
            value = board[i][j]

            # draw tiles based on value in level array
            if 0 < value < 4:
                screen.blit(tiles[value], (j * TILE_SIZE, i * TILE_SIZE))
            
            # draw acid tiles  
            elif value == 4:
                screen.blit(tiles[value], (j * TILE_SIZE, i * TILE_SIZE + int(0.75 * TILE_SIZE)))
                acids.append(pygame.rect.Rect((j * TILE_SIZE, i * TILE_SIZE), (TILE_SIZE, int(.25 * TILE_SIZE))))
            elif 6 <= value < 10:
                if not inventory[value - 6]:
                    screen.blit(keys[value - 6], (j * TILE_SIZE + int(0.2 * TILE_SIZE), i * TILE_SIZE))

            # draw doors and locks if not in inventory
            elif 10 <= value < 14:
                screen.blit(doors[value - 10], (j * TILE_SIZE, i * TILE_SIZE))
            # draw lock if key not in inventory
                if not inventory[value - 10]:
                    screen.blit(lock, (j * TILE_SIZE + int(0.2 * TILE_SIZE), i * TILE_SIZE + int(0.2 * TILE_SIZE)))
    return acids

def print_endscreen(win_or_lose):
    pygame.draw.rect(screen, 'black', [100, 150, WIDTH-400, HEIGHT-300], 0, 10) 
    pygame.draw.rect(screen, 'white', [100, 150, WIDTH-400, HEIGHT-300], 10, 10) 
    font = pygame.font.Font('assets/fonts/neo_sci_fi/neo_scifi.ttf', 100)
    end_text = font.render("You " + win_or_lose, True, 'white')
    screen.blit(end_text, (115, 300))  
    end_text2 = font.render(f"Your Time: {time//20} ", True, 'white')
    screen.blit(end_text2, (800, 300))  
    end_text3 = font.render("Enter to Restart", True, 'white')
    screen.blit(end_text3, (300, 500))  










# ====================
# MAIN GAME LOOP
# ====================
run = True
while run:
    timer.tick(fps)

    # update counter for animation (Frames 0-19 of the player sprite)
    if counter< 19:
        counter += 1
    else:
        counter = 0
    # update time only if not win or lose
    if not win and not lose:
        time += 1 
    # drawing the background  
    screen.fill('black')
    screen.blit(bg, (0, 0))

    # drawing the board, player and HUD
    acid_list = draw_board(level) # get acid rectangles for collision detection
    draw_player(counter, direction, mode) # draw player
    draw_inventory() # draw inventory and HUD and timer

    # check for win or lose conditions
    # if win or lose, display end screen and play sound
    if win:
        print_endscreen('win!')
        if win and time < high_score or high_score == 0 or high_score == '': 
            file = open('high_score.txt', 'w')
            high_score = time//20
            file.write(str(high_score))
            file.close()
        end_sound.play()

    # if lose, display lose screen and play sound
    elif lose:
        print_endscreen('lose!')
        end_sound.play()

    # handle x-direction movement here
    if mode == 'walk':
        if direction == -1 and player_x > 0 and colliding != -1:
            player_x -= player_speed
        elif direction == 1 and player_x < WIDTH - 70 and colliding != 1:
            player_x += player_speed
    # Check for collisions with tiles here
    colliding, door_collisions = check_collisions()

    # jumping code and vertical checks
    if in_air:
        y_change -= gravity
        player_y -= y_change
    in_air, player_y = check_verticals(player_y)
    if not in_air:
        y_change = 0

    #Event handler (keyboard inputs, closing window, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        #TESTING RESIZING!!!!!!!!!!!!!!
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            # right arrow key for walking right 
            if event.key == pygame.K_RIGHT:
                direction = 1
                mode = 'walk'
            # left arrow key for walking left
            elif event.key == pygame.K_LEFT:
                direction = -1
                mode = 'walk'
            # space bar for jumping (if not already in air) 
            if event.key == pygame.K_SPACE and not in_air:
                in_air = True
                y_change = jump_height
                jump_sound.play()

        if event.type == pygame.KEYUP:
            # stop moving when right or left arrow keys are released
            if event.key == pygame.K_RIGHT and direction == 1:
                mode = 'idle'
            elif event.key == pygame.K_LEFT and direction == -1:
                mode = 'idle'

            # Enter -> durch Portal gehen
            if event.key == pygame.K_RETURN and not win and not lose:
                for i in range(len(door_collisions)):
                    if door_collisions[i]:
                        if i != 3: # normal Portal (blue, green, red) -> teleport to other phase
                            portal_sound.play()
                            acid_list = []
                            active_phase, player_coords = teleport(i, active_phase)
                            player_x = player_coords[0] * 100
                            player_y = player_coords[1] * 100 - (8 * player_scale - 100) 
                            level = levels[active_level][active_phase]
                            init_x = player_x
                            init_y = player_y
                            y_change = 0
                        else: # golden portal -> next level
                            if active_level < len(levels) - 1:
                                portal_sound.play()
                                active_level += 1
                                active_phase = 3
                                acid_list = []
                            else:
                                win = True 
                            level = levels[active_level][active_phase]
                            inventory = [False, False, False, False] # reset inventory
                            # find new player spawn position
                            for _  in range(len(level)):
                                if 5 in level[_]:
                                    start_pos = (_, level[_].index(5)) # row, column of player spawn 
                            player_x = start_pos[1] * 100
                            player_y = start_pos[0] * 100 - (8 * player_scale - 100) 
                            level = levels[active_level][active_phase]
                            init_x = player_x
                            init_y = player_y
                            y_change = 0

            # Enter key if win/lose -> restart game from level 1
            elif event.key == pygame.K_RETURN and (win or lose):
                active_level = 0
                active_phase = 3
                win = False
                lose = False
                time = 0 
                level = levels[active_level][active_phase]
                inventory = [False, False, False, False]
                for _  in range(len(level)):
                    if 5 in level[_]:
                        start_pos = (_, level[_].index(5))
                player_x = start_pos[1] * 100
                player_y = start_pos[0] * 100 - (8 * player_scale - 100) 
                init_x = player_x
                init_y = player_y
                y_change = 0
                lives = 3

    # check for collisions with acid here
    for i in range(len(acid_list)):
        if acid_list[i].collidepoint(player_x + 30, player_y + 20):
            acid_sound.play()
            lives -= 1
            player_x = init_x
            player_y = init_y 

            player_x = init_x
            player_y = init_y
            y_change = 0
            in_air = False

            if lives == 0: # if no lives left, lose game 
                active_level = 0
                active_phase = 3
                level = levels[active_level][active_phase]
                inventory = [False, False, False, False]

    # check if lose condition is completed here
    if lives > 0:
        lose = False
    else:
        lose = True

    # check if player is colliding with any portals for enter message
    if True in door_collisions:
        enter_message = True
    else:
        enter_message = False
                
    # update the display and quit program
    pygame.display.flip()
pygame.quit()
