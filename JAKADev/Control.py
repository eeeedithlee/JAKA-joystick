import time

import jkrc
import pygame
import numpy as np

# Define some const
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PI = 3.1415926
# Move mode
ABS = 0
INCR = 1
SPEED = 0.1


# This is a simple class that will help us print to the screen
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 40)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 30

    def indent(self):
        self.x += 20

    def unindent(self):
        self.x -= 20


# 读入目标位置和控制模式，用jog控制
def _move_control(position, control_mode, move_mode, jog_vel, robot_controlled):
    rob = robot_controlled
    if control_mode == 0:
        _pos = position[:] + [0, 0, 0]
    else:
        _pos = [0, 0, 0] + position[:]
    for i in range(5):
        rob.jog(i, move_mode, 1, pos[i], SPEED)
        time.sleep(5)

    return _pos


def read_coord(_position):
    del _position[2]
    return _position


pygame.init()

# Set the width and height of the screen [width,height]
size = [800, 800]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Controller")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# Init the robot
robot = jkrc.RC("10.5.5.100")
ret = robot.login()
ret = robot.power_on()
ret = robot.enable_robot()

# Init the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Check for original pos
checked = 0
pos_0 = [joystick.get_axis(i) for i in range(4)]

# Set the switch to define the control mode
# 0:J1J2, 1:J3J4,2:J5J6
mode = 0

# -------- Main Program Loop -----------
while not done:
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    # DRAWING STEP
    screen.fill(WHITE)
    textPrint.reset()

    # 提取0，1，3号接口数值
    pos = read_coord([(joystick.get_axis(i) - pos_0[i]) / 10 for i in range(4)])
    print(pos)

    button = joystick.get_button(13)
    if button == 1:
        mode = 1 - mode
        textPrint.print(screen, "Switch mode!")

    textPrint.print(screen, "Mode {}".format(mode))

    _move_control(pos, mode, INCR, SPEED, robot)
    # ret = robot.joint_move(joint_pos, INCR, 1, SPEED)

    for i in range(4):
        textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, pos[i]))

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    # clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
robot.logout()
