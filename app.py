import requests
from flask import Flask, request, make_response

app = Flask(__name__)
YEMOT_API_URL = "https://call2all.co.il"

@app.route('/copy-module', methods=['GET', 'POST'])
def copy_module():
    # קבלת כל הנתונים שימות המשיח כבר אספה מהמאזין בבטחה
    system_src = request.values.get('system_src')
    pass_src = request.values.get('pass_src')
    ext_src = request.values.get('ext_src')
    
    system_dst = request.values.get('system_dst')
    pass_dst = request.values.get('pass_dst')
    ext_dst = request.values.get('ext_dst')

    # הגנה: אם אחד הנתונים חסר, המערכת לא תבצע העתקה שגויה
    if not all([system_src, pass_src, ext_src, system_dst, pass_dst, ext_dst]):
        return ym_say_and_hangup("t-שגיאה. לא התקבלו כל הנתונים הדרושים מהמערכת.")

    try:
        path_src = f"/ivr/{ext_src.strip('/')}/"
        path_dst = f"/ivr/{ext_dst.strip('/')}/"
        
        # 1. הורדת קובץ ה-ext.ini ממערכת המקור
        src_response = requests.get(f"{YEMOT_API_URL}DownloadFile?token={system_src}:{pass_src}&path={path_src}ext.ini")

        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים או שהשלוחה לא קיימת.")

        # 2. העלאת קובץ ה-ext.ini למערכת היעד
        dst_response = requests.post(
            f"{YEMOT_API_URL}UploadFile?token={system_dst}:{pass_dst}&path={path_dst}&fileName=ext.ini",
            files={'file': ('ext.ini', src_response.text, 'text/plain')}
        )

        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה. השלוחה הועתקה.")
        return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד.")
        
    except Exception as e:
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת עם שרתי ה-API.")

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

__all__ = ['app']

