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
import io
import time
import base64
import pytz

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
ALBUM_RANGE_NAME = '相簿!A:A'

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id  # 獲取用戶 ID
    message = event.message.text.strip()  # 獲取並清理用戶的文字訊息

    # 檢查訊息是否匹配「相簿」
    if re.match('相簿', message):
        handle_album_upload(event)  # 執行相簿上傳功能


def handle_album_upload(event):
    """
    處理相簿圖片上傳
    使用者傳送的圖片會上傳到 Imgur，並儲存 URL 至 Google Sheets 的「相簿」工作表。
    """
    user_id = event.source.user_id  # 使用者 ID
    message_content = line_bot_api.get_message_content(event.message.id)  # 獲取圖片訊息內容
    image_data = BytesIO(message_content.content)  # 將圖片轉換成二進制資料流

    # 上傳圖片至 Imgur
    uploaded_url = upload_to_imgur(image_data)
    if uploaded_url:
        try:
            # 將圖片 URL 儲存至「相簿」工作表
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            sheet.values().append(
                spreadsheetId=SHEET_ID,
                range=ALBUM_RANGE_NAME,
                valueInputOption="RAW",
                body={"values": [[uploaded_url]]}
            ).execute()

            # 回應使用者上傳成功
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="圖片已成功上傳至相簿！")
            )
        except HttpError as err:
            print(f"Google Sheets API Error: {err}")
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="儲存圖片失敗，請稍後再試！")
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="上傳圖片失敗，請稍後再試！")
        )

    
def upload_to_imgur(image_data):
    """
    將圖片上傳至 Imgur 並取得圖片的 URL
    :param image_data: 圖片的二進制資料流 (BytesIO)
    :return: 成功則回傳圖片 URL，失敗則回傳 None
    """
    headers = {
        'Authorization': f'Client-ID {IMGUR_CLIENT_ID}',  # Imgur API 的 Client ID
    }
    files = {
        'image': image_data.getvalue(),  # 提交圖片資料流
    }
    response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)
    response_data = response.json()

    if response_data.get('success'):
        return response_data['data']['link']  # 回傳圖片 URL
    else:
        print(f"Imgur Upload Error: {response_data}")
        return None


# 主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
