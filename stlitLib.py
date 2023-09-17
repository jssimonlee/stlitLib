import streamlit as st
import os
import time
from streamlit_option_menu import option_menu

    
##with st.sidebar:
##    with st.echo():
##        st.write("This code will be st.writeed to the sidebar.")
##
##    with st.spinner("Loading..."):
##        time.sleep(5)
##    st.success("Done!")

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
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime


    # Function to crawl a web page and extract links
    def crawl_web(url):  
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')
                titleData = soup.find_all('p', attrs = {'class':'title'})
                contentData = soup.find_all('div', attrs = {'class':'info on'})
                for index, each in enumerate(titleData):
                    
                    # 강좌 시작일
                    lecStDay = contentData[index].find_all('span')[1].get_text()[7:].split(' ~ ')[0]
                    # 강좌 종료일
                    lecEndDay = contentData[index].find_all('span')[1].get_text()[7:].split(' ~ ')[1]
                    # 강좌 시작일과 종료일을 datetime형식으로 변환
                    start = datetime(int(lecStDay.split('-')[0]),int(lecStDay.split('-')[1]),int(lecStDay.split('-')[2]))
                    end = datetime(int(lecEndDay.split('-')[0]),int(lecEndDay.split('-')[1]),int(lecEndDay.split('-')[2]))
                    # 오늘과 시작일을 비교(today함수는 시간까지 나오기 때문에 날짜만 나오는 시작 끝 시간과 계산을 통해 값을 추정해야함) 
                    timedifSt = setDay - start
                    timedifEnd = end - setDay
                    # 크레마를 제거하기위해
                    if "크레마" not in each.get_text().splitlines()[1].split('.')[1].strip():
                        if (timedifSt.days < 1 and timedifSt.days >= 0):
                            # 강좌 제목, 강좌링크, 강좌일자, 신청자수를 리스트로 만들어서 함수에 넘겨서 함수에서 프린트하도록함
                            preText = [each.get_text().splitlines()[1].split('.')[1].strip(), "강좌상세링크: " + each.find('a').attrs['href'], contentData[index].find_all('span')[1].get_text(), contentData[index].find_all('span')[3].get_text()]
                            crawl_yeyak(each.find('a').attrs['href'], preText)
                        elif  timedifSt.days >= 0 and timedifEnd.days > 0:
                            # 강좌 제목, 강좌링크, 강좌일자, 신청자수를 리스트로 만들어서 함수에 넘겨서 함수에서 프린트하도록함
                            preText = [each.get_text().splitlines()[1].split('.')[1].strip(), "강좌상세링크: " + each.find('a').attrs['href'], contentData[index].find_all('span')[1].get_text(), contentData[index].find_all('span')[3].get_text()]
                            crawl_yeyak(each.find('a').attrs['href'], preText)
        
        except Exception as e:
            st.write(f"Error crawling {url}: {e}")

    # 예약사이트 크롤링
    def crawl_yeyak(url, preText):
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            global totalCnt
            # Check if the request was successful
            wkdayList = ["월","화","수","목","금","토","일"]
            wkDay = wkdayList[datetime.date(setDay).weekday()]
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')
                titleData = soup.find_all('ul', attrs = {'class':'detail-info-list'})
                findFlag = False
                for each in titleData:
                    smtitle = each.find_all('dt')
                    smcontent = each.find_all('dd')
                    for index1, each1 in enumerate(smtitle):
                        pickList = ["요일/시간","교육대상","장소"]
                        if each1.get_text().strip() in pickList:
                            if each1.get_text().strip() == "요일/시간":
                                # 요일은 첫번째글자에서 가져오고 크레마는 월,화,수,목,금,토,일로 되어있기 때문에 두번째 글자가 콤마 인것을 제거하면 크레마는 제거된다(크레마 신청이 너무 많아서 제외하기 위해)
                                if wkDay == smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n","")[0] and smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n","")[1] != ",":
                                    for txt in preText:
                                        st.write(txt)
                                    st.write(each1.get_text().strip(),':', smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n",""))
                                    findFlag = True
                            if findFlag and each1.get_text().strip() == "교육대상":
                                st.write(each1.get_text().strip(),':', smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n",""))
                            if findFlag and each1.get_text().strip() == "장소":
                                st.write(each1.get_text().strip(),':', smcontent[index1].get_text().strip().replace("\t","").replace("  ","").replace("\n",""))
                                st.divider()
                                st.write("\n")
                                findFlag = False
                                totalCnt = totalCnt + 1
        
        except Exception as e:
            st.write(f"Error crawling {url}: {e}")
            

    # Define the starting URL and depth of crawling
    starting_url = 'https://www.hscitylib.or.kr/jalib/menu/11257/program/30021/lectureList.do?targetCd=&statusCd=finish&currentPageNo=1&searchCondition=title&searchKeyword='
    #starting_url = 'https://www.hscitylib.or.kr/jalib/menu/11257/program/30021/lectureList.do?currentPageNo=1&statusCd=&targetCd=&searchCondition=title'
                    #https://www.hscitylib.or.kr/jalib/menu/11257/program/30021/lectureList.do?targetCd=&statusCd=&searchCondition=title&searchKeyword=
    #starting_url = 'https://www.hscitylib.or.kr/iutlib/menu/11388/program/30021/lectureList.do?currentPageNo=1&statusCd=&targetCd='

    # Start crawling
    d = st.date_input("날짜를 선택하세요", datetime.today())
    # datetime.date와 datetime.datetime형식이 안맞아서 날짜를 다시 넣어주어야함
    setDay = datetime(d.year,d.month,d.day)
    totalCnt = 0    
    crawl_web(starting_url)
    crawl_web(starting_url.replace("No=1","No=2"))
    ##crawl_web(starting_url.replace("No=1","No=3"))
    st.write(str(totalCnt) + "개가 검색되었습니다.")


