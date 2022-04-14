# coding: utf-8
import asyncio
import datetime
import discord
import re
from subprocess  import Popen, PIPE, call
from discord.ext import tasks



with open("./personal_data/token.txt", "r", encoding="utf_8") as f:
    TOKEN = f.readline()
with open("./personal_data/channelid.txt", "r", encoding="utf_8") as f:
    CHANNEL_ID = int(f.readline())
with open("./personal_data/ip.txt", "r", encoding="utf_8") as f:
    phone_IP = f.readline()

wifi_condition = 1 # 続している状態で起動せよ
light_condition = 0
changeflag=0
today = datetime.date.today() # today.month で月を取得
month = today.month
client = discord.Client() # 接続に必要なオブジェクトを生成

def determine_season(month): # 1~4,11.12月：冬, 5~10月：夏
    if 4 < month < 11:
        season = "summer"
    else:
        season = "winter"
    return season

async def light_on():
    global light_condition
    channel = client.get_channel(CHANNEL_ID)
    while light_condition!=3:
        print(light_condition)
        call(["python3", "irrp.py", "-p", "-g17", "-f", "infrared_signal", "light:on"])
        print(light_condition)
        if light_condition==0:
            light_condition=3
        else:
            light_condition-=1
    await channel.send("つけたよ！")
    print("light ON")
    
async def light_down():
    global light_condition
    channel = client.get_channel(CHANNEL_ID)
    while light_condition!=1:
        call(["python3", "irrp.py", "-p", "-g17", "-f", "infrared_signal", "light:on"])
        if light_condition==0:
            light_condition=3
        else:
            light_condition-=1
    await channel.send("くらくしたよ！")
    print("light DOWN")

async def light_off():
    global light_condition
    light_condition = 0
    channel = client.get_channel(CHANNEL_ID)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "infrared_signal", "light:off"])
    await channel.send("でんきをけしたよ！")
    print(light_condition)
    print("light OFF")

async def aircon_off():
    channel = client.get_channel(CHANNEL_ID)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "infrared_signal", "aircon:off"])
    await channel.send("エアコンをけしたよ！")
    print("aircon OFF")

async def aircon_on():
    channel = client.get_channel(CHANNEL_ID)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "infrared_signal", "aircon:on"])
    await channel.send("エアコンをつけたよ！")
    print("aircon ON")

async def good_morning(time_alarm):
    channel = client.get_channel(CHANNEL_ID)
    
    time_now = datetime.datetime.now().time()
    time_alarm=int(time_alarm)    
    time_alarm = datetime.time(time_alarm//100,time_alarm-time_alarm//100*100)
    
    date=datetime.date.today()
    
    if time_alarm < time_now:
        time_alarm = datetime.datetime.combine(date+datetime.timedelta(days=1),time_alarm)
    else:
        time_alarm = datetime.datetime.combine(date,time_alarm)
    
    time_now = datetime.datetime.combine(date,time_now)
    wait_time = time_alarm-time_now
    print(wait_time)
    await asyncio.sleep(wait_time.total_seconds())
    await light_on()
    await channel.send("おはよう！")

async def good_night():
    channel = client.get_channel(CHANNEL_ID)
    await light_down()
    await channel.send("くらくしたよ！")
    print("light DOWN")
    await asyncio.sleep(1200)
    await channel.send("そろそろけすよ")
    await asyncio.sleep(30)
    await light_off()
    await aircon_off()
    print("light OFF")
    await channel.send("おやすみ")

async def greet():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("きたよ！")

@client.event # イベントを受信するための構文. デコレータ（おまじない的な）
async def on_ready(): # 起動したときにターミナルにログイン通知を表示
    await greet()
    print("---------------------------------")
    print("Logged in as")
    print("NAME :", client.user.name)
    print("ID   :", client.user.id)
    print("---------------------------------")
    # ihoneが接続しているかどうか判定し接続していない場合強制終了したい
    
@client.event # メッセージ受信時に動作する処理
async def on_message(message):
    global light_condition
    global changeflag
    if client.user != message.author:
        print(message.content)
        if message.content.startswith("ping"):
            print(message.content)
            await message.channel.send("PONG!")         
        if message.content.startswith("でんきつ"):
            await message.channel.send("はーい！")
            await light_on()
        if message.content.startswith("でんきけ"):
            await message.channel.send("はーい！")
            await light_off()
        if message.content.startswith("えあこんけ"):
            await message.channel.send("はーい！")
            await aircon_off()
        if message.content.startswith("えあこんつ"):
            await message.channel.send("はーい！")
            await aircon_on()
        if message.content.startswith("おやす"):
            await message.channel.send("はーい！")
            await good_night()
        if re.search("おこし",message.content):
            await message.channel.send("はーい！")
            print(message.content)
            print(message.content.startswith)
            time_alarm = int(re.sub("\\D", "", message.content))
            if 0<=time_alarm<2400:
                await message.channel.send(str(time_alarm)+"にでんきをつけるよ！")
                await good_morning(time_alarm)
            else:
                await message.channel.send("時間は0~2359で入力してね！")
        if re.search("くらく",message.content):
            await message.channel.send("はーい！")
            await light_down()
        if changeflag==1 and message.content.isdigit()==True:
            light_condition=int(message.content)
            await message.channel.send("りょーかい！")
            changeflag=0
        if re.search("ちがう",message.content):
            await message.channel.send("今の状態を入力してね！\n0：真っ暗\n1：常夜灯\n2：ちょっとくらい\n3：全灯")
            changeflag=1
        if re.search("じょうたい",message.content):
            d={'0':"真っ暗",'1':"常夜灯",'2':"ちょっとくらい",'3':"全灯"}
            await message.channel.send("今の状態は "+d[str(light_condition)]+" のはずだよ！")
            changeflag=1

    
            
@tasks.loop(seconds=15)
async def loop():
    global wifi_condition
    global previous_wifi_condition
    
    p1=Popen(["ping", "-c", "2","192.168.2.11"], stdout=PIPE,stderr=PIPE)
    #print(phone_IP)

    stdout_value = p1.stdout.read()
    print(stdout_value)
    previous_wifi_condition = wifi_condition
    if b'0 received' not in stdout_value:
        wifi_condition = 1 # 接続中
        print("FOUND Phone")
        if previous_wifi_condition != wifi_condition:
            await light_on()                
    else:
        wifi_condition = 0 # 接続なし
        print("NO Phone")
        if previous_wifi_condition != wifi_condition:
            await light_off()
            await aircon_off()


loop.start()

client.run(TOKEN)



