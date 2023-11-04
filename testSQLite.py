import sqlite3 as sl

conn = sl.connect('test.db')
cursor = conn.cursor()

sql1 = '''
    create table emp(
        id integer primary key autoincrement, -- 'employee id',
        name text not null, -- 'employee name',
        address varchar(50) not null, -- 'employee address',
        age integer not null, -- 'employee age',
        salary integer not null -- 'employee annual salary'
    ) -- 'employee table'
'''
sql2 = '''
    insert into emp (name, address, age, salary) values ('Tom', 'abc street', 25, 80000)
'''
sql3 = '''
    insert into emp (name, address, age, salary) values ('Rose', 'cde avenue', 23, 80000)
'''

cursor.execute(sql1)
cursor.execute(sql2)
cursor.execute(sql3)

conn.commit()
conn.close()


