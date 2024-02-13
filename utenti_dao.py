import sqlite3

def get_users(): #gets all users
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti'
    cursor.execute(sql)
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users


def get_user_by_mail(mail): #gets the user with the given mail
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE mail_utente = ?'
    cursor.execute(sql, (mail,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def get_user_by_username(username): #gets the user with the given username
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE username = ?'
    cursor.execute(sql, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

def get_user_by_id(user_id): #gets the user with the given username
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE user_id = ?'
    cursor.execute(sql, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def add_user(user):

    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO utenti(mail_utente,username,password,tipo,img_prof) VALUES(?,?,?,?,?)'

    try:
        cursor.execute(
            sql, (user['mail_utente'], user['username'], user['password'], user['tipo'], user['img_prof']))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success