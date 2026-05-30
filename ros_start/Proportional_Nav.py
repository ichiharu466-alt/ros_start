import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

#class内のdefで変数を共有することができる
class Propotional_Nav(Node):
    def __init__(self):
        super().__init__("one_meter_node")

        self.publisher = self.create_publisher(Twist, "sobit_pro/cmd_vel", 10)
        self.subscription = self.create_subscription(Odometry, "sobit_pro/odom", self.odom_callback, 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.pos_x = 0.0

    def odom_callback(self, msg):
        self.pos_x = msg.pose.pose.position.x

    def timer_callback(self):



        msg = Twist()
        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = Propotional_Nav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()


# import math
# current_angle = math.atan2(target_y, target_x)

# dt = 0.05 

# diff_angle = current_angle - self.prev_angle
# if diff_angle > math.pi:
#     diff_angle -= 2 * math.pi
# elif diff_angle < -math.pi:
#     diff_angle += 2 * math.pi
    
# los_rate = diff_angle / dt

# N = 3.0
# cmd_yaw_rate = N * los_rate

# self.prev_angle = current_angle

# return cmd_yaw_rate