import requests
url = "http://fcm.googleapis.com/fcm/send"
def send_push_notification(path, name):

    payload = "{\r\n\t\"data\": {\r\n\t\t\"image\": \"" + path + "\",\r\n\t\t\"title\": \"" + name + "\",\r\n\t\t\"body\": \"" + name + " has just entered the lobby, He is a returning premium, platinum customer.\",\r\n\t\t\"AnotherActivity\": \"True\"\r\n\t},\r\n\t\"registration_ids\" : [\"daqEjnaoV8Q:APA91bH_rldCc-4q1DIm4528sYraj4OL7ApToEleVaV_yx1soc7kYsGmSx8Bhbx69j18tL1poY0ow3oRK6bRpJhGMSLieR066nug2MzkUSGTWfQ-wpBKiLdoy5KGXD5Sz-r4RlQZO8L8\",\r\n\t\"dkwrOBNh1fQ:APA91bErtEfp0tw2e7upEHJ4FW5s7bkKV9Xh3eMfCivYPOr3ghJ95SFLguSoijleJQNM5lsuw43EgIrHSWo19Hx6vELEBpezkX6D_WO96FgvIrTvx_eXy3qvaaxlcGEXoNL9HtjiFtHO\"]\r\n}\r\n"
    headers = {
        'Content-Type': "application/json",
        'Authorization': "key=AAAA7Hzd-jo:APA91bGk3wVFAYWlHLO-0KZOsgxinaM5jw-d4zkG5_5Pxl-IrpeN2cctFNC1ChoHT7RXv52AiHMaOPQeUUbjh3N7IQdPMVF4XUc1e1WFSfApic8P7Lxl4Y2TGhIDVvOBWSM-E-sHA6TM",
        'cache-control': "no-cache",
        'Postman-Token': "275ab208-149e-460b-a109-8119595b1bd3"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    return response
