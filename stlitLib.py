import streamlit as st
import os
import time
from streamlit_option_menu import option_menu   # 메뉴를 꾸미는 라이브러리
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3 as sq
import pandas as pd
from PIL import Image
from jamo import h2j, j2hcj #한글을 자모로 분리하는 라이브러리
import qrcode
import xml.etree.ElementTree as ET


# https://icons.getbootstrap.com/

st.set_page_config(page_title ='도서관 도구', page_icon = "📚") #🛠📚🏛
with st.sidebar:
    choice = option_menu(None, ["오늘의 도서관강좌", "QR코드 만들기"],
                         icons=['brush', 'qr-code'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "4!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#08c7b4"},
    }
    )

if choice == "QR코드 만들기":
    # 한글입력받은 것을 자모 분리하여 영어해당자판으로 바꾸어서 리턴(코라스의 아이디는 한글에 해당하는 영어로 입력되어야함)
    def kortoEng(input_text):
        out_text = ""
        test_dict = {'ㄱ': 'r', 'ㄲ': 'R', 'ㄴ': 's', 'ㄷ': 'e', 'ㄸ': 'E', 'ㄹ': 'f', 'ㅁ': 'a', 'ㅂ': 'q', 'ㅃ': 'Q', 'ㅅ': 't', 'ㅆ': 'T', 'ㅇ': 'd', 'ㅈ': 'w', 'ㅉ': 'W', 'ㅊ': 'c', 'ㅋ': 'z', 'ㅌ': 'x', 'ㅍ': 'v', 'ㅎ': 'g', 'ㅏ': 'k', 'ㅐ': 'o', 'ㅑ': 'i', 'ㅒ': 'O', 'ㅓ': 'j', 'ㅔ': 'p', 'ㅕ': 'u', 'ㅖ': 'P', 'ㅗ': 'h', 'ㅘ': 'hk', 'ㅙ': 'ho', 'ㅚ': 'hl', 'ㅛ': 'y', 'ㅜ': 'n', 'ㅝ': 'nj', 'ㅞ': 'np', 'ㅟ': 'nl', 'ㅠ': 'b', 'ㅡ': 'm', 'ㅢ': 'ml', 'ㅣ': 'l', 'ㄳ': 'rt', 'ㄵ': 'sw', 'ㄶ': 'sg', 'ㄺ': 'fr', 'ㄻ': 'fa', 'ㄼ': 'fq', 'ㄽ': 'ft', 'ㄾ': 'fx', 'ㄿ': 'fv', 'ㅀ': 'fg', 'ㅄ': 'qt'}
        for char in input_text:
            if '가' <= char <= '힣':
                separated_text = j2hcj(h2j(char))
                eng = ''
                for kor in separated_text:
                    eng = test_dict[kor]
                    out_text = out_text + eng
            else:
                out_text = out_text + char
        return out_text

    #st.header("QR코드 생성")
    option = st.selectbox(
        ':joystick: 어떤 QR코드를 만드시겠어요?',
        ('코라스 ID와 비번', '인터넷주소', '와이파이 자동접속'))

    if option == '코라스 ID와 비번':
        #st.subheader("코라스 로그인 아이디 비번입력")
        st.info(f"""* 코라스 로그인시 바코드 리더기로 QR코드를 읽어서 한번에 로그인 하는 QR코드
* 시간경과시 로그인 비번만으로 로그인 하는 QR코드 총 2가지 동시 생성""")
        col1, col2 = st.columns(2)
        with col1:
            kollasId = st.text_input('👭 아이디를 입력하세요')
        with col2:
            kollasPw = st.text_input('🔑 비번을 입력하세요', type="password")
        qrWidth = st.slider(":level_slider: QR코드 크기를 조절하세요",20,400,110)
        btn_clicked = st.button("만들기")
        if btn_clicked and kollasId and kollasPw:
            kollasId = kortoEng(kollasId)
            kollasPw = kortoEng(kollasPw)
            inStr = kollasId + "\t" + kollasPw
            img = qrcode.make(inStr)
            type(img)
            img.save("lib.png")
            qrimg = Image.open("lib.png")
            col3, col4 = st.columns(2)
            with col3:
                st.image(qrimg, width=qrWidth, caption="코라스 ID와 비번")
            # 비번만 나오는 QR동시 생성
            kollasPw = kortoEng(kollasPw)
            inStr = kollasPw
            img = qrcode.make(inStr)
            type(img)
            img.save("libpw.png")
            qrimg = Image.open("libpw.png")
            with col4:
                st.image(qrimg, width=qrWidth-10, caption="코라스 비번만")
            with col3:
                # Image Merge(한번에 한개의 파일만 다운로드 가능하기 때문에 하나로 합침)
                image1 = Image.open('lib.png')
                image2 = Image.open('libpw.png')
                image1_size = image1.size
                image2_size = image2.size
                new_image = Image.new('RGB',(2*image1_size[0], image1_size[1]), (250,250,250))
                new_image.paste(image1,(0,0))
                new_image.paste(image2,(image1_size[0],0))
                new_image.save("kollasQR.png","PNG")
                # 통합한 파일 다운로드
                with open("kollasQR.png", "rb") as f:
                    file_contents = f.read()
                st.download_button(label="다운로드", data=file_contents, key="kollasQR.png", file_name="kollasQR.png")
            # st.warning("다운로드버튼을 누르면 다운로드 폴더에 kollasQR.png 파일을 생성합니다.", icon="✔")
            st.warning('화면출력을 원하시면 Ctrl버튼과 "P"버튼을 동시에 눌러서 바코드가 있는 페이지만 프린트하세요', icon="✔")



    elif option == '인터넷주소':
        intLink = st.text_input(':earth_asia: 인터넷주소를 입력하세요')
        qrWidth = st.slider(":level_slider: QR코드 크기를 조절하세요",20,700,110)
        btn_clicked = st.button("만들기")
        if btn_clicked and intLink:
            img = qrcode.make(intLink)
            type(img)
            img.save("link.png")
            qrimg = Image.open("link.png")
            st.image(qrimg, width=qrWidth, caption="인터넷주소")
            # 파일 다운로드
            with open("link.png", "rb") as f:
                file_contents = f.read()
            st.download_button(label="다운로드", data=file_contents, key="link.png", file_name="link.png")
            # st.warning("다운로드버튼을 누르면 다운로드 폴더에 link.png 파일을 생성합니다.", icon="✔")
            st.warning('화면출력을 원하시면 Ctrl버튼과 "P"버튼을 동시에 눌러서 바코드가 있는 페이지만 프린트하세요', icon="✔")

    elif option == '와이파이 자동접속':
        col1, col2 = st.columns(2)
        with col1:
            wifiId = st.text_input(':satellite_antenna: 아이디(SSID)를 입력하세요')
        with col2:
            wifiPw = st.text_input('🔑 비밀번호을 입력하세요', type="password")
        qrWidth = st.slider(":level_slider: QR코드 크기를 조절하세요",20,700,110)
        btn_clicked = st.button("만들기")
        if btn_clicked and wifiId and wifiPw:
            kollasId = kortoEng(wifiId)
            kollasPw = kortoEng(wifiPw)
            inStr = "WIFI:T:WPA;S:" + wifiId + ";P:" + wifiPw + ";H:;"
            img = qrcode.make(inStr)
            type(img)
            img.save("wifi.png")
            qrimg = Image.open("wifi.png")
            st.image(qrimg, width=qrWidth, caption="와이파이 QR")
            # 파일 다운로드
            with open("wifi.png", "rb") as f:
                file_contents = f.read()
            st.download_button(label="다운로드", data=file_contents, key="wifi.png", file_name="wifi.png")
            #st.warning("다운로드버튼을 누르면 다운로드 폴더에 wifi.png 파일을 생성합니다.", icon="✔")
            st.warning('화면출력을 원하시면 Ctrl버튼과 "P"버튼을 동시에 눌러서 바코드가 있는 페이지만 프린트하세요', icon="✔")


# 화성시통합예약시스템에서 제공하는 openAPI를 이용해서 데이터 받아서 DataFrame으로 만듬
# 한번 데이터를 불러오면 cache해서 똑같은 걸 불러올때는 ttl시간까지는 다시 불러오지 않음
@st.cache_data(show_spinner="화성시통합예약시스템 검색중", ttl="10m")
def crawl_web(url, lib):
    try:
        print("crawl_web접근", lib, datetime.today())
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            tree = ET.fromstring(response.text)
            libNameLi = []
            titleLi = []
            lecForLi = []
            linkLi = []
            lecTimeLi = []
            applyStLi = []
            applyEndLi = []
            lecWeekdayLi = []
            lecDayStLi = []
            lecDayEndLi = []
            applyCntLi = []
            lecPlaceLi =[]
            for tag in tree[1]:
                libNameLi.append(tag.find("INSTITUTION_NM").text)
                titleLi.append(tag.find("LECTURE_NM").text)
                lecForLi.append(tag.find("TARGET_NM").text)
                linkLi.append(tag.find("DETAIL_URL").text)
                lecTimeLi.append(tag.find("LECTURE_BEGIN_HM").text + " ~ " + tag.find("LECTURE_END_HM").text)
                applyStLi.append(tag.find("LECTURE_APPLY_BEGIN_DT").text)
                applyEndLi.append(tag.find("LECTURE_APPLY_END_DT").text)
                lecWeekdayLi.append(tag.find("LECTURE_DAY_OF_WEEK").text)
                lecDayStLi.append(tag.find("LECTURE_BEGIN_YMD").text)
                lecDayEndLi.append(tag.find("LECTURE_END_YMD").text)
                applyCntLi.append(tag.find("APPLY_USER_NUM").text + " / " + tag.find("APPLY_LIMIT_NUM").text)
                lecPlaceLi.append(tag.find("LECTURE_PLACE").text)
            df = pd.DataFrame({'도서관이름':libNameLi,'강좌제목':titleLi,'교육대상':lecForLi,'강좌링크':linkLi,'강좌시간':lecTimeLi,'접수시작일시간':applyStLi,'접수종료일시간':applyEndLi,
                               '강좌요일':lecWeekdayLi,'강좌시작일':lecDayStLi,'강좌종료일':lecDayEndLi,'신청자수':applyCntLi,'교육장소':lecPlaceLi})

            return df
    except Exception as e:
        print(f"Error crawling {url}: {e}")

if choice == "오늘의 도서관강좌":
    cremaX = False
    col1, col2 = st.columns(2)
    with col1:
        lib = st.selectbox(':classical_building: 도서관을 선택하세요.',('진안','병점','태안','중앙이음터','동탄복합','왕배','목동','달빛','두빛','봉담','삼괴','송린','송산','남양','정남','둥지','노을빛','다원','서연','작은도서관'))
    with col2:
        d = st.date_input(":spiral_calendar_pad: 날짜를 선택하세요", datetime.today(), datetime(datetime.today().year,datetime.today().month,1))
        ## datetime.date와 datetime.datetime형식이 안맞아서 날짜를 다시 넣어주어야함
        setDay = datetime(d.year,d.month,d.day)
        # tab과 검색결과에 Display할 날짜, 오늘은 오늘로 표시하고 나머지 일은 날짜를 적는다.
        if setDay == datetime(datetime.today().year,datetime.today().month,datetime.today().day):
            disDay = "오늘"
        else:
            disDay = str(setDay)[:10] + "일"
    st.markdown("""---""")
    tab1, tab2, tab3 = st.tabs(["🎨 " + disDay + ' 도서관강좌', "📝 " + disDay + ' 접수 중인 도서관강좌 ', '🔎 도서관강좌 검색'])
    with tab1:
        starting_url = f"https://yeyak.hscity.go.kr/api/apiLectureList.do?recordCountPerPage=50&searchCondition=contents&searchKeyword={lib}"
        df = crawl_web(starting_url, lib)

        # 강좌요일이 int가 아니고 가끔 1,2,3같이 나열되어서 나온다(주의 하루가 아니고 여러일 할때) 이것을 첫자만 남기고 없앤다
        # xml로 넘어온 데이터는 모두 string이라서 형식을 맞추어 줘야한다.
        df['강좌시작일'] = pd.to_datetime(df['강좌시작일'])
        df['강좌종료일'] = pd.to_datetime(df['강좌종료일'])

        # datetime의 요일 값과 사이트의 요일 값이 달라서 맞춤
        wkDay = datetime.date(setDay).weekday()+1
        # pandas에서는 조건과 조건이 연결될때 반드시 조건 마다 ()를 쳐 주어야한다.
        # 강좌시작일이 선택한 날자이거나 이전이라도 강좌 종료일이 선택한 날보다 미래이면서 요일이 같을때
        # 강좌요일이 1,2,3처럼 요일값이 나열될때가 있어서 str.contains로 검색하여 모두 검색되도록 함
        finalDf = df[(df['강좌시작일'] == setDay) | (((df['강좌시작일'] < setDay) & (df['강좌종료일'] >= setDay)) & (df['강좌요일'].str.contains(str(wkDay))))]
        # 크레마 제외
        if lib == '진안' and df['강좌제목'].str.count('크레마').sum() >= 1:
            cremaX = st.checkbox("크레마제외",True,"crema1")
        if cremaX:
            finalDf = finalDf[~finalDf['강좌제목'].str.contains('크레마')]
        # 진안도서관을 검색해도 다른 항목이 나올때가 있어서 제거
        if lib == '작은도서관':
            lib = '호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉'
        finalDf = finalDf[finalDf['도서관이름'].str.contains(lib)]
        st.success("🎨 " + lib.replace('도서관','').replace('호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉','작은') + "도서관(" + disDay + ") 수업 강좌 " + str(len(finalDf)) + "개가 검색 되었습니다.")
        for ind in finalDf.index:
            st.markdown(f"""|`강좌제목`|[{finalDf["강좌제목"][ind]}]({finalDf["강좌링크"][ind]})|
|------------|-----------------|
|`강좌대상`|{finalDf["교육대상"][ind]} (신청자수: {finalDf["신청자수"][ind]})|
|`수강기간`|{finalDf["강좌시작일"][ind].strftime('%Y-%m-%d') + " ~ " + finalDf["강좌종료일"][ind].strftime('%Y-%m-%d')}|
|`접수기간`|{finalDf["접수시작일시간"][ind] + " ~ " + finalDf["접수종료일시간"][ind]}|
|`강좌시간`|{finalDf["강좌시간"][ind]}|
|`교육장소`|{finalDf["교육장소"][ind]}|
#
""")
            

    with tab2:
        cremaX = False
        if lib == '진안':
            cremaX = st.checkbox("크레마제외",True,"crema2")

        starting_url = f"https://yeyak.hscity.go.kr/api/apiLectureList.do?recordCountPerPage=50&searchCondition=contents&searchKeyword={lib}"

        df = crawl_web(starting_url, lib)
        # xml로 넘어온 데이터는 모두 string이라서 형식을 맞추어 줘야한다.
        def clearDay(x):
            return x[:10]
        df['접수시작일'] = pd.to_datetime(df['접수시작일시간'].apply(clearDay))
        df['접수종료일'] = pd.to_datetime(df['접수종료일시간'].apply(clearDay))

        # pandas에서는 조건과 조건이 연결될때 반드시 조건 마다 ()를 쳐 주어야한다.
        # 강좌시작일이 선택한 날자이거나 이전이라도 강좌 종료일이 선택한 날보다 미래이면서 요일이 같을때
        finalDf = df[(df['접수시작일'] == setDay) | ((df['접수시작일'] < setDay) & (df['접수종료일'] >= setDay))]
        # 크레마 제외
        if cremaX:
            finalDf = finalDf[~finalDf['강좌제목'].str.contains('크레마')]
        # 진안도서관을 검색해도 다른 항목이 나올때가 있어서 제거
        if lib == '작은도서관':
            lib = '호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉'
        finalDf = finalDf[finalDf['도서관이름'].str.contains(lib)]
        st.success("📝 " + lib.replace('도서관','').replace('호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉','작은') + "도서관( " + disDay + ") 접수 강좌 " + str(len(finalDf)) + "개가 검색 되었습니다.")
        #markdown 언어 사용 표 만들기 표사이에 공백을 주기위해 header(#   )를 추가
        for ind in finalDf.index:
            st.markdown(f"""|`강좌제목`|[{finalDf["강좌제목"][ind]}]({finalDf["강좌링크"][ind]})|
|------------|-----------------|
|`강좌대상`|{finalDf["교육대상"][ind]} (신청자수: {finalDf["신청자수"][ind]})|
|`수강기간`|{finalDf["강좌시작일"][ind] + " ~ " + finalDf["강좌종료일"][ind]}|
|`접수기간`|{finalDf["접수시작일시간"][ind] + " ~ " + finalDf["접수종료일시간"][ind]}|
|`강좌시간`|{finalDf["강좌시간"][ind]}|
|`교육장소`|{finalDf["교육장소"][ind]}|
#
""")

    with tab3:
        textIn = st.text_input("검색어를 입력하세요")
        starting_url = f"https://yeyak.hscity.go.kr/api/apiLectureList.do?recordCountPerPage=50&searchCondition=contents&searchKeyword={lib}"

        df = crawl_web(starting_url, lib)

        # 진안도서관을 검색해도 다른 항목이 나올때가 있어서 제거
        if lib == '작은도서관':
            lib = '호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉'
        if textIn:
            finalDf = df[df['강좌제목'].str.contains(textIn)]
            finalDf = finalDf[finalDf['도서관이름'].str.contains(lib)]
            st.success("🔎 " + lib.replace('도서관','').replace('호연|양감|늘봄|기아|마도|샘내|팔탄|커피|비봉','작은') + "도서관 수업 강좌 " + str(len(finalDf)) + "개가 검색 되었습니다.")

            for ind in finalDf.index:
                st.markdown(f"""|`강좌제목`|[{finalDf["강좌제목"][ind]}]({finalDf["강좌링크"][ind]})|
|------------|-----------------|
|`강좌대상`|{finalDf["교육대상"][ind]} (신청자수: {finalDf["신청자수"][ind]})|
|`수강기간`|{finalDf["강좌시작일"][ind] + " ~ " + finalDf["강좌종료일"][ind]}|
|`접수기간`|{finalDf["접수시작일시간"][ind] + " ~ " + finalDf["접수종료일시간"][ind]}|
|`강좌시간`|{finalDf["강좌시간"][ind]}|
|`교육장소`|{finalDf["교육장소"][ind]}|
#
""")
        
