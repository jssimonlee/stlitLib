import streamlit as st
import os
import time
from streamlit_option_menu import option_menu
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3 as sq
    

# https://icons.getbootstrap.com/

with st.sidebar:
    choice = option_menu(None, ["Upload", "Download", "오늘의 도서관강좌"],
                         icons=['cloud-upload', 'cloud-download', 'brush'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "4!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#08c7b4"},
    }
    )

if choice == "오늘의 도서관강좌":
    def crawl_web(url):
        global setDay
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')
                titleData = soup.find_all('p', attrs = {'class':'title'})
                contentData = soup.find_all('div', attrs = {'class':'info on'})
                # 모든 id 데이터를 찾아서 db에 넘겨서 있는지 검색
                idList = [item.find('a').attrs['href'].split('=')[-1] for item in titleData]
                fetchList = fetch_data(idList)
                #st.write(fetchList)
                for index, each in enumerate(titleData):
                    # 강좌 시작일
                    lecStDay = contentData[index].find_all('span')[1].get_text()[7:].split(' ~ ')[0]
                    # 강좌 종료일
                    lecEndDay = contentData[index].find_all('span')[1].get_text()[7:].split(' ~ ')[1]
                    # 강좌 시작일과 종료일을 datetime형식으로 변환
                    start = datetime(int(lecStDay.split('-')[0]),int(lecStDay.split('-')[1]),int(lecStDay.split('-')[2]))
                    end = datetime(int(lecEndDay.split('-')[0]),int(lecEndDay.split('-')[1]),int(lecEndDay.split('-')[2]))
                    # 오늘과 시작일을 비교(today함수는 시간까지 나오기 때문에 날짜만 나오는 시작 끝 시간과 계산을 통해 값을 추정해야함)
                    timedifSt = start - setDay
                    timedifEnd = end - setDay
                    idNum = each.find('a').attrs['href'].split('=')[-1]
                    # 시작일이 오늘이상이거나 종료일이 오늘 또는 미래인 것만 검색
                    if  (timedifSt.days >=0 or timedifEnd.days >=0) and (idNum in fetchList):
                        # 제목에 불필요한 번호가 .과 함께 있어서 제거
                        titlePos = each.get_text().splitlines()[1].find('.')
                        title = each.get_text().splitlines()[1][titlePos+1:].strip()
                        preText = [idNum, title, each.get_text().splitlines()[2], each.find('a').attrs['href'], contentData[index].find_all('span')[1].get_text().split(':')[1].strip(), contentData[index].find_all('span')[3].get_text().split(':')[1].strip()]
                        # 여기서 보낸건 모두 db에 저장
                        if "크레마" not in title:
                            crawl_yeyak(each.find('a').attrs['href'], preText)
        
        except Exception as e:
            st.write(f"Error crawling {url}: {e}")

    # 예약사이트 크롤링(여기에 들어온 건 모두 db에 저장)
    def crawl_yeyak(url, dataList):
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')
                titleData = soup.find_all('ul', attrs = {'class':'detail-info-list'})
                findFlag = False
                # db에 저장하기위해서 저장항목을 리스트로 만듬
                for each in titleData:
                    smtitle = each.find_all('dt')
                    smcontent = each.find_all('dd')
                    for index1, each1 in enumerate(smtitle):
                        if each1.get_text().strip() == "요일/시간":
                            # 강좌일자
                            lecTime = smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n","")
                            dataList.append(lecTime)
                        if each1.get_text().strip() == "장소":
                            lecPlace = smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n","")
                            dataList.append(lecPlace)
                            # db에 데이터 넣기
                            insert_data(dataList)
                            
        except Exception as e:
            st.write(f"Error crawling {url}: {e}")


    # db에 id가 있는지 확인(있으면 출력, 없는 건 리스트로 돌려줌)
    def fetch_data(idList):
        conn = sq.connect("libLec.db")
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS lec (id integer primary key, title text, lecFor text, link text, lecDay text, applyCnt text, lecTime text, lecPlace text)")
        rtList = []
        for data in idList:
            # 입력받은 리스트의 id가 있는지 확인하고 없으면 돌려주고 있으면 표시한다.
            c.execute("SELECT EXISTS(SELECT 1 FROM lec WHERE id = ?)", (data,))
            result = c.fetchone()[0]
            if result == 0:
                rtList.append(data)
            else:
                c.execute("SELECT * FROM lec WHERE id = ?", (data,))
                results = c.fetchall()
                if results:
                    for row in results:
                        dayMatchCheck(row)
        conn.close()
        return rtList


    # db에 data입력
    def insert_data(dataList):
        conn = sq.connect("libLec.db")
        c = conn.cursor()
        c.execute("INSERT INTO lec (id,title,lecFor,link,lecDay,applyCnt,lecTime,lecPlace) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (dataList[0], dataList[1], dataList[2], dataList[3], dataList[4], dataList[5], dataList[6], dataList[7]))
        conn.commit()
        conn.close()    


    # 화면에 표시하는 함수
    def display(dataList):
        global totalCnt
        totalCnt = totalCnt + 1
        st.write("제목: " + dataList[1])
        st.write("대상: " + dataList[2])
        st.write("링크: " + dataList[3])
        st.write("일자: " + dataList[4])
        st.write("인원: " + dataList[5])
        st.write("시간: " + dataList[6])
        st.write("장소: " + dataList[7])
        st.markdown("""---""")
        st.write("\n")


    # 시작일과 종료일을 받아서 선정한 날짜와 맞는지 확인
    def dayMatchCheck(dataList):
        # 강좌 시작일
        lecStDay = dataList[4].split(' ~ ')[0].strip()
        # 강좌 종료일
        lecEndDay = dataList[4].split(' ~ ')[1].strip()
        # 강좌 시작일과 종료일을 datetime형식으로 변환
        start = datetime(int(lecStDay.split('-')[0]),int(lecStDay.split('-')[1]),int(lecStDay.split('-')[2]))
        end = datetime(int(lecEndDay.split('-')[0]),int(lecEndDay.split('-')[1]),int(lecEndDay.split('-')[2]))
        global setDay
        timedifSt = start - setDay
        timedifEnd = end - setDay
        wkdayList = ["월","화","수","목","금","토","일"]
        wkDay = wkdayList[datetime.date(setDay).weekday()]
        if (timedifSt.days == 0) or (timedifSt.days < 0 and timedifEnd.days >= 0) and wkDay == dataList[6][0]:
            display(dataList)


        
    # Define the starting URL and depth of crawling
    starting_url = 'https://www.hscitylib.or.kr/jalib/menu/11257/program/30021/lectureList.do?currentPageNo=1&statusCd=&targetCd=&searchCondition=title'
                    #https://www.hscitylib.or.kr/jalib/menu/11257/program/30021/lectureList.do?targetCd=&statusCd=&searchCondition=title&searchKeyword=
    #starting_url = 'https://www.hscitylib.or.kr/iutlib/menu/11388/program/30021/lectureList.do?currentPageNo=1&statusCd=&targetCd='

    # Start crawling
    d = st.date_input("날짜를 선택하세요", datetime.today())
    st.markdown("""---""")
    # datetime.date와 datetime.datetime형식이 안맞아서 날짜를 다시 넣어주어야함
    setDay = datetime(d.year,d.month,d.day)
    totalCnt = 0

        
    crawl_web(starting_url)
    crawl_web(starting_url.replace("No=1","No=2"))
    ##crawl_web(starting_url.replace("No=1","No=3"))
    st.write(str(totalCnt) + "개가 검색 되었습니다.")

