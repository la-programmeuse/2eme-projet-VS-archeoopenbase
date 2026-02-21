from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
import pymongo
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import bcrypt 
from bson.objectid import ObjectId

load_dotenv()
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads') 


client = MongoClient("mongodb+srv://laprogrammeuse_db_user:2jWIe266TsEycWi6@cluster0.2g3fh0q.mongodb.net/?appName=Cluster0")  # ton URI
db = client["projet_2_VS_code"] 


app.secret_key = "2jWIe266TsEycWi6"

@app.route('/')
def index():
    annonce_data= list(db["annonces"].find({}))
    print("Articles récupérés :", annonce_data)
    for annonce in annonce_data:
        annonce["_id"] = str(annonce["_id"])
                # Conversion sécurisée en float si la clé existe
        for key in ["lat", "lng"]:
            if key in annonce and annonce[key] is not None:
                try:
                    annonce[key] = float(annonce[key])
                except ValueError:
                    annonce[key] = None
    return render_template("index.html", annonce=annonce_data)

@app.route("/search", methods = ['GET'])
def search():
    print(db["annonces"].find_one())
    query = request.args.get('q', '').strip()

    if query == '':
        result = list(db["annonces"].find({}))
    else :
        result =   list(db["annonces"].find({
            "$or" : [
                {"titre_annonces" : {"$regex" : query, "$options" : "i"} },
                {"phrase_annonces" : {"$regex" : query, "$options" : "i"} }
            ]
        }))
    return render_template("search_result.html", annonces=result, query=query)

@app.route("/index/<id_post>")
def lieu(id_post):
    post  = db["annonces"].find_one({"_id": ObjectId(id_post)})
    return render_template("/post.html", post=post)

@app.route('/connect', methods=['POST', 'GET'])
def connect():
    if request.method == "POST":
        db_users = db["user"]
        user = db_users.find_one({"utilisateur" : request.form["utilisateur"]}) 
        if user: 
            if request.form['mots_de_passe'] == user['mots_de_passe']:
                 session['user'] = request.form["utilisateur"]
                 return redirect(url_for('index'))
            else:
                return render_template('connect.html', erreur = "mots de passe incorrect")
        else:
            return render_template('connect.html', erreur = "nom d'utilisateur incorrect")
    else:
        return render_template('connect.html') 

@app.route("/register", methods = ['POST' , 'GET'])
def register():
    if request.method == 'POST':
        db_users = db["user"]
        if(db_users.find_one({'name' : request.form ['utilisateur']})):
            return render_template('register.html', erreur = "le nom d'utilisateur a deja ete utiliser desoler :(")
        else : 
            if (request.form['mots_de_passe'] == request.form['confirme_mots_de_passe']):
                db_users.insert_one({
                    'utilisateur' : request.form['utilisateur'],
                    'mots_de_passe' : request.form['mots_de_passe'] 
                })
                session['user'] = request.form["utilisateur"]
                return redirect(url_for('index'))
            else:
                return render_template('register.html', erreur= "ce n'est pas les meme mots de passe")
    else : 
        return render_template('register.html')
    
@app.route('/publish', methods = ['POST', 'GET']) 
def publish():
    if 'user' not in session:
        return render_template('register.html')

    app.config['UPLOAD_FOLDER'] = "static/uploads"

    if request.method == "POST":
        print("request.files keys:", request.files.keys())
        db_annonces = db['annonces']
        titre = request.form["titre_annonces"]
        description = request.form["phrase_annonces"]
        Latitude = request.form["lat"]
        Longitude = request.form["lng"]
        image = request.files.get("image")


        filename = ""  # valeur par défaut si pas d'image
        if image and image.filename != "":
            from werkzeug.utils import secure_filename
            import os
            filename = secure_filename(image.filename)
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(upload_path)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            print("Fichier enregistré :", filename)
            print("Dossier uploads contient :", os.listdir(app.config['UPLOAD_FOLDER']))
            print("Image sauvegardée ici :", upload_path)
            print("CWD :", os.getcwd())
            print("Liste uploads :", os.listdir("static/uploads"))

        filename = filename.strip()

        if titre and description:
            db_annonces.insert_one({
                'titre_annonces' : titre,
                'phrase_annonces' : description,
                'lat' : Latitude,
                'lng' : Longitude,
                'image': filename
            })
            return redirect("/")
        else: 
            return render_template("publish.html", erreur = 'Veuillez remplir tout les champs obligatoires svp')
    return render_template("publish.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/test")
def test():
    test_data = list(db["test"].find({}))
    return render_template('test.html', test = test_data )


app.run(host ='0.0.0.0', port=81)
    