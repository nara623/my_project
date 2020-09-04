import selenium.webdriver as webdriver
import re

url = "https://www.instagram.com/grace1.co.kr__/"

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('disable-gpu')
driver = webdriver.Chrome('C:/Users/nara6/Downloads/chromedriver_win32/chromedriver', options=options)

driver.implicitly_wait(5)
driver.get(url)

profileDesc = driver.find_element_by_class_name('-vDIg').text

#print("profileDesc:", profileDesc)

driver.quit()

#한줄 단위로 잘라서 리스트 만들기
ready = profileDesc
preResult = ready.split('\n')
#print(preResult)

#숫자를 추출하여 리스트로 만듬
numbers = re.findall("\d+", profileDesc)
numbers_str = []
for number in numbers:
  numbers_str.append(str(number))
#print(numbers_str[0])


#for문 돌리면서 numbers에 포함된 숫자일 경우, 스페이스바를 기준으로 뒤에있는 문자를 추출
# (특정 문자열에 포함 여부 판단하는 함수)
#29로 특정하지 않고 numbers에 포함된 숫자인지 여부를 판단할수는 없나?

#날짜와 상품 추출
#스페이스바로 split했을 때 뒤에 아무것도 없을시 에러남 -> if문으로 처리 필요

month = 0
my_09list = []
for item in preResult:
    for i in numbers_str:
        if i in item:
            splite_items = item.split(' ')
            len_item = len(splite_items)
            if len_item > 1:
                day = item.split(' ')[0]
                product = item.split(' ')[1]
                my_09dic = {'month':month, 'day':day, 'product':product}
                my_09list.append(my_09dic)

            if len_item == 1:
                if "월" in item:
                    month = item.split(' ')[0]
            break
print(my_09list)

#구글캘린더 API

from google_auth_oauthlib.flow import InstalledAppFlow

# 구글 클라우드 콘솔에서 다운받은 OAuth 2.0 클라이언트 파일경로
creds_filename = 'C:/Users/nara6/OneDrive/바탕 화면/sparta/client_secret_801342737766-qsk28glnm5kmsr246sq636l449u4qqmo.apps.googleusercontent.com.json'

# 사용 권한 지정
# https://www.googleapis.com/auth/calendar	               캘린더 읽기/쓰기 권한
# https://www.googleapis.com/auth/calendar.readonly	       캘린더 읽기 권한
SCOPES = ['https://www.googleapis.com/auth/calendar']

# 파일에 담긴 인증 정보로 구글 서버에 인증하기
# 새 창이 열리면서 구글 로그인 및 정보 제공 동의 후 최종 인증이 완료됩니다.
flow = InstalledAppFlow.from_client_secrets_file(creds_filename, SCOPES)
creds = flow.run_local_server(port=0)

#서비스 객체 생성
from googleapiclient.discovery import build

service = build('calendar', 'v3', credentials=creds)

#일정 list up
import datetime
today = datetime.datetime.now()
this_year = today.year

#gonggu_month = re.findall("\d+", my_09list[0]["month"])
#gonggu_day = re.findall("\d+", my_09list[0]["day"])
#gonggu_product = my_09list[0]["product"]
#gonggu_month_int = [int (i) for i in gonggu_month]
#gonggu_day_int = [int (i) for i in gonggu_day]
#print(gonggu_month_int)
#print(gonggu_day_int)

#gonggu_list = str(this_year) + "-" + str(gonggu_month_int[0]) + "-" + str(gonggu_day_int[0])
#formatedDate = datetime.datetime.strptime(gonggu_list, '%Y-%m-%d').date()
#print(formatedDate)

#json serializable error 없애기
#변수를 문자열로
#for문으로 my_09list를 yyyy-mm-dd 형식으로 모두 만들기

formatedDate_list = []
for x in my_09list:
    gonggu_month = re.findall("\d+", x["month"])
    gonggu_day = re.findall("\d+", x["day"])
    gonggu_product = x["product"]
    gonggu_month_int = [int(i) for i in gonggu_month]
    gonggu_day_int = [int (i) for i in gonggu_day]

    gonggu_list = str(this_year) + "-" + str(gonggu_month_int[0]) + "-" + str(gonggu_day_int[0])
    formatedDate = datetime.datetime.strptime(gonggu_list, '%Y-%m-%d').date()
    #0000-00-00 format
    formatedDate_list.append({"date09": formatedDate, "product09": gonggu_product})

print(formatedDate_list)

#일정 생성 insert
event = {
        'summary': str(formatedDate_list[1]["product09"]), # 일정 제목
        'location': str(url), # 일정 장소
        'description': ' ', # 일정 설명
        'start': { # 시작 날짜
            'date': str(formatedDate_list[1]["date09"]),
            'timeZone': 'Asia/Seoul',
        },
        'end': { # 종료 날짜
            'date': str(formatedDate_list[1]["date09"]),
            'timeZone': 'Asia/Seoul',
        },

        'reminders': { # 알림 설정
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60}, # 24 * 60분 = 하루 전 알림
                {'method': 'popup', 'minutes': 10}, # 10분 전 알림
            ],
        },
    }

# calendarId : 캘린더 ID. primary이 기본 값입니다.
event = service.events().insert(calendarId='rqo73vvah50f2jn0026km9c27c@group.calendar.google.com', body=event).execute()
print('Event created: %s' % (event.get('htmlLink')))


