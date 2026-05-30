import rclpy                             # ROS2 Pythonクライアントライブラリをインポート
from rclpy.node import Node              # ノードクラスをインポート
from std_msgs.msg import String          # 標準メッセージ型のStringをインポート

# メイン関数の定義 
def main(args=None):
  rclpy.init(args=args)                  # ROS2システムの初期化
  node = Node('minimal_publisher')       # 'minimal_publisher'という名前のノードを作成
  # 'topic'という名前のトピックにString型メッセージをパブリッシュするパブリッシャを作成
  #メッセージ型, トピック名, パブリッシャが保持できるメッセージの最大数
  publisher = node.create_publisher(String, 'topic', 10)
  
  # タイマーのコールバック関数を定義
  def timer_callback():
      msg = String()                     # String型メッセージのインスタンスを作成
      msg.data = 'Hello World'           # メッセージのデータフィールドに文字列を設定
      publisher.publish(msg)             # メッセージをパブリッシュ
      # ログにパブリッシュしたメッセージを出力
      node.get_logger().info('"%s"というメッセージを送っているのだ' % msg.data)
  
  timer_period = 0.5                               # タイマーの周期を0.5秒に設定
  node.create_timer(timer_period, timer_callback)  # タイマーを作成し、コールバック関数を設定
  
  try:
      rclpy.spin(node)       # ノードをスピンしてコールバック関数を実行し続ける
  except KeyboardInterrupt:  # キーボード割り込み（Ctrl+C）をキャッチ
      pass                   # 何もしない
  finally:
      if rclpy.ok():                               # ROS2プロセスが終了しているか確認
         rclpy.shutdown()                          # ROS2をシャットダウン
      print("The proccess has finished")           # プログラム終了時にメッセージを表示

# スクリプトが直接実行された場合
if __name__ == '__main__': 
  main()                     # メイン関数を実行