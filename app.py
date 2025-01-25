import warnings
from linebot.exceptions import LineBotSdkDeprecatedIn30

# 忽略 LineBotSdkDeprecatedIn30 类型的警告
warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, ImageSendMessage, ImageMessage, ImagemapSendMessage, BaseSize, ImagemapArea, MessageImagemapAction, URIImagemapAction, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackEvent, RichMenuSwitchAction, URIAction
from linebot.models.events import FollowEvent
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
from urllib.parse import urljoin
from threading import Thread
from PIL import Image
import re
import gspread
import json
import requests
import io
import time
import base64
import pytz
import logging
import random
import schedule
import threading
import asyncio

app = Flask(__name__)

# 使用你的 Channel Access Token
line_bot_api = LineBotApi('avse9S8Wbam6zQnvgNqap+K79TvVraVLg3etB6PvG3M2I3wyTcUmyOvIOBhdQTNUktIpi5ZRBFb2jya7g4nL3hQ06V71HUob4Y8tIteLAg5ZWYs/iDqBZkQ8mirBGAfb16AoucpiEGqvlCim6Eb0AwdB04t89/1O/w1cDnyilFU=')
# 使用你的 Channel Secret
handler = WebhookHandler('9329a50c057bd803f427f661a4eeaa9f')

# Line Notify 权杖
LINE_NOTIFY_TOKEN = 'bGIMW7T9dEhO5FEXZi3hQ4DuLe1UfcRiVxCHXEC8X9d'

LINE_CHANNEL_ACCESS_TOKEN = 'avse9S8Wbam6zQnvgNqap+K79TvVraVLg3etB6PvG3M2I3wyTcUmyOvIOBhdQTNUktIpi5ZRBFb2jya7g4nL3hQ06V71HUob4Y8tIteLAg5ZWYs/iDqBZkQ8mirBGAfb16AoucpiEGqvlCim6Eb0AwdB04t89/1O/w1cDnyilFU='

# 配置部分
IMGUR_CLIENT_ID = '2546e0b0e617149'
# Google Sheets API 配置
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'npust-bot-8425375b1a4a.json'  # 你的服務帳戶金鑰文件路徑
SPREADSHEET_ID = '12XtyjACnvIWcEUImMyxgq2KK__CG_S7kxmJSFiG4Brs'  # 替換為你的 Google 試算表 ID
RANGE_NAME = 'Sheet1!A:B'  # 假設使用 Sheet1 的 A 列存放 user_id，B 列存放 timetable_url

# 初始化 Google Sheets API 客戶端
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# 读取 JSON 数据
import os
import json
from flask import Flask

app = Flask(__name__)

# 定义所有 JSON 文件的路径
json_files = {
    'mapmenu': 'mapmenu.json',
    'classroom_code': 'classroom_code.json',
    'traffic_info': 'traffic_info.json',
    'train': 'train.json',
    'highspeed': 'highspeed.json',
    'npust_local': 'npust_local.json',
    'bus_info': 'bus_info.json',
    'student_union': 'student_union.json',
    'car_local': 'car_local.json',
    'car_local_north': 'car_local_north.json',
    'car_local_center': 'car_local_center.json',
    'car_local_south': 'car_local_south.json',
    'library': 'library.json',
    'library_time': 'library_time.json',
    'library_floor': 'library_floor.json',
    'library_call': 'library_call.json',
    'bus_stop_menu': 'bus_stop_menu.json',
    'sos': 'sos.json',
    'iOS_widget': 'iOS_widget.json',
    'Android_icon': 'Android_icon.json',
    'food_menu': 'food_menu_new.json',
    'share_friend': 'share_friend.json',
    'AAO_student_assistance_team': 'AAO_student_assistance_team.json',
    'dormitory': 'dormitory.json',
    'dormitory_boy': 'dormitory_boy.json',
    'dormitory_girl': 'dormitory_girl.json',
    '仁齋': '仁齋.json',
    '實齋': '實齋.json',
    '德齋': '德齋.json',
    '信齋': '信齋.json',
    '勇齋': '勇齋.json',
    '慧齋': '慧齋.json',
    '智齋': '智齋.json',
    '誠齋': '誠齋.json',
    'rent': 'rent.json',
    'school_safe': 'school_safe.json',
    'eas': 'eas.json',
    '衛生保健組': '衛生保健組.json',
    'aed': 'aed.json',
    '學生諮商中心': '學生諮商中心.json',
    '學務處': '學務處.json',
    '原住民資源中心': '原住民資源中心.json',
    '軍訓室': '軍訓室.json',
    '教務處': '教務處.json',
    '註冊組': '註冊組.json',
    '課務組': '課務組.json',
    '綜合業務組': '綜合業務組.json',
    '進修教育組': '進修教育組.json',
    '教資中心': '教資中心.json',
    'cctv': 'cctv.json',
    'choose': 'choose.json',
    'report': 'report.json',
    '健身房': '健身房.json',
    '游泳池': '游泳池.json',
    '體育室': '體育室.json',
    '室外球場': '室外球場.json',
    '室內球場': '室內球場.json',
    '田徑場': '田徑場.json',
    '行政單位': '行政單位.json',
    '第一餐廳': '第一餐廳.json',
    '第二餐廳': '第二餐廳.json',
    'system': 'system.json',
    'mail': 'mail.json',
    'office': 'office.json',
    'code_tips': 'code_tips.json',
}

# 读取 JSON 数据
json_data = {}

for key, filename in json_files.items():
    file_path = os.path.join(os.path.dirname(__file__), 'function', filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data[key] = json.load(f)

# 使用 json_data 字典来访问数据
mapmenu_data = json_data['mapmenu']
classroom_code_data = json_data['classroom_code']
traffic_info_data = json_data['traffic_info']
train_data = json_data['train']
highspeed_data = json_data['highspeed']
npust_local_data = json_data['npust_local']
bus_info_data = json_data['bus_info']
student_union_data = json_data['student_union']
car_local_data = json_data['car_local']
car_local_north_data = json_data['car_local_north']
car_local_center_data = json_data['car_local_center']
car_local_south_data = json_data['car_local_south']
library_data = json_data['library']
library_time_data = json_data['library_time']
library_floor_data = json_data['library_floor']
library_call_data = json_data['library_call']
bus_stop_menu_data = json_data['bus_stop_menu']
sos_data = json_data['sos']
iOS_widget_data = json_data['iOS_widget']
Android_icon_data = json_data['Android_icon']
food_menu_data = json_data['food_menu']
share_friend_data = json_data['share_friend']
AAO_student_assistance_team_data = json_data['AAO_student_assistance_team']
dormitory_data = json_data['dormitory']
dormitory_boy_data = json_data['dormitory_boy']
dormitory_girl_data = json_data['dormitory_girl']
仁齋_data = json_data['仁齋']
實齋_data = json_data['實齋']
德齋_data = json_data['德齋']
信齋_data = json_data['信齋']
勇齋_data = json_data['勇齋']
慧齋_data = json_data['慧齋']
智齋_data = json_data['智齋']
誠齋_data = json_data['誠齋']
rent_data = json_data['rent']
school_safe_data = json_data['school_safe']
eas_data = json_data['eas']
衛生保健組_data = json_data['衛生保健組']
aed_data = json_data['aed']
學生諮商中心_data = json_data['學生諮商中心']
學務處_data = json_data['學務處']
原住民資源中心_data = json_data['原住民資源中心']    
軍訓室_data = json_data['軍訓室']
教務處_data = json_data['教務處']
註冊組_data = json_data['註冊組']
課務組_data = json_data['課務組']
綜合業務組_data = json_data['綜合業務組']
進修教育組_data = json_data['進修教育組']
教資中心_data = json_data['教資中心']
cctv_data = json_data['cctv']
choose_data = json_data['choose']
report_data = json_data['report']
健身房_data = json_data['健身房']
游泳池_data = json_data['游泳池']
體育室_data = json_data['體育室']
室外球場_data = json_data['室外球場']
室內球場_data = json_data['室內球場']
田徑場_data = json_data['田徑場']
行政單位_data = json_data['行政單位']
第一餐廳_data = json_data['第一餐廳']
第二餐廳_data = json_data['第二餐廳']
system_data = json_data['system']
mail_data = json_data['mail']
office_data = json_data['office']
code_tips_data = json_data['code_tips']

# 监视所有来自 /callback 的 Post Request
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 发送 LINE Notify 的函数
def send_line_notify(message, token, image_file=None):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {"message": message}
    files = None

    if image_file:
        files = {'imageFile': ('image.jpg', image_file, 'image/jpeg')}
    
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data, files=files)

# 获取用户名称的函数
def get_user_name(user_id):
    profile = line_bot_api.get_profile(user_id)
    return profile.display_name

# 主处理函数
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id  # 获取用户ID
    user_name = get_user_name(user_id)  # 获取用户名称

    message = event.message.text  # 获取用户的文字訊息
    reply_token = event.reply_token

    # 處理問題回報
    if message == "問題回報@開始":
        user_report_status[user_id] = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="若有發現內容錯誤等其他問題，請直接輸入文字送出即可：")
        )
    elif user_report_status.get(user_id) == True:
        # 记录用户报告的问题
        send_line_notify(f"【{user_name}】{message}", LINE_NOTIFY_TOKEN)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="文字內容已送出，感謝您的回報。")
        )
        user_report_status[user_id] = False  # 重置状态

    user_text = event.message.text.strip()

# 判斷使用者輸入是否為「搶先報」
    if user_text == "搶先報":
        category = "全部"
        send_announcements_by_category(event, category, user_id)
        return
    elif message.startswith("搶先報@"):
        category = message.replace("搶先報@", "")
        send_announcements_by_category(event, category, user_id)
        return

    # 確保 message 不為 None 才執行其他處理邏輯
    if message:
        if re.match('校園地圖|地圖', message):
            handle_campus_map(event)
        elif re.match('校園導覽地圖', message):
            handle_campus_guide_map(event)
        elif re.match('各系教室代號', message):
            handle_classroom_codes(event)
        elif re.match('交通資訊', message):
            handle_traffic_info(event)
        elif re.match('台鐵|臺鐵|火車', message):
            handle_train(event)
        elif re.match('高鐵', message):
            handle_highspeed(event)
        elif re.match('自行前往|地址|學校地址|學校位置|位置', message):
            handle_npust_local(event)
        elif re.match('^校園公車社群$', message):
            handle_bus_group(event)
        elif re.match('公車|客運|屏東客運|高雄客運|BUS|509|510|510A|512|606|8232|8232A|8233|8240|巴士|賃居公車|學校公車|校內公車|校園公車|公車資訊|公車路線|公車班次', message):
            handle_bus(event)
        elif re.match('語言中心', message):
            handle_undone(event)
        elif re.match('^校外周圍美食@早餐$', message):
            handle_a_type_food_A(event)
        elif re.match('^校外周圍美食@午餐$', message):
            handle_a_type_food_B(event)
        elif re.match('^校外周圍美食@晚餐/宵夜$', message):
            handle_a_type_food_C(event)
        elif re.match('^校外周圍美食@飲料/甜點$', message):
            handle_a_type_food_D(event)
        elif re.match('^返鄉專車@站點位置$', message):
            handle_car_local(event)
        elif re.match('^返鄉專車@站點位置@北區$', message):
            handle_car_local_north(event)
        elif re.match('^返鄉專車@站點位置@中區$', message):
            handle_car_local_center(event)
        elif re.match('^返鄉專車@站點位置@南區$', message):
            handle_car_local_south(event)
        elif re.search(r'學生會|特約|特約商店|返鄉專車', message):
            handle_student_union(event)    
        elif re.match('^圖書與會展館@開館時間$', message):
            handle_library_time(event)
        elif re.match('^圖書與會展館@樓層簡介$', message):
            handle_library_floor(event)
        elif re.match('^圖書與會展館@聯絡資訊$', message):
            handle_library_call(event)
        elif re.search(r'圖書館|圖書與會展館|玉崗紀念圖書館', message):
            handle_library(event)
        elif re.search(r'安全求助|校安中心|校安|緊急|緊急電話|救命|警衛|分機', message):
            handle_sos(event)
        elif re.match('iOS加入小工具', message):
            handle_iOS_widget(event)
        elif re.match('Android加入捷徑圖標', message):
            handle_Android_icon(event)
        elif re.match('^學生餐廳@營業時間$', message):
            handle_學生餐廳營業時間(event)
        elif re.search(r'周圍美食|學生餐廳|學餐', message):
            handle_food_menu(event)
        elif re.search(r'超商|便利商店|超級商店|便利超商|萊爾富|全家|全家便利商店|門市|萊爾富門市|全家門市', message):
            handle_store(event)
        elif re.search(r'行事曆', message):
            handle_calendar(event)
        elif re.match('我的課表|課表', message):
            handle_timetable(event)
        elif re.match('更換課表|更換圖片|更改圖片|更改課表|刪除課表|刪除圖片|改圖片|改課表|換課表|換圖片', message):
            handle_replace_timetable(event)
        elif re.search(r'分享好友|分享', message):
            handle_share_friend(event)
        elif re.search(r'生活輔導組|生輔組', message):
            handle_AAO_student_assistance_team(event)
        elif re.match('宿舍簡介', message):
            handle_dormitory_info(event)
        elif re.match('^仁齋@宿舍照片$', message):
            handle_仁齋(event)
        elif re.match('^實齋@宿舍照片$', message):
            handle_實齋(event)
        elif re.match('^德齋@宿舍照片$', message):
            handle_德齋(event)
        elif re.match('^信齋@宿舍照片$', message):
            handle_信齋(event)
        elif re.match('^勇齋@宿舍照片$', message):
            handle_勇齋(event)
        elif re.match('^慧齋@宿舍照片$', message):
            handle_慧齋(event)
        elif re.match('^智齋@宿舍照片$', message):
            handle_智齋(event)
        elif re.match('^誠齋@宿舍照片$', message):
            handle_誠齋(event)
        elif re.search(r'男生宿舍|男宿|仁齋|實齋|德齋', message):
            handle_dormitory_boy(event)
        elif re.search(r'女生宿舍|女宿|智齋|誠齋|慧齋|勇齋|信齋', message):
            handle_dormitory_girl(event)
        elif re.search(r'學生宿舍|宿舍|住宿', message):
            handle_dormitory(event)
        elif re.match('賃居處所', message):
            handle_rent_local(event)
        elif re.search(r'校外賃居|租屋|校外租屋|租房|校外租房|賃居', message):
            handle_rent(event)
        elif re.match('校園安全', message):
            handle_school_safe(event)
        elif re.match('課外活動指導組|課指組|社團|學生社團|獎學金|助學金|獎助學金', message):
            handle_eas(event)
        elif re.search(r'衛生保健組|衛保組|健康檢查|健檢|新生健康檢查|新生健檢|特約醫院|醫院', message):
            handle_衛生保健組(event)
        elif re.search(r'保險套|販賣機|保險套販賣機', message):
            handle_保險套(event)
        elif re.search(r'哺乳室|集乳室|哺集乳室|育嬰室', message):
            handle_哺乳室(event)
        elif re.search(r'AED|AED專區|Aed|aed|自動體外心臟除顫器|除顫器|心臟', message):
            handle_aed(event)
        elif re.match('資源教室|資源教室簡介', message):
            handle_資源教室(event)
        elif re.search(r'學生諮商中心', message):
            handle_學生諮商中心(event)
        elif re.match('^單位位置@學務處$', message):
            handle_學務處位置(event)
        elif re.search(r'學務處|學生事務處', message):
            handle_學務處(event)
        elif re.match('原住民資源中心|原住民族學生資源中心', message):
            handle_原住民資源中心(event)
        elif re.match('軍訓室', message):
            handle_軍訓室(event)
        elif re.match('^單位位置@教務處$', message):
            handle_教務處位置(event)
        elif re.search(r'教學事務處|教務處', message):
            handle_教務處(event)
        elif re.match('註冊組', message):
            handle_註冊組(event)
        elif re.match('課務組', message):
            handle_課務組(event)
        elif re.match('綜合業務組', message):
            handle_綜合業務組(event)
        elif re.match('進修教育組', message):
            handle_進修教育組(event)
        elif re.match('教資中心|教學資源中心', message):
            handle_教資中心(event)
        elif re.match('查看即時影像|即時畫面|cctv|即時影像|監視器|監控', message):
            handle_cctv(event)
        elif re.search(r'上課時間|各節次上課時間一覽表', message):
            handle_time(event)
        elif re.search(r'網路選課|選課', message):
            handle_choose(event)
        elif re.match('^問題回報$', message):
            handle_report(event)
        elif re.match('^體育室@體適能登錄$', message):
            handle_體適能(event)
        elif re.match('^體育室@場地租借$', message):
            handle_場地租借(event)
        elif re.match('^體育室@室內球場$', message):
            handle_室內球場(event)
        elif re.match('^健身房@收費標準$', message):
            handle_健身房_收費標準(event)
        elif re.match('^健身房@規定$', message):
            handle_健身房_規定(event)
        elif re.search(r'健身房|體適能中心', message):
            handle_健身房(event)
        elif re.match('^游泳池@收費標準$', message):
            handle_游泳池_收費標準(event)
        elif re.search(r'游泳池|泳池', message):
            handle_游泳池(event)
        elif re.match('^單位位置@體育室$', message):
            handle_體育室位置(event)
        elif re.search(r'體育室', message):
            handle_體育室(event)
        elif re.match('^室外球場@場地配置$', message):
            handle_室外球場_場地配置(event)
        elif re.search(r'室外球場|網球|排球|籃球', message):
            handle_室外球場(event)
        elif re.match('^室內球場@場地配置$', message):
            handle_室內球場_場地配置(event)
        elif re.search(r'室內球場|羽球|羽毛球|桌球|體育館|孟祥體育館', message):
            handle_室內球場(event)
        elif re.search(r'田徑場|操場|室外田徑場|室外操場|戶外操場|紅土操場', message):
            handle_田徑場(event)
        elif re.search(r'行政單位', message):
            handle_行政單位(event)
        elif re.match('^查看菜單@名家美食小吃$', message):
            handle_view_menu(event)
        elif re.match('^查看菜單@名家港式快餐$', message):
            handle_view_menu_hk(event)
        elif re.match('^查看菜單@可頌冷飲吧$', message):
            handle_view_menu_drink(event)
        elif re.match('^查看菜單@活力早餐吧$', message):
            handle_view_menu_breakfast(event)
        elif re.match('^查看菜單@吉欣自助餐$', message):
            handle_view_menu_buffet(event)
        elif re.match('^查看菜單@福炙鍋燒$', message):
            handle_view_menu_potburn(event)
        elif re.match('^查看菜單@泰餃情$', message):
            handle_view_menu_dumpling(event)
        elif re.match('^查看菜單@思唯特調飲$', message):
            handle_view_menu_drink2(event)
        elif re.match('^查看菜單@南風美$', message):
            handle_view_menu_brunch(event)
        elif re.match('^查看菜單@侯吉桑$', message):
            handle_view_menu_thicksoup(event)
        elif re.match('^查看菜單@滿飽快餐$', message):
            handle_view_menu_buffet2(event)
        elif re.match('^更換菜單@名家美食小吃$', message):
            handle_replace_menu(event)
        elif re.match('^更換菜單@名家港式快餐$', message):
            handle_replace_menu_hk(event)
        elif re.match('^更換菜單@可頌冷飲吧$', message):
            handle_replace_menu_drink(event)
        elif re.match('^更換菜單@活力早餐吧$', message):
            handle_replace_menu_breakfast(event)
        elif re.match('^更換菜單@吉欣自助餐$', message):
            handle_replace_menu_buffet(event)
        elif re.match('^更換菜單@福炙鍋燒$', message):
            handle_replace_menu_potburn(event)
        elif re.match('^更換菜單@泰餃情$', message):
            handle_replace_menu_dumpling(event)
        elif re.match('^更換菜單@思唯特調飲$', message):
            handle_replace_menu_drink2(event)
        elif re.match('^更換菜單@南風美$', message):
            handle_replace_menu_brunch(event)
        elif re.match('^更換菜單@侯吉桑$', message):
            handle_replace_menu_thicksoup(event)
        elif re.match('^更換菜單@滿飽快餐$', message):
            handle_replace_menu_buffet2(event)
        elif re.search(r'第一餐廳|一餐', message):
            handle_第一餐廳(event)
        elif re.search(r'第二餐廳|二餐', message):
            handle_第二餐廳(event)
        elif re.search(r'信箱|電子郵件|學校信箱|mail|Mail|Gmail|gmail', message):
            handle_mail(event)
        elif re.search(r'校務系統|行政系統|行政資訊系統|學務資訊系統|請假|成績|學貸|停修|停休|暑休|暑修|車證|rfid|RFID|Rfid|缺曠|獎懲|停車證|portal|帳號|Portal', message):
            handle_system(event)
        elif re.search(r'office|word|365|Word|PPT|ppt|powerpoint|Powerpoint|Office|office 365|office365|Office 365|Office365|excel|Excel|Microsoft 365|Microsoft365|microsoft 365|microsoft365|微軟', message):
            handle_office(event)
        elif re.match('^隨機推薦@早餐$|^隨機推薦早餐$|^隨機推薦早餐店家$', message):
            handle_food_recommendation(event, "A")
        elif re.match('^隨機推薦@午餐$|^隨機推薦午餐$|^隨機推薦午餐店家$', message):
            handle_food_recommendation(event, "B")
        elif re.match('^隨機推薦@晚餐/宵夜$|^隨機推薦@晚餐 / 宵夜$|^隨機推薦晚餐$|^隨機推薦宵夜$|^隨機推薦晚餐店家$|^隨機推薦宵夜店家$|^隨機推薦晚餐/宵夜$|^隨機推薦晚餐 / 宵夜$|^隨機推薦晚餐/宵夜店家$|^隨機推薦晚餐 / 宵夜店家$', message):
            handle_food_recommendation(event, "C")
        elif re.match('^隨機推薦@飲料/甜點$|^隨機推薦@飲料 / 甜點$|^隨機推薦飲料$|^隨機推薦甜點$|^隨機推薦飲料店家$|^隨機推薦甜點店家$|^隨機推薦飲料/甜點$|^隨機推薦飲料 / 甜點$|^隨機推薦飲料/甜點店家$|^隨機推薦飲料 / 甜點店家$', message):
            handle_food_recommendation(event, "D")
        elif re.search(r'桌面工具', message):
            handle_follow(event)
        elif re.search(r'教室代號|教室代碼', message):
            handle_code_tips(event)
        elif re.search(r'更改密碼|更換密碼|改密碼|換密碼', message):
            handle_portal_password(event)
        elif re.match('^三小時後天氣$', message):
            handle_3hr_weather(event, user_id)
        elif re.match('^一週天氣$|天氣', message):
            handle_weather(event, sheet, user_id)
        elif re.match('今天第幾週|今天第幾周', message):
            handle_today(event)
        # 使用 handle_user_input 函數處理用戶輸入並返回結果
        result = handle_user_input(message, reply_token, user_id)  # 傳入 reply_token

        # 僅當 result 不為 None 時才回覆訊息
        if result is not None:
            line_bot_api.reply_message(reply_token, TextSendMessage(text=result))
            
def send_loading_animation(user_id):
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    
    # 呼叫所代的參數
    data = {
        "chatId": user_id,
        "loadingSeconds": 5  # 可以修改這個秒數
    }

    # 發送 POST 請求到 LINE API
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 202:
        print("Loading animation sent successfully")
    else:
        print(f"Error: {response.status_code}, {response.text}")



def switch_rich_menu(user_id):
    rich_menu_id = "richmenu-e2a4ec1494832e07320eaf340cad1915"
    try:
        # 執行更換 Rich Menu 的操作
        line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id)
        print("Rich menu 切換成功")
    except Exception as e:
        print(f"Rich menu 切換失敗：{str(e)}")

def handle_選單測試(event):
    user_id = event.source.user_id  # 動態獲取用戶 ID
    switch_rich_menu(user_id)       # 調用函數來更換選單



# 處理「學校信箱」的函式
def handle_mail(event):
    flex_message = FlexSendMessage(
        alt_text='學校信箱',
        contents=mail_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「校務系統」的函式
def handle_system(event):
    quick_reply_buttons = [
        QuickReplyButton(
            action=MessageAction(label="📝 更改密碼", text="更改密碼")
        ),
        QuickReplyButton(
            action=URIAction(label="❔ 忘記密碼", uri="https://www.npust.edu.tw/contact/pmail.aspx")
        )
    ]
    
    flex_message = FlexSendMessage(
        alt_text='校務系統',
        contents=system_data,
        quick_reply=QuickReply(items=quick_reply_buttons)
    )
    
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「校園地圖」的函式
def handle_campus_map(event):
    flex_message = FlexSendMessage(
        alt_text='校園地圖',
        contents=mapmenu_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「校園導覽地圖」的函式
def handle_campus_guide_map(event):
    image_message = ImageSendMessage(
        original_content_url='https://wp.npust.edu.tw/wp-content/uploads/2023/06/20230626_%E6%A0%A1%E5%9C%92%E5%9C%B0%E5%9C%96-1-scaled.jpg',
        preview_image_url='https://wp.npust.edu.tw/wp-content/uploads/2023/06/20230626_%E6%A0%A1%E5%9C%92%E5%9C%B0%E5%9C%96-1-scaled.jpg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「各系教室代號」的函式
def handle_classroom_codes(event):
    # 設置 QuickReply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="🔎 查詢教室", text="查詢教室代號")
            ),
            QuickReplyButton(
                action=MessageAction(label="📖 我的課表", text="我的課表")
            ),
            QuickReplyButton(
                action=MessageAction(label="🗺️ 導覽地圖", text="校園導覽地圖")
            )
        ]
    )

    # 設置 FlexMessage
    flex_message = FlexSendMessage(
        alt_text='各系教室代號',
        contents=classroom_code_data,
        quick_reply=quick_reply_buttons  # 加入 QuickReply
    )
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, flex_message)


# 處理「教室代號查詢」的函式
def handle_code_tips(event):
    # 設置 QuickReply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="🔠 教室代號一覽表", text="各系教室代號")
            ),
            QuickReplyButton(
                action=MessageAction(label="🗺️ 導覽地圖", text="校園導覽地圖")
            )  # 新增一個相同的 QuickReply 按鈕
        ]
    )

    # 設置 FlexMessage
    flex_message = FlexSendMessage(
        alt_text='教室代號查詢',
        contents=code_tips_data,
        quick_reply=quick_reply_buttons  # 加入 QuickReply
    )
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, flex_message)


# 處理「交通資訊」的函式
def handle_traffic_info(event):
    flex_message = FlexSendMessage(
        alt_text='交通資訊',
        contents=traffic_info_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「台鐵」的函式
def handle_train(event):
    flex_message = FlexSendMessage(
        alt_text='臺鐵',
        contents=train_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「高鐵」的函式
def handle_highspeed(event):
    flex_message = FlexSendMessage(
        alt_text='高鐵',
        contents=highspeed_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「自行前往」的函式
def handle_npust_local(event):
    flex_message = FlexSendMessage(
        alt_text='學校地址',
        contents=npust_local_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「未完成功能」的函式
def handle_upload_loading(event):
    
    message = "🔄 課表上傳中，請稍後"
    
    # 傳送一般的文字訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

# 處理「未完成功能餐廳」的函式
def handle_undone_rest(event):
    
    message = "此功能配合新學期校內餐廳調整，待開學後開放。"
    
    # 傳送一般的文字訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

# 處理「學生會」的函式
def handle_student_union(event):
    flex_message = FlexSendMessage(
        alt_text='學生會資訊',
        contents=student_union_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「返鄉專車站點位置」的函式
def handle_car_local(event):
    flex_message = FlexSendMessage(
        alt_text='返鄉專車區域選擇',
        contents=car_local_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「返鄉專車站點位置@北區」的函式
def handle_car_local_north(event):
    flex_message = FlexSendMessage(
        alt_text='返鄉專車北區站點位置',
        contents=car_local_north_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「返鄉專車站點位置@中區」的函式
def handle_car_local_center(event):
    flex_message = FlexSendMessage(
        alt_text='返鄉專車中區站點位置',
        contents=car_local_center_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「返鄉專車站點位置@南區」的函式
def handle_car_local_south(event):
    flex_message = FlexSendMessage(
        alt_text='返鄉專車南區站點位置',
        contents=car_local_south_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「圖書館」的函式
def handle_library(event):
    flex_message = FlexSendMessage(
        alt_text='圖書與會展館資訊',
        contents=library_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「圖書館開館時間」的函式
def handle_library_time(event):
    flex_message = FlexSendMessage(
        alt_text='圖書與會展館開館時間',
        contents=library_time_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「圖書館樓層簡介」的函式
def handle_library_floor(event):
    flex_message = FlexSendMessage(
        alt_text='圖書與會展館樓層簡介',
        contents=library_floor_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「圖書館聯絡資訊」的函式
def handle_library_call(event):
    flex_message = FlexSendMessage(
        alt_text='圖書與會展館聯絡資訊',
        contents=library_call_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「公車資訊」的函式
def handle_bus(event):
    # 設置 QuickReply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="🚌 加入校園公車社群", text="校園公車社群")
            )
        ]
    )

    # 設置 FlexMessage
    flex_message = FlexSendMessage(
        alt_text='公車',
        contents=bus_info_data,
        quick_reply=quick_reply_buttons  # 加入 QuickReply
    )
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「校園公車社群」的函式
def handle_bus_group(event):
    flex_message = FlexSendMessage(
        alt_text='加入校園公車社群',
        contents=bus_stop_menu_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「緊急電話」的函式
def handle_sos(event):
    flex_message = FlexSendMessage(
        alt_text='緊急電話資訊',
        contents=sos_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「iOS小工具」的函式
def handle_iOS_widget(event):
    flex_message = FlexSendMessage(
        alt_text='加入iOS小工具教學',
        contents=iOS_widget_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「Android圖標」的函式
def handle_Android_icon(event):
    flex_message = FlexSendMessage(
        alt_text='加入Android捷徑教學',
        contents=Android_icon_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 當用戶加入好友時的事件處理
@handler.add(FollowEvent)
def handle_follow(event):
    imagemap_message = ImagemapSendMessage(
        base_url="https://i.imgur.com/8dRSzPO.jpeg",
        alt_text="將「NPUST小幫手」加入手機桌面",
        base_size=BaseSize(width=1040, height=1000),
        actions=[
            MessageImagemapAction(
                text="iOS加入小工具",
                area=ImagemapArea(
                    x=89, y=772, width=362, height=185
                )
            ),
            MessageImagemapAction(
                text="Android加入捷徑圖標",
                area=ImagemapArea(
                    x=564, y=774, width=365, height=183
                )
            )
        ]
    )
    line_bot_api.reply_message(event.reply_token, imagemap_message)

# 處理「周圍美食」的函式
def handle_food_menu(event):
    flex_message = FlexSendMessage(
        alt_text='周圍美食',
        contents=food_menu_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「便利商店」的函式
def handle_store(event):
    imagemap_message = ImagemapSendMessage(
            base_url="https://i.imgur.com/7IqTAof.png",  # 圖片的 base URL
            alt_text="校內便利商店資訊",
            base_size=BaseSize(width=1040, height=1040),
            actions=[
                URIImagemapAction(
                    link_uri="https://maps.app.goo.gl/tdzMUNPqXxb7zVtm9",
                    area=ImagemapArea(x=217, y=292, width=280, height=657)
                ),
                URIImagemapAction(
                    link_uri="https://maps.app.goo.gl/LTmt4CBkb1mCtxAn7",
                    area=ImagemapArea(x=580, y=291, width=276, height=659)
            )
        ]
    )
    line_bot_api.reply_message(event.reply_token, imagemap_message)


# 用戶報告狀態的存儲字典（僅在內存中）
user_report_status = {}
upload_failure_log = {}

def save_user_timetable(user_id, timetable_url):
    # 先讀取現有的數據
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # 檢查用戶是否已存在
    user_found = False
    for idx, row in enumerate(rows):
        if row[0] == user_id:
            # 更新現有的 URL
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f'Sheet1!B{idx + 1}',
                valueInputOption='RAW',
                body={'values': [[timetable_url]]}
            ).execute()
            user_found = True
            break
    
    if not user_found:
        # 新增一行
        values = [[user_id, timetable_url]]
        body = {'values': values}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
    print(f"Timetable for user {user_id} saved.")

def load_user_timetable(user_id):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    for row in rows:
        if row[0] == user_id:
            return row[1]
    return None

def delete_user_timetable(user_id):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    for idx, row in enumerate(rows):
        if row[0] == user_id:
            # 刪除該行
            sheet.batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={
                    "requests": [
                        {
                            "deleteDimension": {
                                "range": {
                                    "sheetId": 0,  # 假設是第一個工作表
                                    "dimension": "ROWS",
                                    "startIndex": idx,
                                    "endIndex": idx + 1
                                }
                            }
                        }
                    ]
                }
            ).execute()
            print(f"Timetable for user {user_id} deleted.")
            return
    print(f"No timetable found for user {user_id} to delete.")


timetable_cache = {}  # 用於暫存用戶課表資料

def handle_timetable(event):
    user_id = event.source.user_id  # 获取用户ID
    send_loading_animation(user_id)

    # 先從緩存中查詢用戶的課表 URL
    if user_id in timetable_cache:
        timetable_url = timetable_cache[user_id]
    else:
        # 從Google Sheets加载用户的课表数据
        timetable_url = load_user_timetable(user_id)
        if timetable_url:
            # 将課表 URL 缓存起来
            timetable_cache[user_id] = timetable_url

    if timetable_url:
        # 返回已储存的课表图片，并提供快速回复选项
        quick_reply_buttons = [
            QuickReplyButton(
                action=MessageAction(label='🕒 上課時間', text='上課時間')
            ),
            QuickReplyButton(
                action=MessageAction(label='🔎 查詢教室', text='查詢教室代號')
            ),
            QuickReplyButton(
                action=MessageAction(label='📝 更換課表', text='更換課表')
            )
        ]
        
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=timetable_url,
                preview_image_url=timetable_url,
                quick_reply=QuickReply(items=quick_reply_buttons)
            )
        )
    else:
        # 第一次请求，发送 Flex Message 并要求用户上传课表
        with open('curr.json', 'r', encoding='utf-8') as f:
            curr_data = json.load(f)
        
        line_bot_api.reply_message(
            event.reply_token,
            [
                FlexSendMessage(alt_text="上傳自己的課表", contents=curr_data),
                TextSendMessage(
                    text="請先上傳您的課表圖片才可使用此功能："
                )
            ]
        )
        user_report_status[user_id] = 'awaiting_timetable_image'



def handle_replace_timetable(event):
    user_id = event.source.user_id  # 获取用户ID
    send_loading_animation(user_id)

    # 从Google Sheets加载用户的课表数据
    timetable_url = load_user_timetable(user_id)

    if timetable_url:
        # 删除已储存的课表图片
        delete_user_timetable(user_id)

        # **清除用戶緩存的課表 URL**
        if user_id in timetable_cache:
            del timetable_cache[user_id]  # 清除緩存中的課表

        # 发送 Flex Message 并要求用户上传新课表
        with open('curr.json', 'r', encoding='utf-8') as f:
            curr_data = json.load(f)

        line_bot_api.reply_message(
            event.reply_token,
            [
                FlexSendMessage(alt_text="上傳新的課表", contents=curr_data),
                TextSendMessage(text="已成功刪除原有的圖片，請重新上傳您的新課表圖片：")
            ]
        )
        user_report_status[user_id] = 'awaiting_timetable_image'
    else:
        # 用户没有已存储的课表，无法更换
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="您目前沒有上傳過圖片，無法更換喔！")
        )

        
# 處理「分享好友」的函式
def handle_share_friend(event):
    flex_message = FlexSendMessage(
        alt_text='分享好友',
        contents=share_friend_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「生輔組」的函式
def handle_AAO_student_assistance_team(event):
    flex_message = FlexSendMessage(
        alt_text='生活輔導組資訊',
        contents=AAO_student_assistance_team_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「宿舍簡介」的函式
def handle_dormitory_info(event):
    imagemap_message = ImagemapSendMessage(
        base_url="https://i.imgur.com/jseOXal.jpeg",  # 圖片的 base URL
        alt_text="宿舍簡介",
        base_size=BaseSize(width=1040, height=1040),
        actions=[]  # 將 actions 設為空列表，無交互功能
    )
    line_bot_api.reply_message(event.reply_token, imagemap_message)

# 處理「宿舍資訊」的函式
def handle_dormitory(event):
    flex_message = FlexSendMessage(
        alt_text='宿舍資訊',
        contents=dormitory_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「男生宿舍」的函式
def handle_dormitory_boy(event):
    flex_message = FlexSendMessage(
        alt_text='男生宿舍',
        contents=dormitory_boy_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「女生宿舍」的函式
def handle_dormitory_girl(event):
    flex_message = FlexSendMessage(
        alt_text='女生宿舍',
        contents=dormitory_girl_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「仁齋照片」的函式
def handle_仁齋(event):
    flex_message = FlexSendMessage(
        alt_text='仁齋照片',
        contents=仁齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「實齋照片」的函式
def handle_實齋(event):
    flex_message = FlexSendMessage(
        alt_text='實齋照片',
        contents=實齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「德齋照片」的函式
def handle_德齋(event):
    flex_message = FlexSendMessage(
        alt_text='德齋照片',
        contents=德齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「信齋照片」的函式
def handle_信齋(event):
    flex_message = FlexSendMessage(
        alt_text='信齋照片',
        contents=信齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「勇齋照片」的函式
def handle_勇齋(event):
    flex_message = FlexSendMessage(
        alt_text='勇齋照片',
        contents=勇齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「慧齋照片」的函式
def handle_慧齋(event):
    flex_message = FlexSendMessage(
        alt_text='慧齋照片',
        contents=慧齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「智齋照片」的函式
def handle_智齋(event):
    flex_message = FlexSendMessage(
        alt_text='智齋照片',
        contents=智齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「誠齋照片」的函式
def handle_誠齋(event):
    flex_message = FlexSendMessage(
        alt_text='誠齋照片',
        contents=誠齋_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「校外賃居」的函式
def handle_rent(event):
    flex_message = FlexSendMessage(
        alt_text='校外賃居資訊',
        contents=rent_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「賃居處所」的函式
def handle_rent_local(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/nkd1RwQ.jpeg',
        preview_image_url='https://i.imgur.com/nkd1RwQ.jpeg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「校園安全」的函式
def handle_school_safe(event):
    flex_message = FlexSendMessage(
        alt_text='校園安全資訊',
        contents=school_safe_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「課外活動指導組」的函式
def handle_eas(event):
    flex_message = FlexSendMessage(
        alt_text='課外活動指導組資訊',
        contents=eas_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「衛生保健組」的函式
def handle_衛生保健組(event):
    flex_message = FlexSendMessage(
        alt_text='衛生保健組資訊',
        contents=衛生保健組_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「保險套販賣機」的函式
def handle_保險套(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/OYJRDBh.jpeg',
        preview_image_url='https://i.imgur.com/OYJRDBh.jpeg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「哺乳室」的函式
def handle_哺乳室(event):
    response_message = (
        "一、哺（集）乳室設置地點：綜合大樓一樓健康促進諮商中心內\n\n"
        "二、哺（集）乳室使用須知：\n"
        "（一）鼓勵本校同仁哺餵母乳，配合行政院衛生署母乳哺育政策及兩性工作平等法之精神，特設置本室。\n\n"
        "（二）開放時間配合本校健康中心服務時間為週一至週五，上午08:30至下午16:30，請先至健康中心櫃台填寫「哺乳室使用者登記簿」；國定假日、星期六及日不開放。\n\n"
        "（三） 服務對象為哺餵母乳之本校教職工生及參訪本校人士。\n\n"
        "（四）本室設有沙發、洗手台、換尿布台、冰箱等均為公物，敬請愛惜使用，且不可攜出、不得擅自移動或調整，如有損害應照價賠償。其他裝備如吸奶器、奶瓶、冰桶、嬰兒用品等，由使用者自備。\n\n"
        "（五）冰箱為存放母乳（當天為限）之用，除母乳、吸奶裝置與代用之空瓶外，不可放入其他物品。冰存之母乳請標示使用者姓名及集乳時間，其餘設備亦請標示使用者姓名。存放過期之母乳或不合規定之物品，管理單位將予丟棄以維冰箱清潔。已標示之母乳於到期時將先予提醒，若48小時後仍無人認領或取走，將予以丟棄。\n\n"
        "（六）使用者進入後可上鎖，使用後離開時請記得關燈並將個人物品攜離以維護清潔，並請告知健康中心人員；非哺乳人員及男性不得任意進入哺乳室。\n\n"
        "（七）使用本室如有任何疑問或需協助者，請洽健康中心（本校分機7607）。"
    )
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))

# 處理「AED」的函式
def handle_aed(event):
    flex_message = FlexSendMessage(
        alt_text='AED專區',
        contents=aed_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「學生諮商中心」的函式
def handle_學生諮商中心(event):
    flex_message = FlexSendMessage(
        alt_text='學生諮商中心資訊',
        contents=學生諮商中心_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「資源教室」的函式
def handle_資源教室(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/u1El4u8.jpeg',
        preview_image_url='https://i.imgur.com/u1El4u8.jpeg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「學務處」的函式
def handle_學務處(event):
    flex_message = FlexSendMessage(
        alt_text='學務處資訊',
        contents=學務處_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「學務處位置」的函式
def handle_學務處位置(event):
    # 回傳文字訊息與兩張圖片
    response = [
        TextSendMessage(text="本處各組、中心及室位置分處孟祥體育館及綜合大樓兩地。\n\n學務長室及課外活動組導組位於孟祥體育館一樓。\n\n生活輔導組、衛生保健組、學生諮商中心、軍訓室及原住民學生資源中心則位於綜合大樓一樓。"),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/0CWYlKG.jpeg',
            preview_image_url='https://i.imgur.com/0CWYlKG.jpeg'
        ),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/cfp25OC.jpeg',
            preview_image_url='https://i.imgur.com/cfp25OC.jpeg'
        )
    ]
    line_bot_api.reply_message(event.reply_token, response)

# 處理「軍訓室」的函式
def handle_軍訓室(event):
    flex_message = FlexSendMessage(
        alt_text='軍訓室資訊',
        contents=軍訓室_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「原住民資源中心」的函式
def handle_原住民資源中心(event):
    flex_message = FlexSendMessage(
        alt_text='原住民族學生資源中心資訊',
        contents=原住民資源中心_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「教務處」的函式
def handle_教務處(event):
    flex_message = FlexSendMessage(
        alt_text='教務處資訊',
        contents=教務處_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「註冊組」的函式
def handle_註冊組(event):
    flex_message = FlexSendMessage(
        alt_text='註冊組資訊',
        contents=註冊組_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)
    
# 處理「課務組」的函式
def handle_課務組(event):
    flex_message = FlexSendMessage(
        alt_text='課務組資訊',
        contents=課務組_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「綜合業務組」的函式
def handle_綜合業務組(event):
    flex_message = FlexSendMessage(
        alt_text='綜合業務組資訊',
        contents=綜合業務組_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「進修教育組」的函式
def handle_進修教育組(event):
    flex_message = FlexSendMessage(
        alt_text='進修教育組資訊',
        contents=進修教育組_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「教資中心」的函式
def handle_教資中心(event):
    flex_message = FlexSendMessage(
        alt_text='教學資源中心資訊',
        contents=教資中心_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「教務處位置」的函式
def handle_教務處位置(event):
    # 回傳文字訊息與兩張圖片
    response = [
        TextSendMessage(text="本處各組及中心位置分處行政大樓。"),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/ODRatnx.jpeg',
            preview_image_url='https://i.imgur.com/ODRatnx.jpeg'
        ),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/GxgWlL9.jpeg',
            preview_image_url='https://i.imgur.com/GxgWlL9.jpeg'
        )
    ]
    line_bot_api.reply_message(event.reply_token, response)

def forecast(address):
    # 將主要縣市個別的 JSON 代碼列出
    api_list = {
        "宜蘭縣": "F-D0047-001", "桃園市": "F-D0047-005", "新竹縣": "F-D0047-009", "苗栗縣": "F-D0047-013",
        "彰化縣": "F-D0047-017", "南投縣": "F-D0047-021", "雲林縣": "F-D0047-025", "嘉義縣": "F-D0047-029",
        "屏東縣": "F-D0047-033", "臺東縣": "F-D0047-037", "花蓮縣": "F-D0047-041", "澎湖縣": "F-D0047-045",
        "基隆市": "F-D0047-049", "新竹市": "F-D0047-053", "嘉義市": "F-D0047-057", "臺北市": "F-D0047-061",
        "高雄市": "F-D0047-065", "新北市": "F-D0047-069", "臺中市": "F-D0047-073", "臺南市": "F-D0047-077",
        "連江縣": "F-D0047-081", "金門縣": "F-D0047-085"
    }

    # 提取縣市名稱
    for name in api_list:
        if name in address:
            city_id = api_list[name]
            break
    else:
        return {"錯誤": "地址無法識別"}

    result = {}
    code = 'CWA-E44C950E-9394-45A9-BB52-15531607A061'
    t = time.time()
    t1 = time.localtime(t+28800)
    t2 = time.localtime(t+28800+10800)
    now = time.strftime('%Y-%m-%dT%H:%M:%S', t1)
    now2 = time.strftime('%Y-%m-%dT%H:%M:%S', t2)
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{city_id}?Authorization={code}&elementName=WeatherDescription&timeFrom={now}&timeTo={now2}'
    req = requests.get(url)
    data = req.json()
    location = data['records']['locations'][0]['location']
    city = data['records']['locations'][0]['locationsName']
    
    # 僅顯示指定鄉鎮的天氣資訊
    target_area = '內埔鄉'
    for i in location:
        area = i['locationName']
        if target_area in area:
            note = i['weatherElement'][0]['time'][0]['elementValue'][0]['value']
            result[f'{city}{area}'] = '三小時後天氣將變換為' + note
            break  # 找到目標鄉鎮後可以退出循環

    if not result:
        result = {"錯誤": "指定鄉鎮的天氣資訊無法找到"}
    return result

def handle_weather_event(event):
    # 假設這裡的 address 是固定的 '屏東縣內埔鄉'
    address = '屏東縣內埔鄉'
    weather_data = forecast(address)
    
    # 組裝回覆訊息
    response_message = '\n'.join([f"{key}：{value}" for key, value in weather_data.items()])
    
    # 定義 Quick Reply 按鈕 (只有一個按鈕)
    quick_reply = QuickReply(
    items=[
        QuickReplyButton(
            action=MessageAction(label="📹 查看即時影像", text="即時影像")
        ),
        QuickReplyButton(
            action=MessageAction(label="⛅ 查看一週天氣", text="一週天氣")
        )
    ]
)

    # 回覆訊息並帶上 Quick Reply 選項
    line_bot_api.reply_message(
        event.reply_token, 
        TextSendMessage(text=response_message, quick_reply=quick_reply)
    )

# 處理「cctv」的函式
def handle_cctv(event):
    flex_message = FlexSendMessage(
        alt_text='即時影像畫面',
        contents=cctv_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

def handle_time(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/Fn9ylS6.png',
        preview_image_url='https://i.imgur.com/Fn9ylS6.png',
        quick_reply=QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="📖 我的課表", text="我的課表")
                ),
                QuickReplyButton(
                    action=MessageAction(label="🔎 查詢教室", text="查詢教室代號")
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, image_message)

    

# 處理「選課」的函式
def handle_choose(event):
    quick_reply = QuickReply(
        items=[
            QuickReplyButton(
                action=URIAction(label="📚 開課查詢", uri="https://course.npust.edu.tw/Cnc/Reports/OpenComm")
            )
        ]
    )
    
    flex_message = FlexSendMessage(
        alt_text='選課系統查詢',
        contents=choose_data,
        quick_reply=quick_reply
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「問題回報_開始」的函式
def handle_report(event):
    flex_message = FlexSendMessage(
        alt_text='問題回報',
        contents=report_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「體適能登錄」的函式
def handle_體適能(event):
    # 回傳文字訊息與圖片
    response = [
        TextSendMessage(text="前往校務行政系統網站，選擇體育室分類並點選「體適能資料」即可新增該學期資料。\n\nhttps://course.npust.edu.tw/TMIS/Ped/Fitness.aspx"),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/6fkuY03.png',
            preview_image_url='https://i.imgur.com/6fkuY03.png'
        )
    ]
    line_bot_api.reply_message(event.reply_token, response)

# 處理「場地租借」的函式
def handle_場地租借(event):
    # 回傳文字訊息與圖片
    response = [
        TextSendMessage(text="前往校務行政系統網站，選擇體育室分類並點選「體育室場地借用」或「場地使用時程表」即可租借場地及查看時程表。\n\nhttps://course.npust.edu.tw/TMIS/Ped/Fitness.aspx"),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/hV8Rad7.png',
            preview_image_url='https://i.imgur.com/hV8Rad7.png'
        )
    ]
    line_bot_api.reply_message(event.reply_token, response)

# 處理「室內球場」的函式
def handle_室內球場(event):
    flex_message = FlexSendMessage(
        alt_text='室內球場資訊',
        contents=室內球場_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「室內球場_場地配置」的函式
def handle_室內球場_場地配置(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/kD1ZEME.jpeg',
        preview_image_url='https://i.imgur.com/kD1ZEME.jpeg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「室外球場」的函式
def handle_室外球場(event):
    flex_message = FlexSendMessage(
        alt_text='室外球場資訊',
        contents=室外球場_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「室外球場_場地配置」的函式
def handle_室外球場_場地配置(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/cSCZ4B3.jpeg',
        preview_image_url='https://i.imgur.com/cSCZ4B3.jpeg'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「健身房」的函式
def handle_健身房(event):
    flex_message = FlexSendMessage(
        alt_text='健身房資訊',
        contents=健身房_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「健身房收費標準」的函式
def handle_健身房_收費標準(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/bzdRkRt.png',
        preview_image_url='https://i.imgur.com/bzdRkRt.png'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

def handle_健身房_規定(event):
    response_message = (
        "01.健身房採用線上預約制，可預約三日內開放時段。凡預約未到3次者，則兩週內不得申請。\n\n"
        "02.為了維護會員使用權利，每人每次依時段至多限使用1.5小時，入場時請自備零錢及識別證件，未帶識別證件者依其他人士身份入場收費。\n\n"
        "03.為了維持健身房的使用順暢，每時段使用人數至多40人。\n\n"
        "04.使用者必須穿著適當運動服、運動鞋，並請攜帶毛巾，禁止赤腳、穿著拖鞋、涼鞋等不適當服裝或上半身打赤膊者。\n\n"
        "05.使用者必須自行確保身體狀況良好，負責個人安全。\n\n"
        "06.活動前請先了解各項運動器材的使用方法，並做足暖身運動，減少個人傷害與器材損壞。\n\n"
        "07.使用重量訓練器材時，請輕放所持的重量鐵塊；使用完畢時，需將啞鈴、鐵片等歸回原位。\n\n"
        "08.重量訓練組與組間休息請起身，請勿長時間佔用機器，並與同好一起分享、輪流使用。\n\n"
        "09.使用器材後，請主動擦拭器材上留下的汗漬。\n\n"
        "10.本中心全面禁止飲食(礦泉水除外)。\n\n"
        "11.請尊重其他使用者，切勿喧嘩、高談闊論或干擾他人之行為。如個人在運動中所發聲、喊叫行為，以不影響他人為前提。\n\n"
        "12.請按正常程序使用各項器材，避免撞擊聲響，共同維護現場安全及設備。\n\n"
        "13.使用者請勿攜帶貴重物品，若有遺失情事發生，恕不負保管責任。\n\n"
        "14.使用者若不當使用致器材損害，應照價賠償（若使用前已發現器材損壞，請立即告知管理人員，以釐清責任）。\n\n"
        "15.如有未盡事宜，本室將另行公告之。"
    )
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))

# 處理「游泳池收費標準」的函式
def handle_游泳池_收費標準(event):
    image_message = ImageSendMessage(
        original_content_url='https://i.imgur.com/x1t9Lr3.png',
        preview_image_url='https://i.imgur.com/x1t9Lr3.png'
    )
    line_bot_api.reply_message(event.reply_token, image_message)

# 處理「游泳池」的函式
def handle_游泳池(event):
    flex_message = FlexSendMessage(
        alt_text='游泳池資訊',
        contents=游泳池_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「體育室」的函式
def handle_體育室(event):
    flex_message = FlexSendMessage(
        alt_text='體育室資訊',
        contents=體育室_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「體育室位置」的函式
def handle_體育室位置(event):
    # 回傳文字訊息與兩張圖片
    response = [
        TextSendMessage(text="本室位置分處孟祥體育館一樓。"),
        ImageSendMessage(
            original_content_url='https://i.imgur.com/gjvcrCk.jpeg',
            preview_image_url='https://i.imgur.com/gjvcrCk.jpeg'
        )
    ]
    line_bot_api.reply_message(event.reply_token, response)

# 處理「田徑場」的函式
def handle_田徑場(event):
    flex_message = FlexSendMessage(
        alt_text='田徑場資訊',
        contents=田徑場_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「行政單位」的函式
def handle_行政單位(event):
    flex_message = FlexSendMessage(
        alt_text='行政單位資訊',
        contents=行政單位_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「第一餐廳」的函式
def handle_第一餐廳(event):
    # 設置 QuickReply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="🕒 學生餐廳 營業時間", text="學生餐廳@營業時間")
            )
        ]
    )

    # 設置 FlexMessage
    flex_message = FlexSendMessage(
        alt_text='第一餐廳資訊',
        contents=第一餐廳_data,
        quick_reply=quick_reply_buttons  # 加入 QuickReply
    )
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「第二餐廳」的函式
def handle_第二餐廳(event):
    # 設置 QuickReply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="🕒 學生餐廳 營業時間", text="學生餐廳@營業時間")
            )
        ]
    )

    # 設置 FlexMessage
    flex_message = FlexSendMessage(
        alt_text='第二餐廳資訊',
        contents=第二餐廳_data,
        quick_reply=quick_reply_buttons  # 加入 QuickReply
    )
    
    # 回覆訊息
    line_bot_api.reply_message(event.reply_token, flex_message)

# 處理「學生餐廳營業時間」的函式
def handle_學生餐廳營業時間(event):
    imagemap_message = ImagemapSendMessage(
        base_url="https://i.imgur.com/Lddl8Mj.png",  # 圖片的 base URL
        alt_text="學生餐廳營業時間",
        base_size=BaseSize(width=1040, height=1040),
        actions=[]  # 將 actions 設為空列表，無交互功能
    )
    line_bot_api.reply_message(event.reply_token, imagemap_message)


######################################################################################################


blacklist = ['']  # 用戶 ID 黑名單列表

user_report_status = {}
upload_failure_log = {}
user_upload_image_count = {}

import os
import base64
import requests

def upload_image_to_imgbb(image_file, user_id):
    send_loading_animation(user_id)
    API_KEY = "99cc4dafd7347191eede3de64e206d05"
    url = "https://api.imgbb.com/1/upload"

    # 將圖片以 base64 格式進行編碼
    image_base64 = base64.b64encode(image_file).decode('utf-8')

    payload = {
        'key': API_KEY,
        'image': image_base64,
    }

    try:
        response = requests.post(url, data=payload)
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")  # 打印出回應的原始文本內容

        if response.status_code == 200:
            try:
                response_data = response.json()  # 解析 JSON
                return response_data["data"]["url"]  # 返回圖像的 URL
            except ValueError as e:
                print(f"Failed to parse JSON: {str(e)}")
                upload_failure_log[user_id] = f"Failed to parse JSON: {str(e)}"
                return None
        else:
            upload_failure_log[user_id] = f"Error {response.status_code}: {response.text}"
            return None

    except Exception as e:
        upload_failure_log[user_id] = f"Exception: {str(e)}"
        return None

    
def compress_image(image_file, quality=70):
    """
    將圖片壓縮至指定品質，並返回壓縮後的二進制數據。
    """
    try:
        image = Image.open(io.BytesIO(image_file))  # 打開圖片
        buffer = io.BytesIO()  # 建立緩衝區
        image.save(buffer, format="JPEG", quality=quality)  # 壓縮並保存圖片
        return buffer.getvalue()  # 返回壓縮後的二進制數據
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return image_file  # 如果壓縮失敗，返回原始圖片
    
def log_upload_failure(user_id, error_message=None):
    """
    記錄用戶上傳失敗的日誌，並顯示在 Render 候台。
    :param user_id: 用戶的 ID
    :param error_message: 失敗的詳細錯誤訊息（可選）
    """
    # 生成時間戳
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 構建詳細的日誌內容
    log_message = f"[{timestamp}] Upload failure for user {user_id}."
    if error_message:
        log_message += f" Error: {error_message}"

    # 將日誌輸出到 Render 的候台 (標準輸出)
    print(log_message)

def save_menu_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu!A:F',  # 更新為 A 到 F 欄，F 欄新增存儲 user_id
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu' sheet.")


def load_latest_menu():
    # 從 'menu_drink' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = event.source.user_id

    # 根據不同的狀態進行圖片上傳處理
    if user_report_status.get(user_id) in ['awaiting_menu_images', 'awaiting_menu_hk_images', 'awaiting_menu_drink_images', 'awaiting_timetable_image', 'awaiting_menu_breakfast_images', 'awaiting_menu_buffet_images', 'awaiting_menu_potburn_images', 'awaiting_menu_drink2_images', 'awaiting_menu_dumpling_images', 'awaiting_menu_brunch_images', 'awaiting_menu_thicksoup_images', 'awaiting_menu_buffet2_images']:

        # 檢查用戶是否在黑名單中，僅針對菜單圖片上傳進行檢查
        if user_report_status.get(user_id) in ['awaiting_menu_images', 'awaiting_menu_hk_images', 'awaiting_menu_drink_images', 'awaiting_menu_breakfast_images', 'awaiting_menu_buffet_images', 'awaiting_menu_potburn_images', 'awaiting_menu_drink2_images', 'awaiting_menu_dumpling_images', 'awaiting_menu_brunch_images', 'awaiting_menu_thicksoup_images', 'awaiting_menu_buffet2_images']:
            if user_id in blacklist:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="🚫 您已被禁止上傳圖片，無法進行此操作。\n如有疑慮請點擊選單中右上方設定>問題回報")
                )
                user_report_status.pop(user_id, None)
                return  # 阻止後續的圖片上傳處理

        message_id = event.message.id
        message_content = line_bot_api.get_message_content(message_id)

        if isinstance(event.message, ImageMessage):
            image_binary = message_content.content

            # 判斷是否是課表圖片上傳
            if user_report_status.get(user_id) == 'awaiting_timetable_image':
                imgbb_url = upload_image_to_imgbb(image_binary, user_id)

                if imgbb_url:
                    save_user_timetable(user_id, imgbb_url)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="✅ 課表已成功上傳！")
                    )
                    user_report_status.pop(user_id, None)  # 結束awaiting_timetable_image狀態
                else:
                    log_upload_failure(user_id)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="上傳課表功能維護中，請稍後再試。")
                    )
                    user_report_status.pop(user_id, None)  # 即使失敗也結束狀態
            else:
                # 其他類型的圖片上傳處理
                imgbb_url = upload_image_to_imgbb(image_binary, user_id)

                if imgbb_url:
                    if 'menu_urls' not in user_report_status:
                        user_report_status['menu_urls'] = []

                    user_report_status['menu_urls'].append(imgbb_url)

                    if len(user_report_status['menu_urls']) < user_upload_image_count.get(user_id, 1):
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=f"已收到第 {len(user_report_status['menu_urls'])} 張圖片，請繼續上傳剩餘圖片：")
                        )
                    else:
                        user_profile = line_bot_api.get_profile(user_id)
                        user_name = user_profile.display_name

                        if user_report_status.get(user_id) == 'awaiting_menu_images':
                            save_menu_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_hk_images':
                            save_menu_hk_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_drink_images':
                            save_menu_drink_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_breakfast_images':
                            save_menu_breakfast_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_buffet_images':
                            save_menu_buffet_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_potburn_images':
                            save_menu_potburn_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_drink2_images':
                            save_menu_drink2_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_dumpling_images':
                            save_menu_dumpling_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_brunch_images':
                            save_menu_brunch_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_thicksoup_images':
                            save_menu_thicksoup_images(user_report_status['menu_urls'], user_id, user_name)
                        elif user_report_status.get(user_id) == 'awaiting_menu_buffet2_images':
                            save_menu_buffet2_images(user_report_status['menu_urls'], user_id, user_name)

                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="✅ 所有菜單圖片皆已成功上傳！\n每個人都可以查看您所上傳的菜單。")
                        )

                        user_report_status.pop('menu_urls', None)
                        user_report_status[user_id] = False
                else:
                    log_upload_failure(user_id)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="上傳菜單功能維護中，請稍後再試。")
                    )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="上傳的內容並非圖片，已取消本次上傳")
            )





def handle_view_menu(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@名家美食小吃")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )


def handle_replace_menu(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/名家美食小吃.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

from linebot.models import PostbackEvent, TextSendMessage, PostbackAction

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data  # postback 傳來的資料格式
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name

    # 處理重新推薦相同類型的店家
    if data.startswith("recommend_again"):
        meal_type = data.split(',')[1]  # 提取餐點類型
        handle_food_recommendation(event, meal_type)

    # 處理上傳菜單的 postback
    elif data.startswith("上傳菜單"):
        try:
            parts = data.split('@')
            restaurant_name = parts[1]
            image_count = int(parts[2].replace('張', ''))  # 取得圖片數量（1～3）

            # 儲存該用戶要上傳的圖片數量
            user_upload_image_count[user_id] = image_count

            # 根據不同的餐廳名稱設置不同的上傳狀態
            restaurant_status_map = {
                "名家美食小吃": 'awaiting_menu_images',
                "名家港式快餐": 'awaiting_menu_hk_images',
                "可頌冷飲吧": 'awaiting_menu_drink_images',
                "活力早餐吧": 'awaiting_menu_breakfast_images',
                "吉欣自助餐": 'awaiting_menu_buffet_images',
                "福炙鍋燒": 'awaiting_menu_potburn_images',
                "泰餃情": 'awaiting_menu_dumpling_images',
                "思唯特調飲": 'awaiting_menu_drink2_images',
                "南風美": 'awaiting_menu_brunch_images',
                "侯吉桑": 'awaiting_menu_thicksoup_images',
                "滿飽快餐": 'awaiting_menu_buffet2_images'
            }

            if restaurant_name in restaurant_status_map:
                user_report_status[user_id] = restaurant_status_map[restaurant_name]
                # 回應使用者，提示上傳圖片
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"請上傳 {image_count} 張菜單圖片：")
                )
            else:
                # 如果餐廳名稱不符合，回傳錯誤訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="無法識別的餐廳名稱，請確認後重新選擇。")
                )
        except (IndexError, ValueError) as e:
            # 當資料格式不正確時處理錯誤
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="資料格式有誤，請重新嘗試。")
            )

    # 處理切換圖文選單的 postback
    elif data == 'dark':
        # 切換到深色模式圖文選單
        rich_menu_id_dd = 'richmenu-9e7c4f93b32620efddc2ae8a7f28dfaa'  # dd 圖文選單的 rich_menu_id
        line_bot_api.link_rich_menu_to_user(user_id=user_id, rich_menu_id=rich_menu_id_dd)

        # 回覆訊息，告知已切換成功
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="🌙 已切換至深色模式")
        )
    elif data == 'light':
        # 切換到淺色模式圖文選單
        rich_menu_id_d = 'richmenu-b67cc7c7392f66fc1c3bcd812905c47c'  # d 圖文選單的 rich_menu_id
        line_bot_api.link_rich_menu_to_user(user_id=user_id, rich_menu_id=rich_menu_id_d)

        # 回覆訊息，告知已切換成功
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="☀️ 已切換至淺色模式")
        )



#####################################################################
#############################################################################################################################################################################

def save_menu_hk_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_hk!A:F',  # 更新為 A 到 F 欄，F 欄新增存儲 user_id
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_hk' sheet.")

def load_latest_menu_hk():
    # 從 'menu_drink' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_hk!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None





def handle_view_menu_hk(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_hk_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_hk()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@名家港式快餐")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )


def handle_replace_menu_hk(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/名家港式快餐.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

###################################################################################################################################################
################################################################################################################################################

def save_menu_drink_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_drink!A:F',  # 更新為 menu_drink 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_drink' sheet.")

def load_latest_menu_drink():
    # 從 'menu_drink' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_drink!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_drink(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_drink_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_drink()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@可頌冷飲吧")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )


def handle_replace_menu_drink(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/可頌冷飲吧.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'


#############################################################################################
##############################################################################################

def save_menu_breakfast_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_breakfast!A:F',  # 更新為 menu_breakfast 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_breakfast' sheet.")

def load_latest_menu_breakfast():
    # 從 'menu_breakfast' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_breakfast!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_breakfast(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_breakfast_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_breakfast()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@活力早餐吧")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_breakfast(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/活力早餐吧.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

#############################################################################################
##############################################################################################

def save_menu_buffet_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_buffet!A:F',  # 更新為 menu_buffet 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_buffet' sheet.")

def load_latest_menu_buffet():
    # 從 'menu_buffet' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_buffet!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_buffet(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_buffet_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_buffet()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@吉欣自助餐")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_buffet(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/吉欣自助餐.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

######################################################################################################

def save_menu_potburn_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_potburn!A:F',  # 更新為 menu_potburn 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_potburn' sheet.")

def load_latest_menu_potburn():
    # 從 'menu_potburn' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_potburn!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_potburn(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_potburn_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_potburn()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@福炙鍋燒")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_potburn(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/福炙鍋燒.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

#########################################################################################################

def save_menu_drink2_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_drink2!A:F',  # 更新為 menu_drink2 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_drink2' sheet.")

def load_latest_menu_drink2():
    # 從 'menu_drink2' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_drink2!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_drink2(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_drink2_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_drink2()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@思唯特調飲")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_drink2(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/思唯特調飲.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

###########################################################################################

def save_menu_dumpling_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_dumpling!A:F',  # 更新為 menu_dumpling 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_dumpling' sheet.")

def load_latest_menu_dumpling():
    # 從 'menu_dumpling' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_dumpling!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_dumpling(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_dumpling_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_dumpling()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@泰餃情")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_dumpling(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/泰餃情.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

######################################################################################

def save_menu_brunch_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_brunch!A:F',  # 更新為 menu_brunch 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_brunch' sheet.")

def load_latest_menu_brunch():
    # 從 'menu_brunch' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_brunch!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_brunch(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_brunch_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_brunch()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@南風美")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_brunch(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/南風美.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

############################################################################################################

def save_menu_thicksoup_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_thicksoup!A:F',  # 更新為 menu_thicksoup 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_thicksoup' sheet.")

def load_latest_menu_thicksoup():
    # 從 'menu_thicksoup' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_thicksoup!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_thicksoup(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_thicksoup_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_thicksoup()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@侯吉桑")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_thicksoup(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/侯吉桑.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

################################################################################################

def save_menu_buffet2_images(menu_urls, user_id, user_name):
    # 設定台灣時間時區（UTC+8）
    tz = pytz.timezone('Asia/Taipei')
    
    # 獲取當前的台灣時間
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # 將多個菜單連結、上傳者姓名、時間和 ID 新增至試算表的最下面一行
    values = [[user_name, timestamp, user_id] + menu_urls]
    body = {'values': values}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='menu_buffet2!A:F',  # 更新為 menu_buffet2 工作表
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    print(f"Menu images, user name, timestamp, and user_id saved to the 'menu_buffet2' sheet.")

def load_latest_menu_buffet2():
    # 從 'menu_buffet2' 工作表中讀取所有的菜單連結和上傳日期，返回最後一行的菜單連結和上傳日期
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='menu_buffet2!A:F').execute()
    rows = result.get('values', [])

    if rows:
        # 返回最後一行的圖片 URL 列表（D, E, F 欄）和上傳日期（B 欄）
        upload_date = rows[-1][1]  # B欄是上傳日期
        menu_urls = rows[-1][3:6]  # D, E, F欄的圖片 URL
        return menu_urls, upload_date  # 返回菜單 URL 和上傳日期
    return None, None

def handle_view_menu_buffet2(event):
    user_id = event.source.user_id

    # 檢查用戶是否正處於上傳圖片流程，若是，則取消該流程
    if user_report_status.get(user_id) == 'awaiting_menu_buffet2_images':
        user_report_status.pop(user_id, None)  # 取消上傳圖片流程

    # 從 Google Sheets 載入最新的多張菜單圖片和上傳日期
    latest_menu_urls, upload_date = load_latest_menu_buffet2()

    if latest_menu_urls:
        # 提取年月日
        date_only = upload_date.split(" ")[0]  # 只取年月日部分
        messages = []
        for i, menu_url in enumerate(latest_menu_urls):
            if menu_url:  # 確保圖片 URL 存在
                # 只有在最後一張圖片中加入 Quick Reply
                if i == len(latest_menu_urls) - 1:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url,
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(
                                action=MessageAction(label=f"🕒 上傳於{date_only}", text=f"圖片上傳日期：{upload_date}")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="📝 更換菜單", text="更換菜單@滿飽快餐")
                            )
                        ])
                    ))
                else:
                    messages.append(ImageSendMessage(
                        original_content_url=menu_url,
                        preview_image_url=menu_url
                    ))

        # 發送多張圖片訊息
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="目前沒有上傳的菜單。")
        )

def handle_replace_menu_buffet2(event):
    user_id = event.source.user_id

    # 不刪除任何圖片，直接讓用戶上傳新的菜單，並更新試算表中的最新菜單記錄
    with open('./menu/滿飽快餐.json', 'r', encoding='utf-8') as f:
        menu_data = json.load(f)

    line_bot_api.reply_message(
        event.reply_token,
        [
            FlexSendMessage(alt_text="選擇要上傳的菜單數量", contents=menu_data),
            TextSendMessage(text="請選擇要上傳的圖片數量，最多可上傳 3 張菜單圖片。")
        ]
    )
    user_report_status[user_id] = 'awaiting_menu_selection'

############################################################################################################

# 處理「MS 365」的函式
def handle_office(event):
    flex_message = FlexSendMessage(
        alt_text='Microsoft 365 使用教學',
        contents=office_data
    )
    line_bot_api.reply_message(event.reply_token, flex_message)
############################################################################################################
# 初始化 Google Sheets API 客戶端
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# 更新範圍變數名稱，擴展至 G 欄以包含店家類型資料
RANGE_STORE_DATA = '表單回應!D:I'  # D 欄為店家名稱，E 欄為 Google Maps 連結，G 欄為類型代號

# 根據餐點類型代號隨機推薦符合條件的店家
def get_food_store_from_sheet(food_type_code):
    # 使用 Google Sheets API 取得試算表資料
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_STORE_DATA).execute()
    values = result.get('values', [])

    if not values:
        return None, None, None

    # 調整過濾邏輯
    filtered_stores = []
    for row in values[1:]:  # 跳過標題列
        if len(row) >= 6:  # 確保 G 欄和 I 欄存在
            type_codes = [code.strip() for code in row[3].split(",")]  # 拆分店家的類型代碼

            # 檢查輸入的類型代碼是否在店家的類型代碼中
            if food_type_code.strip() in type_codes:
                filtered_stores.append(row)

    if not filtered_stores:
        return None, None, None

    # 隨機選擇符合條件的店家
    random_row = random.choice(filtered_stores)
    store_name = random_row[0]  # 假設 D 欄是店家名稱
    google_map_link = random_row[1] if len(random_row) > 1 else None  # 假設 E 欄是 Google Maps 連結
    store_location = random_row[5] if len(random_row) > 5 else "未知地點"  # 假設 I 欄是店家位置

    return store_name, google_map_link, store_location


# 根據店家名稱和地圖連結生成 Quick Reply 訊息
def create_quick_reply_with_map(store_name, google_map_link, store_location, food_type_code):
    quick_reply_items = []
    
    # 如果有地圖連結，將「地圖連結」按鈕放在第一個位置
    if google_map_link:
        quick_reply_items.append(
            QuickReplyButton(action=URIAction(label="🗺️ 地圖連結", uri=google_map_link))
        )
    
    # 「🔀 重新推薦」按鈕
    quick_reply_items.append(
        QuickReplyButton(
            action=PostbackAction(label="🔀 重新推薦", data=f"recommend_again,{food_type_code}")
        )
    )
    
    # 「➕ 新增店家」按鈕
    quick_reply_items.append(
        QuickReplyButton(
            action=URIAction(label="➕ 新增店家", uri="https://liff.line.me/2006282783-OEmAmdWo")
        )
    )
    
    # 生成 Quick Reply 按鈕
    quick_reply_buttons = QuickReply(items=quick_reply_items)
    
    # 在店家名稱後方附加位置
    message_text = f"推薦店家：{store_name}（{store_location}）"
    
    message = TextSendMessage(
        text=message_text,
        quick_reply=quick_reply_buttons
    )
    
    return message

last_recommended_store = None

# 使用此函數處理 LINE Bot 隨機推薦店家
def handle_food_recommendation(event, meal_type):
    global last_recommended_store  # 使用全域變數

    store_name, google_map_link, store_location = None, None, None

    # 選擇店家，直到不與上次推薦的相同
    while True:
        store_name, google_map_link, store_location = get_food_store_from_sheet(meal_type)
        
        # 如果找不到店家，返回提示信息
        if store_name is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未找到符合條件的店家"))
            return
        
        # 如果選中的店家與最後推薦的店家不同，則跳出循環
        if store_name != last_recommended_store:
            break

    # 更新最近推薦的店家
    last_recommended_store = store_name

    # 生成 Quick Reply 訊息並回覆
    message = create_quick_reply_with_map(store_name, google_map_link, store_location, meal_type)
    line_bot_api.reply_message(event.reply_token, message)



##### 以下為  早餐Flex message ############
import json

def create_flex_message_by_type(type_code, title, image_url, random_label):
    def get_stores_by_location(type_code):
        # 這裡需要連接 Google 試算表並獲取資料 (假設資料已存在)
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_STORE_DATA).execute()
        values = result.get('values', [])
        if not values:
            return None

        stores_near_school = []
        stores_in_longquan = []
        stores_in_neipu = []

        for row in values[1:]:
            if len(row) >= 6:
                codes = [code.strip() for code in row[3].split(",")]  # G 欄類型代號
                store_name = row[0]  # D 欄店家名稱
                location = row[5]  # I 欄店家位置

                if type_code in codes:
                    if location == "校門口附近":
                        stores_near_school.append(store_name)
                    elif location == "龍泉市區":
                        stores_in_longquan.append(store_name)
                    elif location == "內埔市區/其他":
                        stores_in_neipu.append(store_name)

        return stores_near_school, stores_in_longquan, stores_in_neipu

    # 根據傳入的類型代號篩選店家
    stores_near_school, stores_in_longquan, stores_in_neipu = get_stores_by_location(type_code)

    near_school_text = "、".join(stores_near_school) if stores_near_school else "暫無資料"
    longquan_text = "、".join(stores_in_longquan) if stores_in_longquan else "暫無資料"
    neipu_text = "、".join(stores_in_neipu) if stores_in_neipu else "暫無資料"

    # 生成 Flex Message
    flex_message = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "url": image_url
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "weight": "bold",
                    "size": "xl",
                    "text": title
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "icon",
                            "url": "https://i.imgur.com/WcLwFtg.png",
                            "offsetTop": "5px",
                            "size": "lg"
                        },
                        {
                            "type": "text",
                            "text": "校門口附近",
                            "weight": "bold",
                            "size": "md",
                            "margin": "lg",
                            "offsetEnd": "8px"
                        }
                    ],
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": near_school_text,
                    "weight": "regular",
                    "size": "sm",
                    "margin": "lg",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "icon",
                            "url": "https://i.imgur.com/WcLwFtg.png",
                            "offsetTop": "5px",
                            "size": "lg"
                        },
                        {
                            "type": "text",
                            "text": "龍泉市區",
                            "weight": "bold",
                            "size": "md",
                            "margin": "lg",
                            "offsetEnd": "8px"
                        }
                    ],
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": longquan_text,
                    "weight": "regular",
                    "size": "sm",
                    "margin": "lg",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "icon",
                            "url": "https://i.imgur.com/WcLwFtg.png",
                            "offsetTop": "4px",
                            "size": "lg"
                        },
                        {
                            "type": "text",
                            "text": "內埔市區 / 其他",
                            "weight": "bold",
                            "size": "md",
                            "margin": "lg",
                            "offsetEnd": "8px"
                        }
                    ],
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": neipu_text,
                    "weight": "regular",
                    "size": "sm",
                    "margin": "lg",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "xl"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "➕新增店家",
                        "uri": "https://liff.line.me/2006282783-OEmAmdWo"
                    },
                    "style": "secondary",
                    "gravity": "center",
                    "height": "sm",
                    "margin": "xl",
                    "color": "#D0D0D0"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": random_label,
                        "data": f"recommend_again,{type_code}"
                    },
                    "style": "primary",
                    "gravity": "center",
                    "height": "sm",
                    "color": "#ffa556",
                    "margin": "xl"
                }
            ]
        }
    }

    return json.dumps(flex_message)


# 生成類型 A (早餐) 的 Flex Message
breakfast_flex_message = create_flex_message_by_type(
    "A", 
    "校外周圍美食 - 早餐", 
    "https://i.imgur.com/Z328b6X.jpeg", 
    "🔀隨機推薦店家@早餐"
)

# 生成類型 B (午餐) 的 Flex Message
lunch_flex_message = create_flex_message_by_type(
    "B", 
    "校外周圍美食 - 午餐", 
    "https://i.imgur.com/W460a82.jpeg", 
    "🔀隨機推薦店家@午餐"
)

# 生成類型 C (晚餐/宵夜) 的 Flex Message
dinner_flex_message = create_flex_message_by_type(
    "C", 
    "校外周圍美食 - 晚餐 / 宵夜", 
    "https://i.imgur.com/rYBahkY.jpeg", 
    "🔀隨機推薦店家@晚餐/宵夜"
)

# 生成類型 D (飲料/甜點) 的 Flex Message
supper_flex_message = create_flex_message_by_type(
    "D", 
    "校外周圍美食 - 飲料 / 甜點", 
    "https://i.imgur.com/F6Z9z9d.jpeg", 
    "🔀隨機推薦店家@飲料/甜點"
)
###############################################################

# 在所有 handle_a_type_food 函數內，把 event['replyToken'] 改成 event.reply_token

def handle_a_type_food_A(event):
    title = "校外周圍美食 - 早餐"
    image_url = "https://i.imgur.com/Z328b6X.jpeg"
    random_label = "🔀隨機推薦店家"

    breakfast_flex_message = create_flex_message_by_type(
        "A",  # 類型代號
        title,  # 標題
        image_url,  # 圖片連結
        random_label  # 隨機推薦標籤
    )

    # Quick Reply 的項目
    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="🍜 午餐", text="校外周圍美食@午餐")),
        QuickReplyButton(action=MessageAction(label="🍛 晚餐/宵夜", text="校外周圍美食@晚餐/宵夜")),
        QuickReplyButton(action=MessageAction(label="🥤 飲料/甜點", text="校外周圍美食@飲料/甜點"))
    ])

    # 使用正確的 reply_token 並回傳 Flex Message 和 Quick Reply
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text=title,
            contents=json.loads(breakfast_flex_message),
            quick_reply=quick_reply_buttons  # Quick Reply 放在這裡
        )
    )



def handle_a_type_food_B(event):
    title = "校外周圍美食 - 午餐"
    image_url = "https://i.imgur.com/W460a82.jpeg"
    random_label = "🔀隨機推薦店家"

    lunch_flex_message = create_flex_message_by_type(
        "B",  # 類型代號
        title,  # 標題
        image_url,  # 圖片連結
        random_label  # 隨機推薦標籤
    )

    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="🍳 早餐", text="校外周圍美食@早餐")),
        QuickReplyButton(action=MessageAction(label="🍛 晚餐/宵夜", text="校外周圍美食@晚餐/宵夜")),
        QuickReplyButton(action=MessageAction(label="🥤 飲料/甜點", text="校外周圍美食@飲料/甜點"))
    ])

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text=title,
            contents=json.loads(lunch_flex_message),
            quick_reply=quick_reply_buttons
        )
    )


def handle_a_type_food_C(event):
    title = "校外周圍美食 - 晚餐 / 宵夜"
    image_url = "https://i.imgur.com/rYBahkY.jpeg"
    random_label = "🔀隨機推薦店家"

    dinner_flex_message = create_flex_message_by_type(
        "C",  # 類型代號
        title,  # 標題
        image_url,  # 圖片連結
        random_label  # 隨機推薦標籤
    )

    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="🍳 早餐", text="校外周圍美食@早餐")),
        QuickReplyButton(action=MessageAction(label="🍜 午餐", text="校外周圍美食@午餐")),
        QuickReplyButton(action=MessageAction(label="🥤 飲料/甜點", text="校外周圍美食@飲料/甜點"))
    ])

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text=title,
            contents=json.loads(dinner_flex_message),
            quick_reply=quick_reply_buttons
        )
    )


def handle_a_type_food_D(event):
    title = "校外周圍美食 - 飲料 / 甜點"
    image_url = "https://i.imgur.com/F6Z9z9d.jpeg"
    random_label = "🔀隨機推薦店家"

    supper_flex_message = create_flex_message_by_type(
        "D",  # 類型代號
        title,  # 標題
        image_url,  # 圖片連結
        random_label  # 隨機推薦標籤
    )

    # 設置 Quick Reply 的按鈕
    quick_reply_buttons = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="🍳 早餐", text="校外周圍美食@早餐")),
        QuickReplyButton(action=MessageAction(label="🍜 午餐", text="校外周圍美食@午餐")),
        QuickReplyButton(action=MessageAction(label="🍛 晚餐/宵夜", text="校外周圍美食@晚餐/宵夜"))
    ])

    # 回傳 Flex Message 和 Quick Reply
    line_bot_api.reply_message(
        event.reply_token,  # 使用正確的 reply_token
        FlexSendMessage(
            alt_text=title,
            contents=json.loads(supper_flex_message),
            quick_reply=quick_reply_buttons  # 加入 Quick Reply
        )
    )


def handle_AD(event):
    imagemap_message = ImagemapSendMessage(
        base_url="https://i.imgur.com/fFWVaKZ.png",  # 新的圖片 base URL
        alt_text="校外周圍美食店家功能正式上線！",
        base_size=BaseSize(width=1040, height=1000),
        actions=[
            MessageImagemapAction(
                text="周圍美食",
                area=ImagemapArea(
                    x=0, y=0, width=1040, height=797
                )
            ),
            MessageImagemapAction(
                text="周圍美食",
                area=ImagemapArea(
                    x=0, y=796, width=487, height=204
                )
            ),
            URIImagemapAction(
                link_uri="https://liff.line.me/2006282783-OEmAmdWo",
                area=ImagemapArea(
                    x=485, y=796, width=555, height=204
                )
            )
        ]
    )
    line_bot_api.reply_message(event.reply_token, imagemap_message)

####################################################################################

# 初始化 Google Sheets API 客戶端
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# 定義例外教室名稱清單
exceptions = [
    "木球場", "功能訓練中心", "工作犬訓練中心", "多功能運動", "羽球場", "迎賓館", "迎賓館餐廳", "述耘堂", "桌球室", "技擊室",
    "高球場", "排球場", "網球場", "舞蹈室", "養殖場", "機械工廠", "機械工廠傳統", "籃球場", "保力林場", "達仁林場",
    "體育館", "體教一", "體教七", "體教二", "體教三", "體教五", "體教四", "體適能中心",
    "AG", "AH", "AIM", "AQ", "AR", "AS", "BD", "BE", "BS", "BT", "CE", "CM",
    "EP", "FC", "FP", "FS", "GH", "HE", "HO", "HR", "IB", "IC", "IH", "LA",
    "ME", "MW", "PI", "PM", "PMH", "RE", "RO", "SA", "SAM", "TA", "VEL", "VM", "VM2",
    "WH", "WP", "HF", "HL", "VE", "園藝場"
]

# 正則表達式提取並格式化教室代號（支援在句子中提取）
def extract_and_format_room_code(input_text):
    # 例外名稱的正則模式，確保 CM 只會在不後接數字時匹配
    exception_pattern = r'\b(?:' + '|'.join(re.escape(name) for name in exceptions) + r')\b(?!\s*\d)'
    
    # 正常教室代號的正則模式
    room_code_pattern = r'[A-Za-z]{1,5}\s*[0-9]{1,5}\s*[A-Za-z]?'

    # 在整個正則表達式的開頭添加 (?i) 來忽略大小寫
    full_pattern = r'(?i)(' + exception_pattern + r')|(' + room_code_pattern + r')'

    matches = re.findall(full_pattern, input_text)

    # 統一格式：大寫並去除空格
    formatted_codes = []
    for match in matches:
        # 檢查是否匹配了例外名稱
        exception_match = match[0]
        room_code_match = match[1]
        
        if exception_match:
            formatted_codes.append(exception_match.upper())  # 若匹配到例外名稱，統一轉為大寫
        elif room_code_match:
            formatted_codes.append(room_code_match.replace(" ", "").upper())  # 標準化教室代號

    return formatted_codes

# 檢查教室代號是否在試算表中，並返回相關資訊
def get_room_data_from_spreadsheet(formatted_code):
    RANGE_STORE_DATA = '教室代號查詢!A:J'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_STORE_DATA).execute()
    values = result.get('values', [])

    for row in values:
        if len(row) > 2 and row[2].replace(" ", "").upper() == formatted_code:
            capacity = row[5] if row[5] != "0" else "無資料"  # 容納人數
            return {
                "room_code": row[3],
                "room_type": row[4],
                "capacity": capacity,
                "management_unit": row[6],
                "location": f"{row[7]}{row[8]}",
                "map_url": row[9]
            }
    return None

# 創建 Flex Message
def create_flex_message(data):
    # 判斷容納人數的顯示內容
    capacity_text = (
        f"{data['capacity']}人" if data['capacity'] != "無資料" and data['capacity'] != " " 
        else data['capacity']
    )

    flex_content = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "教室代號查詢結果",
                    "size": "xl",
                    "weight": "bold",
                    "wrap": True,
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": "若查詢之教室為辦公室、研討室及儲藏室等非班級課表授課用途則無法查詢。",
                    "margin": "md",
                    "size": "sm",
                    "gravity": "center",
                    "color": "#aaaaaa",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/o39UWP0.png",
                                    "size": "lg",
                                    "offsetTop": "5.2px"
                                },
                                {
                                    "type": "text",
                                    "weight": "bold",
                                    "margin": "sm",
                                    "text": "教室代號"
                                },
                                {
                                    "type": "text",
                                    "text": data['room_code'],
                                    "align": "end",
                                    "flex": 0
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/xHR8KJV.png",
                                    "size": "lg",
                                    "offsetTop": "4.9px"
                                },
                                {
                                    "type": "text",
                                    "weight": "bold",
                                    "margin": "sm",
                                    "text": "教室類型"
                                },
                                {
                                    "type": "text",
                                    "text": data['room_type'],
                                    "align": "end",
                                    "flex": 0
                                }
                            ],
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/PqJ3NJd.png",
                                    "size": "lg",
                                    "offsetTop": "4.9px"
                                },
                                {
                                    "type": "text",
                                    "weight": "bold",
                                    "margin": "sm",
                                    "text": "容納人數"
                                },
                                {
                                    "type": "text",
                                    "text": capacity_text,
                                    "align": "end",
                                    "flex": 0
                                }
                            ],
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/EXWhw1d.png",
                                    "size": "lg",
                                    "offsetTop": "4.9px"
                                },
                                {
                                    "type": "text",
                                    "weight": "bold",
                                    "margin": "sm",
                                    "text": "管理單位"
                                },
                                {
                                    "type": "text",
                                    "text": data['management_unit'],
                                    "align": "end",
                                    "flex": 0
                                }
                            ],
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://i.imgur.com/7sf4gv9.png",
                                    "size": "lg",
                                    "offsetTop": "5.1px"
                                },
                                {
                                    "type": "text",
                                    "weight": "bold",
                                    "margin": "sm",
                                    "text": "教室位置"
                                },
                                {
                                    "type": "text",
                                    "text": data['location'],
                                    "align": "end",
                                    "flex": 0
                                }
                            ],
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "lg",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "uri",
                                        "label": "🗺️Google Maps 連結",
                                        "uri": data['map_url']
                                    },
                                    "height": "sm",
                                    "style": "primary",
                                    "color": "#AD5A5A",
                                    "gravity": "center"
                                }
                            ],
                            "margin": "xl"
                        }
                    ],
                    "margin": "lg"
                }
            ]
        }
    }
    return FlexSendMessage(alt_text="教室代號查詢結果", contents=flex_content)


# 主程式處理用戶訊息並傳送結果
def handle_user_input(input_text, reply_token, user_id):
   
    # 格式化並提取教室代號
    formatted_codes = extract_and_format_room_code(input_text)
    
    # 如果沒有提取到有效的教室代號，返回 None 表示不進行回覆
    if not formatted_codes:
        return None
    
    send_loading_animation(user_id)
    # 遍歷所有格式化過的教室代號
    for code in formatted_codes:
        # 從資料庫或 Google Sheets 查詢教室資料
        data = get_room_data_from_spreadsheet(code)

        # 如果查詢到該教室資料，則回傳 Flex Message
        if data:
            flex_message = create_flex_message(data)  # 根據教室資料創建 Flex Message
            
            # 為 Flex Message 添加 Quick Reply 按鈕
            flex_message.quick_reply = QuickReply(items=[
                QuickReplyButton(
                    action=MessageAction(label="🔠 教室代號一覽表", text="各系教室代號")
                ),
                QuickReplyButton(
                    action=MessageAction(label="🗺️ 導覽地圖", text="校園導覽地圖")
                )  # 重複添加相同的 Quick Reply 按鈕
            ])

            # 傳送 Flex Message
            line_bot_api.reply_message(reply_token, flex_message)
            return

    # 若所有格式化過的代號都無法查詢到資料，回覆 Flex Message 並附加 Quick Reply 按鈕
    no_result_flex_message = FlexSendMessage(
        alt_text="查無此教室代號",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "查無此教室代號",
                        "size": "xl",
                        "weight": "bold",
                        "wrap": True
                    },
                    {
                        "type": "text",
                        "text": "若查詢之教室為辦公室、研討室及儲藏室等非班級課表授課用途則無法查詢。",
                        "wrap": True,
                        "size": "sm",
                        "margin": "md",
                        "color": "#aaaaaa"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "如查詢教室為「VMⅡ」，請以阿拉伯數字代替羅馬數字：",
                                "wrap": True,
                                "size": "md"
                            },
                            {
                                "type": "text",
                                "text": "例如VMⅡ103請改成搜尋VM2103。",
                                "wrap": True,
                                "size": "md",
                                "margin": "lg"
                            }
                        ]
                    }
                ]
            }
        },
        quick_reply=QuickReply(items=[
            QuickReplyButton(
                action=MessageAction(label="🔠 教室代號一覽表", text="各系教室代號")
            ),
            QuickReplyButton(
                action=MessageAction(label="🗺️ 導覽地圖", text="校園導覽地圖")
            )  # 重複添加相同的 Quick Reply 按鈕
        ])
    )

    line_bot_api.reply_message(reply_token, no_result_flex_message)


def handle_portal_password(event):
    response_message = (
        "校務系統(Portal)更改密碼，請前往並登入學校信箱，選擇個人設定>信箱安全>密碼設定\n"
        "https://wp.npust.edu.tw/mail\n\n"
        "數位學習平台更改密碼則先點擊右上方個人頭像>偏好>更改密碼即可。"
    )
    
    image_url = "https://i.imgur.com/wH8XfDB.jpeg"
    
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=response_message),
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        ]
    )
#######################################################################

# 常量設定
RANGE_WEATHER_DATA = '一週天氣!A:I'

def determine_time_label(hour):
    if 0 <= hour < 6:
        return "凌晨"
    elif 6 <= hour < 12:
        return "早上"
    elif 12 <= hour < 18:
        return "下午"
    else:
        return "晚上"

# 初始化變數

taiwan_tz = timezone('Asia/Taipei')

# 儲存內存資料
weather_data_cache = {}

def fetch_weather_data():
    global weather_data_cache
    
    # API 資料獲取模擬
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_WEATHER_DATA).execute()
    rows = result.get('values', [])

    if not rows or len(rows) < 2:
        print("沒有可用的天氣資料！")
        return

    # 解析資料並存入內存
    today = datetime.now(taiwan_tz).strftime("%Y-%m-%d")
    weekday_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
    
    header_data = {
        "weather": rows[1][1],
        "temp_min": rows[1][2],
        "temp_max": rows[1][3],
        "rain_prob": rows[1][4] if rows[1][4] else "－",
        "humidity": rows[1][5],
        "uv_index": rows[1][6],
        "icon_url": rows[1][8]
    }

    future_weather_data = []
    merged_weather_data = {}

    for row in rows[2:]:
        datetime_range = row[0]
        start_datetime, _ = datetime_range.split(" ~ ")
        start_obj = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        weekday = weekday_map[start_obj.weekday()]
        formatted_date = start_obj.strftime(f"%m/%d({weekday})")

        start_hour = start_obj.hour
        time_label = determine_time_label(start_hour)

        temp_min = int(row[2]) if row[2] else float('inf')
        temp_max = int(row[3]) if row[3] else float('-inf')

        rain_prob = row[4].strip() if row[4] else "－%"
        if rain_prob.isdigit():
            rain_prob = f"{int(rain_prob)}%"

        icon_url = row[8]

        if start_obj.strftime("%Y-%m-%d") != today:
            if formatted_date not in merged_weather_data:
                merged_weather_data[formatted_date] = {
                    "temp_min": temp_min,
                    "temp_max": temp_max,
                    "rain_prob_sum": 0,
                    "rain_prob_count": 0,
                    "icon_url": icon_url
                }

            if rain_prob != "－%":
                merged_weather_data[formatted_date]["rain_prob_sum"] += int(rain_prob.replace("%", ""))
                merged_weather_data[formatted_date]["rain_prob_count"] += 1

            merged_weather_data[formatted_date]["temp_min"] = min(merged_weather_data[formatted_date]["temp_min"], temp_min)
            merged_weather_data[formatted_date]["temp_max"] = max(merged_weather_data[formatted_date]["temp_max"], temp_max)
        else:
            if temp_min == temp_max:
                display_temp = f"{temp_min}°C"
            else:
                display_temp = f"{temp_min} ~ {temp_max}°C"

            future_weather_data.append({
                "display_time_range": f"今天{time_label}",
                "temperature": display_temp,
                "rain_prob": rain_prob,
                "icon_url": icon_url
            })

    for date, data in merged_weather_data.items():
        if data["rain_prob_count"] > 0:
            avg_rain_prob = data["rain_prob_sum"] // data["rain_prob_count"]
            rain_prob_display = f"{avg_rain_prob}%"
        else:
            rain_prob_display = "－%"

        future_weather_data.append({
            "display_time_range": date,
            "temperature": f"{data['temp_min']} ~ {data['temp_max']}°C",
            "rain_prob": rain_prob_display,
            "icon_url": data["icon_url"]
        })

    weather_data_cache = {
        "header_data": header_data,
        "future_weather_data": future_weather_data
    }
    print("天氣資料已更新")


# 定時任務：每 15 分鐘執行
def schedule_weather_task():
    while True:
        try:
            fetch_weather_data()  # 執行資料抓取
        except Exception as e:
            print(f"定時任務執行失敗：{e}")
        time.sleep(15 * 60)  # 等待 15 分鐘

# 啟動時先抓取一次資料
fetch_weather_data()

# 啟動定時任務執行緒
task_thread = threading.Thread(target=schedule_weather_task)
task_thread.daemon = True
task_thread.start()



# 主程式處理 (範例：接收事件處理)
def handle_weather(event, sheet, user_id):
    send_loading_animation(user_id)
    global weather_data_cache

    if not weather_data_cache:
        fetch_weather_data()

    header_data = weather_data_cache.get("header_data", {})
    future_weather_data = weather_data_cache.get("future_weather_data", [])

    header_title = "屏東縣內埔鄉目前天氣"
    temperature = f"{header_data.get('temp_min', 'N/A')} ~ {header_data.get('temp_max', 'N/A')}°C" if header_data.get('temp_min') != header_data.get('temp_max') else f"{header_data.get('temp_min', 'N/A')}°C"
    rain_prob_ = f"{header_data.get('rain_prob', 'N/A')}%"
    uv_index = header_data.get("uv_index", "N/A")
        
    # 動態生成 Flex Message
    flex_message_data = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": header_title,
                            "color": "#ffffff66",
                            "size": "sm",
                            "offsetBottom": "1px"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "color": "#ffffff",
                                    "size": "xl",
                                    "flex": 2,
                                    "weight": "bold",
                                    "text": header_data.get("weather", "N/A"),
                                    "wrap": True,
                                    "offsetTop": "12px"
                                },
                                {
                                    "type": "image",
                                    "url": header_data.get("icon_url", ""),
                                    "size": "sm",
                                    "flex": 1,
                                    "offsetEnd": "3px"
                                }
                            ],
                            "spacing": "md",
                            "offsetBottom": "10px"
                        },
                        {
                            "type": "text",
                            "text": f"🌡️ 溫度：{temperature}",
                            "color": "#ffffff",
                            "size": "sm",
                            "weight": "bold",
                            "offsetTop": "-10px"
                        },
                        {
                            "type": "text",
                            "text": f"🌧️ 降雨：{rain_prob_}    🔆 紫外線：{uv_index}",
                            "color": "#ffffff",
                            "size": "sm",
                            "offsetTop": "-6px",
                            "weight": "bold"
                        }
                    ]
                }
            ],
            "paddingAll": "20px",
            "backgroundColor": "#0367D3",
            "spacing": "md",
            "height": "154px",
            "paddingTop": "17px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "未來天氣資訊",
                    "weight": "bold",
                    "size": "md",
                    "color": "#111111"
                },
                *[{
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "image",
                            "url": weather["icon_url"],
                            "size": "22px",
                            "flex": 0,
                            "offsetBottom": "1.7px"
                        },
                        {
                            "type": "text",
                            "text": weather["display_time_range"],
                            "size": "sm",
                            "flex": 0,
                            "align": "start"
                        },
                        {
                            "type": "text",
                            "text": f"🌡️ {weather['temperature']}",
                            "size": "sm",
                            "flex": 2,
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": f"🌧️ {weather['rain_prob']}",
                            "size": "sm",
                            "align": "end",
                            "flex": 0
                        }
                    ],
                    "spacing": "lg",
                    "paddingTop": "10px"
                } for weather in future_weather_data],
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "資料來源：中央氣象署",
                    "offsetTop": "8px",
                    "size": "xs",
                    "color": "#aaaaaa",
                    "margin": "sm"
                }
            ]
        }
    }

    # 定義 Quick Reply
    quick_reply = QuickReply(
    items=[
        QuickReplyButton(
            action=MessageAction(label="📹 查看即時影像", text="即時影像")
        ),
        QuickReplyButton(
            action=MessageAction(label="⛅ 查看三小時後天氣", text="三小時後天氣")
        )
    ]
)

    # 回傳天氣資訊，附加 Quick Reply
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text="天氣資訊",
            contents=flex_message_data,
            quick_reply=quick_reply  # 添加 Quick Reply
        )
    )

THREE_HR_RANGE_NAME = '三小時後天氣!B3'  # 使用更有意義的變數名稱

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# 從 Google Sheets 中讀取儲存格內容
def get_cell_value(spreadsheet_id, range_name):
    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        return values[0][0] if values else "無資料"
    except Exception as e:
        print(f"讀取 Google Sheets 時發生錯誤：{e}")
        return "無資料"

# 儲存內存資料
threehr_data_cache = {}

def fetch_3hrweather_data():
    global threehr_data_cache
    print("開始抓取天氣資料...")
    cell_value = get_cell_value(SPREADSHEET_ID, THREE_HR_RANGE_NAME)
    if cell_value:
        threehr_data_cache['three_hour_weather'] = cell_value
        print(f"天氣資料已更新：{cell_value}")
    else:
        print("未取得天氣資料")

# 定時任務：每 15 分鐘執行
def schedule_3hrweather_task():
    while True:
        try:
            fetch_3hrweather_data()  # 執行資料抓取
        except Exception as e:
            print(f"定時任務執行失敗：{e}")
        time.sleep(15 * 60)  # 等待 15 分鐘

# 啟動時先抓取一次資料
fetch_3hrweather_data()

# 啟動定時任務執行緒
task_thread = threading.Thread(target=schedule_3hrweather_task)
task_thread.daemon = True
task_thread.start()

# 定義處理三小時後天氣的函式
def handle_3hr_weather(event, user_id):
    send_loading_animation(user_id)
    global threehr_data_cache

    # 確保內存有資料，若無則重新獲取
    if 'three_hour_weather' not in threehr_data_cache:
        fetch_3hrweather_data()

    cell_value = threehr_data_cache.get('three_hour_weather', "無資料")

    # 設定 Quick Reply 按鈕
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(
                action=MessageAction(label="📹 查看即時影像", text="即時影像")
            ),
            QuickReplyButton(
                action=MessageAction(label="⛅ 查看一週天氣", text="一週天氣")
            )
        ]
    )

    # 回覆訊息到 LINE 使用者，附加 Quick Reply
    reply_message = TextSendMessage(
        text=f"屏東縣內埔鄉：三小時後天氣將變換為{cell_value}",
        quick_reply=quick_reply_buttons
    )
    line_bot_api.reply_message(event.reply_token, reply_message)

# 類型對應的目標 URL
ANNOUNCEMENT_URLS = {
    "全部": "https://www.npust.edu.tw/news1/index2.aspx",
    "行政": "https://www.npust.edu.tw/news1/index2.aspx?sel=1",
    "生活": "https://www.npust.edu.tw/news1/index2.aspx?sel=2",
    "研發": "https://www.npust.edu.tw/news1/index2.aspx?sel=3",
    "教學": "https://www.npust.edu.tw/news1/index2.aspx?sel=4",
    "學術": "https://www.npust.edu.tw/news1/index2.aspx?sel=5",
    "新生": "https://www.npust.edu.tw/news1/index2.aspx?sel=A",
    "校園": "https://www.npust.edu.tw/news1/index2.aspx?sel=6",
    "藝文": "https://www.npust.edu.tw/news1/index2.aspx?sel=7",
    "求職": "https://www.npust.edu.tw/news1/index2.aspx?sel=8",
    "考試": "https://www.npust.edu.tw/news1/index2.aspx?sel=9",
    "獎助學金": "https://www.npust.edu.tw/news1/index2.aspx?sel=B",
    "計畫徵求": "https://www.npust.edu.tw/news1/index2.aspx?sel=C",
    "防疫": "https://www.npust.edu.tw/news1/index2.aspx?sel=D",
}

CATEGORY_IMAGES = {
    "全部": "https://i.imgur.com/sfMCfoV.png",
    "行政": "https://i.imgur.com/IHa9emz.png",
    "生活": "https://i.imgur.com/UdJ0mnR.png",
    "研發": "https://i.imgur.com/JB1p2b9.png",
    "教學": "https://i.imgur.com/bi4HLvd.png",
    "學術": "https://i.imgur.com/sSOph5Q.png",
    "新生": "https://i.imgur.com/HmMGoLs.png",
    "校園": "https://i.imgur.com/zMc5LKM.png",
    "藝文": "https://i.imgur.com/nW1CO3u.png",
    "求職": "https://i.imgur.com/UgPq2Br.png",
    "考試": "https://i.imgur.com/jW7w5Mg.png",
    "獎助學金": "https://i.imgur.com/BuNeXa7.png",
    "計畫徵求": "https://i.imgur.com/fa9jaGi.png",
    "防疫": "https://i.imgur.com/lK7xLUP.png"
}

# 全局內存快取
announcements_cache = {}

# 抓取公告的函數
def fetch_announcements():
    global announcements_cache
    cache = {}
    
    for category, url in ANNOUNCEMENT_URLS.items():
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('#ContentPlaceHolder1_gviewEmployees tr')[1:]

            announcements = []
            for row in rows[:10]:  # 只取前10則公告
                columns = row.find_all('td')
                if len(columns) < 5:
                    continue

                date = columns[0].text.strip()
                unit = columns[1].text.strip()
                announcement_category = columns[2].text.strip()
                title = columns[3].text.strip()
                link_tag = columns[3].find('a')
                link = link_tag['href'] if link_tag else '#'
                if not link.startswith('http'):
                    link = f"https://www.npust.edu.tw/news1/{link}"

                announcements.append({
                    "date": date,
                    "unit": unit,
                    "category": announcement_category,
                    "title": title,
                    "link": link
                })

            cache[category] = announcements

    announcements_cache = cache

# 定時任務：每 15 分鐘執行
def schedule_announcement_task():
    while True:
        fetch_announcements()  # 執行資料抓取
        time.sleep(15 * 60)  # 等待 15 分鐘

# 啟動時先抓取一次資料
fetch_announcements()

# 啟動定時任務執行緒
task_thread = threading.Thread(target=schedule_announcement_task)
task_thread.daemon = True
task_thread.start()

# QuickReply 生成函數
def generate_quick_reply(current_category):
    quick_reply_items = [
        QuickReplyButton(
            action=MessageAction(label=category, text=f"搶先報@{category}"),
            image_url=CATEGORY_IMAGES.get(category)  # 加入圖片 URL
        )
        for category in ANNOUNCEMENT_URLS.keys() if category != current_category
    ]
    return QuickReply(items=quick_reply_items)

# 主函數：從內存回傳公告內容
def send_announcements_by_category(event, category, user_id):
    send_loading_animation(user_id)
    if category not in ANNOUNCEMENT_URLS:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ 查無此公告類型，請重新輸入！")
        )
        return

    announcements = announcements_cache.get(category, [])
    if not announcements:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ 目前此類別沒有最新公告。")
        )
        return

    # 動態生成 Flex Message 的內容
    bubbles = []
    for announcement in announcements:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "23:13",
                        "url": "https://i.imgur.com/Guji8rN.jpeg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "size": "xs",
                                "color": "#ffffff",
                                "align": "center",
                                "gravity": "center",
                                "text": announcement["category"]  # 使用抓取到的公告類別
                            }
                        ],
                        "height": "25px",
                        "backgroundColor": "#0066FF",
                        "cornerRadius": "100px",
                        "offsetStart": "13px",
                        "paddingAll": "5px",
                        "paddingStart": "8px",
                        "paddingEnd": "8px",
                        "offsetTop": "13px",
                        "position": "absolute"
                    }
                ],
                "paddingAll": "0px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": announcement["title"],
                        "weight": "bold",
                        "size": "md",
                        "wrap": True,
                        "maxLines": 3,
                        "color": "#333333",
                        "flex": 2000
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"公告日期：{announcement['date']}",
                                "size": "sm",
                                "color": "#999999",
                                "margin": "sm"
                            },
                            {
                                "type": "text",
                                "text": f"公告單位：{announcement['unit']}",
                                "size": "sm",
                                "color": "#999999",
                                "margin": "sm"
                            }
                        ],
                        "flex": 1,
                        "margin": "sm"
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "查看詳情",
                            "uri": announcement["link"]
                        },
                        "color": "#0066FF",
                        "height": "sm",
                        "margin": "lg"
                    }
                ]
            }
        }
        bubbles.append(bubble)

    # 建立 Flex Message
    flex_message_content = {
        "type": "carousel",
        "contents": bubbles
    }
    quick_reply = generate_quick_reply(category)

    flex_message = FlexSendMessage(
        alt_text=f"搶先報{category}公告",
        contents=flex_message_content,
        quick_reply=quick_reply
    )
    line_bot_api.reply_message(event.reply_token, flex_message)


# 設定台灣時區
tz = timezone('Asia/Taipei')

# 全域變數儲存週數日期
week_date_ranges = []

# 函數：從網站獲取週數日期
def fetch_week_date_ranges():
    global week_date_ranges

    try:
        # 抓取第一個按鈕的連結
        list_url = "https://moodle.npust.edu.tw/moodleset/course/index.php?categoryid=54"
        list_response = requests.get(list_url)
        list_response.encoding = 'utf-8'
        list_html_content = list_response.text
        list_soup = BeautifulSoup(list_html_content, "html.parser")
        first_button = list_soup.select_one(".coursename a")

        if not first_button:
            logging.warning("未找到第一個按鈕的連結")
            return

        protected_url = first_button['href']

        # 訪客登入並解析週數範圍
        login_url = "https://moodle.npust.edu.tw/moodleset/login/index.php"
        session = requests.Session()
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.text, "html.parser")
        logintoken = soup.find("input", {"name": "logintoken"})["value"]

        payload = {
            "logintoken": logintoken,
            "username": "guest",
            "password": "guest"
        }

        response = session.post(login_url, data=payload)
        if "以訪客身分登入" in response.text:
            logging.error("訪客登入失敗")
            return

        protected_page = session.get(protected_url)
        protected_soup = BeautifulSoup(protected_page.text, "html.parser")
        week_sections = protected_soup.select(".section.main .sectionname span")
        week_date_ranges = [week.text.split(". ", 1)[1] for week in week_sections if ". " in week.text]
        logging.info(f"已更新週數範圍：{week_date_ranges}")

    except Exception as e:
        logging.exception(f"抓取週數範圍時發生錯誤：{e}")


# 設定排程：每天午夜更新週數日期
scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(fetch_week_date_ranges, 'cron', hour=0, minute=0)
scheduler.start()

# 啟動時立即更新一次
fetch_week_date_ranges()

# Helper 函數：判斷今天是第幾週
def get_current_week(today, week_date_ranges):
    for i, date_range in enumerate(week_date_ranges, start=1):
        try:
            start_date, end_date = date_range.split(" - ")

            # 解析開始和結束日期
            start_date_obj = tz.localize(datetime.strptime(f"{start_date} {today.year}", "%m月 %d日 %Y"))
            end_date_obj = tz.localize(datetime.strptime(f"{end_date} {today.year}", "%m月 %d日 %Y"))

            # 將結束時間調整為當天的最後一秒
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)

            # 處理跨年情境
            if "12月" in start_date and "01月" in end_date and today.month == 1:
                start_date_obj = start_date_obj.replace(year=today.year - 1)

            logging.debug(f"第{i}週範圍：{start_date_obj} - {end_date_obj}，今日：{today}")

            if start_date_obj <= today <= end_date_obj:
                logging.info(f"今日符合第{i}週範圍")
                return i
        except Exception as e:
            logging.exception(f"解析第{i}週範圍時發生錯誤：{e}")
    logging.warning("今日不在任何週數範圍內")
    return None

def handle_today(event):
    try:
        today = datetime.now(tz)
        logging.debug(f"今日日期：{today}")
        logging.debug(f"當前週數範圍：{week_date_ranges}")

        current_week = get_current_week(today, week_date_ranges)
        year = today.year
        month = today.month
        day = today.day

        response_text = f"今天是{year}年{month:02d}月{day:02d}日\n"

        if current_week:
            week_type = "單數週" if current_week % 2 != 0 else "雙數週"
            exam_week = "（期中考週）" if current_week == 9 else "（期末考週）" if current_week == 18 else ""
            response_text += f"本週為第{current_week}週{exam_week}（{week_type}）"
        else:
            response_text += "目前為寒暑假期間。"

        logging.info(f"回傳訊息：{response_text}")

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )
    except Exception as e:
        logging.exception(f"處理今天資訊時發生錯誤：{e}")





# 全域變數，用於保存圖片 URL
calendar_images = []

# 提取圖片 URL 的函式
def fetch_calendar_images():
    global calendar_images
    url = "https://aa.npust.edu.tw/calendar/calendar.html"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for section in soup.find_all('h2'):
                semester_name = section.text.strip()
                if semester_name != "行事曆":  # 過濾掉不需要的標題
                    img_tag = section.find_next('img')
                    if img_tag and 'src' in img_tag.attrs:
                        # 將相對路徑轉換為絕對路徑
                        img_url = urljoin(url, img_tag['src'])
                        results.append(img_url)
            calendar_images = results  # 更新全域變數
            print("行事曆圖片 URL 提取成功：", calendar_images)
        else:
            print(f"無法獲取網頁內容，HTTP 狀態碼: {response.status_code}")
    except Exception as e:
        print(f"提取行事曆圖片時發生錯誤：{e}")

# 啟動時執行一次
fetch_calendar_images()

# 設定每天 00:00 執行
def schedule_task():
    schedule.every().day.at("00:00").do(fetch_calendar_images)

    while True:
        schedule.run_pending()
        time.sleep(1)

# 啟動排程執行的執行緒
threading.Thread(target=schedule_task, daemon=True).start()

# 處理「行事曆」的函式
def handle_calendar(event):
    # 獲取當前日期和週數資訊
    try:
        today = datetime.now(tz)
        current_week = get_current_week(today, week_date_ranges)

        # Quick Reply 按鈕的顯示文字
        if current_week:
            quick_reply_text = f"🗓️ 本週為學期第{current_week}週"
        else:
            quick_reply_text = "🗓️ 目前為寒暑假期間"

        # 創建 Quick Reply，按下後傳送固定文字 "今天第幾週"
        quick_reply = QuickReply(items=[
            QuickReplyButton(
                action=MessageAction(label=quick_reply_text, text="今天第幾週")
            )
        ])

        # 創建圖片訊息，使用內存中提取的圖片 URL
        if len(calendar_images) >= 2:
            image_message_1 = ImageSendMessage(
                original_content_url=calendar_images[0],  # 上學期圖片
                preview_image_url=calendar_images[0]
            )

            image_message_2 = ImageSendMessage(
                original_content_url=calendar_images[1],  # 下學期圖片
                preview_image_url=calendar_images[1],
                quick_reply=quick_reply  # 將 Quick Reply 附加到第二張圖片
            )

            # 回應消息
            line_bot_api.reply_message(
                event.reply_token,
                [image_message_1, image_message_2]
            )
        else:
            line_bot_api.reply_message(event.reply_token, TextMessage(text="⚠️學校網站異常中，暫時無法顯示行事曆圖片，請稍後再嘗試。"))
    except Exception as e:
        print(f"處理行事曆時發生錯誤：{e}")

# Google Sheets API 配置

WORKSHEET_NAME = "'測試代號'!A:B"

# Google Sheets API 初始化
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# 目標網址
url = "https://course.npust.edu.tw/Cnc/Reports/QueryCourseforStud"

# 建立 Session
session = requests.Session()

# 發送初始請求取得表單資料
response = session.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# 取得必要的隱藏表單欄位值
viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']

# 設定表單資料模擬按下 "訪客登入" 按鈕
data = {
    '__EVENTTARGET': 'BtnGuest',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategenerator,
    '__EVENTVALIDATION': eventvalidation,
}

# 發送 POST 請求模擬登入
post_response = session.post(url, data=data)

# 驗證是否成功跳轉頁面
if post_response.status_code == 200:
    result_soup = BeautifulSoup(post_response.text, 'html.parser')

    # 提取「使用教室」選單中的教室代號
    room_dropdown = result_soup.find('select', {'id': 'MainContent_DropDownListRoom'})
    if room_dropdown:
        room_options = room_dropdown.find_all('option')
        room_list = [option.text.strip() for option in room_options if option.text.strip()]
    else:
        room_list = []
else:
    room_list = []

# 如果獲取到教室代號，更新 Google 試算表
if room_list:
    # 清空 A:B 範圍內容
    clear_body = {}
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=WORKSHEET_NAME,
        body=clear_body
    ).execute()

    # 分析教室代號並準備資料
    rows = []
    for room in room_list:
        parts = room.split(' ')
        if len(parts) == 2:
            rows.append(parts)

    # 批次插入資料
    if rows:
        body = {
            'values': rows
        }
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=WORKSHEET_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        print("教室代號已更新至 Google 試算表。")
else:
    print("無法取得教室代號，請檢查網頁或程式碼。")


# 主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)