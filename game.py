import sys
import pygame
import random
import math
import time
import configparser
from abc import ABC

# Importing data from the configuration file
config_parser = configparser.RawConfigParser()
config_file = "./game_config.cfg"
config_parser.read(config_file)
width = int(config_parser.get("info", "width"))
height = int(config_parser.get("info", "height"))
game_name = config_parser.get("info", "name")
game_icon = config_parser.get("info", "icon")
game_font = config_parser.get("info", "font")
game_speed = float(config_parser.get("info", "game_speed"))
global_x_vel = float(config_parser.get("info", "player_velocity_x"))
global_y_vel = float(config_parser.get("info", "player_velocity_y"))
max_rounds = int(config_parser.get("info", "max_rounds"))
fps = int(config_parser.get("info", "fps"))
black_hole_count = int(config_parser.get("info", "black_hole_count"))
high_score = int(config_parser.get("score_keeping", "high_score"))


# Initialize a PyGame classes, window, font manager audio mixer and clock
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

# Loading sound tracks
pygame.mixer.music.load("Audio/PercussionSpaceMusic.mp3")
explosion = pygame.mixer.Sound("Audio/Explosion.wav")

# Configure the display
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption(game_name)
pygame.display.set_icon(pygame.image.load(game_icon))
pixel_font = pygame.font.Font(game_font, 15)
pixel_font_lg = pygame.font.Font(game_font, 40)
pixel_font_xl = pygame.font.Font(game_font, 80)


# Global Variables
p1_score = 0
p2_score = 0
white = (255, 255, 255)
black = (0, 0, 0)


# Class definitions
# Abstract base class for all game objects to inherit the draw() method from
class GameObject(ABC):
    def draw(self):
        screen.blit(self.image, (int(self.x), int(self.y)))


class Player(GameObject):
    def __init__(self, image, x, y):
        self.image = pygame.image.load(image)
        self.x = x
        self.y = y
        self.x_vel = 0
        self.y_vel = 0
        self.active = False
        self.success = False

    # Method to update the player's location
    # Location correction to account for boundaries
    def update_location(self, dt):
        self.x += self.x_vel*dt
        if self.x <= 0:
            self.x = 0
        elif self.x >= 360:
            self.x = 360
        self.y += self.y_vel*dt
        if self.y <= 0:
            self.y = 0
        elif self.y >= 713:
            self.y = 713


class DockSite(GameObject):
    def __init__(self, x, y):
        self.image = pygame.image.load("Sprites/DockSites.png")
        self.x = x
        self.y = y


class BlackHole(GameObject):
    def __init__(self, x, y):
        self.image = pygame.image.load("Sprites/BlackHole.png")
        self.x = x
        self.y = y
        self.p1_crossed = False
        self.p2_crossed = False


class Asteroid(GameObject):
    def __init__(self, x, y):
        self.image = pygame.image.load("Sprites/Asteroid.png")
        self.x = x
        self.y = y
        self.x_vel = 0
        self.p1_crossed = False
        self.p2_crossed = False

    def update_location(self, dt):
        self.x += self.x_vel*dt//3
        if self.x > 400:
            self.x = -random.randint(0, 100)


# Game Manager function deciding which game screen to show
# and what difficulty to set for which player
def game_manager():

    # Make the background music loop infinitely
    pygame.mixer.music.play(-1)
    landing_page()

    global p1_score, p2_score
    # Both players start from level 1
    p1_level = 1
    p2_level = 1

    while p1_level <= max_rounds and p2_level <= max_rounds:
        p1_level, p2_level = game_play(p1_level, p2_level)

    display_result(p1_level, p2_level, p1_score, p2_score)

    # Updating high score in configuration file if required
    max_score = max(p1_score, p2_score)
    if max_score > high_score:
        # Also display the high score page
        high_score_screen(high_score, max_score)
        config_parser.set('score_keeping', 'high_score', str(max_score))
        with open("game_config.cfg", 'w') as config_file_write:
            config_parser.write(config_file_write)


def black_holes_draw(black_holes):
    for black_hole in black_holes:
        black_hole.draw()


def dock_sites_draw(dock_sites):
    for dock_site in dock_sites:
        dock_site.draw()


def asteroids_draw(asteroids):
    for asteroid in asteroids:
        asteroid.draw()


def collision_detection(obj1, obj2, collider):
    # Calculating Euclidean Distance between the two objects
    dist = math.sqrt(pow(obj1.x - obj2.x, 2) + pow(obj1.y - obj2.y, 2))
    # If distance is under some threshold, the objects have collided
    if collider == "black_hole":
        threshold = 40
    else:
        threshold = 50
    if dist <= threshold:
        return True


def black_hole_collision(player, black_holes):
    # For every BlackHole, run collision detection against the player in
    # question
    for black_hole in black_holes:
        if collision_detection(player, black_hole, "black_hole"):
            return True


def asteroid_collision(player, asteroids):
    for asteroid in asteroids:
        if collision_detection(player, asteroid, "asteroid"):
            return True


def create_explosion(player):
    # Play the explosion sound effect
    explosion.play(0)
    # Make explosion appear on screen
    player.image = pygame.image.load("Sprites/Explosion.png")
    player.draw()
    pygame.display.update()
    time.sleep(0.2)


def stay_on_page(bg, s1, s2, mode):
    moving_on = False
    while not moving_on:
        for event in pygame.event.get():
            # If the cross on the window is clicked, close the window
            if event.type == pygame.QUIT:
                sys.exit()
            # If Space bar is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                moving_on = True
        screen.blit(bg, (0, 0))
        # If the scores need to be displayed
        if mode == "score":
            p1_score_render = pixel_font_lg.render(str(s1) + "P", True, white)
            p2_score_render = pixel_font_lg.render(str(s2) + "P", True, white)
            screen.blit(p1_score_render, (240, 402))
            screen.blit(p2_score_render, (240, 480))
        pygame.display.update()


def landing_page():
    bg = pygame.image.load("Sprites/LandingPage.png")
    stay_on_page(bg, 0, 0, "render")
    instructions1()


def instructions1():
    bg = pygame.image.load("Sprites/Instructions1.png")
    stay_on_page(bg, 0, 0, "render")
    instructions2()


def instructions2():
    bg = pygame.image.load("Sprites/Instructions2.png")
    stay_on_page(bg, 0, 0, "render")


def display_result(p1_l, p2_l, p1_s, p2_s):
    if p1_l > p2_l:
        bg = pygame.image.load("Sprites/P1Wins.png")
    elif p1_l < p2_l:
        bg = pygame.image.load("Sprites/P2Wins.png")
    else:
        if p1_s > p2_s:
            bg = pygame.image.load("Sprites/P1Wins.png")
        else:
            bg = pygame.image.load("Sprites/P2Wins.png")
    stay_on_page(bg, p1_s, p2_s, "score")


def high_score_screen(ohs, nhs):
    bg = pygame.image.load("Sprites/High Score.png")
    stay_on_page(bg, ohs, nhs, "score")


# The main game logic
def game_play(p1_level, p2_level):

    # Global scorekeepers
    global p1_score
    global p2_score
    global game_speed

    # Time since pygame.init() was called
    start_ticks = pygame.time.get_ticks()
    # Declaring required GameObjects for current game state
    # Two players, starting at opposite ends of the screen
    p1 = Player("Sprites/Player1.png", 155, 705)
    p2 = Player("Sprites/Player2.png", 205, 5)

    # 6 DockSites
    dock_sites = [DockSite(0, 0),
                  DockSite(0, 140),
                  DockSite(0, 280),
                  DockSite(0, 420),
                  DockSite(0, 560),
                  DockSite(0, 700)]

    # Randomly creating and placing BlackHole instances on DockSites
    black_holes = []
    for i in range(black_hole_count):
        zone = random.choice([140, 280, 420, 560])
        black_holes.append(BlackHole(random.randint(0, 330), zone))

    asteroids = [Asteroid(-random.randint(0, 100), 70),
                 Asteroid(-random.randint(0, 100), 210),
                 Asteroid(-random.randint(0, 100), 350),
                 Asteroid(-random.randint(0, 100), 490),
                 Asteroid(-10, 630)]

    # Boolean flags to keep track of stuff
    p1.active = True
    p2.active = False

    p1.success = False
    p2.success = False

    in_play = True

    # The main game loop
    while in_play:

        # Make game speed independent of system performance
        dt = clock.tick(fps)
        # The number of seconds passed since the start of current round
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        # Event detection
        for event in pygame.event.get():
            # If the cross on the window is clicked, close the window
            if event.type == pygame.QUIT:
                sys.exit()
            # If a key is pressed
            if event.type == pygame.KEYDOWN:
                # Movement logic for Player 1
                if p1.active:
                    if event.key == pygame.K_LEFT:
                        p1.x_vel = -global_x_vel
                    if event.key == pygame.K_RIGHT:
                        p1.x_vel = global_x_vel
                    if event.key == pygame.K_UP:
                        p1.y_vel = -global_y_vel
                    if event.key == pygame.K_DOWN:
                        p1.y_vel = global_y_vel

                # Movement logic for Player 2
                if p2.active:
                    if event.key == pygame.K_a:
                        p2.x_vel = -global_x_vel
                    if event.key == pygame.K_d:
                        p2.x_vel = global_x_vel
                    if event.key == pygame.K_w:
                        p2.y_vel = -global_y_vel
                    if event.key == pygame.K_s:
                        p2.y_vel = global_y_vel
            # If a key is released
            if event.type == pygame.KEYUP:
                # Movement logic for Player 1
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    p1.x_vel = 0
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    p1.y_vel = 0

                # Movement logic for Player 2
                if event.key in [pygame.K_a, pygame.K_d]:
                    p2.x_vel = 0
                if event.key in [pygame.K_w, pygame.K_s]:
                    p2.y_vel = 0

        p1.update_location(dt)
        p2.update_location(dt)
        for asteroid in asteroids:
            asteroid.update_location(dt)

        # Collision Handling
        # If it's Player 1's turn
        if p1.active:
            # Modify each Asteroid velocity based on the player's current level
            for asteroid in asteroids:
                asteroid.x_vel = math.pow(p1_level, game_speed)
                # If an Asteroid has been crossed, reward the player
                if not asteroid.p1_crossed and p1.y < asteroid.y - 50:
                    asteroid.p1_crossed = True
                    p1_score += 10

            for black_hole in black_holes:
                # If a BlackHole has been crossed, reward the player
                if not black_hole.p1_crossed and p1.y < black_hole.y - 40:
                    black_hole.p1_crossed = True
                    p1_score += 5

            # If the player collides with either a BlackHole or an Asteroid
            if black_hole_collision(p1, black_holes) or asteroid_collision(
                    p1, black_holes):
                # Show the explosion
                create_explosion(p1)
                # Turn change logic
                p1.active = False
                p2.active = True
                start_ticks = pygame.time.get_ticks()

        # If it's Player 2's turn
        if p2.active:
            # Modify every Asteroid instance velocity based on the player's
            # current level
            for asteroid in asteroids:
                asteroid.x_vel = math.pow(p2_level, game_speed)
                # If an Asteroid has been crossed, reward the player
                if not asteroid.p2_crossed and p2.y > asteroid.y + 50:
                    asteroid.p2_crossed = True
                    p2_score += 10

            for black_hole in black_holes:
                # If an Asteroid has been crossed, reward the player
                if not black_hole.p2_crossed and p2.y > black_hole.y + 50:
                    black_hole.p2_crossed = True
                    p2_score += 5

            # If the player collides with either a BlackHole or an Asteroid
            if black_hole_collision(p2, black_holes) or asteroid_collision(
                    p2, asteroids):
                # Show the explosion
                create_explosion(p2)
                # Round end logic
                p2.active = False
                in_play = False

        # Boolean update decision
        # If Player 1 got to the other side
        if p1.y <= 10:
            # Turn change logic
            p1.active = False
            p2.active = True
            p1.success = True
            p1.y = 705
            start_ticks = pygame.time.get_ticks()
            # Compute score
            p1_time_taken = seconds + 1
            p1_score += (1000 // p1_time_taken)

        # If Player 2 got to the other side
        if p2.y >= 710:
            # Round end logic
            p2.active = False
            p2.success = True
            in_play = False
            # Compute score
            p2_time_taken = seconds + 1
            p2_score += (1000 // p2_time_taken)

        # Update the screen content
        screen.fill((0, 0, 20))
        dock_sites_draw(dock_sites)
        black_holes_draw(black_holes)
        asteroids_draw(asteroids)
        if p1.active:
            p1.draw()
        p2.draw()

        # Score rendering
        p1_score_renderer = pixel_font.render("P1: " + str(p1_score), True,
                                              white)
        p2_score_renderer = pixel_font.render("P2: " + str(p2_score), True,
                                              white)
        pygame.draw.rect(screen, black, (0, 0, 120, 15))
        screen.blit(p1_score_renderer, (5, 0))
        screen.blit(p2_score_renderer, (65, 0))

        # Time rendering
        seconds_renderer = pixel_font.render("Time: " + str(seconds), True,
                                             white)
        pygame.draw.rect(screen, black, (335, 0, 65, 17))
        screen.blit(seconds_renderer, (337, 0))

        # Level rendering
        p1_level_renderer = pixel_font.render("P1 Level: " + str(p1_level),
                                              True, white)
        p2_level_renderer = pixel_font.render("P2 Level: " + str(p2_level),
                                              True, white)
        pygame.draw.rect(screen, black, (0, 737, 72, 15))
        pygame.draw.rect(screen, black, (328, 737, 72, 15))
        screen.blit(p1_level_renderer, (5, 735))
        screen.blit(p2_level_renderer, (330, 735))

        pygame.display.update()

    if p1.success:
        p1_level += 1
    if p2.success:
        p2_level += 1

    # Smooth up transition
    time.sleep(0.2)

    # Send the updated level values back to Game Manager
    return p1_level, p2_level


if __name__ == "__main__":
    game_manager()
