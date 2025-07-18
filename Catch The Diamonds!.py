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
failed = False
paused = False

# PUCK
puck_width, puck_height = 50, 50
puck_color = random_bright_color()
puck_speed = 100
limit_speed = 250
puck_padding = 25   # so it is not generated at the edge of window
puck_x = get_random(-W_Width/2+puck_padding, W_Width/2-puck_padding)
puck_y = W_Height / 2 - puck_padding

# CATCHER
catcher_width, catcher_height = 100, 20
default_catcher_color = catcher_color = (0.6, 1, 1)
catcher_speed = 4 * W_Width
catcher_x = 0   # centered
catcher_y = -W_Height/2 + 20

# BUTTONS
button_width = 50
button_height = 50
button_padding = 15
reset_button_x = -W_Width/2 + button_padding
pause_button_x = 0-button_width/2
exit_button_x = W_Width/2 - button_width - button_padding
reset_button_y = pause_button_y = exit_button_y = W_Height/2 - button_padding

delta_time = 0.01

def specialKeyListener(key, x, y):
    global W_Width, W_Height
    global catcher_x, catcher_y, catcher_width, catcher_height, catcher_speed
    global delta_time

    if paused or failed:
        return

    #padding = 10

    glutPostRedisplay()
    if key == GLUT_KEY_RIGHT:
        if catcher_x + catcher_width/2 < W_Width/2:
            catcher_x += catcher_speed * delta_time
    if key == GLUT_KEY_LEFT:
        if catcher_x - catcher_width/2 > -W_Width/2:
            catcher_x -= catcher_speed * delta_time

    # if key==GLUT_KEY_PAGE_UP:

    # if key==GLUT_KEY_PAGE_DOWN:

    # case GLUT_KEY_INSERT:
    #
    #
    # case GLUT_KEY_HOME:
    #
    # case GLUT_KEY_END:
    #


# TOP LEFT anchor point of button
def mouse_button_inside(mouse_x, mouse_y, button_x, button_y, width, height):
    return button_x < mouse_x < button_x + width and button_y > mouse_y > button_y - height
# TOP LEFT AS ORIGIN
def mouse_convert_coordinate(x,y):
    global W_Width, W_Height

    a = x - W_Width/2
    b = W_Height/2 - y
    return a, b


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




def findzone(x1, y1, x2, y2):
    dx = x2-x1
    dy = y2-y1
    if abs(dx) > abs(dy): # 0 3 4 7
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
    else: #1 2 5 6
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
    if 2 <= zone <= 5: #2 3 4 5
        x = -x  
    if 4 <= zone <= 7: # 4 5 6 7
        y = -y
    if zone == 1 or zone == 2 or zone == 5 or zone == 6: #dy large
        x, y = y, x #making dx large

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



def draw_puck(x, y):
    global puck_width, puck_height
    # let's draw in clockwise direction

    # ANCHOR (CENTER)
    draw_line_8way(x, y+puck_height/2, x+puck_width/2, y)    # top right
    draw_line_8way(x-puck_width/2, y, x, y+puck_height/2)    # top left
    draw_line_8way(x+puck_width/2, y, x, y-puck_height/2)    # bottom right
    draw_line_8way(x, y-puck_height/2, x-puck_width/2, y)    # bottom left


def draw_catcher(x, y):
    global catcher_width, catcher_height
    

    # ANCHOR (CENTER)
    bottom_padding = catcher_width/8
    draw_line_8way(x-catcher_width/2, y+catcher_height/2, x+catcher_width/2, y+catcher_height/2)    # top
    draw_line_8way(x-catcher_width/2 + bottom_padding, y-catcher_height/2, x+catcher_width/2 - bottom_padding, y-catcher_height/2)    # bottom
    draw_line_8way(x-catcher_width/2, y+catcher_height/2, x-catcher_width/2 + bottom_padding, y-catcher_height/2)    # left
    draw_line_8way(x+catcher_width/2, y+catcher_height/2, x+catcher_width/2 - bottom_padding, y-catcher_height/2)    # right


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
        draw_line_8way(pause_button_x, pause_button_y, pause_button_x + button_width, pause_button_y - button_height/2)      # up
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

    global puck_x, puck_y, puck_color
    global catcher_x, catcher_y, catcher_color

    r, g, b = puck_color
    glColor3f(r, g, b)
    draw_puck(puck_x, puck_y)

    r, g, b = catcher_color
    glColor3f(r, g, b)
    draw_catcher(catcher_x, catcher_y)

    draw_buttons()

    glutSwapBuffers()

    t1 = time()  # end of measurement
    delta_time = t1-t0

def new_puck():
    global puck_x, puck_y, puck_color
    puck_color = random_bright_color()
    puck_x = get_random(-W_Width / 2 + puck_padding, W_Width / 2 - puck_padding)
    puck_y = W_Height / 2 - puck_padding


def capture_puck():
    global puck_speed, limit_speed
    global score

    new_puck()
    score += 1

    if puck_speed * 1.1 < limit_speed:
        puck_speed *= 1.1
    else:
        puck_speed = limit_speed

    print('Score:', score)


def reset_game():
    global score, paused, failed, catcher_color, default_catcher_color
    global catcher_x, catcher_y, puck_speed

    new_puck()
    catcher_color = default_catcher_color
    score = 0

    catcher_x = 0
    puck_speed = 100

    paused = False
    failed = False
    new_game()


def fail():
    global score, catcher_color
    global puck_y
    global failed

    catcher_color = (1, 0, 0)
    print('Game Over!')
    print('Final Score: ', score)
    failed = True

    # out of sight
    puck_y = -W_Height


# box1 is pucker, box2 is catcher
def has_collided(box1, box2):
    return (box1.x - box1.width/2 < box2.x + box2.width/2 and box1.x + box1.width > box2.x - box2.width/2
            and box1.y - box1.height/2 < box2.y + box2.height/2 and box1.y + box1.height > box2.y - box2.height/2)


def animate():
    # //codes for any changes in Models, Camera
    glutPostRedisplay()
    global puck_x, puck_y, puck_width, puck_height, catcher_x, catcher_y, catcher_width, catcher_height, puck_speed
    global failed, paused
    global delta_time

    # print(delta_time)
    if not failed and not paused:
        puck_y -= puck_speed * delta_time

        box1 = Box(puck_x, puck_y, puck_width, puck_height)
        box2 = Box(catcher_x, catcher_y, catcher_width, catcher_height)
        if has_collided(box1, box2):
            capture_puck()

        if puck_y < -W_Height/2:
            fail()


def new_game():
    print('---STARTING OVER---')
    print('Score:', 0)



glutInit()
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  # //Depth, Double buffer, RGB color

# glutCreateWindow("My OpenGL Program")
wind = glutCreateWindow(b"Catch the Diamonds!")
print('---START---')
print('SCORE: 0')

glutDisplayFunc(display)  # display callback function
glutIdleFunc(animate)  # what you want to do in the idle time (when no drawing is occuring)

glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)

glutMainLoop()  # The main loop of OpenGL
