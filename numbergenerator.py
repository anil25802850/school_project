# import mysql.connector

# mydb = mysql.connector.connect(
#     user='root',
#     host='localhost',
#     password='Anilk',
#     database='school'
# )

# def full_id(school_id,person):
#     cursor=mydb.cursor()
#     cursor.execute('SELECT SCHOOL_NAME FROM SCHOOL WHERE ID=%s',[school_id])
#     school_name =cursor.fetchone()[0]
#     first_3letters = school_name[0:3].upper()
#     s_id=int(school_id) #1 017  
#     if s_id < 10:
#         school_id = '00' + str(s_id)
#     elif s_id < 100:
#         school_id = '0' + str(s_id)
#     else:
#         school_id = str(s_id)
#     person = person
#     print(person)
#     t_id = 'T' if person == 'teacher' else 'S'
#     till_now = first_3letters + school_id + t_id + '%'
#     print(till_now)
#     if person == 'teacher':
#         cursor.execute('select max(id) from teachers where id like %s', [till_now])
#         maximum = cursor.fetchone()[0]
#     elif person=='student':
#         cursor.execute('select max(id) from student where id like %s', [till_now])
#         maximum = cursor.fetchone()[0]
#     print('maximum', maximum)
#     if maximum is None:
#         maximum = '000'
#     last = int(maximum[-3::]) + 1
#     if last < 10:
#         last = '00' + str(last)
#     elif last < 100:
#         last = '0' + str(last)
#     else:
#         last = str(last)
#     print('max', maximum)
#     print('last', last)
#     full_id = first_3letters + str(school_id) + t_id + last
#     print('full_id', full_id)
#     return str(full_id)
# print('id', full_id(school_id=10,person='student'))

# a=[5,10,22,56]
# for i in a:
#     print(a.index(i)+1)

# marks={'ID1':27,'ID2':150}
def rankcalculator(marks):
    a=list(sorted(marks,key=lambda x:marks[x],reverse=True))
    print(a)
    ranks=[]
    for index,item in enumerate(a):
        ranks+=[[item,index+1]]
    print(ranks)
    for key,values in marks.items():
        for rank in ranks:
            if key==rank[0]:
                marks[key]=[values,rank[1]]
    return marks