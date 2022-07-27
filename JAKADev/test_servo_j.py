# -*- coding: utf-8 -*-
import sys
import time
import jkrc

PI = 3.1415926

ABS = 0  # 绝对运动
INCR = 1  # 增量运动
Enable = True
Disable = False

robot = jkrc.RC("10.5.5.100")  # 返回一个机器人对象
robot.login()  # 登录
robot.power_on()  # 上电
robot.enable_robot()

robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, PI/2)
#robot.servo_move_use_joint_LPF(0.5)
robot.servo_move_use_joint_NLF(2,2,4)
#robot.servo_move_use_joint_MMF(max_buf=20 , kp=0.2 , kv=0.4 ,ka=0.2)#不能处理突变？
robot.servo_move_enable(Enable)  # 进入位置控制模式
time.sleep(0.1)
print("enable")
# for i in range(10):
#     robot.servo_j(joint_pos=[0.00001*i*i, 0, 0, 0, 0, 0.00001*i*i], move_mode=INCR)  #
#     time.sleep(0.008)
for _ in range(2000):
    robot.servo_j(joint_pos=[], move_mode=INCR)  #
    time.sleep(0.008)
# print("turn back")
# for i in range(100):
#     robot.servo_j(joint_pos=[-0.00001*i*i, 0, 0, 0, 0, -0.00001*i*i], move_mode=INCR)
#     time.sleep(0.008)
robot.servo_move_enable(Disable)  # 退出位置控制模式
print("disable")
robot.logout()  # 登出
