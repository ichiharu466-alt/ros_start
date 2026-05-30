import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート

# MinimalClientクラスを定義し、Nodeクラスを継承
class MinimalClient(Node):
   def __init__(self):
       # 親クラスのコンストラクタを呼び出し、ノード名を'minimal_client'に設定
       super().__init__('minimal_client')
       # 'mode_ctrl'という名前でModeCtrlサービスクライアントを作成
       self.client = self.create_client(ModeCtrl, 'mode_ctrl')
       # サービスが利用可能になるまで１秒ごとに繰り返す
       while not self.client.wait_for_service(timeout_sec=1.0):
           self.get_logger().info('Service not available, waiting again...')
       # リクエストオブジェクトを作成
       self.request = ModeCtrl.Request()

   # サービスリクエストを送信する関数
   def send_request(self, mode):
       # リクエストのモードを設定
       self.request.mode = mode
       # 非同期でサービスを呼び出し、将来の結果を取得
       self.future = self.client.call_async(self.request)
       # 結果が得られるまでスピン（待機）
       rclpy.spin_until_future_complete(self, self.future)
       # 結果を返す
       return self.future.result()

# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   # MinimalClientノードのインスタンスを作成
   minimal_client = MinimalClient()
   # モードを指定
   mode = 1 
   # リクエストを送信
   response = minimal_client.send_request(mode)# モードを指定
   # レスポンスを表示
   print(f'Response: {response.response}')
   # ノードを破棄
   minimal_client.destroy_node()
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()