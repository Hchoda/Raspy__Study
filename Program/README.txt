
README.txt：Programの中身の説明
server.py：GPSモジュールを用いて現在地情報の取得
socket.py：地磁気センサー・サーボモータ・振動モジュールを用いて案内する
micropyGPS.py：server.pyで必要

micropyGPSとserver.pyは同一ディレクトリにおいておく．
この二つは1つのラズパイで制御し，
もう一つのラズパイのシステムとsocket通信でデータを送受信する．

socket.pyとserver.pyで通信する.

socket.pyで現在地の情報および案内対象の距離を計算する
一定の距離に近づいた時の緯度・経度情報をserver.pyに送信する．

server.pyでは緯度・経度情報と地磁気センサーを用いて案内対象の
角度を計算し，サーボモータで回転させる．