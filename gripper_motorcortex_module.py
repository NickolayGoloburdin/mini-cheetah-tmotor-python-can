import motorcortex
from src.motor_driver.canmotorlib import CanMotorController
import numpy as np
import time

def setZeroPosition(motor):
    pos, _, _ = motor.set_zero_position()
    while abs(np.rad2deg(pos)) > 0.5:
        pos, vel, curr = motor.set_zero_position()
        print("Position: {}, Velocity: {}, Torque: {}".format(np.rad2deg(pos), np.rad2deg(vel), curr))

def moveTo(start, end, vel, motor_controller: CanMotorController, torque_min=None, torque_max=None):
    t_exec = abs(end-start)*3/2/vel

    def getTargetPose(time, vel_sign):
        
        if time <= t_exec/3:
            pos = start + vel_sign*3/2*vel/t_exec*time**2
        elif time <= t_exec * 2 / 3:
            pos = start + vel_sign*vel/6 * t_exec + vel_sign*vel*(time - t_exec/3)
        elif time <= t_exec:
            pos = start + vel_sign*vel*(time - 2*t_exec/3) - 3*vel_sign*vel/2/t_exec*(time - 2*t_exec/3)**2 + vel_sign*vel*t_exec/2
        else:
            pos = end

        return pos
    
    sign = abs(end - start) / (end - start)

    start_time = time.time()
    cur_time = start_time
    torque_lim_counter = 0
    # pose_ar = []
    # time_ar = []
    while cur_time - start_time <= t_exec:
        cur_time = time.time()
        dt = cur_time - start_time
        pos = getTargetPose(dt, sign)
        try:
            c_pos, c_vel, c_curr = motor_controller.send_deg_command(pos, 0, 50, 1, 0)
            if (not torque_min is None):
                if(torque_min > c_curr or torque_max < c_curr):
                    if (torque_lim_counter > 5):
                        print("Torque limiter: {0}".format(c_curr))
                        return
                    else:
                        torque_lim_counter+=1
                else:
                    torque_lim_counter = 0

            print("Position: {}, Velocity: {}, Torque: {}".format(c_pos, c_vel,
                                                                c_curr))
        except:
            pass
    
    # plt.plot(time_ar, pose_ar)
    # plt.show()
    c_pos, c_vel, c_curr =motor_controller.send_deg_command(end, 0, 50, 1, 0)
    print("Position: {}, Velocity: {}, Torque: {}".format(c_pos, c_vel,
                                                        c_curr))
    return c_pos

def can_drive():
    motor_id = 0x01
    motor_controller = CanMotorController('/dev/ttyUSB0', motor_id)

    # startTime = time.perf_counter()

    pos, vel, curr = motor_controller.enable_motor()

    # pos, vel, curr = motor_controller.send_deg_command(0, 0, 0, 0, 0)
    print("Initial Position: {}, Velocity: {}, Torque: {}".format(np.rad2deg(pos), np.rad2deg(vel),
                                                                    curr))

    # endTime = time.perf_counter()
    # print("Time for One Command: {}".format(endTime - startTime))
    time.sleep(1)

    # setZeroPosition(motor_controller)


    c_pos = np.rad2deg(pos)
    c_pos = moveTo(c_pos, 25, 6, motor_controller, torque_min=-2, torque_max=2.0)

    # for i in range(100):
    #     time.sleep(1)
    #     c_pos = moveTo(c_pos, 70, 25, motor_controller)
    #     time.sleep(1)
    #     c_pos = moveTo(c_pos, 25, 25, motor_controller)

    # pos, vel, curr = motor_controller.disable_motor()
    # print("Final Position: {}, Velocity: {}, Torque: {}".format(np.rad2deg(pos), np.rad2deg(vel), curr))

if __name__=="__main__":
    parameter_tree = motorcortex.ParameterTree()
    motorcortex_types = motorcortex.MessageTypes()

    try:
        req, sub = motorcortex.connect('wss://192.168.1.4:5568:5567', motorcortex_types, parameter_tree,
                                        timeout_ms=1000, certificate="mcx.cert.pem",
                                        login="admin", password="vectioneer")

        print("Request connection is etablished")
    except Exception as e:
        print(f"Failed to establish connection: {e}")
        exit()