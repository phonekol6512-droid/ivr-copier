import os
import requests
from flask import Flask, request, make_response

app = Flask(__name__)

# כתובת ה-API הרשמית של ימות המשיח
YEMOT_API_URL = "https://call2all.co.il"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    # קבלת הפרמטרים הנוכחיים מהשיחה
    # אם המשתמש מקיש נתון, ימות המשיח שולחת אותו בפרמטר ששמו כפי שהגדרנו ב-read
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # שלב 1: בקשת נתוני מקור (מאיפה להעתיק)
    if not system_src:
        return ym_read("system_src", "t-נא הקש את מספר מערכת המקור, ובסיומה סולמית")
    if not pass_src:
        return ym_read("pass_src", "t-נא הקש את סיסמת מערכת המקור, ובסיומה סולמית")
    if not ext_src:
        return ym_read("ext_src", "t-נא הקש את מספר השלוחה להעתקה, ובסיומה סולמית")

    # שלב 2: בקשת נתוני יעד (לאן להעתיק)
    if not system_dst:
        return ym_read("system_dst", "t-נא הקש את מספר מערכת היעד, ובסיומה סולמית")
    if not pass_dst:
        return ym_read("pass_dst", "t-נא הקש את סיסמת מערכת היעד, ובסיומה סולמית")
    if not ext_dst:
        return ym_read("ext_dst", "t-נא הקש את שלוחת היעד החדשה, ובסיומה סולמית")

    # שלב 3: ביצוע ההעתקה בפועל מאחורי הקלעים באמצעות ה-API
    try:
        # תיקון פורמט נתיב השלוחה (לוודא שמתחיל ומסתיים בלוכסן, למשל /ivr/1/)
        path_src = f"/ivr/{ext_src.strip('/')}/"
        path_dst = f"/ivr/{ext_dst.strip('/')}/"

        # 1. קריאת קובץ ההגדרות ext.ini ממערכת המקור
        # (הערה: עבור העתקת הגדרות בלבד. אם יש קבצי שמע, נדרש לרוקן/להעתיק את רשימת הקבצים)
        src_file_url = f"{YEMOT_API_URL}DownloadFile?token={system_src}:{pass_src}&path={path_src}ext.ini"
        src_response = requests.get(src_file_url)

        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים או שהקובץ אינו קיים.")

        ini_content = src_response.text

        # 2. העלאת קובץ ההגדרות ext.ini למערכת היעד
        upload_url = f"{YEMOT_API_URL}UploadFile?token={system_dst}:{pass_dst}&path={path_dst}&fileName=ext.ini"
        
        # שליחת התוכן כקובץ text/plain
        files = {'file': ('ext.ini', ini_content, 'text/plain')}
        dst_response = requests.post(upload_url, files=files)

        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. השלוחה הועתקה.")
        else:
            return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד. אנא בדוק את הפרטים.")

    except Exception as e:
        return ym_say_and_hangup("t-תרחשה שגיאה בתקשורת עם השרתים.")

# פונקציות עזר ליצירת תגובות בפורמט של ימות המשיח
def ym_read(var_name, text_to_say):
    """מנחה את המערכת להקריא טקסט ולשמור את ההקשה של המשתמש למשתנה"""
    response_str = f"read={text_to_say}=f,{var_name},1,10,7,No,yes,no"
    response = make_response(response_str)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

def ym_say_and_hangup(text_to_say):
    """משמיע הודעה ומנתק/חוזר לשלוחה קודמת"""
    response_str = f"id_list_message={text_to_say}"
    response = make_response(response_str)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

if __name__ == '__main__':
    app.run(port=5000)
