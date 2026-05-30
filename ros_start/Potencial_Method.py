import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from tf_transformations import euler_from_quaternion
import math

class Potential_Method(Node):
    def __init__(self):
        super().__init__("potential_nav_node")

        #publisher, subscriber, timerの設定
        self.publisher = self.create_publisher(Twist, "/sobit_pro/cmd_vel", 10)
        self.create_subscription(Odometry, "/sobit_pro/odom", self.odom_callback, 10)
        self.create_subscription(LaserScan, "/sobit_pro/scan", self.scan_callback, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

        # 現在地の取得と目標値の設定
        self.pos_x, self.pos_y = 0.0, 0.0
        self.goal_x, self.goal_y = 5.0, -1.0
        self.yaw = 0.0
        self.obstacles = []

        # 速度平滑化
        self.vx = 0.0
        self.vy = 0.0

        #設定するパラメーターの値　A:引力の強さ　B:斥力の強さ　m:斥力の勾配の変化率
        self.A, self.B, self.m = 0.5, 0.15, 2.0 

    def odom_callback(self, msg):

        #変数にodometory情報を代入
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y

        # quaternion取得
        q = msg.pose.pose.orientation

        # yawへ変換
        _, _, self.yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])

        self.get_logger().info(f"x:{self.pos_x:.2f} y:{self.pos_y:.2f} yaw:{self.yaw:.2f}")

    def scan_callback(self, msg):
        # データを領域の分割（両側に壁合った時に分割してないと重心が中央になってしまう）
        num_sectors = 8  
        sectors = [[] for _ in range(num_sectors)]
        
        # 点群をセクターに振り分ける
        for i, r in enumerate(msg.ranges):

            # 範囲内かつ信頼できるデータのみ抽出
            if msg.range_min < r < 2.0:
                angle = msg.angle_min + i * msg.angle_increment
                
                # angle + math.pi -pi < angle < pi を 0 < angle <2pi　整数の角度に変換
                # atan2を使って角度を正規化
                sector_idx = int((angle + math.pi) / (2 * math.pi / num_sectors)) % num_sectors
                
                # 極座標からデカルト座標への変換
                x = r * math.cos(angle)
                y = r * math.sin(angle)

                # デカルト座標に変換後リストに追加
                sectors[sector_idx].append((x, y))

        for sector in sectors:

            # 点が5つ以上の領域には障害物があると判断　ノイズ除去のため
            if len(sector) > 5:

                #重心の計算　各点のx座標、y座標の平均で重心を求める
                sum_x = sum(p[0] for p in sector)
                sum_y = sum(p[1] for p in sector)

                self.obstacles.append((sum_x / len(sector), sum_y / len(sector)))

    def timer_callback(self):

        # ゴールとの距離(x軸方向:dx_g　y軸方向:dy_g)
        dx_g, dy_g = self.goal_x - self.pos_x, self.goal_y - self.pos_y

        # ゴールとの距離（直線的な）の計算
        # ＜tips - max関数使う理由：0乗算の回避と数値の爆発を回避＞
        dist_g = max(math.sqrt(dx_g**2 + dy_g**2), 0.1)
        
        # 引力の計算　(dx_g / dist_g)で正規化を行う　ゴールが遠いときに数値の爆発を防ぐため
        # また教科書のように計算しないのは離れてても一定の引力でゴールにたどり着けるように
        f_att_x = self.A * (dx_g / dist_g)
        f_att_y = self.A * (dy_g / dist_g)

        # 斥力の値を代入する変数を定義
        f_rep_x, f_rep_y = 0.0, 0.0

        # 各セクター内の重心の座標をox oyに代入してループ
        for ox, oy in self.obstacles:

            # robot座標 → world座標
            wx = ox * math.cos(self.yaw) - oy * math.sin(self.yaw)
            wy = ox * math.sin(self.yaw) + oy * math.cos(self.yaw)

            do = math.sqrt(wx**2 + wy**2)

            if 0.1 < do < 2.0:

                # 教科書式
                force = (self.B * self.m) / (do**(self.m + 1))

                # 正規化
                f_rep_x -= force * (wx / do)
                f_rep_y -= force * (wy / do)

        # 引力と斥力それぞれの合成ベクトルの計算
        att_mag = math.sqrt(f_att_x**2 + f_att_y**2)
        rep_mag = math.sqrt(f_rep_x**2 + f_rep_y**2)

        # それぞれの力の大きさを表示
        self.get_logger().info(f"引力:{att_mag:.3f}, 斥力:{rep_mag:.3f}")

        #引力と斥力の合計
        total_x, total_y = f_att_x + f_rep_x, f_att_y + f_rep_y

        msg = Twist()

        #引力と斥力を合わせた合成ベクトル
        norm = math.sqrt(total_x**2 + total_y**2)

        # 速度出しすぎないための正規化
        if norm > 0.5: 
            total_x *= (0.5 / norm)
            total_y *= (0.5 / norm)
        
        # 過去の速度を参照する割合α
        alpha = 0.6

        # 速度平滑化（急に速度が変化しないように）
        self.vx = alpha * self.vx + (1 - alpha) * total_x
        self.vy = alpha * self.vy + (1 - alpha) * total_y

        # world座標 → robot座標へ変換
        cmd_x = self.vx * math.cos(-self.yaw) - self.vy * math.sin(-self.yaw)
        cmd_y = self.vx * math.sin(-self.yaw) + self.vy * math.cos(-self.yaw)

        
        msg.linear.x = float(cmd_x)
        msg.linear.y = float(cmd_y)
        self.publisher.publish(msg)

#main関数
def main():
    rclpy.init()
    node = Potential_Method()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()