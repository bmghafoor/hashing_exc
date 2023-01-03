from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from sqlalchemy.exc import IntegrityError
from form import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_exercise"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect('/secret')
    
    return render_template('register.html',form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit:
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['invalid username/password']



    return render_template('login.html', form=form)


@app.route("/users/<int:id>")
def show_user(id):
    """Example page for logged-in-users."""

    user = User.query.get_or_404(id)

    return render_template("users.html", user=user)


@app.route('/secret')
def secret():
    if "user_id" not in session:
        flash('Please Login first','danger')
        return redirect('/login')
    return render_template('secret.html')



@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/login')





@app.route('/users/<int:id>/feedback/add', methods = ['GET', 'POST'])
def add_feedback(id):
    
    if "user_id" not in session:
        flash('Sign in', 'danger')
        return redirect('/login')
    
    form = FeedbackForm()

    if form.validate_on_submit:
        title = form.title.data
        content = form.content.data


        feedback = Feedback(title=title, content=content, user_id = id)
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{id}')

    return render_template('feedbackform.html', form=form)

@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    session.pop('user_id')
    return redirect ('/login')

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)


    form = FeedbackForm()

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("feedbackedit.html", form=form, feedback=feedback)

