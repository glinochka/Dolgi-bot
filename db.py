from mysql.connector import connect, Error
from decouple import config




# подключение к бд, выдаёт False если подключение провалено
def conn():
    try:
        connection = connect(host=config('host'),
                             user=config('user_name'),
                             password=config('pass'),
                             database=config('database'),
                             port=config('port'),
                             charset='utf8',
                             use_unicode=True)
        return connection
    except Error as e:
        print(e)
        return False
# внесение в бд нового юзера если юзер с таким ником уже есть возвращает False, если у юзера не было tg_id, добавляет
def user_to_db(name, link, chat_id):
    cnct = conn()

    if cnct:
        command = f'''
            INSERT INTO users(name,link,chat_id)
            VALUE('{name}','{link}',{chat_id})
            '''

        with cnct.cursor() as cur:
            cur.execute(command)
            cnct.commit()

def link(name):
    cnct = conn()

    if cnct:
        command = f'''
            SELECT link FROM USERS where name = '{name}' limit 1
            '''

        with cnct.cursor() as cur:
            cur.execute(command)
            link_ = [i[0] for i in cur.fetchall()]
        return link_[0]

def users():
    cnct = conn()

    if cnct:
        command = f'''
            SELECT name FROM USERS
            '''

        with cnct.cursor() as cur:
            cur.execute(command)
            users = cur.fetchall()
        return [i[0] for i in users]

def user(chat_id):
    cnct = conn()

    if cnct:
        command = f'''
            SELECT name FROM USERS where chat_id = {chat_id} limit 1
            '''

        with cnct.cursor() as cur:
            cur.execute(command)
            user_ = [i[0] for i in cur.fetchall()]
        return user_[0]

def chat(name):
    cnct = conn()

    if cnct:
        command = f'''
            SELECT chat_id FROM USERS where name = '{name}' limit 1
            '''

        with cnct.cursor() as cur:
            cur.execute(command)
            chat_ = [i[0] for i in cur.fetchall()]
        return chat_[0]
def dolg_to_db(doljnik,creditor,dolg):
    cnct = conn()

    if cnct:
        command = f'''
                INSERT INTO dolg(doljnik,creditor,dolg)
                VALUE('{doljnik}','{creditor}',{dolg})
                '''

        with cnct.cursor() as cur:
            cur.execute(command)
            cnct.commit()

def count():
    cnct = conn()

    if cnct:
        command = f'''
                    select doljnik, creditor, sum(dolg) as dolg from dolg
                    group by doljnik, creditor;
                    '''

        with cnct.cursor() as cur:
            cur.execute(command)

            table = cur.fetchall()
        return table
def dolgi(doljnik):
    cnct = conn()

    if cnct:
        command = f'''
                    select id , creditor, dolg from dolg
                    where doljnik = '{doljnik}'
                    '''

        with cnct.cursor() as cur:
            cur.execute(command)

            table = cur.fetchall()
        return table

def dolg(id):
    cnct = conn()

    if cnct:
        command = f'''
                    select  doljnik, creditor, dolg from dolg
                    where id = {id}
                    '''

        with cnct.cursor() as cur:
            cur.execute(command)

            res = cur.fetchall()[0]
        return res
def minus_dolg(id):
    cnct = conn()

    if cnct:
        command = f'''
                    delete from dolg
                    where id = {id}
                    '''

        with cnct.cursor() as cur:
            cur.execute(command)
            cnct.commit()


