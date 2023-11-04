# This is a douban Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from bs4 import BeautifulSoup  # web page analysis
import re  # Regular express analysis
import sys
import urllib.error, urllib.request  # setURL, obtain the web content
import xlwt  # excel operation
import sqlite3 # SQLite database operation

FIND_HREF = re.compile(r'<a href="(.*?)">')
FIND_IMAGE = re.compile(r'<img.*src="(.*?)"', re.S)
FIND_TITLE = re.compile(r'<span class="title">(.*?)</span>')
FIND_RATING = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
FIND_RATENUMBER = re.compile(r'<span>(\d*)人评价</span>')
FIND_INQ = re.compile(r'<span class="inq">(.*?)</span>')
FIND_BRIEFINTRO = re.compile(r'<p class="">(.*?)</p>', re.S)


def main():
    baseurl = 'https://movie.douban.com/top250?start='
    datalist = getdata(baseurl)

    # save data to the excel
    # savepath = 'doubantop250_2023_Nov.xls'
    # savedata(savepath, datalist)

    # save data to the database using SQLite
    database_save_path: str = 'doubantop250.db'
    save_data_to_database(database_save_path, datalist)
    print('Web Crawling Finished')  # Press Ctrl+F8 to toggle the breakpoint.


# getting data from internet
def getdata(baseurl):
    datalist = []
    print('getting the data from internet', baseurl)
    for page in range(10):
        url = baseurl + str(page * 25)
        html = geturl(url)

        # analysis the page
        bs = BeautifulSoup(html, "html.parser")
        for item in bs.find_all('div', class_='item'):
            data = [] # save all the information from web crawling
            item = str(item) # change to string so that we can use it in findall() method

            # processing href
            herf = re.findall(FIND_HREF, item)[0] # we have to ask for the string item inside, otherwise we will get a list
            data.append(herf)

            # processing image
            image = re.findall(FIND_IMAGE, item)[0]
            data.append(image)

            # processing title
            titles = re.findall(FIND_TITLE, item) # may received one or two titles
            if len(titles) == 2:
                chtitle = titles[0]
                fortitle = titles[1].replace('\xa0','').replace('/', '')
                data.append(chtitle)
                data.append(fortitle)
            else:
                data.append(titles[0])
                data.append('')

            # processing rating
            rating = re.findall(FIND_RATING, item)[0]
            data.append(rating)

            # processing rate number
            ratenumber = re.findall(FIND_RATENUMBER, item)[0]
            data.append(ratenumber)

            # processing inq
            inq = re.findall(FIND_INQ, item)
            if len(inq) != 0:
                data.append(inq[0].replace('。', ''))
            else:
                data.append('')

            # processing briefintro
            briefintro = re.findall(FIND_BRIEFINTRO, item)[0]
            briefintro = re.sub('<br(\s+)?/>(\s+)?', '', briefintro)
            briefintro = re.sub('/', '', briefintro)
            briefintro = re.sub('\xa0', ' ', briefintro)
            data.append(briefintro.strip())

            datalist.append(data)

    return datalist



def geturl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=headers)
    html = ""
    try:
        # We proceed the GET request
        response = urllib.request.urlopen(request)
        html = response.read().decode('utf-8')
    except Exception as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


# Save data to local
def savedata(savepath, datalist):
    print('save the data to local', savepath)
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('doubantop250')

    firstRow = ('Href', 'Image', 'Chinese Title', 'Foreign Title', 'Rating', 'Rate Number', 'Inq', 'Brief Introduction')
    for i in range(0, len(firstRow)):
        worksheet.write(0, i, firstRow[i])

    for i in range(0, len(datalist)):
        for j in range(0, len(datalist[i])):
            worksheet.write(i + 1, j, datalist[i][j])

    workbook.save(savepath)


def save_data_to_database(database_save_path, datalist):
    init_database(database_save_path)
    pass

def init_database(database_save_path):
    connect = sqlite3.connect(database_save_path)
    cursor = connect.cursor()

    create_table = '''
        create table if not exists doubantop250
            -- a table of top 250 movies in douban
        (
            id integer primary key autoincrement, -- id of the list
            href text not null, -- href of the movie introduction
            image, -- href of the movie image
            chinese_title, -- the chinese title of the movie
            foreign_title, -- the foreign title of the movie
            rating integer, -- the rate (max 10, min 1) of the movie
            rating_number integer, -- number of rating for the movie
            inq text, -- conclude the movie in one word
            brief_intro text -- brief introduction of the cast
        )
    '''

    cursor.execute(create_table)
    connect.commit()
    connect.close()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
