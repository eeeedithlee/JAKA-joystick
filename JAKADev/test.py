import time
import jkrc
import pygame


def example():
    COORD_BASE = 0  # 基坐标系
    COORD_JOINT = 1  # 关节空间
    COORD_TOOL = 2  # 工具坐标系
    ABS = 0  # 绝对运动
    INCR = 1  # 增量运动
    cart_x = 0  # x方向
    cart_y = 1  # y方向
    cart_z = 2  # z方向
    cart_rx = 3  # rx方向
    cart_ry = 4  # ry方向
    cart_rz = 5  # rz方向
    # ip = jkrc.get_controller_ip()

    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    button = joystick.get_button(13)
    print(button)
    time.sleep(1)
    print(button)



    robot = jkrc.RC("10.5.5.100")
    ret = robot.login()
    print(ret)
    ret = robot.power_on()
    print(ret)
    ret = robot.enable_robot()
    print(ret)
    pos = robot.get_tcp_position()
    print(pos)
    PI = 3.1415926
    while True:
        vel = joystick.get_axis(0)
        print(vel)
        button = joystick.get_button(13)
        print(button)
        # robot.jog(aj_num=cart_z, move_mode=INCR, coord_type=COORD_BASE, jog_vel=vel, pos_cmd=10)
        # print(ret)
        time.sleep(0.1)
        print("awake")
    # tcp_pos = [10, 0, 0, 0, 0, 0]
    # ret = robot.linear_move(tcp_pos,0,1,10)


