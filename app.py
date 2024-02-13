# import module
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime, timedelta

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao, annunci_dao, foto_dao, visite_dao

from models import User

# Import the Image module from the PIL (Python Imaging Library) package. Used to preprocess the images uploaded by the users. Ensure 'Pillow' is installed before running the application by using the command 'pip install Pillow'
from PIL import Image

PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# create the application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'Key segreta di AbitaTO'

login_manager = LoginManager()
login_manager.init_app(app)


# define the homepage
@app.route('/')
def home():
    room_order=0 #0= price order; 1=room order
    if current_user.is_authenticated: 
        if current_user.tipo == 1:
                posts_result = annunci_dao.get_available_posts_desc_price(current_user.id) #doesn't show the landlord's post
        else:
                posts_result = annunci_dao.get_available_posts_desc_price('') #shows all posts
    else:
            posts_result = annunci_dao.get_available_posts_desc_price('')
   
    posts_db = [dict(row) for row in posts_result] #it's a list of dict, where each dict is a post

    for post in posts_db:
        photos_result=foto_dao.get_photos_by_PostID(post['ID_annuncio'])

        photos_db = []
        for row in photos_result:
            photos_db.append(row['nome_file'])

        post['Photos']=photos_db

    return render_template("home.html", posts=posts_db, room_order=room_order)



@app.route('/about')
def about():
    return render_template("about.html")



@app.route('/locali-crescenti')
def home_room_asc():
    room_order=1 #0=price order; 1=room order

    if current_user.is_authenticated: 
        if current_user.tipo == 1:
                posts_result = annunci_dao.get_available_posts_asc_rooms(current_user.id) #doesn't show the landlord's post
        else:
                posts_result = annunci_dao.get_available_posts_asc_rooms('') #shows all posts
    else:
            posts_result = annunci_dao.get_available_posts_asc_rooms('')
   
   
    posts_db = [dict(row) for row in posts_result] #it's a list of dict, where each dict is a post

    for post in posts_db:
        photos_result=foto_dao.get_photos_by_PostID(post['ID_annuncio'])

        photos_db = []
        for row in photos_result:
            photos_db.append(row['nome_file'])

        post['Photos']=photos_db

    return render_template("home.html", posts=posts_db, room_order=room_order)



# define the single post page    
@app.route('/annunci/<int:ID_annuncio>')
def single_post(ID_annuncio):
    post_result = annunci_dao.get_post_by_ID(ID_annuncio)
    post=dict(post_result)

    photos_result=foto_dao.get_photos_by_PostID(ID_annuncio)

    photos_db = []
    for row in photos_result:
        photos_db.append(row['nome_file'])

    post['Photos']=photos_db
    post['ID_annuncio']=ID_annuncio

    #Start_date and end_date for the date input in the form
    # obtain today's date
    today = datetime.now().date()
    # start_date=following day
    start_date = today + timedelta(days=1)
    # end_date = 1 week later
    end_date = today + timedelta(days=7)

    
    #if user is authenticated, load the appointments
    if current_user.is_authenticated:
        next_week={}
        for delta in range((end_date - start_date).days + 1):
            timeslots=["9-12","12-14","14-17", "17-20"]
            current_date = start_date + timedelta(days=delta)
    
            visits_result=visite_dao.get_notAvailable_time(ID_annuncio, current_date) #gets the not available timeslots for the current date
            if visits_result:
                visits_db=[]
                for row in visits_result:
                    visits_db.extend(row) #with append() you get a list of list: [[elements]]; extend() "appends" only the elements of the list: [elements]
                next_week[current_date]=[]
                for timeslot in visits_db:
                    if timeslot in timeslots:
                        timeslots.remove(timeslot)
            
            next_week[current_date] = timeslots
        return render_template('post.html', post=post, next_week=next_week, start_date=start_date, end_date=end_date)
    return render_template('post.html', post=post, start_date=start_date, end_date=end_date)



@app.route('/annunci/new', methods=['POST'])
@login_required
def new_post():
     
    post=request.form.to_dict()
    
    #validation
    if(post['titolo']==''):
        app.logger.error('Devi inserire un titolo')
        return redirect(url_for('home'))
    if(post['prezzo']==''):
        app.logger.error('Devi inserire un affitto mensile')
        return redirect(url_for('home'))
    else:
        post['prezzo']=int(post['prezzo'])
        if(int(post['prezzo'])<0):
            app.logger.error('L\'affitto deve essere un numero positivo')
            return redirect(url_for('home'))
            
    if(post['indirizzo']==''):
        app.logger.error('Devi inserire l\'indirizzo dell\'abitazione')
        return redirect(url_for('home'))
    if(post['locali']==''):
        app.logger.error('Devi selezionare il numero di locali')
        return redirect(url_for('home'))
    if(post['tipo_casa']==''):
        app.logger.error('Devi selezionare la tipologia di abitazione')
        return redirect(url_for('home'))
    if(post['descrizione']==''):
        app.logger.error('Devi inserire una descrizione')
        return redirect(url_for('home'))
    
    if('arredo' in post): #if the key is not in the dictionary it means that the toggle switch was not selected
        if(post['arredo']=="on"): # on=1 --> arredata; off=0 --> non arredata
            post['arredo']=1
    else:
        post['arredo']=0
    
    if('disponibile' in post):
        if(post['disponibile']=="on"): # on=1 --> disponibile; off=0 --> non disponibile
            post['disponibile']=1
    else:
        post['disponibile']=0

    if not request.files.getlist("imgFiles"):
        app.logger.error('Devi Inserire almeno una immagine')
        return redirect(url_for('home'))
    

    #insert post in database
    user_id=int(current_user.id)  
    post['id_locatore'] = user_id
    success, post_id= annunci_dao.add_post(post)
    if success:
        app.logger.info('Annuncio creato correttamente')
    else:
        app.logger.error('Errore nella creazione dell\'annuncio: riprova!')
        return redirect(url_for('home'))

     # Get the list of files from webpage 
    files = request.files.getlist("imgFiles")

    if files:
        #save files
        for id, file in enumerate(files):

            # Open the user-provided image using the Image module
            img = Image.open(file)

            # Get the width and height of the image
            width, height = img.size

            # Calculate the new height while maintaining the aspect ratio based on the desired width
            new_height = height/width * POST_IMG_WIDTH

            # Define the size for thumbnail creation with the desired width and calculated height
            size = POST_IMG_WIDTH, new_height
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Extracting file extension from the image filename
            ext = file.filename.split('.')[-1]

            # Getting the current timestamp in seconds
            secondi = int(datetime.now().timestamp())

            # Saving the image with a unique filename in the 'static' directory
            img.save('static/@' + current_user.username.lower() + '-' + str(secondi) + '-' + str(id) +'.' + ext)

            # Updating the 'immagine_post' field in the post dictionary with the image filename
            img_name = '@' + current_user.username.lower() + '-' + str(secondi) + '-'+ str(id) + '.' + ext

            success = foto_dao.add_photo(img_name,post_id)
            if success:
                app.logger.info('Foto caricate correttamente')
            else:
                app.logger.error('Errore nel caricamento delle foto: riprova!')
                
    flash('Annuncio creato correttamente', 'success')
    return redirect(url_for('home'))



@app.route('/prenotazione/new', methods=['POST'])
@login_required
def new_visita():

    visit=request.form.to_dict()

    if visit['Data'] == '' or datetime.strptime(visit['Data'], '%Y-%m-%d').date() <= date.today() or  datetime.strptime(visit['Data'], '%Y-%m-%d').date() > date.today() + timedelta(days=7) :
        app.logger.error('Data errata!')
        return redirect(url_for('single_annuncio', ID_annuncio=visit['ID_annuncio']))
        
    if visit['Ora'] == '':
        app.logger.error('La richiesta deve avere una fascia oraria!')
        return redirect(url_for('single_annuncio', ID_annuncio=visit['ID_annuncio']))
    
    if visit['Modalità'] == '':
        app.logger.error('La richiesta deve avere una modalità!')
        return redirect(url_for('single_annuncio', ID_annuncio=visit['ID_annuncio']))

    
    visit['ID_annuncio'] = int(visit['ID_annuncio'])
    visit['User_id'] = int(current_user.id)
    visit['Stato'] = 'richiesta'
    visit['Motivazione'] = ''

    if visite_dao.get_accepted_visit_date_time(visit): #verifica se ci sono date nella stessa fascia oraria e nello stesso giorno 
        flash('C\'è già una prenotazione per questa casa nella fascia oraria della data selezionata!', 'danger')
        return redirect(url_for('single_post', ID_annuncio=int(visit['ID_annuncio'])))
    elif visite_dao.check_visit_userID(visit['User_id'], visit['ID_annuncio']): #check if the user has already booked a visit in the past and it's still pending or it was accepted
        flash('C\'è già una prenotazione accettata o richiesta a tuo nome per questa casa!', 'danger')
        return redirect(url_for('single_post', ID_annuncio=int(visit['ID_annuncio'])))


    success = visite_dao.add_visit(visit)

    if success:
        app.logger.info('Visita creata correttamente')
    else:
        app.logger.error('Errore nella creazione della visita: riprova!')
        return redirect(url_for('single_post', ID_annuncio=int(visit['ID_annuncio'])))

            
    flash('Visita confermata!', 'success')
    return redirect(url_for('home'))



# define the profile page
@app.route('/profilo/@<username>')
@login_required
def profile(username):

    posts_result=annunci_dao.get_posts_userID(current_user.id)
    posts_db = [dict(row) for row in posts_result] #it's a list of dict, where each dict is a post
    visits_user_result=visite_dao.get_visits_userID(current_user.id)
    visits_user_db = [dict(row) for row in visits_user_result]

    for visit in visits_user_db:
        photos_result=foto_dao.get_photos_by_PostID(visit['ID_annuncio'])

        photos_db = []
        for row in photos_result:
            photos_db.append(row['nome_file'])

        visit['Photos']=photos_db
        visit['Data']= datetime.strptime(visit['Data'], '%Y-%m-%d')
        visit['Data']=visit['Data'].date()
        if visit['Modalità']==0:
            visit['Modalità']="presenza"
        else:
            visit['Modalità']="remoto"
    

    for post in posts_db:
        photos_result=foto_dao.get_photos_by_PostID(post['ID_annuncio'])

        photos_db = []
        for row in photos_result:
            photos_db.append(row['nome_file'])

        post['Photos']=photos_db

        if current_user.tipo==1: #adds the visits for that posts
            for post in posts_db:
                visits_landlord_result=visite_dao.get_visits_postID(post['ID_annuncio'])
                visits_landlord_db = [dict(row) for row in visits_landlord_result]
                for visit in visits_landlord_db:
                    visit['Data']= datetime.strptime(visit['Data'], '%Y-%m-%d')
                    visit['Data']=visit['Data'].date()
                    if visit['Modalità']==0:
                        visit['Modalità']="presenza"
                    else:
                        visit['Modalità']="remoto"
                post['Visite']=visits_landlord_db

    return render_template('profile.html', posts=posts_db, visits_user=visits_user_db)




@app.route('/annunci/update/<ID_annuncio>', methods=['POST'])
@login_required
def update_post(ID_annuncio):
     
    post=request.form.to_dict()
    
    #validation
    if(post['titolo']==''):
        app.logger.error('Devi inserire un titolo')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))
    if(post['prezzo']==''):
        app.logger.error('Devi inserire un affitto mensile')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))
    else:
        post['prezzo']=int(post['prezzo'])
    if(post['locali']==''):
        app.logger.error('Devi selezionare il numero di locali')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))
    if(post['tipo_casa']==''):
        app.logger.error('Devi selezionare la tipologia di abitazione')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))
    if(post['descrizione']==''):
        app.logger.error('Devi inserire una descrizione')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))
    
    if('arredo' in post): #if the key is not in the dictionary it means that the toggle switch was not selected
        if(post['arredo']=="on"): # on=1 --> arredata; off=0 --> non arredata
            post['arredo']=1
    else:
        post['arredo']=0
    
    if('disponibile' in post):
        if(post['disponibile']=="on"): # on=1 --> disponibile; off=0 --> non disponibile
            post['disponibile']=1
    else:
        post['disponibile']=0
    

    #update post in database
    user_id=int(current_user.id)  
    post['id_locatore'] = user_id
    post['ID_annuncio']= ID_annuncio
    success= annunci_dao.update_post(post)
    if success:
        app.logger.info('Annuncio modificato correttamente')
    else:
        app.logger.error('Errore nella modifica dell\'annuncio: riprova!')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))


    count=0
    for i in range(0,5):
        if f'DelImg{i}' in post:
            count+=1

    if foto_dao.count_photo(ID_annuncio)==count: #check that the user is not deleting all the photos
        app.logger.error('L\'annuncio deve avere almeno una foto: riprova!')
        flash('L\'annuncio deve avere almeno una foto: riprova!', 'danger')
        return redirect(url_for('single_post', ID_annuncio=ID_annuncio))

    for i in range(0,5): #delete selected images
        if f'DelImg{i}' in post:
            success_delete=foto_dao.del_photo(ID_annuncio, post[f'OldImgFile{i}'])
            if success_delete:
                app.logger.info('Foto eliminata correttamente')
            else:
                app.logger.error('Errore nell\'eliminazione delle foto: riprova!')

    files_to_add=[]
    for i in range(0,5):
        new_file=request.files.get(f'NewImgFile{i}')
        old_file=request.form.get(f'OldImgFile{i}')
        if new_file is not None and new_file.filename != '':
            files_to_add.append({'NewImgFile': new_file, 'OldImgFile': old_file})
        else:
            files_to_add.append({'NewImgFile': None, 'OldImgFile': old_file})
 
    #save files
    for id, file in enumerate(files_to_add): 
        if file['NewImgFile'] is not None and file['NewImgFile']!='':
            # Open the user-provided image using the Image module
            img = Image.open(file['NewImgFile'])

            # Get the width and height of the image
            width, height = img.size

            # Calculate the new height while maintaining the aspect ratio based on the desired width
            new_height = height/width * POST_IMG_WIDTH

            # Define the size for thumbnail creation with the desired width and calculated height
            size = POST_IMG_WIDTH, new_height
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Extracting file extension from the image filename
            ext = file['NewImgFile'].filename.split('.')[-1]

            # Getting the current timestamp in seconds
            secondi = int(datetime.now().timestamp())

            # Saving the image with a unique filename in the 'static' directory
            img.save('static/@' + current_user.username.lower() + '-' + str(secondi) + '-' + str(id) +'.' + ext)

            # Updating the 'immagine_post' field in the post dictionary with the image filename
            img_name = '@' + current_user.username.lower() + '-' + str(secondi) + '-'+ str(id) + '.' + ext

            if file['OldImgFile'] != '' and file['OldImgFile'] is not None: #if it is updating an existing photo
                success = foto_dao.update_photo(img_name,ID_annuncio, file['OldImgFile'])
            else: 
                success = foto_dao.add_photo(img_name,ID_annuncio)
            if success:
                app.logger.info('Foto caricata correttamente')
            else:
                app.logger.error('Errore nel caricamento delle foto: riprova!')

    return redirect(url_for('single_post', ID_annuncio=ID_annuncio))



@app.route('/visite/manage/<ID_visit>', methods=['POST'])
@login_required
def manage_visit(ID_visit):
     
    visit_update=request.form.to_dict()
    landlord=visite_dao.get_landlord_visitID(ID_visit)
    
    #validation
    if(visit_update['stato_aggiornato']=='rifiutata' and visit_update['Motivazione']==''):
        flash('Devi inserire una motivazione in caso di rifiuto!', 'danger')
        app.logger.error('Bisogna inserire una motivazione in caso di rifiuto')
        return redirect(url_for('profile', username=landlord['Username']))
    
    success=visite_dao.update_visit_state(visit_update, ID_visit)
    if success:
        app.logger.info('Visita aggiornata correttamente')
    else:
        app.logger.error('Errore nell\'aggiornamento dello stato della visita: riprova!')

    return redirect(url_for('profile', username=landlord['Username']))



# define the signup page
@app.route('/iscriviti')
def iscriviti():
    
    return render_template('signup.html')



@app.route('/iscriviti', methods=['POST'])
def iscriviti_post():

    new_user_form = request.form.to_dict()

    user_in_db = utenti_dao.get_user_by_mail(new_user_form.get('mail_utente')) #check if user in db
    user_taken = utenti_dao.get_user_by_username(new_user_form.get('username')) #check if username is already taken

    if user_in_db:
        flash('C\'è già un utente registrato con questa mail', 'danger')
        return redirect(url_for('iscriviti'))
    elif user_taken:
        flash('L\'username è già stato preso', 'danger')
        return redirect(url_for('iscriviti'))
    else:
        img_profilo = ''
        usr_image = request.files['img_prof']
        if usr_image:
            # Open the user-provided image using the Image module
            img = Image.open(usr_image)

            # Get the width and height of the image
            width, height = img.size

            # Calculate the new width while maintaining the aspect ratio
            new_width = PROFILE_IMG_HEIGHT * width / height

            # Define the size for thumbnail creation with the desired height and calculated width
            size = new_width, PROFILE_IMG_HEIGHT
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Calculate the coordinates for cropping the image to a square shape
            left = (new_width/2 - PROFILE_IMG_HEIGHT/2)
            top = 0
            right = (new_width/2 + PROFILE_IMG_HEIGHT/2)
            bottom = PROFILE_IMG_HEIGHT

            # Crop the image using the calculated coordinates to create a square image
            img = img.crop((left, top, right, bottom))

            # Extracting file extension from the image filename
            ext = usr_image.filename.split('.')[-1]

            # Saving the image with a unique filename in the 'static' directory
            img.save('static/' + new_user_form.get('username').lower() + '.' + ext)

            img_profilo = new_user_form.get('username').lower() + '.' + ext

            # Updating the 'img_prof' field in the user dictionary with the image filename
            new_user_form['img_prof'] = img_profilo
        else:
            new_user_form['img_prof'] ="default_user.jpg"

        new_user_form['password'] = generate_password_hash(new_user_form.get('password'))
        

        if('tipo' in new_user_form): #if the key is not in the dictionary it means that the toggle switch was not selected --> the user is a client
            if(new_user_form['tipo']=="on"): # on=1 --> locatore; off=0 --> cliente
                new_user_form['tipo']=1
        else:
            new_user_form['tipo']=0

        success = utenti_dao.add_user(new_user_form)

        if success:
            flash('Utente creato correttamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Errore nella creazione del utente: riprova!', 'danger')

    return redirect(url_for('iscriviti'))



#define the login page
@app.route('/login', methods=['POST'])
def login():

  user_form = request.form.to_dict()

  user_db = utenti_dao.get_user_by_mail(user_form['mail_utente'])

  if not user_db or not check_password_hash(user_db['password'], user_form['password']):
    flash('Credenziali non valide, riprova', 'danger')
    return redirect(url_for('home'))
  else:
    new = User(mail_utente=user_db['Mail_utente'], username=user_db['Username'], password=user_db['Password'], tipo=user_db['Tipo'], img_prof=user_db['Img_prof'], id=user_db['User_id'])
    login_user(new, True)
    flash('Bentornat* ' + user_db['username'] + '!', 'success')

    return redirect(url_for('home'))



@login_manager.user_loader
def load_user(user_id):

    db_user = utenti_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(mail_utente=db_user['Mail_utente'], username=db_user['Username'], password=db_user['Password'], tipo=db_user['Tipo'], img_prof=db_user['Img_prof'], id=db_user['User_id'])
    else:
        user = None

    return user



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)