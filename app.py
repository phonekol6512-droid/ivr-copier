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

    if not system_src: return ym_read("system_src", "t-נא הקש את מספר מערכת המקור, ובסיומה סולמית")
    if not pass_src: return ym_read("pass_src", "t-נא הקש את סיסמת מערכת המקור, ובסיומה סולמית")
    if not ext_src: return ym_read("ext_src", "t-נא הקש את מספר השלוחה להעתקה, ובסיומה סולמית")
    if not system_dst: return ym_read("system_dst", "t-נא הקש את מספר מערכת היעד, ובסיומה סולמית")
    if not pass_dst: return ym_read("pass_dst", "t-נא הקש את סיסמת מערכת היעד, ובסיומה סולמית")
    if not ext_dst: return ym_read("ext_dst", "t-נא הקש את שלוחת היעד החדשה, ובסיומה סולמית")

    try:
        path_src = f"/ivr/{ext_src.strip('/')}/"
        path_dst = f"/ivr/{ext_dst.strip('/')}/"
        src_response = requests.get(f"{YEMOT_API_URL}DownloadFile?token={system_src}:{pass_src}&path={path_src}ext.ini")

        if src_response.status_code != 200 or "הסיסמא שגויה" in src_response.text:
            return ym_say_and_hangup("t-שגיאה. נתוני מערכת המקור שגויים.")

        dst_response = requests.post(
            f"{YEMOT_API_URL}UploadFile?token={system_dst}:{pass_dst}&path={path_dst}&fileName=ext.ini",
            files={'file': ('ext.ini', src_response.text, 'text/plain')}
        )

        if dst_response.status_code == 200 and '"responseStatus":"OK"' in dst_response.text:
            return ym_say_and_hangup("t-ההעתקה בוצעה בהצלחה.")
        return ym_say_and_hangup("t-שגיאה בהעלאת הנתונים למערכת היעד.")
    except:
        return ym_say_and_hangup("t-התרחשה שגיאה בתקשורת.")

def ym_read(var_name, text):
   res = make_response(f"read={text}={var_name},1,10,7,Digits")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

def ym_say_and_hangup(text):
    res = make_response(f"id_list_message={text}")
    res.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return res

