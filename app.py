from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify
from datetime import timedelta, datetime
from bson.objectid import ObjectId

import pymongo

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


# ------------------ database and collectios ---------------------- #

myclient = pymongo.MongoClient("mongodb+srv://abhi:1maratha@cluster0.frc7h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = myclient["shikshaeduhub"]
collection_admin = db["admin"]
collection_blog_posts = db["blogposts"]



# ------------------------ cloudinary cloud ------------------------ #

cloudinary.config( 
    cloud_name = "dql90uw2x", 
    api_key = "272696395322952", 
    api_secret = "9UBaqXBLiAikOSFlK55cXKNAsAw",
    secure=True
)

# --------------------------- routes ------------------------------ #
app = Flask(__name__)
app.secret_key = 'my_secret_key'

@app.route('/')
def home():
    rblogposts = collection_blog_posts.aggregate([{ "$sample": { "size": 1 } }])
    blogposts = collection_blog_posts.find().sort("_id",-1)

    return render_template("home.html", email=session.get('email'), rblogposts=rblogposts, blogposts=blogposts )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        

        user = collection_admin.find_one({'email': email})
        
        if email == user["email"] and password == user["password"]:
            
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)
            session['email'] = email

            flash('Login successful!', 'success')
            return redirect(url_for('home'))  # Redirect to index route
        else:
            flash('Invalid email or password', 'error')

    return render_template("login.html")

@app.route('/profile')
def profile():
    email =session.get('email')

    if email:
        user = collection_admin.find_one({'email': email})
        
        
        email = user['email']
        name=user['name']
        password=user['password']
        return render_template('profile.html', email=email, name=name, password=password, user = user)

    return render_template('login.html', email=email, name=name, password=password)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    session.pop('semail', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/blog_write' , methods=["GET", "POST"])
def blog_write():
    
    email = session.get('email')
    admin = collection_admin.find_one({"email": email})
    name = admin['name']

    if request.method == "POST":
        blogcategory = request.form["category"]
        blogtitle = request.form["title"]
        blogcontent = request.form["content"]
        # blogdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        blogdate = datetime.now().strftime(" %B-%d-%Y ")
        blogtime = datetime.now().strftime(" %H:%M:%S ")

        
        blogimage = request.files["image"]
        bimg = cloudinary.uploader.upload(blogimage)
        blogimageurl = bimg["secure_url"]

        collection_blog_posts.insert_one({"blogcategory":blogcategory,
                                          "blogtitle":blogtitle,
                                          "blogcontent":blogcontent,
                                          "blogdate": blogdate,
                                          "blogtime": blogtime,
                                          "blogimageurl":blogimageurl,
                                          "author": name})
        
        return redirect('blogsmanagement') 
    

    return render_template("blog_write.html", email=session.get('email'))


@app.route('/post/<id>')
def post(id):
    
    blogpost = collection_blog_posts.find_one({"_id" : ObjectId(id)})
    return render_template("post.html", email=session.get('email'), blogpost = blogpost)


@app.route('/blogsmanagement')
def blogsmanagement():
    
    email = session.get('email')
    admin = collection_admin.find_one({"email": email})
    name = admin['name']


    blogposts = collection_blog_posts.find({"author":name}).sort("_id",-1)
    return render_template("blogsmanagement.html", email=session.get('email'),blogposts=blogposts)



if __name__ == '__main__':
    app.run(debug=True)