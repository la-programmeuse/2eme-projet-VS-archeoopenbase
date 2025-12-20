from flask import Flask, render_template, request, session, redirect, url_for
import pymongo
import os
from dotenv import load_dotenv
import bcrypt 
from bson.objectid import ObjectId

load_dotenv()
app = Flask(__name__)

client = pymongo.MongoClient(
    "mongodb+srv://laprogrammeuse_db_user:2jWIe266TsEycWi6@cluster0.2g3fh0q.mongodb.net/?appName=Cluster0",
    tlsAllowInvalidCertificates=True
)
db = client["Archeo_essaie_1"]

app.secret_key = "2jWIe266TsEycWi6"

@app.route('/')
def index():
    annonce_data= list(db["annonces"].find({}))
    return render_template('index.html', test = annonce_data)

@app.route("/search", methods = ['GET'])
def search():
    query = request.args.get('q', '').strip()

    if query == '':
        result = list(db["annonce"].find({}))
    else :
        results =   list(db["annonce"].find({
            "$or" : [
                {"titre_annonces" : {"$regex" : query, "$options" : "i"} },
                {"phrase_annonces" : {"$regex" : query, "$options" : "i"} }
            ]
        }))

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
    
@app.route('/publish', methods = ['POST','GET']) 
def publish():
    if 'user' not in session:
        return render_template('register.html')

    if request.method == "POST":
        db_annonces = db['annonces']
        titre = request.form["titre_annonces"]
        description = request.form["phrase_annonces"]

        if titre and description:
            db_annonces.insert_one({
                'titre_annonces' : titre,
                'phrase_annonces' : description,
            })
            return redirect(url_for('index'))
        else: 
            return render_template("publish.html", erreur = 'Veuillez remplir tout les champs obligatoires svp')
    return render_template("publish.html")


@app.route("/test")
def test():
    test_data = list(db["test"].find({}))
    return render_template('test.html', test = test_data )


app.run(host ='0.0.0.0', port=81)
    