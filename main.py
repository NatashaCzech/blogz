from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post = db.Column(db.String(800))

    def __init__(self, title, post):
        self.title = title
        self.post = post

    

@app.route("/")
def form():
    return render_template('blog.html') 

#display single entry or all entries 
@app.route('/blog')
def display_blog():
    post_id = request.args.get('id')
    if (post_id):
        single_post = Blog.query.get(post_id)
        return render_template('single_post.html', single_post=single_post)
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

        title_error=""
        blog_post_error=""

        blog_title = request.form['blog_title']
        post_entry = request.form['blog_post']
        new_post = Blog(blog_title, post_entry)
        
    
        if empty_entry (blog_title) and empty_entry (post_entry):
            db.session.add(new_post)
            db.session.commit()
            post_link ="/blog?id=" + str(new_post.id)
            return redirect(post_link)

        else:
            if not empty_entry (blog_title) and not empty_entry (post_entry):
                title_error =" Don't forget to add your title! "
                blog_post_error = " You'll want to add your blog here! "
                return render_template ('newpost.html', title_error=title_error, blog_post_error=blog_post_error)
            elif not empty_entry (post_entry):
                blog_post_error = " You'll want to add your blog here! "
                return render_template ('newpost.html', blog_post_error=blog_post_error)
            elif not empty_entry (blog_title):
                title_error =" Don't forget to add your title! "
                return render_template ('newpost.html', title_error=title_error)    

        
   
    else:
        return render_template('newpost.html')




if __name__ == '__main__':
    app.run()