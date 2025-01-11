from flask import Flask, render_template, redirect, request, url_for



app = Flask(__name__)
app.secret_key = 'my_secret_key'

@app.route('/')
def index():
    return render_template("Home.html")


if __name__ == '__main__':
    app.run(debug=True)