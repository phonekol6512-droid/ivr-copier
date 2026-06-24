import requests
from flask import Flask, request, make_response

app = Flask(__name__)

# כתובת ה-API הרשמית והמעודכנת של ימות המשיח
YEMOT_API_URL = "https://www.call2all.co.il/ym/api/"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    # קבלת המשתנים שהגדרת בפורמט ה-read שלך
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # שלבי בקשת הנתונים - משתמש בדיוק בפורמט שעובד לך!
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

    # ביצוע ההעתקה בפועל מול ה-API של ימות המשיח
    try:
        # יצירת ה-Tokens בפורמט הרשמי שלהם (מערכת:סיסמה)
        token_src = f"{system_src.strip()}:{pass_src.strip()}"
        token_dst = f"{system_dst.strip()}:{pass_dst.strip()}"
        
        # ניקוי פורמט נתיבי השלוחות (למשל: ivr/1/)
        path_src = f"ivr/{ext_src.strip('/')}/"
        path_dst = f"ivr/{ext_dst.strip('/')}/"

        # 1. הורדת קובץ ה-ext.ini ממערכת המקור
        # ה-API הרשמי דורש שליחת token ו-path לקובץ הספציפי
        download_url = f"{YEMOT_API_URL}DownloadFile"
        params_src = {
            "token": token_src,
            "path": f"{path_src}ext.ini"
        }
        src_response = requests.get(download_url, params=params_src)

        # בדיקה אם הקובץ הורד בהצלחה או שהפרטים שגויים
        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text or "לא נמצא" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים או שהשלוחה לא קיימת.")

        ini_content = src_response.text

        # 2. העלאת קובץ ה-ext.ini למערכת היעד
        # שליחת הקובץ בפורמט Multipart Form-Data הרשמי הנדרש ב-UploadFile
        upload_url = f"{YEMOT_API_URL}UploadFile"
        data_dst = {
            "token": token_dst,
            "path": path_dst,
            "convertAudio": "0" # מונע מהם לנסות להמיר קובץ טקסט לשמע
        }
        files = {
            'file': ('ext.ini', ini_content, 'text/plain')
        }
        
        dst_response = requests.post(upload_url, data=data_dst, files=files)

        # בדיקה האם השרת החזיר סטטוס OK של ימות המשיח
        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. השלוחה הועתקה.")
        else:
            return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד. אנא בדוק את הפרטים.")

    except Exception as e:
        # במקרה חרום, נדפיס את השגיאה האמיתית לתוך ה-Logs ב-Render
        print(f"API Error: {str(e)}")
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת עם השרתים.")

def ym_read(var_name, text):
    # הפורמט המדויק שאתה מצאת ועובד פיקס!
    res = make_response(f"read={text}={var_name},4,12,1,Digits")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

__all__ = ['app']
