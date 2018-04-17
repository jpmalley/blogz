from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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

@app.route('/blog')
def blog():

    post_id = request.args.get("id")

    if post_id:
        single_post = Blog.query.filter_by(id=post_id).first()
        if single_post:
            return render_template('singlepost.html', title=single_post.title, post=single_post)
        else:
            flash('That post does not exist!')
            posts = Blog.query.all()
            return render_template('blog.html', title="Build-a-Blog", posts=posts)

    posts = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('blog.html', title="Build-a-Blog", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error = valid_title(title)
        body_error = valid_body(body)

        if not title_error and not body_error:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            post = Blog.query.filter_by(title=title).first()
            post_id = post.id
            post_url = '/blog?id=' + str(post_id)
            return redirect(post_url)

        else:
            return render_template('newpost.html', title="Add a New Post", post_title=title, title_error=title_error, body=body, body_error=body_error)

    return render_template('newpost.html', title="Add a New Post")

if __name__ == '__main__':
    app.run()