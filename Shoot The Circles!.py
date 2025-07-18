from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random
import math

from time import time


# Axis aligned bounding box
class Box:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Circle:
    def __init__(self, r, x, y, c):
        self.radius = r
        self.x = x
        self.y = y
        self.color = c


def get_random(start, end):
    return random.random()*(end-start) + start


def random_bright_color(): # FOR PUCK
    r = random.random()
    g = random.random()
    b = random.random()
    # normalize to get bright color
    sq = math.sqrt(r*r + g*g + b*b)
    r /= sq
    g /= sq
    b /= sq
    return r, g, b


W_Width, W_Height = 500, 500
score = 0
lives = 3
misses = 3
failed = False
paused = False

# Circles
circle_min_size, circle_max_size = 20, 40   # radius
circle_speed = 100
circle_timer = 2000     # time between 2 circles, in milliseconds
circles = []
circle_padding = 45

# Bullets
bullet_size = 10   # radius
bullet_speed = 300
bullet_color = (1, 1, 0)    # yellow
bullets = []

# Shooter
shooter_size = 15   # radius
default_shooter_color = shooter_color = (0.6, 1, 1)
shooter_speed = 4 * W_Width
shooter = Circle(shooter_size, 0, -W_Height/2 + 20, shooter_color)

# BUTTONS
button_width = 50
button_height = 50
button_padding = 15
reset_button_x = -W_Width/2 + button_padding
pause_button_x = 0-button_width/2
exit_button_x = W_Width/2 - button_width - button_padding
reset_button_y = pause_button_y = exit_button_y = W_Height/2 - button_padding

delta_time = 0.1



   

def keyboardListener(key, x, y):
    global W_Width, W_Height
    global shooter, shooter_speed
    global delta_time
    if failed or paused:
        return

    global bullets
    if key == b'd':
        if shooter.x + shooter.radius < W_Width/2:
            shooter.x += shooter_speed * delta_time
    if key == b'a':
        if shooter.x - shooter.radius > -W_Width/2:
            shooter.x -= shooter_speed * delta_time

    if key==b' ':
        new_bullet()


# TOP LEFT anchor point of button
def mouse_button_inside(mouse_x, mouse_y, button_x, button_y, width, height):
    return button_x < mouse_x < button_x + width and button_y > mouse_y > button_y - height


def mouseListener(button, state, x, y):  # /#/x, y is the x-y of the screen (2D)
    global reset_button_x, reset_button_y, pause_button_x, pause_button_y, exit_button_x, exit_button_y, button_height, button_width
    global paused

    # glutPostRedisplay()
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            x, y = mouse_convert_coordinate(x, y)
            # RESET
            if mouse_button_inside(x, y, reset_button_x, reset_button_y, button_width, button_height):
                reset_game()

            # PAUSE/ PLAY
            if mouse_button_inside(x, y, pause_button_x, pause_button_y, button_width, button_height):
                if not paused:
                    print('PAUSED')
                else:
                    print('RESUMED')

                paused = not paused

            # EXIT
            if mouse_button_inside(x, y, exit_button_x, exit_button_y, button_width, button_height):
                print("---GOODBYE---")
                glutLeaveMainLoop()


# TOP LEFT AS ORIGIN
def mouse_convert_coordinate(x,y):
    global W_Width, W_Height

    a = x - W_Width/2
    b = W_Height/2 - y
    return a, b


def findzone(x1, y1, x2, y2):
    dx = x2-x1
    dy = y2-y1
    if abs(dx) > abs(dy):
        if dx > 0:
            if dy > 0:
                return 0
            else:
                return 7
        else:
            if dy > 0:
                return 3
            else:
                return 4
    else:
        if dx > 0:
            if dy > 0:
                return 1
            else:
                return 6
        else:
            if dy > 0:
                return 2
            else:
                return 5


def convertToZone0(zone, x, y):
    if 2 <= zone <= 5:
        x = -x
    if 4 <= zone <= 7:
        y = -y
    if zone == 1 or zone == 2 or zone == 5 or zone == 6:
        x, y = y, x

    return x, y


def originalZone(zone, x, y):
    if zone == 1 or zone == 2 or zone == 5 or zone == 6:
        x, y = y, x
    if 2 <= zone <= 5:
        x = -x
    if 4 <= zone <= 7:
        y = -y

    return x, y


def write_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def draw_line_raw(zone, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    dNE = 2 * (dy - dx)
    dE = 2 * dy

    x, y = x1, y1

    while x <= x2:
        cx, cy = originalZone(zone, x, y)
        write_pixel(cx, cy)
        x += 1
        if d > 0:
            y += 1
            d = d + dNE
        else:
            d = d + dE


def draw_line_8way(x1, y1, x2, y2):

    zone = findzone(x1, y1, x2, y2)
    x1, y1 = convertToZone0(zone, x1, y1)
    x2, y2 = convertToZone0(zone, x2, y2)
    draw_line_raw(zone, x1, y1, x2, y2)


def write_pixel_circle(x, y, c_x, c_y):
    write_pixel(x+c_x, y+c_y)


def circle_points(x, y, c_x, c_y):
    # Function to plot 8 symmetric points of a circle
    write_pixel_circle(x, y, c_x, c_y)
    write_pixel_circle(y, x, c_x, c_y)
    write_pixel_circle(y, -x, c_x, c_y)
    write_pixel_circle(x, -y, c_x, c_y)
    write_pixel_circle(-x, -y, c_x, c_y)
    write_pixel_circle(-y, -x, c_x, c_y)
    write_pixel_circle(-y, x, c_x, c_y)
    write_pixel_circle(-x, y, c_x, c_y)


def draw_circle(r, c_x, c_y):
    x = 0
    y = r
    d = 1 - r  # Decision variable
    circle_points(x, y, c_x, c_y)

    # for ZONE-1... 8-way done in circle_points
    while x < y:
        if d < 0:
            # Choose East
            d = d + 2 * x + 3
            x = x + 1
        else:
            # Choose South East
            d = d + 2 * x - 2 * y + 5
            x = x + 1
            y = y - 1

        circle_points(x, y, c_x, c_y)


def draw_buttons():

    global reset_button_x, reset_button_y, pause_button_x, pause_button_y, exit_button_x, exit_button_y, button_height, button_width

    # left arrow ( <- ) , Anchor (top left)
    glColor3f(0, 1, 1)
    draw_line_8way(reset_button_x, reset_button_y-button_height/2, reset_button_x + button_width, reset_button_y-button_height/2)
    draw_line_8way(reset_button_x, reset_button_y-button_height/2, reset_button_x + button_width/3, reset_button_y)    # up
    draw_line_8way(reset_button_x, reset_button_y-button_height/2, reset_button_x + button_width/3, reset_button_y-button_height)    # down

    pause_padding = button_width/5
    # pause (||) , Anchor (top left)
    glColor3f(1, 0.75, 0)
    if not paused:
        draw_line_8way(pause_button_x+pause_padding, pause_button_y, pause_button_x+pause_padding, pause_button_y-button_height)
        draw_line_8way(pause_button_x+button_width-pause_padding, pause_button_y, pause_button_x+button_width-pause_padding, pause_button_y - button_height)
    # Play ( |>) , Anchor (top left)
    else:
        draw_line_8way(pause_button_x, pause_button_y, pause_button_x, pause_button_y - button_height)   #left
        draw_line_8way(pause_button_x, pause_button_y, pause_button_x + button_width, pause_button_y - button_height/2)     # up
        draw_line_8way(pause_button_x, pause_button_y - button_height, pause_button_x + button_width, pause_button_y - button_height / 2)    #down

    # exit (X) , Anchor (top left)
    glColor3f(1, 0, 0)
    draw_line_8way(exit_button_x, exit_button_y, exit_button_x+button_width, exit_button_y-button_height)
    draw_line_8way(exit_button_x, exit_button_y-button_height, exit_button_x + button_width, exit_button_y)


def iterate():
    glViewport(0, 0, W_Width, W_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-W_Width/2, W_Width/2, -W_Height/2, W_Height/2, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()


def display():
    global delta_time
    t0 = time()  # start of measurement

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    global bullets, circles, shooter
    global shooter_color

    r, g, b = shooter_color
    glColor3f(r, g, b)
    draw_circle(shooter.radius, shooter.x, shooter.y)

    for circle in circles:
        r, g, b = circle.color
        glColor3f(r, g, b)
        draw_circle(circle.radius, circle.x, circle.y)

    for bullet in bullets:
        r, g, b = bullet.color
        glColor3f(r, g, b)
        draw_circle(bullet.radius, bullet.x, bullet.y)

    draw_buttons()
    glutSwapBuffers()

    t1 = time()  # end of measurement
    delta_time = t1-t0


def new_bullet():
    global bullets, shooter, bullet_size, bullet_color
    new_bul = Circle(bullet_size, shooter.x, shooter.y, bullet_color)
    bullets.append(new_bul)


# Value is a dummy variable only for timer function
def new_circle(value):
    global circles
    global circle_min_size, circle_max_size, circle_timer

    glutTimerFunc(circle_timer, new_circle, 0)  # Create a new circle 2 seconds later, value = 0

    # do not create if failed or paused
    if failed or paused:
        return

    circle_color = random_bright_color()
    circle_radius = get_random(circle_min_size, circle_max_size)
    circle_x = get_random(-W_Width / 2 + circle_padding, W_Width / 2 - circle_padding)
    circle_y = W_Height / 2 - circle_padding

    new_circ = Circle(circle_radius, circle_x, circle_y, circle_color)
    circles.append(new_circ)


def reset_game():
    global score, lives, paused, failed
    global shooter_color, default_shooter_color
    global shooter, bullets, circles, misses

    shooter_color = default_shooter_color
    score = 0
    lives = 3
    misses = 3

    shooter.x = 0

    bullets.clear()
    circles.clear()
    paused = False
    failed = False
    new_game()


def fail():
    global score, shooter_color
    global circles, bullets
    global failed

    shooter_color = (1, 0, 0)
    print('Game Over!')
    print('Final Score: ', score)
    failed = True

    # delete all bullets & circles
    circles.clear()
    bullets.clear()


def has_collided(circle1, circle2):
    dx = circle1.x - circle2.x
    dy = circle1.y - circle2.y
    return math.sqrt(dx*dx + dy*dy) < circle1.radius + circle2.radius


# Check for collisions between bullet and circles, or between shooter and circles, or circle passed screen
def check_circles():
    global circles, bullets, score, lives
    for circle in circles:
        for bullet in bullets:
            if has_collided(circle, bullet):
                circles.remove(circle)
                bullets.remove(bullet)
                score += 1
                print('Score:', score)

        if has_collided(circle, shooter):
            print('Got Hit by a Circle!')
            fail()

        elif circle.y < -W_Height/2 - circle.radius:
            lives -= 1
            print('Missed a circle!')
            if lives > 0:
                circles.remove(circle)
                print(f'Lives Remaining {lives}/3')
            else:
                fail()


# Check if bullet is out of screen without hitting Circles
def check_bullets():
    global bullets, misses
    for bullet in bullets:
        if bullet.y > W_Height/2 + bullet.radius:
            misses -= 1
            print('Bullet Missed!')
            if misses > 0:
                bullets.remove(bullet)
                print(f'Chances remaining {misses}/3')
            else:
                fail()


# MOVEMENTS OF CIRCLES & BULLETS
def movements():
    global circles, bullets
    global circle_speed, bullet_speed
    global delta_time

    for circle in circles:
        circle.y -= circle_speed * delta_time
    for bullet in bullets:
        bullet.y += bullet_speed * delta_time


def animate():
    # //codes for any changes in Models, Camera
    glutPostRedisplay()
    global failed, paused

    if not failed and not paused:
        movements()
        check_circles()
        check_bullets()


def new_game():
    print('---STARTING OVER---')
    print('Score:', 0)


glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # //Depth, Double buffer, RGB color

# glutCreateWindow("My OpenGL Program")
wind = glutCreateWindow(b"Shoot The Circles!")
print('---START---')
print('SCORE: 0')
new_circle(0)

glutDisplayFunc(display)  # display callback function
glutIdleFunc(animate)  # what you want to do in the idle time (when no drawing is occurring)

glutKeyboardFunc(keyboardListener)
#glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)

glutMainLoop()  # The main loop of OpenGL
