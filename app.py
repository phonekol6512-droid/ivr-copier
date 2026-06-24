import requests
from flask import Flask, request, make_response

app = Flask(__name__)

YEMOT_API_URL = "https://call2all.co.il"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # ניהול שלבי בקשת הנתונים (הפורמט המנצח שלך)
    # הוספנו הנחיה במלל למאזין להקיש כוכבית בין השלוחות הפנימיות
    if not system_src: return ym_read("system_src", "t-אנא הקישו את מספר מערכת המקור ובסיומה סולמית")
    if not pass_src:   return ym_read("pass_src", "t-אנא הקישו את סיסמת מערכת המקור ובסיומה סולמית")
    if not ext_src:    return ym_read("ext_src", "t-אנא הקישו את מספר השלוחה. לשלוחה פנימית הקישו כוכבית בין שלוחה לשלוחה, ובסיומה סולמית")
    if not system_dst: return ym_read("system_dst", "t-אנא הקישו את מספר מערכת היעד ובסיומה סולמית")
    if not pass_dst:   return ym_read("pass_dst", "t-אנא הקישו את סיסמת מערכת היעד ובסיומה סולמית")
    if not ext_dst:    return ym_read("ext_dst", "t-אנא הקישו את שלוחת היעד החדשה. לשלוחה פנימית הקישו כוכבית, ובסיומה סולמית")

    try:
        token_src = f"{system_src.strip()}:{pass_src.strip()}"
        token_dst = f"{system_dst.strip()}:{pass_dst.strip()}"
        
        # ניקוי והחלפת כוכביות או מקפים ללוכסנים עבור שלוחות פנימיות
        shluha_src = ext_src.replace('*', '/').replace('-', '/').strip('/')
        shluha_dst = ext_dst.replace('*', '/').replace('-', '/').strip('/')
        
        # בניית הנתיב המדויק ל-API (למשל: ivr2:/1/5/2/ext.ini)
        path_src = f"ivr2:/{shluha_src}/ext.ini"
        path_dst = f"ivr2:/{shluha_dst}/ext.ini"

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
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. השלוחה הועתקה.")
        else:
            return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד.")

    except Exception as e:
        print(f"API Error: {str(e)}")
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת עם השרתים.")

def ym_read(var_name, text):
    # הפורמט המנצח שלך! (הגדלנו ל-20 ספרות כדי לתמוך בשלוחות פנימיות ארוכות)
    res = make_response(f"read={text}={var_name},4,20,1,Digits")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

__all__ = ['app']
