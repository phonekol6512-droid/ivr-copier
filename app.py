import requests
from flask import Flask, request, make_response

app = Flask(__name__)

# כתובת ה-API הרשמית של ימות המשיח
YEMOT_API_URL = "https://www.call2all.co.il/ym/api/"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    # קבלת המשתנים שהגדרת בפורמט ה-read שעובד לך פיקס!
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # ניהול שלבי בקשת הנתונים (הנוסחה המנצחת שלך)
    if not system_src: 
        return ym_read("system_src", "t-אנא הקישו את מספר מערכת המקור ובסיומה סולמית")
    if not pass_src: 
        return ym_read("pass_src", "t-אנא הקישו את סיסמת מערכת המקור ובסיומה סולמית")
    if not ext_src: 
        return ym_read("ext_src", "t-אנא הקישו את מספר השלוחה להעתקה ובסיומה סולמית")
    if not system_dst: 
        return ym_read("system_dst", "t-אנא הקישו את מספר מערכת היעד ובסיומה סולמית")
    if not pass_dst: 
        return ym_read("pass_dst", "t-אנא הקישו את סיסמת מערכת היעד ובסיומה סולמית")
    if not ext_dst: 
        return ym_read("ext_dst", "t-אנא הקישו את שלוחת היעד החדשה ובסיומה סולמית")

    # תהליך ההעתקה בפועל
    try:
        # בניית ה-Tokens הרשמיים (מספר:סיסמה)
        token_src = f"{system_src.strip()}:{pass_src.strip()}"
        token_dst = f"{system_dst.strip()}:{pass_dst.strip()}"
        
        # ניקוי פורמט נתיבי השלוחות
        path_src = f"ivr/{ext_src.strip('/')}/"
        path_dst = f"ivr/{ext_dst.strip('/')}/"

        # 1. הורדת הקובץ ממערכת המקור
        download_url = f"{YEMOT_API_URL}DownloadFile"
        params_src = {
            "token": token_src,
            "path": f"{path_src}ext.ini"
        }
        src_response = requests.get(download_url, params=params_src)

        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text or "לא נמצא" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים או שהשלוחה לא קיימת.")

        ini_content = src_response.text

        # 2. העלאת הקובץ למערכת היעד באמצעות הפקודה הייעודית UploadTextFile לטקסט
        # מעבירים את ה-token, ה-path ואת ה-fileName ישירות ב-URL, ואת התוכן בפרמטר contents
        upload_url = f"{YEMOT_API_URL}UploadTextFile"
        data_dst = {
            "token": token_dst,
            "path": path_dst,
            "fileName": "ext.ini",
            "contents": ini_content
        }
        
        dst_response = requests.post(upload_url, data=data_dst)

        # בדיקה האם השרת החזיר תגובת הצלחה תקינה
        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. השלוחה הועתקה.")
        else:
            return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד. אנא בדוק את הפרטים.")

    except Exception as e:
        print(f"API Error: {str(e)}")
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת עם השרתים.")

def ym_read(var_name, text):
    # הפורמט המדויק שפיצחת שעובד קבוע!
    res = make_response(f"read={text}={var_name},4,12,1,Digits")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

__all__ = ['app']
