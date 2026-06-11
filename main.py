from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text, nullable=False)
	time = db.Column(db.String(100), nullable=False)
	skills = db.Column(db.Text, nullable=False)
	link = db.Column(db.String(200))
	image = db.Column(db.String(200), nullable=False)

	def __init__(self, title, description, time, skills, link, image):
		self.title = title
		self.description = description
		self.time = time
		self.skills = skills
		self.link = link
		self.image = image

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Experience(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	time = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text, nullable=False)

	def __init__(self, title, time, description):
		self.title = title
		self.time = time
		self.description = description

class Profile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	gpa = db.Column(db.String(20))
	courses = db.Column(db.Text)
	tech_skills = db.Column(db.Text)
	programming_lang = db.Column(db.Text)
	dev_tools = db.Column(db.Text)

	def __init__(self, gpa, courses, tech_skills, programming_lang, dev_tools):
		self.gpa = gpa
		self.courses = courses
		self.tech_skills = tech_skills 
		self.programming_lang = programming_lang
		self.dev_tools = dev_tools

class Certification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	date = db.Column(db.String(100))

	def __init__(self, name, date):
		self.name = name 
		self.date = date 

class Award(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	date = db.Column(db.String(100))

	def __init__(self, name, date):
		self.name = name 
		self.date = date 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
	profile = Profile.query.first()
	return render_template("home.html", profile = profile)

@app.route("/education")
def education():
	profile = Profile.query.first()
	all_certifications = Certification.query.all()
	all_awards = Award.query.all()
	return render_template("education.html", profile = profile, certifications = all_certifications, awards = all_awards)

@app.route("/experience")
def experience():
	all_experiences = Experience.query.all()
	return render_template("experience.html", experiences = all_experiences)

@app.route("/projects")
def projects():
	all_projects = Project.query.all()
	return render_template("projects.html", projects = all_projects)

@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		time = request.form['time']
		skills = request.form['skills']
		link = request.form['link']
		image = request.files['image']

		filename = secure_filename(image.filename)

		image.save(
	    	os.path.join(
	        	app.config['UPLOAD_FOLDER'],
	        	filename
	    	)
		)

		project = Project(title, description, time, skills, link, filename)

		db.session.add(project)
		db.session.commit()

		return redirect(url_for('projects'))
	return render_template("add_project.html")

@app.route('/add_experience', methods=['GET', 'POST'])
@login_required
def add_experience():
	if request.method == 'POST':
		title = request.form['title']
		description = request.form['description']
		time = request.form['time']

		experience = Experience(title, time, description)

		db.session.add(experience)
		db.session.commit()

		return redirect(url_for('experience'))
	return render_template("add_experience.html")

@app.route('/add_certification', methods=['GET', 'POST'])
@login_required
def add_certification():
	if request.method == 'POST':
		name = request.form['name']
		date = request.form['date']

		certification = Certification(name, date)
		db.session.add(certification)
		db.session.commit()

		return redirect(url_for('education'))
	return render_template("add_certification.html")

@app.route('/add_award', methods=['GET', 'POST'])
@login_required
def add_award():
	if request.method == 'POST':
		name = request.form['name']
		date = request.form['date']

		award = Award(name, date)
		db.session.add(award)
		db.session.commit()

		return redirect(url_for('education'))
	return render_template("add_award.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("projects"))

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("projects"))

@app.route("/edit_profile", methods = ['GET', 'POST'])
@login_required
def edit_profile():
	profile = Profile.query.first()
	if request.method == "POST":
		profile.gpa = request.form["gpa"]
		profile.courses = request.form["courses"]
		profile.tech_skills = request.form["tech_skills"]
		profile.programming_lang = request.form["programming_lang"]
		profile.dev_tools = request.form["dev_tools"]

		db.session.commit()

		return redirect(url_for("education"))
	return render_template("edit_profile.html", profile = profile)

@app.route("/edit_project/<int:project_id>", methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
	project = Project.query.get_or_404(project_id)

	if request.method == "POST":

		project.title = request.form['title']
		project.description = request.form['description']
		project.time = request.form['time']
		project.skills = request.form['skills']
		project.link = request.form['link']

		db.session.commit()

		return redirect('/projects')
	return render_template('edit_project.html', project=project) 

@app.route("/delete_project/<int:project_id>")
@login_required
def delete_project(project_id):
	project = Project.query.get_or_404(project_id)

	image_path = os.path.join(
    app.config['UPLOAD_FOLDER'],
    project.image)

	if os.path.exists(image_path):
		os.remove(image_path)

	db.session.delete(project)
	db.session.commit()
	return redirect('/projects')

@app.route("/edit_experience/<int:experience_id>", methods=['GET', 'POST'])
@login_required
def edit_experience(experience_id):
	experience = Experience.query.get_or_404(experience_id)

	if request.method == "POST":

		experience.title = request.form['title']
		experience.description = request.form['description']
		experience.time = request.form['time']

		db.session.commit()

		return redirect('/experience')
	return render_template('edit_experience.html', experience=experience) 

@app.route("/delete_experience/<int:experience_id>")
@login_required
def delete_experience(experience_id):
	experience = Experience.query.get_or_404(experience_id)

	db.session.delete(experience)
	db.session.commit()
	return redirect('/experience')

@app.route("/edit_certification/<int:certification_id>", methods=['GET', 'POST'])
@login_required
def edit_certification(certification_id):
	certification = Certification.query.get_or_404(certification_id)

	if request.method == "POST":

		certification.name = request.form['name']
		certification.date = request.form['date']

		db.session.commit()

		return redirect('/education')
	return render_template('edit_certification.html', certification=certification) 

@app.route("/delete_certification/<int:certification_id>")
@login_required
def delete_certification(certification_id):
	certification = Certification.query.get_or_404(certification_id)

	db.session.delete(certification)
	db.session.commit()
	return redirect('/education')

@app.route("/edit_award/<int:award_id>", methods=['GET', 'POST'])
@login_required
def edit_award(award_id):
	award = Awards.query.get_or_404(award_id)

	if request.method == "POST":

		award.name = request.form['name']
		award.date = request.form['date']

		db.session.commit()

		return redirect('/education')
	return render_template('edit_award.html', award=award) 

@app.route("/delete_award/<int:award_id>")
@login_required
def delete_award(award_id):
	award = Award.query.get_or_404(award_id)

	db.session.delete(award)
	db.session.commit()
	return redirect('/education')

if __name__ == "__main__":
	with app.app_context():
		db.create_all()

		if not User.query.filter_by(username="Andrew").first():
			admin = User(
	        	username="Andrew",
	        	password_hash=generate_password_hash("andrewfirstwebsite")
	        )
		
			db.session.add(admin)
			db.session.commit()

		if not Profile.query.first():
			profile = Profile(
				gpa="3.93",
				courses = "Electrical Circuits, Electronic Circuit Design and Analysis, Signals and Systems, Electromagnetic Fields and Waves, Multivariable Calculus, Linear Algebra, Partial Differential Equations",
				tech_skills = "AWS, Circuit Design, PCB, Soldering",
				programming_lang = "Python, Java, C, C++, C#, React Native",
				dev_tools = "MATLAB, LTspice Altium, Arduino, Microsoft Office(word, powerpoint)",
			)
			db.session.add(profile)
			db.session.commit()

	app.run(debug=True)