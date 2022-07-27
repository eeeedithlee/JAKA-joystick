# JAKA-joystick
controlling minicobo by joystick
推荐IDE：PyCharm
## 使用方法
1. 把手柄接上
   如果是首次使用，建议先运行`joystickControl.py`,这个脚本会帮助你了解手柄每个按键对应的端口号。
       
2. 运行ctrl_servo.py

## 代码重点说明
机械臂限位： `LIMIT = (np.array([355, 120, 125, 355, 115, 355]) / 180 * PI).tolist()`

定义手柄输入端口(不清楚对应端口的话去运行joystickControl.py)：`PORT = [0, 1, 3]`

屏幕输出类：`class TextPrint`

按钮类：`class Button(object)`

判断是否a数组中每个数都大于b数组：`_all_larger(a, b)`

让机械臂回到初始位置：`robot.joint_move([0, 0, PI / 2, 0, PI / 2, 0], 0, 1, SPEED)`

