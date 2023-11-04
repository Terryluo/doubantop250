# This is a douban Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import re  # Regular express analysis
import sqlite3  # SQLite database operation
import urllib.error  # setURL, obtain the web content
import urllib.request

import xlwt  # excel operation
from bs4 import BeautifulSoup  # web page analysis

FIND_HREF = re.compile(r'<a href="(.*?)">')
FIND_IMAGE = re.compile(r'<img.*src="(.*?)"', re.S)
FIND_TITLE = re.compile(r'<span class="title">(.*?)</span>')
FIND_RATING = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
FIND_RATENUMBER = re.compile(r'<span>(\d*)人评价</span>')
FIND_INQ = re.compile(r'<span class="inq">(.*?)</span>')
FIND_BRIEFINTRO = re.compile(r'<p class="">(.*?)</p>', re.S)
SAVING_LOCATION = 'remote'  # two values: local / remote


def main():
    baseurl = 'https://movie.douban.com/top250?start='
    datalist = getdata(baseurl)
    if len(datalist) == 0:  # If we did not successfully obtain the information
        print('Web Crawling failed')
        return

    if SAVING_LOCATION == 'local':
        # save data to the excel
        local_save_path = 'doubantop250_2023_Nov.xls'
        save_data_to_local(local_save_path, datalist)
    elif SAVING_LOCATION == 'remote':
        # save data to the database using SQLite
        database_save_path: str = 'doubantop250.db'
        # database_save_path: str = 'test.db' # for testing the operation
        save_data_to_database(database_save_path, datalist)
    else:
        print('Saving direction is not defined')
    print('Web Crawling Finished')  # Press Ctrl+F8 to toggle the breakpoint.


# getting data from internet
def getdata(baseurl):
    datalist = []
    for page in range(10):
        url = baseurl + str(page * 25)
        print('Getting the data from internet', url)
        html = geturl(url)

        # analysis the page
        bs = BeautifulSoup(html, "html.parser")
        for item in bs.find_all('div', class_='item'):
            data = []  # save all the information from web crawling
            item = str(item)  # change to string so that we can use it in findall() method

            # processing href
            herf = re.findall(FIND_HREF, item)[
                0]  # we have to ask for the string item inside, otherwise we will get a list
            data.append(herf)

            # processing image
            image = re.findall(FIND_IMAGE, item)[0]
            data.append(image)

            # processing title
            titles = re.findall(FIND_TITLE, item)  # may received one or two titles
            if len(titles) == 2:
                chtitle = titles[0]
                fortitle = titles[1].replace('\xa0', '').replace('/', '')
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
        'User-Agent':
            '''
                Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
                Chrome/118.0.0.0 Safari/537.36
            '''
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
        print('Failed to obtain the url!')
        return
    print('Successfully obtained the page information!')
    return html


# Save data to local
def save_data_to_local(local_save_path, datalist):
    print('Saving data to local:', local_save_path)
    # create a workbook
    workbook = xlwt.Workbook(encoding='utf-8')
    # create a worksheet
    worksheet = workbook.add_sheet('doubantop250')

    # create first row
    first_row = ('Href', 'Image', 'Chinese Title', 'Foreign Title', 'Rating', 'Rate Number', 'Inq', 'Brief Introduction')
    for i in range(0, len(first_row)):
        worksheet.write(0, i, first_row[i])

    # insert the information into the other rows
    for i in range(0, len(datalist)):
        for j in range(0, len(datalist[i])):
            worksheet.write(i + 1, j, datalist[i][j])

    workbook.save(local_save_path)


def save_data_to_database(database_save_path, datalist):
    print('Saving data to database:', database_save_path)
    init_database(database_save_path)
    connect = sqlite3.connect(database_save_path)
    cursor = connect.cursor()
    try:
        for data in datalist:
            for index in range(len(data)):
                if index == 4 or index == 5:
                    continue
                data[index] = '"' + data[index] + '"'  # become a string so that we could insert into database's column
            sql = '''
                insert into doubantop250 (
                href, image, chinese_title, foreign_title, rating, rating_number, inq, brief_intro
                ) values(%s) 
            ''' % ",".join(data)
            cursor.execute(sql)
            connect.commit()
    except Exception as e:
        print('We got exception while inserting value...')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    finally:
        cursor.close()
        connect.close()


def init_database(database_save_path):
    # connect to database though sqlite3, create database if it does not exist
    connect = sqlite3.connect(database_save_path)

    # create cursor to execute sql command
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
    try:
        # execute sql command and commit to database
        cursor.execute(create_table)
        connect.commit()
    except Exception as e:
        print('We got exception while creating table...')
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    finally:
        # close the cursor and connect
        cursor.close()
        connect.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
