import math
import random
import pygame 
import button
import os
from enemy import Enemy 

pygame.init()

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Castle Defender")
clock = pygame.time.Clock()
FPS = 60

#game settings
high_score = 0
level = 1
level_difficulty = 0
target_difficulty = 1000
DIFFICULTY_MULTIPLER = 1.1
game_over = False

next_level = False
ENEMY_TIMER = 1000 # spawn time 1 second
last_enemy = pygame.time.get_ticks()
enemies_alive = 0

max_towers = 5
TOWER_COST = 5000
tower_positions = [
    [SCREEN_WIDTH - 250, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150],
    [SCREEN_WIDTH - 50, SCREEN_HEIGHT - 150]
]

# load high score
if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())

#define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)

#define font
font = pygame.font.SysFont('Futura', 30)
font_60 = pygame.font.SysFont('Futura', 60)

#background image
bg = pygame.image.load('img/bg.png').convert_alpha()

#castle image
castle_image_100 = pygame.image.load('img/castle/castle_100.png').convert_alpha()
castle_image_50 = pygame.image.load('img/castle/castle_50.png').convert_alpha()
castle_image_25= pygame.image.load('img/castle/castle_25.png').convert_alpha()

#tower image
tower_image_100 = pygame.image.load('img/tower/tower_100.png').convert_alpha()
tower_image_50 = pygame.image.load('img/tower/tower_50.png').convert_alpha()
tower_image_25= pygame.image.load('img/tower/tower_25.png').convert_alpha()

#bullet image
bullet_img = pygame.image.load('img/bullet.png').convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = pygame.transform.scale(bullet_img, (int(b_w * 0.075), int(b_h * 0.075)))

#load enemies
enemy_animations = []
enemy_types = ['knight', 'goblin', 'purple_goblin', 'red_goblin']
enemy_health = [75, 100, 125, 150]

#enemy animation
animation_types = ['walk', 'attack', 'death']
for enemy in enemy_types:
    #load animations
    animation_list = []
    for animation in animation_types:
        #reset temporary list of images
        temp_list = []
        #define no. of frames
        num_of_frames = 20
        for i in range(num_of_frames):
            img = pygame.image.load(f'img/enemies/{enemy}/{animation}/{i}.png').convert_alpha()
            e_w = img.get_width()
            e_h = img.get_height()
            img = pygame.transform.scale(img, (int(e_w*0.2), int(e_h*0.2)))
            temp_list.append(img)
        animation_list.append(temp_list)
    enemy_animations.append(animation_list)

#repair image
repair_img = pygame.image.load("img/repair.png").convert_alpha()
#armour image
armour_img = pygame.image.load("img/armour.png").convert_alpha()

# display level completion
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Display Game Info
def show_info():
    draw_text('Money: ' + str(castle.money) + " G ", font, GREY, 10, 10)
    draw_text('Score: ' + str(castle.score), font, GREY, 180, 10)
    draw_text('HighScore: ' + str(high_score), font, GREY, 180, 30)
    draw_text('Level: ' + str(level), font, GREY, SCREEN_WIDTH // 2, 10)
    draw_text('Health: ' + str(castle.health) + " / " + str(castle.max_health), font, GREY, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 35)
    draw_text('1000 G ', font, GREY, SCREEN_WIDTH - 240, 70)
    draw_text('500 G ', font, GREY, SCREEN_WIDTH - 75, 70)
    draw_text('5000 G ', font, GREY, SCREEN_WIDTH - 155, 70)    


class Castle():
    # constructor class
    def __init__(self, image100, image50, image25, x, y, scale):
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 0
        self.score = 0
        # set image height and width
        width = image100.get_width()
        height = image100.get_height()
        
        # transforming scale of image 
        self.image100 = pygame.transform.scale(image100, (int(width*scale), int(height*scale)))
        self.image50 = pygame.transform.scale(image50, (int(width*scale) , int(height*scale)))
        self.image25 = pygame.transform.scale(image25, (int(width*scale) , int(height*scale)))
        # get the border positions of the image
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def shoot(self):
        # position of turret 
        pos = pygame.mouse.get_pos() 
        x_dist = pos[0] - self.rect.midleft[0]
        y_dist = -(pos[1] - self.rect.midleft[1])
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        
        # generate bullets when mouse is pressed
        if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 60:
            self.fired = True
            bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
            bullet_group.add(bullet)
        if pygame.mouse.get_pressed()[0] == False:
           self.fired = False
           
    # draw the image to its position
    def draw(self):
        #check castle health
        if self.health <= 250:
            self.image = self.image25
        elif self.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100            
                 
        screen.blit(self.image, (self.rect.x, self.rect.y))             
    
    # repair button
    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
            self.health += 500
            self.money -= 1000
            if self.health > self.max_health:
                self.health = self.max_health
    # armour button
    def armour(self):
        if self.money >= 500:
            self.max_health += 250
            self.money -= 500
        
class Tower(pygame.sprite.Sprite):
    def __init__(self, image100, image50, image25, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        
        self.target_acquired = False
        self.angle = 0
        self.last_shot = pygame.time.get_ticks()
        width = image100.get_width()
        height = image100.get_height()
        
        # transforming scale of image 
        self.image100 = pygame.transform.scale(image100, (int(width*scale), int(height*scale)))
        self.image50 = pygame.transform.scale(image50, (int(width*scale), int(height*scale)))
        self.image25 = pygame.transform.scale(image25, (int(width*scale), int(height*scale)))
        
        # get the border positions of the image
        self.image = self.image100
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self, enemy_group):
        self.target_acquired = False

        # target an enemy
        for e in enemy_group:
            if e.alive:
                target_x, target_y = e.rect.midleft
                self.target_acquired = True
                break
            
        if self.target_acquired:
            x_dist = target_x - self.rect.midleft[0]
            y_dist = -(target_y - self.rect.midleft[1])
            self.angle = math.degrees(math.atan2(y_dist, x_dist))
            shot_cooldown = 1000 # 1 second
            
            # fire bullet 
            if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
                self.last_shot = pygame.time.get_ticks()
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)
        
        #check tower health
        if castle.health <= 250:
            self.image = self.image25
        elif castle.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100            
            
class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        # bullet starting position
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle) #converting input angle into radians
        self.speed = 10
        
        # calculating horizontal and vertical speeds according to angle
        self.dx = math.cos(self.angle) * self.speed 
        self.dy = -(math.sin(self.angle) * self.speed) # coordinates are flipped therefore 0 is the top 
    
    def update(self):
        #check bullet out of screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            #delete instance
            self.kill()
            
        #moving bullets
        self.rect.x += self.dx
        self.rect.y += self.dy
       
class Crosshair():
    def __init__(self, scale):
        image = pygame.image.load('img/crosshair.png').convert_alpha()
        width = image.get_width()
        height = image.get_height()
        
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        
        pygame.mouse.set_visible(False)
        
    def draw(self):
        mx, my = pygame.mouse.get_pos()
        self.rect.center = (mx, my)
        screen.blit(self.image, self.rect)
        
              
# castle and turret    
castle = Castle(castle_image_100, castle_image_50, castle_image_25, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 340, 0.21)
# create crosshair
crosshair = Crosshair(0.025)
# create buttons
repair_button = button.Button(SCREEN_WIDTH - 230, 10, repair_img, 0.5)
armour_button = button.Button(SCREEN_WIDTH - 75, 10, armour_img, 1.5)
tower_button = button.Button(SCREEN_WIDTH - 140, 10, tower_image_100, 0.1)

tower_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# running window
run = True
while run:
    
    clock.tick(FPS)
    
    if game_over == False:
        screen.blit(bg, (0, 0))
        
        # draw castle
        castle.draw()
        castle.shoot()
        
        # draw tower
        tower_group.draw(screen)
        tower_group.update(enemy_group)
        
        # draw crosshair
        crosshair.draw()
        
        # draw bullets
        bullet_group.update()
        bullet_group.draw(screen)
        
        # draw enemies
        enemy_group.update(screen, castle, bullet_group)
        
        # show game details
        show_info()
        
        # draw buttons
        if repair_button.draw(screen):
            castle.repair()
        if armour_button.draw(screen):
            castle.armour()
        if tower_button.draw(screen):
            # check money and max tower
            if castle.money >= TOWER_COST and len(tower_group) < max_towers:
                tower = Tower(
                        tower_image_100, 
                        tower_image_50, 
                        tower_image_25, 
                        tower_positions[len(tower_group)][0], 
                        tower_positions[len(tower_group)][1], 
                        0.2)
                tower_group.add(tower)
                castle.money -= 5000
        
        # create enemies based on difficulty
        if level_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > ENEMY_TIMER:
                
                # random number between 4 enemy types (index 0 - 3)
                e = random.randint(0, len(enemy_types) - 1)
                e_spd = random.randint(1, 2)
                e_spawn_pos = random.randint(100, 230)
                enemy_1 = Enemy(enemy_health[e], enemy_animations[e], -100, SCREEN_HEIGHT - e_spawn_pos, e_spd)
                enemy_group.add(enemy_1)
                
                #reset timer
                last_enemy = pygame.time.get_ticks()
                
                level_difficulty += enemy_health[e]
        
        # check if all enemies defeated
        if level_difficulty >= target_difficulty: 
            enemies_alive = 0
            
            for e in enemy_group:
                if e.alive == True:
                    enemies_alive += 1

            if enemies_alive == 0 and next_level == False:
                next_level = True
                level_reset_time = pygame.time.get_ticks()
        
        # move to next level
        if next_level == True:
            draw_text('LEVEL COMPLETE!', font_60, WHITE, 200, 300)
            
            # update high score
            if castle.score > high_score:
                high_score = castle.score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            
            # reset level 
            if pygame.time.get_ticks() - level_reset_time > 1500: # 1.5s
                next_level = False
                level += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= DIFFICULTY_MULTIPLER
                level_difficulty = 0
                enemy_group.empty()
                
        # game over check
        if castle.health == 0:
            game_over = True                
    else:
        # display gameover screen
        draw_text("GAME OVER!", font_60, RED, 270, 250)    
        draw_text("PRESS 'A' TO PLAY AGAIN", font_60, RED, 130, 310)
        pygame.mouse.set_visible(True)    
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            game_over = False
            level = 1
            target_difficulty = 1000
            level_difficulty = 0
            last_enemy = pygame.time.get_ticks()
            enemy_group.empty()
            tower_group.empty()
            castle.score = 0
            castle.health = 1000
            castle.money = 0
            pygame.mouse.set_visible(False)
        
    # event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    #update display window
    pygame.display.update()
                
pygame.quit