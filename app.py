import warnings
from linebot.exceptions import LineBotSdkDeprecatedIn30

# 忽略 LineBotSdkDeprecatedIn30 类型的警告
warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, ImageSendMessage, ImageMessage, ImagemapSendMessage, BaseSize, ImagemapArea, MessageImagemapAction, URIImagemapAction, StickerSendMessage, LocationSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackEvent
from linebot.models.events import FollowEvent
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
from io import BytesIO
import re
import json
import requests
import time
import base64
import pytz

@app.route("/callback", methods=['POST'])
def callback():
    # 處理來自 LINE 的 webhook
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    return 'OK'


app = Flask(__name__)

# 使用你的 Channel Access Token
line_bot_api = LineBotApi('ykm8FFaDZ6tXowVkCNO1FtHFby7qRRytSK1VEr8YzlwlZS/+YpHryoqssihEBolMsldB2s8wB2yL8B5TWXhJqIBS615TdWS+Bklsby5CrZjJp0Ty5J7UnnL4zPpUQ8BTauJDiIUVEs9tdlcNrBOyWQdB04t89/1O/w1cDnyilFU=')
# 使用你的 Channel Secret
handler = WebhookHandler('5bbc11e5756f920090ed0ef20af9ddf0')

# Line Notify 权杖
LINE_NOTIFY_TOKEN = 'bGIMW7T9dEhO5FEXZi3hQ4DuLe1UfcRiVxCHXEC8X9d'

SERVICE_ACCOUNT_FILE = 'npust-bot-8425375b1a4a.json'  # 你的服務帳戶金鑰文件路徑


# Google Sheets API 設定
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '12XtyjACnvIWcEUImMyxgq2KK__CG_S7kxmJSFiG4Brs'
RANGE_NAME = '課表!A:B'

# Imgur API 設定
IMGUR_CLIENT_ID = 'eff6d5e271fbd7b'
IMGUR_UPLOAD_URL = 'https://api.imgur.com/3/upload'

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

def get_sheet_data():
    """從 Google Sheets 讀取資料，並檢查是否有該使用者的課表"""
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])
        return values
    except HttpError as err:
        print(err)
        return []

def update_sheet(user_id, image_url):
    """將用戶的課表圖片 URL 更新至 Google Sheets"""
    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # 更新圖片 URL 至該用戶的列
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=RANGE_NAME,
            valueInputOption="RAW",
            body={"values": [[user_id, image_url]]}
        ).execute()
    except HttpError as err:
        print(err)

def upload_to_imgur(image_url):
    """將圖片上傳至 Imgur 並取得 URL"""
    headers = {
        'Authorization': f'Client-ID {IMGUR_CLIENT_ID}',
    }
    data = {
        'image': image_url,
        'type': 'url',
    }
    response = requests.post(IMGUR_UPLOAD_URL, headers=headers, data=data)
    response_data = response.json()
    
    if response_data['success']:
        return response_data['data']['link']
    return None

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """處理圖片訊息，並判斷是否已有課表"""
    user_id = event.source.user_id
    message_content = line_bot_api.get_message_content(event.message.id)
    image_data = BytesIO(message_content.content)  # 將資料流存成二進制檔案

    # 讀取試算表的資料
    sheet_data = get_sheet_data()

    # 檢查用戶是否已經有上傳的課表
    user_found = False
    image_url = None
    for row in sheet_data:
        if row[0] == user_id:
            user_found = True
            image_url = row[1]
            break

    if user_found:
        # 若已有課表，回傳圖片
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
        )
    else:
        # 將圖片上傳至 Imgur 並取得圖片 URL
        uploaded_url = upload_to_imgur(image_data)
        if uploaded_url:
            update_sheet(user_id, uploaded_url)  # 更新試算表
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="課表已成功上傳！")
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="上傳圖片失敗，請稍後再試！")
            )

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """處理文字訊息"""
    if event.message.text.lower() == "上傳課表":
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="請上傳您的課表圖片！")
        )


# 主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
