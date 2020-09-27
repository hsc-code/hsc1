from flask import Flask,render_template

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def fun():
     return render_template("html")

if __name__ == "__main__":
     app.run()