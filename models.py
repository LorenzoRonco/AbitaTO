from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, mail_utente, username, password, tipo, img_prof, id):
        self.mail_utente = mail_utente
        self.username = username
        self.password = password
        self.tipo = tipo
        self.img_prof = img_prof
        self.id = id