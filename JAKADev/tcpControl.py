import time
import numpy as np
import jkrc
import pygame

# Define some const
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PI = 3.1415926
# Move mode
ABS = 0
INCR = 1
SPEED = PI / 5
PORT = [0, 1, 3]
COORD_BASE = 0
COORD_JOINT = 1
COORD_TOOL = 2
Enable = 1
Disable = 0



# LIMIT = [PI,]

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
        self.x += 10

    def unindent(self):
        self.x -= 20


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
print(ret)

# 关节空间非线性滤波
robot.servo_move_use_joint_NLF(max_vr=2, max_ar=2, max_jr=4)

# 开启servo控制模式
robot.servo_move_enable(Enable)

# Init the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Check for original pos
checked = 0

# Set the switch to define the control mode
# 0:J1J2J3, 1:J4J5J6
button = 0
mode = 0

robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, SPEED)

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
    pos = [joystick.get_axis(i) for i in PORT]
    print(pos)

    button_0 = button
    button = joystick.get_button(13)

    if button == 0 and button_0 == 1:
        mode = 1 - mode
        textPrint.print(screen, "Switch mode!")

    textPrint.print(screen, "Mode {}".format(mode))

    if mode == 0:
        joint_pos = pos + [0, 0, 0]
    else:
        joint_pos = [0, 0, 0] + pos

    joint_pos = [i * 100 for i in joint_pos]

    if any(joint_pos):
        ret = robot.linear_move(joint_pos, 1, 1, 50)
        print(ret)
    else:
        continue

    # ret = robot.jog(joint_pos, INCR, 1, SPEED)

    for i in range(len(pos)):
        textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, pos[i]))

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
robot.logout()
