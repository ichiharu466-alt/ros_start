import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート
from geometry_msgs.msg import Twist         # Twistメッセージをインポート

# DriveModeControllerクラスを定義し、Nodeクラスを継承
class DriveModeController(Node):
   def __init__(self):
       # 親クラスのコンストラクタを呼び出し、ノード名を'drive_mode_controller'に設定
       super().__init__('drive_mode_controller')
       # '/sobit_edu/commands/velocity'という名前のトピックにTwist型メッセージをパブリッシュするパブリッシャーを作成
       self.publisher = self.create_publisher(Twist,                                           
                        '/sobit_edu/commands/velocity', 
                        10) 
       # 'mode_ctrl'という名前でModeCtrlサービスを作成し、コールバック関数を設定
       self.srv = self.create_service(ModeCtrl, 'mode_ctrl', self.mode_ctrl_callback)
       # サービスが利用可能になるまで待機
       self.get_logger().info('Waiting for service...')


   # サービスリクエストを処理するコールバック関数
   def mode_ctrl_callback(self, request, response):   
       msg = Twist()                   # Twist型メッセージのインスタンスを作成   
       # リクエストのモードが1の場合、responseにTrueを設定し、正の速度をパブリッシュ
       if request.mode == 1:
           response.response = True
           msg.linear.x = 1.0           # メッセージの線形速度を設定
           self.publisher.publish(msg)  # メッセージをパブリッシュ
           self.get_logger().info('select mode 1:go ahead')           
       # リクエストのモードが2の場合、responseにFalseを設定し、負の速度をパブリッシュ
       elif request.mode == 2:
           response.response = False
           msg.linear.x = -1.0          # メッセージの線形速度を設定
           self.publisher.publish(msg)  # メッセージをパブリッシュ
           self.get_logger().info('select other mode:go back')           
       # レスポンスを返す
       return response

# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   # DriveModeControllerノードのインスタンスを作成
   drive_mode_controller = DriveModeController()
   # ノードが終了するまでスピン（実行）し続ける
   rclpy.spin(drive_mode_controller)
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()