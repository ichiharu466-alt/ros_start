import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

#class内のdefで変数を共有することができる
class PID_Control(Node):
   def __init__(self):
      super().__init__("pid_control_node")

      #publisher, subscription, timerの設定
      self.publisher = self.create_publisher(Twist, "sobit_pro/cmd_vel", 10)
      self.subscription = self.create_subscription(Odometry, "sobit_pro/odom", self.odom_callback, 10)
      self.timer = self.create_timer(0.5, self.timer_callback)
      self.pos_x = 0.0
      
      #偏差の計算用
      self.target_x = 5.0
      self.pos_x = 0.0

      # 各ゲインの設定
      self.kp = 0.0
      self.ki = 0.01
      self.kd = 0.5

      #計算に必要な変数（callback時に値が初期化されないように）
      self.integral_sum = 0.0 
      self.prev_pos = 0.0 
      self.last_time = self.get_clock().now() 

   def odom_callback(self, msg):
      self.pos_x = msg.pose.pose.position.x

   def timer_callback(self):
      # ローカル変数の定義
      current_time = self.get_clock().now()

      #ナノ秒に変換
      dt = (current_time - self.last_time).nanoseconds / 1e9

      #0除算回避　dt == 0にしない理由はfloatの計算で誤差が起きるため
      if dt < 0.001:
         return

      #偏差の計算
      deviation = self.target_x - self.pos_x

      # Pの計算
      p_val = deviation * self.kp

      # Iの計算
      self.integral_sum +=  deviation * dt
      self.integral_sum = max(min(self.integral_sum, 1.0), -1.0)
      i_val = self.integral_sum * self.ki

      # Dの計算
      d_val = (self.pos_x - self.prev_pos) / dt * -self.kd

      #最終的な速度の計算
      result = p_val + i_val + d_val

      #確認用のログ
      self.get_logger().info(f"現在の位置:{self.pos_x:.3f}")
      self.get_logger().info(f"現在の速度:{result}")
      self.get_logger().info(f"d_val:{d_val}")

      # 値の更新
      self.last_time = current_time
      self.prev_pos = self.pos_x
      
      #publish処理
      msg = Twist()
      msg.linear.x = result
      self.publisher.publish(msg)

#main関数で一連の流れを実行
def main():
   rclpy.init()
   node = PID_Control()
   rclpy.spin(node)
   node.destroy_node()
   rclpy.shutdown()

if __name__ == "__main__":
   main()

# ーーーーーーー比例ゲイン実験ーーーーーーーーーー
# 一回目比例ゲイン0.5（完璧）
# 二回目比例ゲイン1.0（完璧）
# 三回目比例ゲイン2.0（ほんの少し通り過ぎた）
# 四回目比例ゲイン4.0（ほぼ三回目と変わらない）
# 五回目比例ゲイン2.0 ボディの重量を変更（あんまり変化なし）
# 六回目比例ゲイン3.0 設定されていた制限を解除
# 七回目比例ゲイン10.0 想像通りの結果に

# 多分４回目に関してはロボットの設定の最大速度を超えている

# ーーーーーーー微分ゲイン実験ーーーーーーーーーー
# 一回目微分ゲイン0.5（完璧)


