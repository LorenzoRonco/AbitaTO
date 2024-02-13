import sqlite3


def get_posts(): #gets all the rental advertisements
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT ID_annuncio,Locali,Disponibile,Tipo_casa,Titolo,Arredo,Prezzo,Descrizione,Indirizzo,Mail_locatore FROM annunci'
    cursor.execute(sql)
    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return posts


def add_post(post):
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO annunci(locali,disponibile,tipo_casa,titolo,arredo,prezzo,descrizione,indirizzo,id_locatore) VALUES(?,?,?,?,?,?,?,?,?)'
    cursor.execute(sql, (post['locali'], post['disponibile'], post['tipo_casa'],post['titolo'],
                         post['arredo'],post['prezzo'], post['descrizione'],post['indirizzo'],post['id_locatore']))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()
    id=cursor.lastrowid
    cursor.close()
    conn.close()

    return success, id

def get_available_posts_desc_price(ID_utente): #gets available posts ordered by desc price. Do NOT gets the posts of the landlord
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM annunci a, utenti u WHERE a.disponibile=1 AND u.User_id=a.id_locatore AND a.id_locatore != ? ORDER BY a.prezzo DESC'
    cursor.execute(sql, (ID_utente,))
    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return posts


def get_available_posts_asc_rooms(ID_utente):
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM annunci a, utenti u WHERE a.disponibile=1 AND u.User_id=a.id_locatore AND a.id_locatore != ? ORDER BY a.locali ASC'
    cursor.execute(sql, (ID_utente,))
    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return posts

def get_post_by_ID(ID_annuncio): #gets single post by ID
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM annunci a, utenti u WHERE u.User_id=a.id_locatore AND a.ID_annuncio = ?'
    cursor.execute(sql, (ID_annuncio,))
    posts = cursor.fetchone()

    cursor.close()
    conn.close()

    return posts


def get_posts_userID(ID_utente): #gets all the rental advertisements for a user ID
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM annunci a WHERE a.id_locatore=?'
    cursor.execute(sql, (ID_utente,))
    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return posts


def update_post(post):
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE annunci SET Locali=?, Disponibile=?, Tipo_casa=?, Titolo=?, Arredo=?, Prezzo=?, Descrizione=?, id_locatore=? WHERE ID_annuncio=?'
    cursor.execute(sql, (post['locali'], post['disponibile'], post['tipo_casa'],post['titolo'],
                         post['arredo'],post['prezzo'], post['descrizione'],post['id_locatore'], post['ID_annuncio']))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()
    id=cursor.lastrowid
    cursor.close()
    conn.close()

    return success, id