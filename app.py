from flask import Flask,render_template,request,redirect,url_for,session,flash
import sqlite3,os
app=Flask(__name__);app.secret_key="change-this-secret"
DB="exam.db"
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 c=db()
 c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT,role TEXT,name TEXT)")
 c.execute("CREATE TABLE IF NOT EXISTS exams(id INTEGER PRIMARY KEY,title TEXT,subject TEXT,duration INTEGER,questions INTEGER)")
 c.execute("CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY,title TEXT,author TEXT,price REAL)")
 if not c.execute("SELECT 1 FROM users WHERE username='admin'").fetchone(): c.execute("INSERT INTO users(username,password,role,name) VALUES('admin','admin123','admin','Administrator')")
 c.commit();c.close()
@app.before_request
def setup(): init()
def auth(f):
 def w(*a,**k):
  if not session.get("user_id"): return redirect(url_for("login"))
  return f(*a,**k)
 w.__name__=f.__name__;return w
@app.route("/")
def home(): return render_template("index.html")
@app.route("/login",methods=["GET","POST"])
def login():
 if request.method=="POST":
  c=db();u=c.execute("SELECT * FROM users WHERE username=? AND password=?",(request.form["username"],request.form["password"])).fetchone();c.close()
  if u: session["user_id"]=u["id"];session["username"]=u["username"];return redirect(url_for("dashboard"))
  flash("Invalid username or password")
 return render_template("login.html")
@app.route("/logout")
def logout(): session.clear();return redirect(url_for("login"))
@app.route("/dashboard")
@auth
def dashboard():
 c=db();x={"exams":c.execute("SELECT COUNT(*) FROM exams").fetchone()[0],"students":c.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],"books":c.execute("SELECT COUNT(*) FROM books").fetchone()[0]};c.close();return render_template("dashboard.html",**x)
@app.route("/exams",methods=["GET","POST"])
@auth
def exams():
 c=db()
 if request.method=="POST": c.execute("INSERT INTO exams(title,subject,duration,questions) VALUES(?,?,?,?)",(request.form["title"],request.form.get("subject","General"),request.form.get("duration",60),request.form.get("questions",0)));c.commit()
 r=c.execute("SELECT * FROM exams ORDER BY id DESC").fetchall();c.close();return render_template("exams.html",exams=r)
@app.route("/books",methods=["GET","POST"])
@auth
def books():
 c=db()
 if request.method=="POST": c.execute("INSERT INTO books(title,author,price) VALUES(?,?,?)",(request.form["title"],request.form.get("author",""),request.form.get("price",0)));c.commit()
 r=c.execute("SELECT * FROM books ORDER BY id DESC").fetchall();c.close();return render_template("books.html",books=r)
@app.route("/students")
@auth
def students():
 c=db();r=c.execute("SELECT * FROM users WHERE role='student'").fetchall();c.close();return render_template("students.html",students=r)
@app.route("/mock-test")
@auth
def mock_test(): return render_template("mock_test.html")
@app.route("/questions")
@auth
def questions(): return render_template("questions.html")
@app.route("/results")
@auth
def results(): return render_template("results.html")
@app.route("/government-forms")
@auth
def government_forms(): return render_template("government_forms.html")
@app.route("/advertisements")
@auth
def advertisements(): return render_template("advertisements.html")
if __name__=="__main__": init();app.run(debug=True)
