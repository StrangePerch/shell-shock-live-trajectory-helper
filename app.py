import math
import time
import configparser
import numpy as np
import matplotlib.pyplot as plt
from pynput import keyboard, mouse
from screeninfo import get_monitors


def get_x(v, w, a, t):
    return ((w * pow(t, 2)) / 2) + v * math.cos(math.radians(a)) * t


def get_y(v, a, t):
    return ((-gravity * pow(t, 2)) / 2) + v * math.sin(math.radians(a)) * t


def calc_distance(point_a, point_b):
    x1 = point_a[0]
    x2 = point_b[0]
    y1 = point_a[1]
    y2 = point_b[1]
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def on_press(key):
    if supress_input:
        return
    global your_position, target_position, got_you, got_target, debug_position
    if key == keyboard.KeyCode(char='1') and your_position is None:
        your_position = mouse_position
        got_you = True
        print("Your position: ", your_position)
    elif key == keyboard.KeyCode(char='2') and target_position is None:
        target_position = mouse_position
        got_target = True
        print("Target position: ", target_position)
    elif key == keyboard.KeyCode(char='3'):
        debug_position = mouse_position
        print("Position: ", debug_position)


supress_input = False

monitor = get_monitors()[0]

screen_width = monitor.width
screen_height = monitor.height

# CONFIG
config = configparser.ConfigParser()
config.read('config.ini')
debug_size = config["DEBUG"]["screen_size"] == "True"
debug_wind = config["DEBUG"]["wind"] == "True"
game_width = float(config["SETTINGS"]["game_width"])
game_height = float(config["SETTINGS"]["game_height"])
wind_multiplier = float(config["SETTINGS"]["wind_multiplier"])

def transform_x(x):
    global screen_width
    return x / screen_width * game_width


def transform_y(y):
    global screen_height
    return (screen_height - y) / screen_height * game_height


def on_move(mouse_x, mouse_y):
    global mouse_position
    mouse_position = (transform_x(mouse_x), transform_y(mouse_y))


def calc_velocity():
    nearest = None
    calculated_velocity = None
    calculated_flight_time = None

    for v in np.arange(0, 100, 1):
        for t in np.arange(0, 30, 0.1):
            x = get_x(v, wind, shooting_angle, t)
            y = get_y(v, shooting_angle, t)
            cords = (x, y)
            target = (abs(target_position[0] - your_position[0]), target_position[1] - your_position[1])
            distance = calc_distance(target, cords)
            if nearest is None or distance < nearest:
                nearest = distance
                calculated_velocity = v
                calculated_flight_time = t
    calculated_height = pow(calculated_velocity, 2) / (2 * gravity) * pow(math.sin(math.radians(shooting_angle)), 2)
    return calculated_velocity, calculated_flight_time, calculated_height


def calc_wind():
    nearest = None
    calculated_wind = None

    for w in np.arange(-50, 50, 0.1):
        for t in np.arange(0, 30, 0.1):
            x = get_x(velocity, w, shooting_angle, t)
            y = get_y(velocity, shooting_angle, t)
            cords = (x, y)
            target = (hit_point[0] - your_position[0], hit_point[1] - your_position[1])
            distance = calc_distance(target, cords)
            if nearest is None or distance < nearest:
                nearest = distance
                calculated_wind = w
    return calculated_wind


if debug_size:
    print("Program started in GAME SCREEN SIZE DEBUG MODE ( You can change inside config.ini file )")
elif debug_wind:
    print("Program started in WIND DEBUG MODE ( You can change inside config.ini file )")

mouse_position = (0, 0)

your_position = None
target_position = None
debug_position = None

gravity = 9.8

listener = keyboard.Listener(
    on_press=on_press)
listener.start()

listener = mouse.Listener(
    on_move=on_move)
listener.start()

while True:
    print("Waiting for positions (For your position press '1' and press '2' for target)")
    your_position = None
    target_position = None
    while your_position is None or target_position is None:
        time.sleep(1)

    # input
    supress_input = True

    shooting_angle = int(input("Angle: "))

    wind = int(input("Wind: ")) * wind_multiplier

    supress_input = False
    # /input

    velocity, flight_time, height = calc_velocity()

    print("Velocity: ", velocity)
    print("Estimated time ", flight_time, " seconds")
    print("Estimated height ", height)

    if debug_size:
        print("DEBUG SCREEN SIZE:")
        print("Choose hit point with '3'")
        debug_position = None
        while debug_position is None:
            time.sleep(1)
        hit_point = debug_position
        print("Choose highest point of trajectory with '3'")
        debug_position = None
        while debug_position is None:
            time.sleep(1)
        real_height = debug_position[1] - your_position[1]
        print("Height: ", height)
        expected_length = abs(target_position[0] - your_position[0])
        real_length = abs(hit_point[0] - your_position[0])
        x_diff = real_length / expected_length
        print("Changed game width from ", game_width, " to ", game_width / x_diff)
        game_width /= x_diff
        expected_height = height
        y_diff = real_height / expected_height
        print("Changed game height from ", game_height, " to ", game_height / y_diff)
        game_height /= y_diff
        config["SETTINGS"] = {
            'game_width': str(game_width),
            'game_height': str(game_height),
            'wind_multiplier': str(wind_multiplier)}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    elif debug_wind:
        print("DEBUG WIND:")
        print("Choose hit point with '3'")
        debug_position = None
        while debug_position is None:
            time.sleep(1)

        hit_point = debug_position
        print(hit_point)
        real_wind = calc_wind()
        print(real_wind)
        print(wind)
        wind_diff = abs(wind / real_wind)
        print(wind_diff)

        print("Changed wind multiplier from ", wind_multiplier, " to ", wind_multiplier / wind_diff)
        wind_multiplier /= wind_diff

        config["SETTINGS"] = {
            'game_width': str(game_width),
            'game_height': str(game_height),
            'wind_multiplier': str(wind_multiplier)}

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
