from crypt import methods
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_bootstrap import Bootstrap
import os
import requests
import json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Favorite, Cocktail
from forms import EditProfileForm, UserAddForm, LoginForm, SearchDrink
from converter import JSON_converter

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///cocktail_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

toolbar = DebugToolbarExtension(app)

connect_db(app)
Bootstrap(app)



# if a current user is in session, g.user IS that current user. Basically, affirms that this is an active session. 
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

# ================== Home Page ========================
@app.route('/')
def homepage():

    if g.user:    
        favorites = [favorite.id for favorite in g.user.favorites]
        return render_template('home.html', favorites=favorites)
    else:
        return render_template('home-anon.html')


# User signup/login/logout

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def save_drink(drink_id):
    url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"

    response = requests.get(url)

    drink_json = response.json()
    drinks_json = drink_json['drinks']
    drink_obj = drinks_json[0]

    print(drink_obj)
    # converts obj to json/string
    drink = Cocktail.add_drink(drink_id, json.dumps(drink_obj))

    return drink

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash('Username already taken, please try another one.', 'danger')
            return render_template('/signup.html', form=form, user=user)
        
        do_login(user)

        return redirect('/')

    else:
        return render_template('/signup.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    # Need to call the method above in order for it to work
    do_logout()
    flash("You logged out successfully!", 'success')
    return redirect("/login")


@app.route('/edit-profile', methods=['GET','POST'])
def edit_profile():

    form = EditProfileForm()

    if not g.user:
        return redirect('/')
    
    return render_template('/edit-profile.html', user=g.user, form=form)

@app.route('/profile', methods=['GET', 'POST'])
def show_profile():
    if not g.user:
            return redirect('/')

    return render_template('/profile.html')
    

# ==================Drink Searches==================


@app.route('/search', methods=['GET', 'POST'])
    # this is where you would search for cocktails and fetch JSON
def search():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SearchDrink()
    drinks = {}

    if request.method == 'POST':
        drinks = JSON_converter().search(form.search.data)
        return redirect(f'search/{form.search.data}')
        
    return render_template('search.html', form=form, drinks=drinks)

@app.route('/search/<drink>', methods=['GET'])
def show_drink(drink):
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SearchDrink()
    res = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={drink}")   
    
    converter = JSON_converter()
    drink_response = converter.search(drink)
    drinks = converter.convert(drink_response)
    cocktail=drinks
    if form.validate_on_submit():
        return redirect(f"/search/{drinks}")

    if form.validate_on_submit():
        try:
            cocktail = drinks 
            Cocktail.add_drink(
            drink_id = drinks.id,
            user_id = g.user.index
            )
            db.session.commit()

        except IntegrityError:
            flash('Cocktail not found. Please try another one.', 'danger')
            return render_template('/search.html', form=form)
        
    
    return render_template('search.html', drinks=drinks, converter=converter, cocktail=cocktail)



@app.route('/search/<int:drink_id>/favorite', methods=['POST'])
def add_favorite(drink_id):
    # list out g.user.favorites
    # can then click a favorite cocktail to get to next route for fav_id
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    save_drink(drink_id)   
    
    # if request.method == 'POST':
    #     if request.form['submit'] == 'Do Something':
    #         pass # do something

    user_id = g.user.id
    drink = drink_id
    print('XXXXXXXXXXXXXXXXXXX')
    print(user_id)
    print(drink)

    # favorite_drink = SearchDrink.data
    
    
    Favorite.save_drink(user_id, drink)
    flash("Added Favorite.", "success")

    return redirect("/search")



# app.route('/favorite/<fav_id>, methods=['GET'])
    # will show a specific favorite recipe