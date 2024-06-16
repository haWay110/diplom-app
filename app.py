import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# class Article(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     intro = db.Column(db.String(300), nullable=False)
#     text = db.Column(db.Text, nullable=False)
#     date = db.Column(db.DateTime, default=datetime.utcnow)
#
#     def __repr__(self):
#         return '<Article %r>' % self.id

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)  #айди
    name = db.Column(db.String(100), nullable=False)  #название
    sinonim = db.Column(db.String(100), nullable=True)  #синоним
    simptoms = db.Column(db.String(800), nullable=False)  #симптомы
    discription = db.Column(db.Text, nullable=True)  #описание
    danger = db.Column(db.String(300), nullable=False)  #Опасность
    first_aid = db.Column(db.Text, nullable=True)  #Первая помощь
    oreol = db.Column(db.String(300), nullable=True)
    dangers_heal = db.Column(db.Text, nullable=True)  #последствия
    photo = db.Column(db.String(300), nullable=True)  # картинка

    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


##
@app.route('/')
@app.route('/home')
def index():
    articles = Article.query.order_by(Article.date).all()
    return render_template("index.html", articles=articles)


@app.route('/about')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("about.html", articles=articles)


@app.route('/about/<int:id>')
def posts_detail(id):
    article = Article.query.get(id)
    return render_template("about_detail.html", article=article)


@app.route('/about/<int:id>/del')
def posts_delete(id):
    article = Article.query.get_or_404(id)
    photo_path = None

    # Check if the article has a photo and construct the path
    if article.photo:
        photo_path = os.path.join(app.root_path, 'static', article.photo.replace('/', os.path.sep))

    try:
        # Delete the article from the database
        db.session.delete(article)
        db.session.commit()

        # Delete the photo from the file system
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

        return redirect('/about')
    except Exception as e:
        return f"Ошибка: {e}"


#Редактировка
@app.route('/about/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get_or_404(id)
    if request.method == "POST":
        article.name = request.form['name']
        article.sinonim = request.form['sinonim']
        article.simptoms = request.form['simptoms']
        article.discription = request.form['discription']
        article.danger = request.form['danger']
        article.first_aid = request.form['first_aid']
        article.oreol = request.form['oreol']
        article.dangers_heal = request.form['dangers_heal']

        # Обработка изображения
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                # Удаление старого файла, если он есть
                if article.photo:
                    old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(article.photo))
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                # Сохранение нового файла
                photo_filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                photo.save(photo_path)
                article.photo = '/uploads/' + photo_filename  # Прямой слеш для URL

        try:
            db.session.commit()
            return redirect('/about')
        except Exception as e:
            return f"Ошибка обновления: {e}"
    else:
        return render_template("post_update.html", article=article)





@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        name = request.form['name']
        sinonim = request.form['sinonim']
        simptoms = request.form['simptoms']
        danger = request.form['danger']
        first_aid = request.form['first_aid']
        dangers_heal = request.form['dangers_heal']
        discription = request.form['discription']
        oreol = request.form['oreol']

        photo_url = None

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
                photo.save(photo_path)
                photo_url = 'uploads/' + photo.filename

        article = Article(name=name, sinonim=sinonim, simptoms=simptoms, danger=danger, first_aid=first_aid,
                          dangers_heal=dangers_heal, discription=discription, photo=photo_url, oreol=oreol)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Ошибка: {e}"
    else:
        return render_template("create-article.html")




if __name__ == "__main__":
    print("App is running")
    print(db)
    app.run(debug=True)
