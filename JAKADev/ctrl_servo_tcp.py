import time
import numpy as np
import jkrc
import pygame

# Define some const
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (244, 96, 108)
BLUE = (25, 202, 173)
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

LIMIT = (np.array([355, 120, 125, 355, 115, 355]) / 180 * PI).tolist()


# This is a simple class that will help us print to the screen
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 100)

    def print(self, screen, textString, c=BLACK):
        textBitmap = self.font.render(textString, True, c)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 100

    def indent(self):
        self.x += 20

    def unindent(self):
        self.x -= 20


def _all_larger(a, b):
    c = np.array(a) < np.array(b)
    print(c)
    if any(c):
        return False
    else:
        return True


pygame.init()

# Set the width and height of the screen [width,height]
infoObject = pygame.display.Info()
size = [infoObject.current_w, infoObject.current_h]
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

robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, SPEED)

# 关节空间非线性滤波
# robot.servo_move_use_joint_NLF(max_vr=2, max_ar=2, max_jr=4)

# 关节空间一阶低通滤波
robot.servo_move_use_joint_LPF(0.5)

# 开启servo控制模式
robot.servo_move_enable(Enable)
print("Enable servo")
print(ret)
time.sleep(0.1)

# Init the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Check for original pos
checked = 0

# Set the switch to define the control mode
# 0:J1J2J3, 1:J4J5J6
button = 0
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
    pos = [joystick.get_axis(i) for i in PORT]

    # y轴映射反向，更符合直觉
    pos[1] = -pos[1]
    print(pos)

    #判断是否切换mode
    button_0 = button
    button = joystick.get_button(13)

    if button == 0 and button_0 == 1:
        mode = 1 - mode
        textPrint.print(screen, "Switch mode!")


    if mode == 0:
        textPrint.print(screen, "Mode 0: Translation mode")
        joint_p = (np.array(pos) * 3).tolist() + [0, 0, 0]
    else:
        textPrint.print(screen, "Mode 1: Rotation mode")
        joint_p = [0, 0, 0] + (np.array(pos) / 50).tolist()

    textPrint.print(screen, "--------------------------------------")

    joint_p_np = np.array(joint_p)

    ret = robot.get_joint_position()
    real_pos = ret[1]
    # for i in range(len(real_pos)):
    #     textPrint.print(screen, "Robot joint {}: {}".format(i, real_pos[i]))

    if _all_larger(LIMIT, real_pos):# 判断是否到限位
        if np.max(np.abs(joint_p_np)) > 0.05 and mode == 0:
            ret = robot.servo_p(cartesian_pose=joint_p, move_mode=INCR)
            print("servo done,return value is:{}".format(ret))
        elif np.max(np.abs(joint_p_np)) > 0.005 and mode == 1:
            ret = ret = robot.servo_p(cartesian_pose=joint_p, move_mode=INCR)
            print("servo done,return value is:{}".format(ret))
        else:
            pass
    else:
        textPrint.print(screen, "WARNING! Joint is out of range!", RED)

    # 发送指令的周期为8ms
    time.sleep(0.008)

    ret = robot.get_tcp_position()
    real_tcp = ret[1]

    if mode == 0:
        textPrint.print(screen, "x coordinate: {:>6.3f} mm".format(real_tcp[0]), BLUE)
        textPrint.print(screen, "y coordinate: {:>6.3f} mm".format(real_tcp[1]), BLUE)
        textPrint.print(screen, "z coordinate: {:>6.3f} mm".format(real_tcp[2]), BLUE)
    else:
        textPrint.print(screen, "rx coordinate: {:>6.3f} mm".format(real_tcp[3]), BLUE)
        textPrint.print(screen, "ry coordinate: {:>6.3f} mm".format(real_tcp[4]), BLUE)
        textPrint.print(screen, "rz coordinate: {:>6.3f} mm".format(real_tcp[5]), BLUE)

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
robot.servo_move_enable(Disable)
textPrint.print(screen, "Disable servo")
pygame.quit()
robot.logout()
