import sqlite3

def get_accepted_visit_date_time(visit):  #get the accepted visit in that day-time slot
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM visite WHERE Data = ? AND Ora = ? AND Stato == 'accettata' AND ID_annuncio = ?"
    cursor.execute(sql,(visit['Data'],visit['Ora'],visit['ID_annuncio']))
    visit_db = cursor.fetchone()
    cursor.close()
    conn.close()
    return visit_db


def get_notAvailable_time(ID_annuncio, date):  #get not available timeslots of a date
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT DISTINCT Ora FROM Visite WHERE Data = ? AND ID_annuncio = ? AND Stato == 'accettata'"
    cursor.execute(sql,(date, ID_annuncio))
    timeslots = cursor.fetchall()
    cursor.close()
    conn.close()
    return timeslots


def check_visit_userID(User_id, ID_annuncio):  #check if the user has already booked a visit for a post and it's still pending or it was accepted
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM visite WHERE User_id=? AND ID_annuncio = ? and Stato!='rifiutata' "
    cursor.execute(sql,(User_id, ID_annuncio))
    visit_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return visit_db


def add_visit(visit):
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO visite(User_id,ID_annuncio,Data,Ora,Motivazione,Stato,Modalità) VALUES(?,?,?,?,?,?,?)'
    cursor.execute(sql, (visit['User_id'],visit['ID_annuncio'],visit['Data'],visit['Ora'],visit['Motivazione'],visit['Stato'],visit['Modalità']))
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

def get_visits_userID(User_ID):

    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM visite v, annunci a, utenti u WHERE v.User_id=? AND v.ID_annuncio=a.ID_annuncio AND u.User_id=id_locatore"
    cursor.execute(sql,(User_ID,))
    visit_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return visit_db


def get_visits_postID(post_ID):

    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT u.mail_utente, u.username, u.Img_prof, u.User_id, v.Data, v.Ora, v.Motivazione, v.Stato, v.Modalità, v.ID_visita FROM visite v, utenti u WHERE v.ID_annuncio=? AND v.User_id=u.User_id"
    cursor.execute(sql,(post_ID,))
    visit_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return visit_db

def get_landlord_visitID(ID_visit): #gets id and username of the landlord by the visit's ID
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT u.User_id, u.Username FROM visite v, annunci a, utenti u WHERE v.ID_visita=? and v.ID_annuncio=a.ID_annuncio and a.id_locatore=u.User_id"
    cursor.execute(sql,(ID_visit,))
    visit_db = cursor.fetchone()
    cursor.close()
    conn.close()
    return visit_db



def update_visit_state(visit_update, ID_visit):
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE visite SET Stato=?, Motivazione=? WHERE ID_visita=?'
    cursor.execute(sql, (visit_update['stato_aggiornato'], visit_update['Motivazione'], ID_visit))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()
    cursor.close()
    conn.close()

    return success