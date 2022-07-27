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
SPEED = PI / 2
PORT = [0, 1, 3]
COORD_BASE = 0
COORD_JOINT = 1
COORD_TOOL = 2
Enable = 1
Disable = 0

LIMIT = (np.array([355, 120, 125, 355, 115, 355]) / 180 * PI).tolist()

MODE_TEXT = ["Mode 1: Translation mode", "Mode 2: Rotation mode", "Mode 3: Controlling J1 J2 J3",
             "Mode 4: Controlling J4 J5 J6"]


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


class Button(object):
    # 按钮类
    def __init__(self, text, color, x=400, y=700, **kwargs):
        self.font = pygame.font.Font(None, 80)
        self.surface = self.font.render(text, True, color)

        self.WIDTH = self.surface.get_width()
        self.HEIGHT = self.surface.get_height()

        self.x = x
        self.y = y

    def display(self, screen):
        screen.blit(self.surface, (self.x, self.y))

    def check_click(self, position):
        x_match = self.x < position[0] < self.x + self.WIDTH
        y_match = self.y < position[1] < self.y + self.HEIGHT

        if x_match and y_match:
            return True
        else:
            return False


def _all_larger(a, b):
    # 判断是否a数组中每个数都大于b数组
    c = np.array(a) < np.array(b)
    if any(c):
        return False
    else:
        return True


pygame.init()

# Set the width and height of the screen [width,height]
size = [1920, 1080]
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

screen.fill(WHITE)
textPrint.print(screen, MODE_TEXT[0])

# Init the robot
robot = jkrc.RC("10.5.5.100")
ret = robot.login()
ret = robot.power_on()
ret = robot.enable_robot()

robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, SPEED)

# 关节空间非线性滤波
# robot.servo_move_use_joint_NLF(max_vr=4, max_ar=16, max_jr=32)

# 关节空间一阶低通滤波
robot.servo_move_use_joint_LPF(0.3)

# Init the joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Check for original pos
checked = 0

# Set the switch to define the control mode
# 0:J1J2J3, 1:J4J5J6
button = 0
mode = 0

# Set exit button
exit_button = Button('Exit', RED, 500, 800)
reset_button = Button('Exit', RED, 500, 800)

# 开启servo控制模式
robot.servo_move_enable(Enable)
print("Enable servo")
print(ret)
time.sleep(0.05)

# -------- Main Program Loop -----------
while not done:
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    if pygame.mouse.get_pressed()[0]:
        if exit_button.check_click(pygame.mouse.get_pos()):
            break
        if reset_button.check_click(pygame.mouse.get_pos()):
            robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, SPEED)
            robot.servo_move_enable(Enable)
            print("Enable servo")
            print(ret)
            time.sleep(0.05)

    # 绘制UI
    screen.fill(WHITE)
    textPrint.reset()

    # 提取0，1，3号接口数值
    pos = [joystick.get_axis(i) for i in PORT]

    # 判断是否切换mode
    button_0 = button
    button = joystick.get_button(13)

    if button == 0 and button_0 == 1:
        mode = (mode + 1) % 4
        # textPrint.print(screen, "Switch mode!")

    # 根据mode调整控制参数
    if mode == 0:
        joint_p = (np.array(pos) * 5).tolist() + [0, 0, 0]
    elif mode == 1:
        joint_p = [0, 0, 0] + (np.array(pos) / 50).tolist()
    elif mode == 2:
        joint_p = (np.array(pos) / 50).tolist() + [0, 0, 0]
    elif mode == 3:
        joint_p = [0, 0, 0] + (np.array(pos) / 50).tolist()

    textPrint.print(screen, MODE_TEXT[mode])

    textPrint.print(screen, "--------------------------------------")

    joint_p_np = np.array(joint_p)

    ret = robot.get_joint_position()
    real_pos = ret[1]

    # 控制舵机运动
    if _all_larger(LIMIT, real_pos):
        if np.max(np.abs(joint_p_np)) > 0.05 and mode == 0:
            ret = robot.servo_p(cartesian_pose=joint_p, move_mode=INCR)
            print("mode{},return value is:{}".format(mode, ret))
        elif np.max(np.abs(joint_p_np)) > 0.005 and mode == 1:
            ret = robot.servo_p(cartesian_pose=joint_p, move_mode=INCR)
            print("mode{},return value is:{}".format(mode, ret))
        elif np.max(np.abs(joint_p_np)) > 0.005 and (mode == 2 or mode == 3):
            ret = robot.servo_j(joint_pos=joint_p, move_mode=INCR)
            print("mode{},return value is:{}".format(mode, ret))
        else:
            # print("cant move, mode:{}, {}".format(mode, np.max(np.abs(joint_p_np))))
            pass
    else:
        textPrint.print(screen, "WARNING! Joint is out of range!", RED)

    # 发送指令的周期为8ms
    time.sleep(0.008)

    ret = robot.get_tcp_position()
    real_tcp = ret[1]

    # 绘制文本
    if mode == 0:
        textPrint.print(screen, "x coordinate: {:>6.3f} mm".format(real_tcp[0]), BLUE)
        textPrint.print(screen, "y coordinate: {:>6.3f} mm".format(real_tcp[1]), BLUE)
        textPrint.print(screen, "z coordinate: {:>6.3f} mm".format(real_tcp[2]), BLUE)
    elif mode == 1:
        textPrint.print(screen, "rx coordinate: {:>6.3f} mm".format(real_tcp[3]), BLUE)
        textPrint.print(screen, "ry coordinate: {:>6.3f} mm".format(real_tcp[4]), BLUE)
        textPrint.print(screen, "rz coordinate: {:>6.3f} mm".format(real_tcp[5]), BLUE)
    elif mode == 2:
        for i in range(len(pos)):
            textPrint.print(screen, "Joint {} value: {:>6.3f} rad".format(i + 1, real_pos[i]), BLUE)
    elif mode == 3:
        for i in range(len(pos)):
            textPrint.print(screen, "Joint {} value: {:>6.3f} rad".format(i + 4, real_pos[i + 3]), BLUE)

    # 判断是否退出或重置
    if exit_button.check_click(pygame.mouse.get_pos()):
        exit_button = Button('Exit', BLACK, 200, 800)
    else:
        exit_button = Button('Exit', RED, 200, 800)
    if reset_button.check_click(pygame.mouse.get_pos()):
        reset_button = Button('Reset', BLACK, 500, 800)
    else:
        reset_button = Button('Reset', RED, 500, 800)

    exit_button.display(screen)
    reset_button.display(screen)

    # 所有绘制UI的语句应当在此之前

    # 刷新UI
    pygame.display.flip()

    # 20帧每秒
    clock.tick(20)

# 关闭UI并退出
robot.servo_move_enable(Disable)
print("Disable servo")
pygame.quit()
robot.logout()
