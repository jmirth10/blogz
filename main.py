from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
       
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():

    return redirect('/blog')


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    
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
            new_post = Blog(blog_title, blog_body )
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id{}'.format(new_post.id))
        else:
            return render_template('new_post.html', title='New Entry', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)

    return render_template('new_post.html', title='new_post.id')
    
    

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    if blog_id == None :
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs, title='Build-a-Blog')

    else:
        blog = Blog.query.get(blog_id)
        return render_template('entry.html', blog=blog, title='Blog Entry')






    return render_template('blog.html')

if __name__ == '__main__':
    app.run()