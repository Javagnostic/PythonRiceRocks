# implementation of Spaceship - program template for RiceRocks
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = range(3)
time = 0.5
started = False
rock_group = set([])
missile_group_left = set([])
missile_group_right = set([])
explosion_group = set([])
timing = int()
ship = ""
start_button = False
shield_recharge = 0
shield_text_color = "Red"
intro = 0.3

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

"""
The ships' images for the splash PNG are downloaded from the web, modified and used in this non-commercial project;
the intro_sound is downloaded from youtube - Star Wars - The Imperial March (Darth Vader's Theme Serbian way) :)))
(http://www.youtube.com/watch?v=ghEEvE_EYXg)
The ship images in the "started" game are redrawn from those, found in the web,
but modified for the purpose of the game.
Too much time spent in "playing" with the images. No time left for optimizing the code
(especialy for drawing the ship in its different states).
"""

# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris3_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2013.png")

# splash and start image
splash_info = ImageInfo([200, 200], [400, 400])
splash_image = simplegui.load_image("http://i.imgur.com/wwPmps2.png")
splash_start_info = ImageInfo([200, 20], [400, 40])
splash_start_image = simplegui.load_image("http://i.imgur.com/N2GwbzH.png")
splash_top_info = ImageInfo([397, 30], [794, 60])
splash_top_image = simplegui.load_image("http://i.imgur.com/ei8fsxM.png")
# splash_info = ImageInfo([200, 150], [400, 300])
# splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://i.imgur.com/fg6Y705.png")
ship_image2 = simplegui.load_image("http://i.imgur.com/h0FqhLM.png")
#ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")
missile_image2 = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot1.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([50, 50], [100, 100], 17, 70, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/explosion.hasgraphics.png")
#explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
intro_sound = simplegui.load_sound("https://www.dropbox.com/s/blswwdf0tqs7eks/intro.mp3?dl=1")
intro_sound.set_volume(0.3)

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def process_sprite_group(sprite_group, canvas):
    if started:
        for s in set(sprite_group):
            s.draw(canvas)
            if s.update():
                sprite_group.remove(s)
        
def group_collide(sprite_group, other_object):
    if started:
        for s in set(sprite_group):
            if s.collide(other_object):
                explosion_group.add(Sprite(s.get_position(), [0, 0], 0, 0,
                                    explosion_image, explosion_info, explosion_sound))
                sprite_group.remove(s)
                return True
        
def group_group_collide(first_sprite, second_sprite):
    if started:
        for s in set(first_sprite):
            if group_collide(second_sprite, s):
                first_sprite.remove(s)
                return True

# A helper function used for counting the game score,
# supporting the method for increasing the rocks velocities
def next(x):
    return x + 1

# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.slow = 0.15
        self.de_xlr8 = 0.98
        self.angle = angle
        self.angle_vel = 0
        self.angle_acc = 0.05
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.shooting = False
        self.cannon_left = 3.7
        self.cannon_right = 5.7
        self.missile_vel_acc = 5
        
    def draw(self,canvas):
        
        # The different states for drowing the ships.
        # Could not find a way to bind them in one (single) logic
        next_pic = int()
        if not self.thrust and not self.shooting:
            if len(lives) == 2:
                next_pic = len(lives) * len(lives)
            else:
                next_pic += len(lives) * len(lives) - 1
        elif self.thrust and not self.shooting:
            if len(lives) == 2:
                next_pic = len(lives) * len(lives) + 1
            else:
                next_pic += 1
                next_pic += len(lives) * len(lives) - 1
        elif not self.thrust and self.shooting:
            if len(lives) == 2:
                next_pic = len(lives) * len(lives) + 2
            else:
                next_pic += 2
                next_pic += len(lives) * len(lives) - 1
        elif self.thrust and self.shooting:
            if len(lives) == 2:
                next_pic = len(lives) * len(lives) + 3
            else:
                next_pic += 3
                next_pic += len(lives) * len(lives) - 1
        if ship == "X":		# drawing Xwing
            thr_ship_center = (self.image_center[0] + next_pic * self.image_size[0], self.image_center[1])
            canvas.draw_image(ship_image, thr_ship_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        if ship == "T":		# drawing TieFighter
            thr_ship_center = (self.image_center[0] + next_pic * self.image_size[0], self.image_center[1])
            canvas.draw_image(ship_image2, thr_ship_center, self.image_size,
                              self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # angles of the cannons' positions for the Xwing
        self.cannon_left += self.angle_vel
        self.cannon_right += self.angle_vel

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * self.slow
            self.vel[1] += acc[1] * self.slow
            
        self.vel[0] *= self.de_xlr8
        self.vel[1] *= self.de_xlr8

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += self.angle_acc
        
    def decrement_angle_vel(self):
        self.angle_vel -= self.angle_acc
        
    def shoot(self):
        global a_missile_left, a_missile_right
        self.shooting = True
        forward = angle_to_vector(self.angle)
        
        # The Xwing renders two shooting elements from the top view
        if ship == "X":
            cannon_l = angle_to_vector(self.cannon_left)
            missile_left = [self.pos[0] + cannon_l[0] * self.radius, self.pos[1] + cannon_l[1] * self.radius]
            cannon_r = angle_to_vector(self.cannon_right)
            missile_right = [self.pos[0] + cannon_r[0] * self.radius, self.pos[1] + cannon_r[1] * self.radius]
            missile_vel = [self.vel[0] + self.missile_vel_acc * forward[0], self.vel[1] + self.missile_vel_acc * forward[1]]
            missile_group_left.add(Sprite(missile_left, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound))
            missile_group_right.add(Sprite(missile_right, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound))
        
        # The TieFighter renders only one shooting element
        # The missile spawns maybe 8-10 px in front of its cannon,
        # but I left it so, because it looks more "realistic"
        else:
            missile = [self.pos[0] + forward[0] * self.radius, self.pos[1] + forward[1] * self.radius]
            missile_vel = [self.vel[0] + self.missile_vel_acc * forward[0], self.vel[1] + self.missile_vel_acc * forward[1]]
            missile_group_left.add(Sprite(missile, missile_vel, self.angle, 0, missile_image2, missile_info, missile_sound))
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        expl_matrix = [9, 9]
        expl_index = [self.age % expl_matrix[0], (self.age // expl_matrix[0]) % expl_matrix[1]]
        
        if not self.animated:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        elif self.animated:
            canvas.draw_image(self.image, 
                    [self.image_center[0] + expl_index[0] * self.image_size[0], 
                     self.image_center[1] + expl_index[1] * self.image_size[1]], 
                     self.image_size, self.pos, self.image_size)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        if self.lifespan and (self.age <= self.lifespan):
            self.age += 1
            return False
        elif self.lifespan and (self.age > self.lifespan):
            return True
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) < self.radius + other_object.get_radius():
            return True
        else:
            return False
  
# key handlers to control ship   
def keydown(key):
    if started:
        if key == simplegui.KEY_MAP['left']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(True)
        elif key == simplegui.KEY_MAP['space']:
            my_ship.shoot()
        
def keyup(key):
    if started:
        if key == simplegui.KEY_MAP['left']:
            my_ship.increment_angle_vel()
        elif key == simplegui.KEY_MAP['right']:
            my_ship.decrement_angle_vel()
        elif key == simplegui.KEY_MAP['up']:
            my_ship.set_thrust(False)
        elif key == simplegui.KEY_MAP['space']:
            my_ship.shooting = False
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global time, started, score, my_ship, rock_group, lives, score, ship, start_button
    global missile_group_left, missile_group_right, explosion_group, shield_recharge, shield_text_color
    
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    
    # Xwing splash click area (X)
    Xwidth = (center[0] - size[0] / 2 + 10) < pos[0] < (center[0] - 10)
    
    # TieFighter splash click area (X)
    Twidth = (center[0] + 10) < pos[0] < (center[0] + size[0] / 2 - 10)
    
    # Both ships plash click area (Y)
    ships_height = (center[1] - 20) < pos[1] < (center[1] + 150)
    
    # Start button splash click area
    inwidth = (center[0] - size[0] / 4) < pos[0] < (center[0] + size[0] / 4)
    inheight = (center[1] + size[1] / 2 + 10) < pos[1] < (center[1] + size[1] / 2 + 50)
    
    # Enabling start button clicking (no click without selecting a ship firstly)
    if Xwidth and ships_height:
        ship = "X"
        start_button = True
    elif Twidth and ships_height:
        ship = "T"
        start_button = True
    
    if (not started) and inwidth and inheight and start_button:
        started = True
        if ship == "X":
            my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 4.712, ship_image, ship_info)
        if ship == "T":
            my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 4.712, ship_image2, ship_info)

        # The "started" game global vars loaded
        explosion_group = set([])
        rock_group = set([])
        missile_group_left = set([])
        missile_group_right = set([])
        lives = range(3)
        score = 0
        recharge.stop()
        shield_recharge = 0
        shield_text_color = "Red"
        soundtrack.rewind()
        soundtrack.play()

def draw(canvas):
    global time, started, score, my_ship, rock_group, lives, score, ship, shield_recharge
    global intro, missile_group_left, missile_group_right, explosion_group, start_button, shield_text_color
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    if ship == "X":
        my_ship.draw(canvas)
    elif ship == "T":
        my_ship.draw(canvas)
    else:
        my_ship.draw(canvas)
    
    # Applying the "process_sprite_group" helper function
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group_left, canvas)
    process_sprite_group(missile_group_right, canvas)
    process_sprite_group(explosion_group, canvas)
    
    # The blue backgr drawn on the top of the canvas, under the game status elements
    canvas.draw_image(splash_top_image, splash_top_info.get_center(), 
                      splash_top_info.get_size(), [WIDTH / 2, splash_top_info.get_center()[1] - 1], 
                      [splash_top_info.get_size()[0] + 10, splash_top_info.get_size()[1] + 2])
    
    # update ship and sprites
    if ship == "X":
        my_ship.update()
    elif ship == "T":
        my_ship.update()
    else:
        my_ship.update()

    # Applying the "group_collide" helper function and calculating the lives of the ship
    # In fact, the ship has only one life, but its shields can help it to survive more time
    # into the rocky field
    if started and group_collide(rock_group, my_ship):
        if lives != []:
            lives.pop(0)
        if lives == []:
            my_ship = Sprite(my_ship.get_position(), [0, 0], 0, 0,
                             explosion_image, explosion_info, explosion_sound)
            ship_thrust_sound.rewind()
            ship = ""
            start_button = False
            started = False
            intro = 0.3
    
    # Applying the "group_group_collide" helper function
    if group_group_collide(rock_group, missile_group_left) or group_group_collide(rock_group, missile_group_right):
        score = next(score)
    
    # Drawing the "Shield status".
    # Maybe there is much better way for arranging the code here...
    canvas.draw_text("Shield status:", [20, 35], 20, "White", "sans-serif")
    life_pos = 165
    obj_image = ""
    if ship == "X":
        obj_image = ship_image
    if ship == "T":
        obj_image = ship_image2
    if len(lives) == 3 and ship:
        canvas.draw_image(obj_image, [ship_info.get_center()[0] + 14 * ship_info.get_size()[0], ship_info.get_center()[1]],
                          ship_info.get_size(), (life_pos, 30), [ship_info.get_size()[0] / 2, ship_info.get_size()[1] / 2],
                          ship_info.get_radius())
        canvas.draw_text("Fully charged", [195, 35], 16, "#49c43d", "sans-serif")
    if len(lives) == 2 and ship:
        canvas.draw_image(obj_image, [ship_info.get_center()[0] + 13 * ship_info.get_size()[0], ship_info.get_center()[1]],
                          ship_info.get_size(), (life_pos, 30), [ship_info.get_size()[0] / 2, ship_info.get_size()[1] / 2],
                          ship_info.get_radius())
        canvas.draw_text("Weakened shields", [195, 35], 16, "#ff9600", "sans-serif")
    if len(lives) == 1 and ship:
        canvas.draw_image(obj_image, [ship_info.get_center()[0] + 12 * ship_info.get_size()[0], ship_info.get_center()[1]],
                          ship_info.get_size(), (life_pos, 30), [ship_info.get_size()[0] / 2, ship_info.get_size()[1] / 2],
                          ship_info.get_radius())
        if timing % 2 == 0:
            canvas.draw_text("Shields are down!", [195, 35], 16, "Red", "sans-serif")
            
        # The second level shield recharging method of the TieFighter
        if ship == "T" and shield_recharge < 100:
            recharge.start()
            canvas.draw_text(str(shield_recharge) + "% Second level shield recharge", [335, 35], 16, shield_text_color, "sans-serif")
        if shield_recharge >= 50:
            shield_text_color = "#ff9600"
        if shield_recharge >= 90:
            shield_text_color = "#49c43d"
        if ship == "T" and shield_recharge == 100:
            shield_text_color = "Red"
            shield_recharge = 0
            recharge.stop()
            lives.append(1)

    #Score
    score_txt = "Score: " + str(score)
    arrange_right = WIDTH - (30 + frame.get_canvas_textwidth(score_txt, 20))
    canvas.draw_text(score_txt, [arrange_right, 35], 20, "White", "sans-serif")
    
    # draw splash screen if not started
    if not started:
        next_image = 0
        if ship == "X":
            next_image = 1
        elif ship == "T":
            next_image = 2
        splash_center = splash_info.get_center()[0] + next_image * splash_info.get_size()[0]
        canvas.draw_image(splash_image, [splash_center, splash_info.get_center()[1]], 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        splash_start_pos_Y = HEIGHT / 2 + splash_info.get_size()[1] / 2 + 30 
        canvas.draw_image(splash_start_image, splash_start_info.get_center(), 
                          splash_start_info.get_size(), [WIDTH / 2, splash_start_pos_Y], 
                          splash_start_info.get_size())
        soundtrack.rewind()
        intro = 0.3
        intro_sound.play()
        


# Shield recharge timer
# Created a timer handler for the second timer heling the calculating of some of the states of the TieFighter
def charging_shield():
    global shield_recharge
    shield_recharge += 1
    
# timer handler that spawns a rock    
def rock_spawner():
    global a_rock, score, rock_vel, timing, intro
    
    # Used this timer handler also for playing and "fading" the intro_sound
    if intro >= 0.05:
        intro -= 0.05
        intro_sound.set_volume(intro)
        if intro < 0.001:
            intro_sound.rewind()

    """
    The handler spawns the rocks only from the canvas' edges going into the canvas,
    avoiding spawning them in the middle of it.
    With every new destroyed asteroid the rock vel is slightly increased. 
    """

    timing += 1
    rock_pos = random.choice([[0, random.randrange(0, WIDTH + 1)], [random.randrange(0, HEIGHT + 1), 0],
                              [WIDTH, random.randrange(0, WIDTH + 1)], [random.randrange(0, HEIGHT + 1), HEIGHT]])

    if score == 0:
        rock_vel = [random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3]
    elif next(score):
        rock_vel = [random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3]
        rock_vel[0] *= (score * 0.2)
        rock_vel[1] *= (score * 0.2)
    if (rock_pos[0] == 0 and rock_vel[0] < 0):
        rock_vel[0] = -rock_vel[0]
    elif (rock_pos[1] == 0 and rock_vel[1] < 0):
        rock_vel[1] = -rock_vel[1]
    elif (rock_pos[0] == WIDTH and rock_vel[0] > 0):
        rock_vel[0] = -rock_vel[0]
    elif (rock_pos[1] == HEIGHT and rock_vel[1] > 0):
        rock_vel[1] = -rock_vel[1]
    
    rock_avel = random.random() * 0.2 - 0.1
    
    if started:
        if len(rock_group) < 12 and dist(rock_pos, my_ship.get_position()) > 200:
            rock_group.add(Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info))
            
# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 4.712, ship_image, ship_info)

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)
timer = simplegui.create_timer(1000.0, rock_spawner)
recharge = simplegui.create_timer(150.0, charging_shield)

# get things rolling
timer.start()
frame.start()