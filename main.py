from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
       
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        body_error = ''
        title_error = ''

        if not blog_title:
            title_error = 'Title must contain text.'
        
        if not blog_body:
            body_error = 'Body must contain text.'
                
        if not body_error and not title_error:
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('./blog?id={}'.format(new_post.id))
        else:
            return render_template('new_post.html', title='New Entry', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)

    return render_template('new_post.html', title='new_post.id')
    
    

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    single_user_id = request.args.get('owner_id')

    if single_user_id:
        ind_user_post = Blog.query.filter_by(owner_id=single_user_id)
        return render_template('single_user.html', posts=ind_user_post)
    if blog_id == None :
        posts = Blog.query.all()
        return render_template('blog.html', posts=posts, title='Blogz')

    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

    return render_template('blog.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/login')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''

        existing_user = User.query.filter_by(username=username).first()
        
        if existing_user:
            username_error = 'That username already exists.'

        if username == '':
            username_error = 'That is not a valid username.'

        elif " " in username:
            username_error = 'The username must have no spaces.'
            

        elif len(username) < 3 or len(username) > 20:
            username_error = 'The username must be between 3-20 characters in length'
            

        if password == '':
            password_error = 'That is not a valid password.'

        elif " " in password:
            password_error = 'The password must have no spaces.'
            password = ""

        elif len(password) < 3 or len(password) > 20:
            password_error = 'The password must be between 3-20 characters in length'
            password = ""

        if verify == ' ' or verify != password:
            verify_error = 'Passwords do not match.'
            verify = ''
            
        if not existing_user and not username_error and not password_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template('signup.html',username=username,
            username_error=username_error,
            password_error=password_error, 
            verify_error=verify_error,)

    return render_template('signup.html', title='Sign Up')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()