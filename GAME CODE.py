import pygame 
import math
import os, sys
import random
from datetime import datetime

TIME_TO_NEW_ENEMY = 1           # generate new enemy every X seconds(in whole seconds)
MONSTER_CAP = 7                 # max number of enemies on screen
SLIME_DAMAGE = 15
PINK_SLIME_DAMAGE = 25
PLAYER_UNDER_ATTACK_COOLDOWN = 2       # player has X seconds between each hit it takes(in whole seconds)
DROP_DISAPPEAR = 6              # seconds untill drop disappears
HEART_HP = 10                   # hp that heart dropped from monsters give
STAMINA = 10
STRONG_HEART_HP = 20
STRONG_STAMINA = 20

pygame.init()
window = pygame.display.set_mode((1024, 512))
clock = pygame.time.Clock()
# INIT_GAME:
# sets game screen and loads start up screen, ends when game starts(or red x is pressed)
# return true if game should start normally
def init_game(window):
    # set screen caption
    pygame.display.set_caption("Slime Hunter")
    # Start Up Screen:
    start_up_screen = pygame.image.load("./slime_hunter/pictures/start_up/start_up_screen.png")
    # check if quit is pressed
    run = True
    start = False
    show_start_up_screen = True
    while run and not(start):
        if show_start_up_screen:
            window.blit(start_up_screen, (0,0))
            pygame.display.update()
            show_start_up_screen = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            start = True
        if keys[pygame.K_i]:
            # if red x is pressed while in info screen, quit game
            if info_screen(window):
                run = False
            show_start_up_screen = True
    return run

# INFO_SCREEN:
# if player presses "i" while in init screen than it goes here, ends when player presses "b"- goes back to init_game
# returns True if game should quit after this function
def info_screen(window):
    more_info = pygame.image.load("./slime_hunter/pictures/start_up/more_information.png")
    window.blit(more_info, (0,0))
    pygame.display.update()
    run = True
    b_pressed = False
    while run and not(b_pressed):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_b]:
            b_pressed = True
    return not(run)

def player_died(window, score):
    start_up_bg = pygame.image.load("./slime_hunter/pictures/start_up/forest_background_blurred.png")
    window.blit(start_up_bg, (0,0))
    font = pygame.font.SysFont("comicsansms", 40)
    text = font.render("YOU DIED! YOUR SOCRE IS: " + str(score), True, (0, 0, 0))
    window.blit(text, (200, 200))
    pygame.display.update()
# LOAD_IMAGES:
# gets image path, x and y scaling size, and true or false if image needs mirroring, or scaling
# returns images array
def load_images(img_path, scale_x, scale_y, flip = False, scale = True):
    i = 0
    images_arr = []
    for image in os.listdir(img_path):
        images_arr.append(pygame.image.load(str(img_path) + str(image)))
        if scale:
            images_arr[i] = pygame.transform.scale(images_arr[i], (scale_x, scale_y))
        if flip:
            images_arr[i] = pygame.transform.flip(images_arr[i], True, False)
        i += 1
    return images_arr

class character(object):
    def __init__(self, x, y, hp, damage):
        self.x = x                              # x location
        self.y = y                              # y location
        self.hp = hp                            # health
        self.side = 0                           # side character is looking at. right = 1, left = 0
        self.attacking = False                  # is attacking now
        self.under_attack = False               # is under attack now
        self.under_attack_animation_count = 0   # which frame of getting hit to show
        self.damage = damage                    # damage character does(for witch its staff hit)
        self.attacked_animation_step = 0        # whick frame of attacked to show
        self.animation_step = 0                 # which frame from walking animation to show
        self.dead = False                       # hp is less than or equals to 0
class witch(character):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, 100, 50)
        self.width = width
        self.height = height
        self.stamina = 100
        self.use_skill = False
        self.skill_animation = 0.5
        self.jump = False
        self.way_down = False               # for jump- is going up or down
        self.jump_help = 0
        self.idle = 0                       # idle = 1 when not walking and idling
        self.walk = 0                                                  # walk = 1 when walking
        self.under_attack_cooldown = PLAYER_UNDER_ATTACK_COOLDOWN      # wait a second between each hit
        self.attacking_animation_step = 0
        self.under_attack_animation_step = 0
        self.slime_kill_count = 0
        self.under_attack_type = 0          # which monster put the player in this mode(for damage)
        self.teleport = False
        self.last_teleport = 0
        self.on_step = False                # standing on step
        self.standing_in_portal_time = -1    # time player is standing in portal(to activate after 1 second)
    def attack(self):
        if self.side == 1:
            window.blit(attack_right[round(self.attacking_animation_step)%16], (self.x,self.y))
            self.attacking_animation_step += 0.5
        else:
            window.blit(attack_left[round(self.attacking_animation_step)%16], (self.x,self.y))
            self.attacking_animation_step += 0.5
        if self.attacking_animation_step%16 == 0:
            self.attacking = False
            self.attacking_animation_step = 0
    def walkOrIdle(self):
        if self.walk == 0:
            if self.side == 1:
                window.blit(idle_right[round(self.animation_step)%14], (self.x,self.y))
                self.animation_step += 0.35
            else:
                window.blit(idle_left[round(self.animation_step)%14], (self.x,self.y))
                self.animation_step += 0.35
        else:
            if self.side == 1:
                window.blit(walk_right[round(self.animation_step)%28], (self.x,self.y))
                self.animation_step += 0.7
            else:
                window.blit(walk_left[round(self.animation_step)%28], (self.x,self.y))
                self.animation_step += 0.7
    def usingSkill(self):
        if self.side == 1:
            window.blit(skill_right[round(self.skill_animation)%18], (self.x,self.y))
            self.skill_animation += 0.5
        else:
            window.blit(skill_left[round(self.skill_animation)%18], (self.x,self.y))
            self.skill_animation += 0.5
        if self.skill_animation%18 == 0:
            self.use_skill = False
            self.skill_animation = 0
            self.stamina -= 35
    def underAttack(self):
        if self.under_attack_animation_step < 14:
            if self.side == 1:
                if not(round(self.animation_step)%3 == 0):
                    window.blit(idle_right[round(self.animation_step)%14], (self.x,self.y))
                self.animation_step += 0.35
                self.under_attack_animation_step += 1
                self.x -= 4
            else:
                if not(round(self.animation_step)%3 == 0):
                    window.blit(idle_left[round(self.animation_step)%14], (self.x,self.y))
                self.animation_step += 0.35
                self.under_attack_animation_step += 1
                self.x += 4
        else:
            seconds = datetime.now().second
            self.under_attack_cooldown = seconds
            if self.under_attack_type == 1:
                ouch = SLIME_DAMAGE
            else:
                ouch = PINK_SLIME_DAMAGE
            if self.hp - ouch <= 0:
                self.hp = 0
                self.dead = True
            else:
                self.hp -= ouch
            self.under_attack = False
            self.under_attack_animation_step = 0
            self.use_skill = False
            self.skill_animation = 0
            if self.side == 1:
                window.blit(idle_right[0], (self.x,self.y))
            else:
                window.blit(idle_left[0], (self.x,self.y))
    def teleporting(self):
        if self.side == 1:
            self.x += 110
        else:
            self.x -= 110
        self.teleport = False
        if self.stamina < 15:
            self.stamina = 0
        else:
            self.stamina -= 15
        self.last_teleport = datetime.now().second
    def draw(self):
        if not(self.under_attack):
            if self.use_skill == False:
                if self.attacking:
                    self.attack()
                elif self.teleport:
                    self.teleporting()
                else:
                    self.walkOrIdle()
            else:
                self.usingSkill()
        # under attack
        else:
            self.underAttack()
        # draw hp and stamina
        pygame.draw.rect(window,(227,61,61), (410, 465, self.hp * 1.79, 17))
        pygame.draw.rect(window,(169,61,227), (410, 488, self.stamina * 1.79, 17))
class slime(character):
    def __init__(self, x, y):
        super().__init__(x, y, 100, SLIME_DAMAGE)
        self.last_turned = datetime.now().second    # last time the enemy turned (or had a chance to)
        self.turned = False
        self.turn_second = 0
        self.turn_millisecond = 0
        self.is_there_next_time = False
        self.distance_to_attack = 150               # how far player has to be from enemy to attack
        self.generate_enemy(player.x, player.y)
    def generate_enemy(self, player_x, player_y):
        # choose side for enemy to generate
        if player_x < 100:
            x_location = round(random.uniform(140, 980))
        elif player_x > 750:
            x_location = round(random.uniform(30, 710))
        else:
            side = round(random.uniform(1,2))
            if side == 1:
                x_location = round(random.uniform(150, player_x)) - 170 
                self.side = 1
            else:
                x_location = round(random.uniform(player_x, 750)) + 170
                self.side = 0
        self.x = x_location
        self.seconds_untill_turn = datetime.now().second
    def turn(self):
        seconds = datetime.now().second
        milliseconds = round(datetime.now().microsecond / 100000)
        # schedule next turn
        if not(self.is_there_next_time):
            # second for turn
            turn_temp1 = round(random.uniform(1,3))
            # 0.x second for turn
            turn_temp2 = round(random.uniform(0,9))
            self.turn_second = seconds + turn_temp1
            if self.turn_second >= 60:
                self.turn_second -= 60
            self.turn_millisecond = milliseconds + turn_temp2
            self.is_there_next_time = True
        if seconds - self.turn_second == 0 and milliseconds - self.turn_millisecond == 0 and not(self.turned):
            self.turned = True
            side = round(random.uniform(1,2))
            self.last_turned = seconds
            if side == 1:
                if self.side == 1:
                    self.side = 0
                else:
                    self.side = 1
        if seconds - self.last_turned > 1 and self.turned:
            self.turned = False
            self.is_there_next_time = False
        # makes sure it doesnt go out of bounds
        if self.x < -80:
            self.side = 1
        elif self.x > 850:
            self.side = 0
        # walk after turn
        if self.side == 0:
            self.x -= 1
            window.blit(slime_walk_left[self.animation_step%28], (self.x,self.y))
            self.animation_step += 1
        else:
            self.x += 1
            window.blit(slime_walk_right[self.animation_step%28], (self.x,self.y))
            self.animation_step += 1  
    def attacked(self, player):
        if player.side == 1:
            window.blit(slime_attacked_left[round(self.attacked_animation_step)%12], (self.x,self.y))
            self.x += 3
            self.attacked_animation_step += 0.5
        else:
            window.blit(slime_attacked_right[round(self.attacked_animation_step)%12], (self.x,self.y))
            self.x -= 3
            self.attacked_animation_step += 0.5
        if self.attacked_animation_step == 12:
            self.attacked_animation_step = 0
            self.under_attack = False
            player.attacking = False
            self.hp -= player.damage
            if self.hp <= 0:
                self.dead = True
    def draw(self, player, game):
        if not(self.dead):
            if not(self.under_attack):
                self.turn()
                if player.attacking and player.attacking_animation_step > 9:
                    if (player.side == 1 and 90 > (self.x - player.x) > 10) or\
                        (player.side == 0 and 130 > (player.x - self.x) > 50) and\
                            player.y > 150:
                        self.under_attack = True
                elif (0 < player.x - self.x < 35 or 0 < self.x - player.x < 10) and player.y > 150:
                    seconds = datetime.now().second
                    if abs(seconds - player.under_attack_cooldown) >= PLAYER_UNDER_ATTACK_COOLDOWN:
                        player.under_attack = True
                        player.under_attack_type = 1
            # attacked
            else:
                self.attacked(player)
        # dead
        else:
            if self.attacked_animation_step != 7:
                if self.side == 1:
                    window.blit(slime_dead_right[round(self.attacked_animation_step)], (self.x,self.y))
                    self.attacked_animation_step += 0.5
                else:
                    window.blit(slime_dead_left[round(self.attacked_animation_step)], (self.x,self.y))
                    self.attacked_animation_step += 0.5
class pink_slime(character):
    def __init__(self, x, y):
        super().__init__(x, y, 150, PINK_SLIME_DAMAGE)
        self.last_turned = datetime.now().second    # last time the enemy turned (or had a chance to)
        self.turned = False
        self.turn_second = 0
        self.turn_millisecond = 0
        self.is_there_next_time = False
        self.distance_to_attack = 150               # how far player has to be from enemy to attack
        self.generate_enemy(player.x, player.y)
    def generate_enemy(self, player_x, player_y):
        # choose side for enemy to generate
        if player_x < 100:
            x_location = round(random.uniform(140, 980))
        elif player_x > 750:
            x_location = round(random.uniform(30, 710))
        else:
            side = round(random.uniform(1,2))
            if side == 1:
                x_location = round(random.uniform(150, player_x)) - 170 
                self.side = 1
            else:
                x_location = round(random.uniform(player_x, 750)) + 170
                self.side = 0
        self.x = x_location
        self.seconds_untill_turn = datetime.now().second
    def turn(self):
        seconds = datetime.now().second
        milliseconds = round(datetime.now().microsecond / 100000)
        # schedule next turn
        if not(self.is_there_next_time):
            # second for turn
            turn_temp1 = round(random.uniform(1,3))
            # 0.x second for turn
            turn_temp2 = round(random.uniform(0,9))
            self.turn_second = seconds + turn_temp1
            if self.turn_second >= 60:
                self.turn_second -= 60
            self.turn_millisecond = milliseconds + turn_temp2
            self.is_there_next_time = True
        if seconds - self.turn_second == 0 and milliseconds - self.turn_millisecond == 0 and not(self.turned):
            self.turned = True
            side = round(random.uniform(1,2))
            self.last_turned = seconds
            if side == 1:
                if self.side == 1:
                    self.side = 0
                else:
                    self.side = 1
        if seconds - self.last_turned > 1 and self.turned:
            self.turned = False
            self.is_there_next_time = False
        # makes sure it doesnt go out of bounds
        if self.x < -80:
            self.side = 1
        elif self.x > 850:
            self.side = 0
        # walk after turn
        if self.side == 0:
            self.x -= 1
            window.blit(pink_slime_walk_left[self.animation_step%28], (self.x,self.y))
            self.animation_step += 1
        else:
            self.x += 1
            window.blit(pink_slime_walk_right[self.animation_step%28], (self.x,self.y))
            self.animation_step += 1  
    def attacked(self, player):
        if player.side == 1:
            window.blit(pink_slime_attacked_left[round(self.attacked_animation_step)%12], (self.x,self.y))
            self.x += 3
            self.attacked_animation_step += 0.5
        else:
            window.blit(pink_slime_attacked_right[round(self.attacked_animation_step)%12], (self.x,self.y))
            self.x -= 3
            self.attacked_animation_step += 0.5
        if self.attacked_animation_step == 12:
            self.attacked_animation_step = 0
            self.under_attack = False
            player.attacking = False
            self.hp -= player.damage
            if self.hp <= 0:
                self.dead = True
    def draw(self, player, game):
        if not(self.dead):
            if not(self.under_attack):
                self.turn()
                if player.attacking and player.attacking_animation_step > 9:
                    if (player.side == 1 and 90 > (self.x - player.x) > 10) or\
                        (player.side == 0 and 130 > (player.x - self.x) > 50) and\
                            player.y > 150:
                        self.under_attack = True
                elif (0 < player.x - self.x < 35 or 0 < self.x - player.x < 10) and player.y > 150:
                    seconds = datetime.now().second
                    if abs(seconds - player.under_attack_cooldown) >= PLAYER_UNDER_ATTACK_COOLDOWN:
                        player.under_attack = True
                        player.under_attack_type = 2
            # attacked
            else:
                self.attacked(player)
        # dead
        else:
            if self.attacked_animation_step != 7:
                if self.side == 1:
                    window.blit(pink_slime_dead_right[round(self.attacked_animation_step)], (self.x,self.y))
                    self.attacked_animation_step += 0.5
                else:
                    window.blit(pink_slime_dead_left[round(self.attacked_animation_step)], (self.x,self.y))
                    self.attacked_animation_step += 0.5


class monster_drop(object):
    def __init__(self, x, y, type_of_drop):
        self.fresh_drop = True                  # drops falls now
        self.x = x + 100
        self.y = y + 180
        self.type_of_drop = type_of_drop        # 1 for heart, 2 for stamina, 3 for strong heart, 4 for strong stamina
        self.time_of_drop = datetime.now().second
        self.time_drop_lasts = DROP_DISAPPEAR                # seconds untill drop disappears
        self.picked_up = False
        self.draw_animation = 0
        self.end_pickup = False
    def draw(self, player_x):
        if self.fresh_drop:
            if self.type_of_drop == 1:
                window.blit(heart[round(self.draw_animation)], (self.x, self.y))
            elif self.type_of_drop == 2:
                window.blit(stamina_heart[round(self.draw_animation)], (self.x, self.y))
            elif self.type_of_drop == 3:
                window.blit(strong_heart[round(self.draw_animation)], (self.x, self.y))
            elif self.type_of_drop == 4:
                window.blit(strong_stamina_heart[round(self.draw_animation)], (self.x, self.y))
            self.draw_animation += 0.5
            if self.draw_animation == 5:
                self.fresh_drop = False
        else:
            # if player is near: return true and start pickup animation
            if abs((player_x + 100) - self.x) < 15 and player.y > 100:
                self.picked_up = True
            else:
                if self.type_of_drop == 1:
                    window.blit(heart[4], (self.x, self.y))
                elif self.type_of_drop == 2:
                    window.blit(stamina_heart[4], (self.x, self.y))
                elif self.type_of_drop == 3:
                    window.blit(strong_heart[4], (self.x, self.y))
                elif self.type_of_drop == 4:
                    window.blit(strong_stamina_heart[4], (self.x, self.y))
        return self.picked_up
    def pickup_draw(self, player_x):
        # go to hp bar
        if self.x > 400:
            self.x -= (self.x - 400) / 30
        else:
            self.x += (400 - self.x) / 30
        if self.type_of_drop == 1 or self.type_of_drop == 3:
            if self.y < 460:
                self.y -= (self.y - 460) / 15
        else:
            if self.y < 480:
                self.y -= (self.y - 480) / 15
        if self.type_of_drop == 1:
            window.blit(heart[4], (self.x, self.y))
        elif self.type_of_drop == 2:
            window.blit(stamina_heart[4], (self.x, self.y))
        elif self.type_of_drop == 3:
            window.blit(strong_heart[4], (self.x, self.y))
        elif self.type_of_drop == 4:
            window.blit(strong_stamina_heart[4], (self.x, self.y))
        if abs(self.x - 400) < 20 or abs(self.x - 550) < 20:
            if self.type_of_drop == 1 or self.type_of_drop == 3:
                if abs(self.y - 460) < 15:
                    self.end_pickup = True
            else:
                if abs(self.y - 480) < 15:
                    self.end_pickup = True
        return self.end_pickup
class portal(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.back_animation = 0
        self.front_animation = 0
    def drawBack(self):
        window.blit(portal_back[round(self.back_animation)%10], (self.x, self.y))
        self.back_animation += 0.25
    def drawFront(self):
        window.blit(portal_front[round(self.front_animation)%10], (self.x, self.y))
        self.front_animation += 0.25
class game_manager(object):
    def __init__(self):
        self.time_for_new_ememy = TIME_TO_NEW_ENEMY     # create new enemy every x seconds
        self.last_created = datetime.now().second       # time when enemy was last created
        self.enemy_created = False                      # if enemy was created in the current cycle
        self.monster_count = 0                          # how many monsters are currently allive
        self.time_for_next_level = 30                   # seconds untill portal opens
        self.time = datetime.now().second
        self.level_2 = False
    def newEnemy(self):
        seconds = datetime.now().second
        # monster limit
        if self.monster_count < MONSTER_CAP:
            if abs(seconds - self.last_created) >= self.time_for_new_ememy and not(self.enemy_created):    
                self.enemy_created = True
                self.last_created = seconds
                self.monster_count += 1
                return True
            self.enemy_created = False
        else:
            self.last_created = seconds
        return False
    def nextLevel(self):
        pass
    def drawMonsters(self):
        if self.newEnemy():
            enemy_type = round(random.uniform(1, 4))
            if enemy_type == 4:
                enemies.append(pink_slime(500, 200))
            else:
                enemies.append(slime(500, 200))
        if player.use_skill and player.skill_animation >= 12:
            affect_monsters = 0
            for monster in enemies:
                if affect_monsters <= 3:
                    monster.under_attack = True
                    affect_monsters += 1
                else:
                    affect_monsters += 1
        for monster in enemies:
            if monster.dead and monster.attacked_animation_step == 7:
                should_drop = round(random.uniform(1,2))
                if type(monster) is slime:
                    player.slime_kill_count += 1
                    if should_drop == 1:
                        drop = round(random.uniform(1,3))
                        if drop == 1 or drop == 2:
                            hearts.append(monster_drop(monster.x, monster.y, 1))
                        else:
                            hearts.append(monster_drop(monster.x, monster.y, 2))
                elif type(monster) is pink_slime:
                    player.slime_kill_count += 2
                    if should_drop == 1:
                        drop = round(random.uniform(1,3))
                        if drop == 1 or drop == 2:
                            hearts.append(monster_drop(monster.x, monster.y, 3))
                        else:
                            hearts.append(monster_drop(monster.x, monster.y, 4))
                del enemies[enemies.index(monster)]
                self.monster_count -= 1     
            else:
                monster.draw(player, self)
    def drawHearts(self):
        for heart in hearts:
            if abs(datetime.now().second - heart.time_of_drop) == DROP_DISAPPEAR and not(heart.picked_up):
                del hearts[hearts.index(heart)]
            else:
                if heart.draw(player.x):
                    if heart.pickup_draw(player.x):
                        if heart.type_of_drop == 1:
                            if 100 - player.hp >= HEART_HP:
                                player.hp += HEART_HP
                            else:
                                player.hp = 100
                        elif heart.type_of_drop == 2:
                            if 100 - player.stamina >= STAMINA:
                                player.stamina += STAMINA
                            else:
                                player.stamina = 100
                        elif heart.type_of_drop == 3:
                            if 100 - player.hp >= STRONG_HEART_HP:
                                player.hp += STRONG_HEART_HP
                            else:
                                player.hp = 100
                        elif heart.type_of_drop == 4:
                            if 100 - player.stamina >= STRONG_STAMINA:
                                player.stamina += STRONG_STAMINA
                            else:
                                player.stamina = 100 
                        del hearts[hearts.index(heart)]
    def drawPlayerAndPortal(self):
        if abs(seconds - datetime.now().second) >= 1:
            if player.stamina <= 97:
                player.stamina += 3
            else:
                player.stamina = 100
        if player.slime_kill_count >= 100:
            gate.drawBack()
        player.draw()
        if player.slime_kill_count >= 100:
            gate.drawFront()
        # use portal
        if player.slime_kill_count >= 100 and 30 < player.x < 100 and player.y < 100\
           and player.standing_in_portal_time == -1:
            player.standing_in_portal_time = datetime.now().second
        if player.slime_kill_count >= 100 and 30 < player.x < 100 and player.y < 100\
            and abs(datetime.now().second - player.standing_in_portal_time) >= 1:
            self.level_2 = True
        if player.standing_in_portal_time != -1 and (player.x > 100 or player.x < 30)\
            and player.slime_kill_count >= 100:
            player.standing_in_portal_time = -1      
    def redrawGameWindow(self):
        if not(player.dead):
            window.blit(background, (0,0))
            window.blit(bars, (350, 440))
            self.drawHearts()
            self.drawMonsters()
            font = pygame.font.SysFont("comicsansms", 36)
            text = font.render(str(player.slime_kill_count), True, (142, 64, 64))
            window.blit(text, (530, 15))
            self.drawPlayerAndPortal()
            pygame.display.update()
        else:
            player_died(window, player.slime_kill_count)
    def redrawGameWindowLevel2(self):
        window.blit(level_2_bg, (0,0))
        pygame.display.update()

start = init_game(window)
if not(start):
    pygame.quit()
else:
    start_up_screen = pygame.image.load("./slime_hunter/pictures/start_up/start_up_screen.png")
    loading = pygame.image.load("./slime_hunter/pictures/start_up/loading.png")
    level_2_bg = pygame.image.load('./slime_hunter/pictures/Background/pale_background.png')
    window.blit(loading, (0,0))
    pygame.display.update()
    if True:
        background = pygame.image.load('./slime_hunter/pictures/background/forest_background_with_step_and_score.png')
        bars = pygame.image.load('./slime_hunter/pictures/other/bar.png')
        heart = load_images('./slime_hunter/pictures/other/heart/', 50, 50, False, False)
        stamina_heart = load_images('./slime_hunter/pictures/other/stamina_heart/', 50, 50, False, False)
        strong_heart = load_images('./slime_hunter/pictures/other/strong_heart/', 50, 50, False, False)
        strong_stamina_heart = load_images('./slime_hunter/pictures/other/strong_stamina_heart/', 50, 50, False, False)
        # fps
        clock.tick(30)
        load = 289
        load_bar = 0
        # load portal
        portal_front = load_images('./slime_hunter/pictures/portal/front/', 210, 210, False, True)
        portal_back = load_images('./slime_hunter/pictures/portal/back/', 210, 210, False, True)
        
        load_bar += load * 0.2
        pygame.draw.rect(window,(142,64,64), (457,240,load_bar,26))
        pygame.display.update()

        # load witch
        idle_left = load_images('./slime_hunter/pictures/witch/idle/', 220, 220, False, True)
        idle_right = load_images('./slime_hunter/pictures/witch/idle/', 220, 220, True, True)
        attack_right = load_images('./slime_hunter/pictures/witch/hit/', 220, 220, True, True)
        attack_left = load_images('./slime_hunter/pictures/witch/hit/', 220, 220, False, True)
        walk_left = load_images('./slime_hunter/pictures/witch/walk/', 220, 220, False, True)
        walk_right = load_images('./slime_hunter/pictures/witch/walk/', 220, 220, True, True)
        
        load_bar += load * 0.2
        pygame.draw.rect(window,(142,64,64), (457,240,load_bar,27))
        pygame.display.update()

        hit_left = load_images('./slime_hunter/pictures/witch/hit/', 220, 220, False, True)
        hit_right = load_images('./slime_hunter/pictures/witch/hit/', 220, 220, True, True)
        getting_hit_left = load_images('./slime_hunter/pictures/witch/getting_hit/', 220, 220, False, True)
        getting_hit_right = load_images('./slime_hunter/pictures/witch/getting_hit/', 220, 220, True, True) 
        skill_right = load_images('./slime_hunter/pictures/witch/skill/', 220, 220, True, True)
        skill_left = load_images('./slime_hunter/pictures/witch/skill/', 220, 220, False, True)       

        load_bar += load * 0.2
        pygame.draw.rect(window,(142,64,64), (457,240,load_bar,27))
        pygame.display.update()

        # load slime
        slime_walk_left = load_images('./slime_hunter/pictures/slime/walk/', 260, 260, False, True)
        slime_walk_right = load_images('./slime_hunter/pictures/slime/walk/', 260, 260, True, True)
        slime_attacked_left = load_images('./slime_hunter/pictures/slime/attacked/', 260, 260, False, True)
        slime_attacked_right = load_images('./slime_hunter/pictures/slime/attacked/', 260, 260, True, True)
        slime_dead_left = load_images('./slime_hunter/pictures/slime/dead/', 260, 260, False, True)
        slime_dead_right = load_images('./slime_hunter/pictures/slime/dead/', 260, 260, True, True)

        load_bar += load * 0.2
        pygame.draw.rect(window,(142,64,64), (457,240,load_bar,27))
        pygame.display.update()
        
        # load pink slime
        pink_slime_walk_left = load_images('./slime_hunter/pictures/pink_slime/walk/', 260, 260, False, True)
        pink_slime_walk_right = load_images('./slime_hunter/pictures/pink_slime/walk/', 260, 260, True, True)
        pink_slime_attacked_left = load_images('./slime_hunter/pictures/pink_slime/attacked/', 260, 260, False, True)
        pink_slime_attacked_right = load_images('./slime_hunter/pictures/pink_slime/attacked/', 260, 260, True, True)
        pink_slime_dead_left = load_images('./slime_hunter/pictures/pink_slime/dead/', 260, 260, False, True)
        pink_slime_dead_right = load_images('./slime_hunter/pictures/pink_slime/dead/', 260, 260, True, True)
        
        load_bar += load * 0.2
        pygame.draw.rect(window,(142,64,64), (457,240,load_bar,27))
        pygame.display.update()

    player = witch(450, 230, 220, 220)
    game = game_manager()
    enemies = []
    hearts = []
    seconds = datetime.now().second
    gate = portal(90, 40)
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False   
        seconds = datetime.now().second
        keys = pygame.key.get_pressed()
        if player.use_skill == False:
            if keys[pygame.K_RIGHT]:
                if not(player.y < 100 and (player.x > 225)):
                    player.x += 1.5
                    player.walk = 1
                else:
                    player.walk = 0
                player.side = 1
            elif keys[pygame.K_LEFT]:
                if not(player.y < 100 and (player.x < 40)):
                    player.x -= 1.5
                    player.walk = 1
                else:
                    player.walk = 0
                player.side = 0
            else:
                player.walk = 0
            if keys[pygame.K_UP] or player.jump:
                if not(player.jump):
                    player.jump = True
                    player.jump_help = 6
                else:
                    if not(player.way_down) and player.jump_help >= 0.5:
                        player.y -= player.jump_help ** 1.3
                        player.jump_help -= 0.5
                    else:
                        player.way_down = True
                if player.way_down and player.jump_help <= 6:
                    player.y += player.jump_help ** 1.3
                    player.jump_help += 0.5
                elif player.way_down and player.jump_help >= 6:
                    player.jump = False
                    player.way_down = False
            if keys[pygame.K_LCTRL]:
                player.attacking = True  
            if keys[pygame.K_SPACE] and player.stamina > 40:
                player.use_skill = True
            if keys[pygame.K_LSHIFT]:
                if 40 < player.x < 225 and player.jump and player.y > 100 and\
                    not(player.teleport) and player.stamina > 15 and\
                    abs(datetime.now().second - player.last_teleport) >= 1:
                    player.y -= 200
                    player.on_step = True
                    player.last_teleport = datetime.now().second
                    player.stamina -= 15
                elif abs(datetime.now().second - player.last_teleport) >= 1 and player.stamina > 15 and\
                    not(player.on_step):
                    player.teleport = True
                elif 40 < player.x < 225 and player.y < 100 and player.stamina > 15 and\
                    abs(datetime.now().second - player.last_teleport) >= 1:
                    player.y += 200
                    player.on_step = False
                    player.last_teleport = datetime.now().second
                    player.stamina -= 15
        if game.level_2:
            game.redrawGameWindowLevel2()
        else:
            game.redrawGameWindow()
    pygame.quit()