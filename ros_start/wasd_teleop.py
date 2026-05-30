import sys 
import tty
import time
import select
import termios
import rclpy 
from rclpy.node import Node

#対応するinterfaceをimport topic info "トピック名で見れる"
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class WASD_TELEOP(Node):
    def __init__(self):
        super().__init__("wasd_teleop")
        self.publisher = self.create_publisher(Twist, "sobit_pro/cmd_vel", 10)
        self.subscription = self.create_subscription(Odometry, "sobit_pro/odom", self.sub_callback, 10)
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.curr_vel = 0.0
        self.curr_ang = 0.0
        self.vel_step = 0.05
        self.ang_step = 0.05
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        new_settings = termios.tcgetattr(sys.stdin)
        new_settings[3] = new_settings[3] & ~termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def sub_callback(self, msg):
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y
        self.get_logger().info(f'Position: x={self.pos_x:.2f}, y={self.pos_y:.2f}')
        self.get_logger().info(f'Position: x={self.pos_x:.2f}, y={self.pos_y:.2f}')
        
#実際に全部を実行するmain関数
def main(args=None):
    rclpy.init(args=args)
    node = WASD_TELEOP()

    while rclpy.ok():
        msg = Twist()
        key = node.get_key()
        if key == 'q':
            node.get.logger().info("終了します")
            break
        elif key == 'w':
            node.curr_vel += node.vel_step
        elif key == 's':
            node.curr_vel -= node.vel_step
        elif key == 'a':
            node.curr_ang += node.ang_step
        elif key == 'd':
            node.curr_ang -= node.ang_step
        else:
            node.curr_vel *= 0.9
            node.curr_ang *= 0.9

        msg.linear.x = node.curr_vel
        msg.angular.z = node.curr_ang
        rclpy.spin_once(node, timeout_sec=0)
        node.publisher.publish(msg)
        time.sleep(0.05)

    stop_msg = Twist()
    node.publisher.publish(stop_msg)
    node.destroy_node()
    rclpy.shutdown()

#直接実行された場合main関数呼び出し
if __name__ == '__main__':
    main()
