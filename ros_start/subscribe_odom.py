import rclpy                       # ROS 2 Pythonクライアントライブラリをインポート
from rclpy.node import Node        # ノードクラスをインポート
from nav_msgs.msg import Odometry  # オドメトリメッセージをインポート

def odom_callback(msg):
   # オドメトリデータをログに出力
   rclpy.logging.get_logger('sub_odom').info(f'Odom data: {msg}')  

# メイン関数の定義
def main(args=None):  
   # ROS 2の初期化
   rclpy.init(args=args) 
   # 'sub_odom'という名前のノードを作成 
   node = Node('sub_odom')  
   # トピック（Odometry型）をサブスクライブ
   subscription = node.create_subscription(Odometry,
                                           '/sobit_pro/odom',   
                                           odom_callback, 10)
   try:
       rclpy.spin(node)       # ノードをスピンしてコールバック関数を実行し続ける
   except KeyboardInterrupt:  # キーボード割り込み（Ctrl+C）をキャッチ
       pass                   # 何もしない
   finally:
       node.destroy_node()    # ノードを破棄
       rclpy.shutdown()       # ROS 2をシャットダウン
       print("finished")      # プログラム終了時にメッセージを表示

 # スクリプトが直接実行された場合
if __name__ == '__main__':    # スクリプトが直接実行された場合
   main()                     # メイン関数を実行
   