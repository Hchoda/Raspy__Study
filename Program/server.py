# -*- coding:utf-8 -*-
#socket通信の部分に必要なモジュール
import socket
import time

host = ('192.168.179.3', 6789)#親のラズパイのIPアドレス
max_size = 1024

#GPSモジュールに必要なモジュール
import serial
import threading
import time
from micropyGPS import MicropyGPS#同ディレクトリのmicropyGPSをimportしていたはず？
from math import sin,cos,tan,atan2,acos,pi

############GPSモジュールに関する設定などはここ#################
gps = MicropyGPS(9, 'dd')

def rungps():#GPSモジュールで位置情報の取得
    s = serial.Serial('/dev/serial0', 9600, timeout=10)
    s.readline()
    while True:
        sentence = s.readline().decode('utf-8')
        if sentence[0] != '$':
            continue
        for x in sentence:
            gps.update(x)

gpsthread = threading.Thread(target=rungps, args=())
gpsthread.daemon = True
gpsthread.start()
############################################################

############案内対象や配列の初期化#################
x = [135.1513,135.1509,135.1518,135.151097,135.1512,135.1515,135.152]#案内対象の経度
y = [34.2671,34.2656,34.2669,34.266249,34.2667,34.2658,34.268]#案内対象の緯度
dist_comp = [20,30,25,19,26,27,27]#案内対象との距離の比較
#place = ['1:情報学センター','2:経済学部','3:教育学部','4:観光学部','5:図書館','6:基礎教育棟','7:システム工学部B棟']

chance = [0,0,0,0,0,0,0]#実行された回数を保存する配列

angle = []
dis = []

#地球のなんかの値
r = 6378.137e3

#################################################

def azimuth(x1, y1, x2, y2):#角度を計算する関数
    _x1, _y1, _x2, _y2 = x1*pi/180, y1*pi/180, x2*pi/180, y2*pi/180
    d_x = _x2 - _x1
    _y = sin(d_x)
    _x = cos(_y1) * tan(_y2) - sin(_y1) * cos(d_x)

    psi = atan2(_y, _x) * 180 / pi
    if psi < 0:
        return 360 + atan2(_y, _x) * 180 / pi
    else:
        return atan2(_y, _x) * 180 / pi

def distance(x1, y1, x2, y2, r):#距離を計算する関数
    _x1, _y1, _x2, _y2 = x1*pi/180, y1*pi/180, x2*pi/180, y2*pi/180
    d_x = _x2 - _x1
    val = sin(_y1) * sin(_y2) + cos(_y1) * cos(_y2) * cos(d_x)
    return r * acos(val)

def GPS_module():#GPSモジュールの関数を作成する．
    while True:
        if gps.clean_sentences > 20:
            angle = []
            dis = []
            send_data = []
            h = gps.timestamp[0] if gps.timestamp[0] < 24 else gps.timestamp[0] - 24
            for index in range(len(x)):
                #現在地と案内対象の距離
                dist_data = distance(gps.longitude[0],gps.latitude[0],x[index],y[index],r)
                dis.append(dist_data)
            #ある一定の距離になると発火(ここの値を調査する)
            for index in range(len(x)):
                if float(dis[index]) <= float(dist_comp[index]): 
                #現在地と案内対象の角度
                    if chance[index] == 0: 
                        print("初めての実行")
                        print("緯度：",gps.latitude[0])
                        print("軽度：",gps.longitude[0])
                        angle = azimuth(gps.longitude[0],gps.latitude[0],x[index],y[index])
                        chance[index] = 1
                        send_data.append(angle)
                        send_data.append(index)
                        return send_data
            time.sleep(3.5)
#角度のデータとどの場所なのかを格納する

def main_socket():
    #socketを作るGPSモジュールを動かしている
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(host)
    server.listen(1)
    while True:
        print("サーバ接続設定完了")
        client, addr = server.accept()
        msg = GPS_module()
        client.sendall(str(msg).encode())
        receve_data = client.recv(max_size)
        encode_data = receve_data.decode()
    
        client.close()
    server.close()

if __name__ == '__main__':#main
    main_socket()#main_socket()を無限ループで実行している
