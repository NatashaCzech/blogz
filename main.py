from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '\xdf\xb0\xf7\xff\xd7\x80$\xc0\xe5\xcf\xf9\xf5\n\xb3w\xaa'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(120))
    post = db.Column(db.String(800))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship( 'Blog', backref='owner') 

    def __init__(self,username, password):
        self.username = username
        self.password = password  

    
    

@app.before_request
def require_login():
    allowed_routes = ['user_login', 'signup', 'display_blog', 'index',]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    all_users = User.query.distinct()
    return render_template('index.html', list_all_users=all_users)

#display single entry or all entries 
@app.route('/blog')
def display_blog():
    post_id = request.args.get('id')
    user_id = request.args.get('owner_id')
    if (post_id):
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html', single_post=single_post)
    else:
        if (user_id):
            user_posts = Blog.query.filter_by(owner_id = user_id)
            return render_template ('singleuser.html', posts = user_posts)

        else:
            all_blog_entries = Blog.query.all()  
            return render_template ('blog.html', posts= all_blog_entries)

def empty_entry(x):
    if x:
        return True
    else:
        return False

@app.route('/newpost', methods=['POST' , 'GET'])
def add_new_post():

    if request.method == 'POST':


        owner = User.query.filter_by (username=session['username']).first()
        blog_title = request.form['blog_title']
        post_entry = request.form['post_entry']
        new_post = Blog(blog_title, post_entry, owner)
        
    
        if empty_entry (blog_title) and empty_entry (post_entry):
            db.session.add(new_post)
            db.session.commit()
            post_link ="/blog?id=" + str(new_post.id)
            return redirect('/newpost')

        else:
            if not empty_entry (blog_title) and not empty_entry (post_entry):
                flash('You need to add your title and enter your blog text!', 'error')
                return render_template ('newpost.html', blog_title=blog_title, post_entry=post_entry)
            elif not empty_entry (post_entry):
                flash('Add your blog here!', 'error')
                return render_template ('newpost.html', blog_title=blog_title)
            elif not empty_entry (blog_title):
                flash('Add your title!','error')
                return render_template ('newpost.html', post_entry=post_entry)

        
   
    else:
        return render_template('newpost.html')

@app.route ('/signup', methods=['POST', 'GET'])

def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        verified_password = request.form['verified_password'] 

        if len(username) == 0:
            flash('Whoa there! Fill in your username please.', 'error')
            return render_template('signup.html')
            
        if len(password) == 0:
            flash('You need to fill in your password please.', 'error')
            return render_template('signup.html')
            
        if len(verified_password) == 0:
            flash('Please re-type your password.', 'error')
            return render_template('signup.html')

        if len(username) <3:
            flash('You came up short! Make that Username longer;)', 'error')
            return render_template('signup.html')

        if len(password) <3:
            flash('You came up short!', 'error')
            return render_template('signup.html')

        if verified_password != password:
            flash('Whoops! Passwords did not match. Try again.', 'error')
            return render_template('signup.html')

    
        existing_user = User.query.filter_by(username=username).first()

        existing_user_error = ""

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')

        else:
            existing_user_error = "Sorry, that user already exists."
            return render_template('signup.html')

    else: 
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])

def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username and not password:
            flash('Whoa! Fill these in please!', 'error')
            return render_template('login.html')
        if not username:
            flash('Username Required', 'error')
            return render_template('login.html')
        if not password:
            flash('Password Required', 'error')
            return render_template('login.html')


        user = User.query.filter_by(username=username).first()

        #Work- Try some flash messaging

        if not user:
            flash('Wrong! Try again!', 'error')
            return render_template('login.html')
       
        if user.password != password:
            flash('Incorrect Password', 'error')
            return render_template('login.html')

        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()