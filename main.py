from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

def valid_title(title):
    error = 'Please enter a title'
    if not title:
        return error
    else:
        return ''

def valid_body(body):
    error = 'Please enter body content'
    if not body:
        return error
    else:
        return ''

def verify_password(password, verify):
    if password == verify and password != '':
        return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['index', 'blog', 'login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['user'] = username
            flash('You have logged in', 'success')
            return redirect('/newpost')
        else:
            if not user:
                flash('Username does not exist', 'error')
            elif not check_pw_hash(password, user.pw_hash):
                flash('Your password is incorrect', 'error')

    return render_template('login.html')

    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if verify_password(password, verify):
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = username
                return redirect('/newpost')
            else:
                flash('Your passwords do not match', 'error')
        else:
            flash('This user already exists', 'error')

    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    del session['user']
    flash('You have been logged out', 'success')
    return redirect('/blog')

@app.route('/blog')
def blog():

    post_id = request.args.get("id")

    if post_id:
        single_post = Blog.query.filter_by(id=post_id).first()
        if single_post:
            owner = User.query.filter_by(id=single_post.owner_id).first()
            author = owner.username
            return render_template('singlepost.html', title=single_post.title, post=single_post, author=author)
        else:
            flash('That post does not exist!', 'error')

    author = request.args.get("userid")
    
    if author:
        author_id = User.query.filter_by(username=author).first()
        owner_id = author_id.id
        posts = Blog.query.filter_by(owner_id=owner_id).order_by(Blog.id.desc()).all()
        return render_template('blog.html', title=author + "'s Posts", posts=posts)

    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title="Blogz", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['user']).first()

        title_error = valid_title(title)
        body_error = valid_body(body)

        if not title_error and not body_error:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            post = Blog.query.filter_by(title=title).first()
            post_id = post.id
            post_url = '/blog?id=' + str(post_id)
            return redirect(post_url)

        else:
            return render_template('newpost.html', title="Add a New Post", post_title=title, title_error=title_error, body=body, body_error=body_error)

    return render_template('newpost.html', title="Add a New Post")

@app.route('/')
def index():

    authors = User.query.order_by(User.username).all()
    return render_template('index.html', title="Authors", authors=authors)

if __name__ == '__main__':
    app.run()