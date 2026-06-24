import requests
from flask import Flask, request, make_response

app = Flask(__name__)

YEMOT_API_URL = "https://www.call2all.co.il/ym/api/"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # שימוש בפורמט המנצח והמדויק שאתה פיצחת!
    if not system_src: return ym_read("system_src", "t-אנא הקישו את מספר המערכת שברצונכם להעתיק ממנה את השלוחה, בסיום הקישו סולמית")
    if not pass_src:   return ym_read("pass_src", "t-אנא הקישו את סיסמת המערכת, בסיום הקישו סולמית")
    if not ext_src:    return ym_read("ext_src", "t- אנא הקישו את מספר השלוחה אותה תרצו להעתיק, ובסיום הקישו סולמית, לתת תיקייה הקישו כוכבית בין תיקייה לתיקייה")
    if not system_dst: return ym_read("system_dst", "t-אנא הקישו את מספר המערכת אליה ברצונכם להעתיק את השלוחה, ובסיום הקישו סולמית")
    if not pass_dst:   return ym_read("pass_dst", "t-אנא הקישו את סיסמת המערכת, בסיום הקישו סולמית")
    if not ext_dst:    return ym_read("ext_dst", "t-אנא הקישו את השלוחה אליה ברצונכם להעתיק את ההגדרות, בסיום הקישו סולמית, לתת תיקייה הקישו כוכבית בין תיקייה לתיקייה")

    try:
        token_src = f"{system_src.strip()}:{pass_src.strip()}"
        token_dst = f"{system_dst.strip()}:{pass_dst.strip()}"
        
        # ניקוי המחרוזת והחלפת כוכביות ללוכסנים בצורה תקינה ומאובטחת
        clean_src = ext_src.strip().replace('*', '/').replace('-', '/').strip('/')
        clean_dst = ext_dst.strip().replace('*', '/').replace('-', '/').strip('/')
        
        # בניית הנתיב המדויק לפי הספר של ימות המשיח
        path_src = f"ivr2:/{clean_src}/ext.ini"
        path_dst = f"ivr2:/{clean_dst}/ext.ini"

        # 1. הורדת הקובץ ממערכת המקור
        download_url = f"{YEMOT_API_URL}DownloadFile"
        src_response = requests.get(download_url, params={"token": token_src, "path": path_src})

        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text or "לא נמצא" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים או שהשלוחה לא קיימת.")

        ini_content = src_response.text

        # 2. העלאת הקובץ למערכת היעד
        upload_url = f"{YEMOT_API_URL}UploadTextFile?token={token_dst}&what={path_dst}&contents={requests.utils.quote(ini_content)}"
        dst_response = requests.post(upload_url)

        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. פון קול כל מה שצריך במקום אחד.")
        else:
            return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד.")

    except Exception as e:
        print(f"API Error: {str(e)}")
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת עם השרתים.")

def ym_read(var_name, text):
    # הפורמט המדויק והבדוק שלך!
    res = make_response(f"read={text}={var_name},4,12,1,Digits")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

__all__ = ['app']
