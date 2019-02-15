# -*- coding:utf-8 -*-
#全体的に使用する
import time
#音声再生で使用する
import os
#socket通信で必要なもの
import socket

host = ('192.168.179.3', 6789)#ホストのIPアドレス
max_size = 1000
#振動モジュールで必要
import board
import busio
import adafruit_drv2605
#サーボモータで必要
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
#地磁気センサーで必要
import smbus		#import SMBus module of I2C
import math
#some MPU6050 Registers and their Address
Register_A     = 0              #Address of Configuration register A
Register_B     = 0x01           #Address of configuration register B
Register_mode  = 0x02           #Address of mode register

X_axis_H    = 0x03              #Address of X-axis MSB data register
Z_axis_H    = 0x05              #Address of Z-axis MSB data register
Y_axis_H    = 0x07              #Address of Y-axis MSB data register
declination = -0.00669          #define declination angle of location where measurement going to be done
pi          = 3.14159265359     #define pi value

#地磁気センサーの初期設定
def Magnetometer_Init():
        bus.write_byte_data(Device_Address, Register_A, 0x70)
        bus.write_byte_data(Device_Address, Register_B, 0xa0)
        bus.write_byte_data(Device_Address, Register_mode, 0)

#地磁気センサーで使用する関数
def read_raw_data(addr):
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
        value = ((high << 8) | low)
        if(value > 32768):
            value = value - 65536
        return value

bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x1e   # HMC5883L magnetometer device address
Magnetometer_Init()     # initialize HMC5883L magnetometer
###############
#
###vibration
###システムのバイブレーションを動かす関数
#
###############
def vibration():#バイブレーション
    i2c = busio.I2C(board.SCL, board.SDA)
    drv = adafruit_drv2605.DRV2605(i2c)

    for i in range(3):
        drv.set_waveform(52)
        drv.play()
        time.sleep(1.0)
###############
#
###receve_client
###server.pyで送信されたデータを受信する関数．
#
###############
def receve_client():#通信部分．受信部分だけ
    host = ('192.168.179.3', 6789)#ホストのIPアドレス
    max_size = 1000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(host)
    print("データ受信待ち")
    receve_data = client.recv(max_size)#データの受け取り。[角度、どの場所なのか]
    raspi_data = receve_data.decode()
    target = "OK"
    client.sendall(str(target).encode())
    client.close()
    return raspi_data
###############
#
###goal_angle
###目的地までの角度を計算する
#
###############
def goal_angle(x,y):#回転する角度の計算式．ここは，どちらの値が大きいかを計算している
    print("y:",y)
    if x > float(y):
        a = x - float(y)
        repair_angle(a)
    else:
        a = float(y) - x
        reverse_repair_angle(a)

###############
#
###repair_angle
###普通の回転
#
###############
def repair_angle(rotation):
    if rotation > 90:#回転角度が90度を超える場合
        sub_rotation = rotation - 90
        new_rotation = 600
        new_sub_rotation = sub_rotation * 5 / 2
        new_sub_rotation2 = int(new_sub_rotation) + 375
        pwm.set_pwm(0,0,new_rotation)
        pwm.set_pwm(1,0,new_sub_rotation2)
        time.sleep(2)
    else:
        new_rotation = rotation * 5 / 2
        new_rotation2 = int(new_rotation) + 375
        pwm.set_pwm(0,0,new_rotation2)
        time.sleep(2)

###############
#
###reverse_repair_angle
###逆回転
#
###############
def reverse_repair_angle(rotation):
    if rotation > 90:#回転角度が90度を超える場合
        sub_rotation = rotation - 90
        new_rotation = 150
        new_sub_rotation = sub_rotation * 5 / 2
        new_sub_rotation2 = 375 - int(new_sub_rotation)
        pwm.set_pwm(0,0,new_rotation)
        pwm.set_pwm(1,0,new_sub_rotation2)
        time.sleep(2)
    else:
        new_rotation = rotation * 5 / 2
        new_rotation2 = 375 - int(new_rotation)
        pwm.set_pwm(0,0,new_rotation2)
        time.sleep(2)

###############
#
###angle
###地磁気センサー
#
###############
def angle(GPS_angle):#ここに地磁気センサーのプログラムを書く
    #Read Accelerometer raw value
    x = read_raw_data(X_axis_H)
    z = read_raw_data(Z_axis_H)
    y = read_raw_data(Y_axis_H)
    heading = math.atan2(y, x) + declination
    #Due to declination check for >360 degree
    if(heading > 2*pi):
        heading = heading - 2*pi
    #check for sign
    if(heading < 0):
        heading = heading + 2*pi
    #convert into angle
    heading_angle = int(heading * 180/pi)
    return goal_angle(heading_angle,GPS_angle)#サーボで回す角度を指定
###############
#
###servo
###サーボモータと音声案内
#
###############
def servo(set_data):#ここの一連の流れを確認する．set_data = [回転する角度、何番目の案内場所]
    angle(set_data[1:13])
    set_place = int(set_data[-2])
    if set_place == 0:
        print("学術情報センター")
        os.system("aplay -D plughw:1,0 voice/set0.wav")
    elif set_place == 1:
        print("経済学部")
        os.system("aplay -D plughw:1,0 voice/set1.wav")
    elif set_place == 2:
        print("教育")
        os.system("aplay -D plughw:1,0 voice/set2.wav")
    elif set_place == 3:
        print("観光")
        os.system("aplay -D plughw:1,0 voice/set3.wav")
    elif set_place == 4:
        print("図書館")
        os.system("aplay -D plughw:1,0 voice/set4.wav")
    elif set_place == 5:
        print("基礎")
        os.system("aplay -D plughw:1,0 voice/set5.wav")
    else :
        print("システム工学部B")
        os.system("aplay -D plughw:1,0 voice/set6.wav")
    time.sleep(2)
    pwm.set_pwm(0,0,375)
    pwm.set_pwm(1,0,375)
###############
#
###first
###サーボモータの初期値を設定する
#
###############
def first():#初期設定
    pwm.set_pwm(0,0,375)
    pwm.set_pwm(1,0,375)

###############
#
###mainの関数
###ここを無限にループしてる
#
###############
if __name__ == '__main__':#mainの関数
    first()#初期設定
    print("初期設定完了")
    while True:
        print("クライアント接続")
        main_data = receve_client()#受信部分クライアント。main_data = [回転する角度、何番目の案内場所]
        vibration()#バイブレーション
        servo(main_data)#サーボモータ．main_data = [回転する角度、何番目の案内場所]
        #send_client()#送信部分のクライアント接続
