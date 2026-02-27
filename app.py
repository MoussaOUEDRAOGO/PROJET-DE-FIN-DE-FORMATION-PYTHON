from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy 
from flask_login import login_user, logout_user, login_required, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import flash

#Initialisation de l’application et de la base de données
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)

#Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#Fonction pour charger l’utilisateur connecté
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Modèles de la base de données
class AEBMBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    post_date = db.Column(db.DateTime)
    content = db.Column(db.Text)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


#page d'acceuil
@app.route("/")
def home():
    article = AEBMBlog.query.order_by(AEBMBlog.post_date.desc()).all()
    print(current_user.is_anonymous)
    if current_user.is_anonymous:
        name = "guest"
    else:
        name = current_user.username
        print("bye")

    return render_template('index.html', article=article, name=name)

#page about
@app.route('/about')
def about():
    return render_template('about.html')

#page ajouter un post
@app.route('/addpost', methods=['POST', 'GET'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']

        post = AEBMBlog(title=title, author=author, 
                       content=content, post_date=datetime.now())

        db.session.add(post)
        db.session.commit()
        print("Done")
        return redirect(url_for('home'))
    return render_template('add.html')

#page modifier un post
@app.route('/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update(id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        print(content)

        post = AEBMBlog.query.filter_by(id=id).first()

        post.title = title
        post.author = author
        post.content = content

        db.session.add(post)
        db.session.commit()
        return redirect("/")

    edit = AEBMBlog.query.filter_by(id=id).first()
    return render_template('update.html', edit=edit)

#supprimer un post
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    d = AEBMBlog.query.filter_by(id=id).first()
    db.session.delete(d)
    db.session.commit()
    return redirect(url_for('home'))


#connnexion
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('home'))

        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

#inscription
from flask_login import login_user

@app.route('/signin', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmpassword']

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('signin'))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        login_user(user)  # <-- Connexion automatique
        return redirect(url_for('home'))  # Redirection vers home

    return render_template('signin.html')




@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))  


with app.app_context():
    db.create_all()
    print("Base de données 'blogs.db' et tables créées !")
    
#Exécution de l'application
# main driver function
if __name__ == '__main__':
  
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=True)