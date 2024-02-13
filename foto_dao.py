import sqlite3

def get_photos_by_PostID(ID_post): #gets all the photos of a single post
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT nome_file FROM foto WHERE ID_annuncio = ?'
    cursor.execute(sql,(ID_post,))
    photos = cursor.fetchall()
    cursor.close()
    conn.close()
    return photos

def add_photo(img_name,post_id):

    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO foto(nome_file,ID_annuncio) VALUES(?,?)'

    try:
        cursor.execute(sql, (img_name,post_id))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()
    cursor.close()
    conn.close()

    return success


def del_photo(post_id, filename): #delete all the post's photo by post_ID and filename
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'DELETE FROM foto WHERE ID_annuncio=? and nome_file=?'

    try:
        cursor.execute(sql, (post_id,filename))
        conn.commit()
        success=True
    except Exception as e:
        print('ERROR DURING DELETE', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    cursor.close()
    conn.close()

    return success



def update_photo(new_img_name, post_id, old_img_name): #update photo with a new filename
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE foto SET nome_file=? WHERE ID_annuncio=? and nome_file=?'
    cursor.execute(sql, (new_img_name,post_id,old_img_name))
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


def count_photo(post_id): #counts photo by post_id
    conn = sqlite3.connect('db/db_affitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'SELECT COUNT(*) AS numero_di_foto FROM foto WHERE ID_annuncio = ?'
    cursor.execute(sql, (post_id,))
    n_photos = cursor.fetchone()['numero_di_foto']
    cursor.close()
    conn.close()
    return n_photos