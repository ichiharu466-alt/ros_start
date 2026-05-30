import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

#class内のdefで変数を共有することができる
class OneMeterStop(Node):
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

        if self.pos_x < 5.0:
            msg.linear.x = 0.05
            self.get_logger().info(f"移動中: {self.pos_x:.3f}")
        else:
            msg.linear.x = 0.0  
            self.get_logger().info(f"停止中: {self.pos_x:.3f}")

        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = OneMeterStop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

#コールバックはTopicが届いたら何をするか決めること