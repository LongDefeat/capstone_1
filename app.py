from crypt import methods
from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_bootstrap import Bootstrap
import os
import requests
import json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import os

from models import Drink_and_Measurement, db, connect_db, User, Favorite, Cocktail
from forms import EditProfileForm, UserAddForm, LoginForm, SearchDrink
from converter import cocktail_api

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///cocktail_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI').replace('postgres://', 'postgresql://')

toolbar = DebugToolbarExtension(app)

connect_db(app)
Bootstrap(app)


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

# ================== User signup/login/logout ===================# 

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
    drink_name = drink_obj['strDrink']

     
    # converts obj to json/string
    drink = Cocktail.add_drink(drink_id, drink_name)

    # add combined ingredients/measurements to instructions/measurements table

    ingredients = []
    measures = []
    combined = []

    for i in range(1, 15):
        if drink_obj[f'strIngredient{i}'] != None:
            ingredients.append(drink_obj[f'strIngredient{i}'])

        if drink_obj[f'strMeasure{i}'] != None:
            measures.append(drink_obj[f'strMeasure{i}'])
    
    for index, val in enumerate(ingredients):
        if index >= len(measures):
            combined.append(f'{ingredients[index]}')
        else:
            combined.append(f'{measures[index]} {ingredients[index]}')
    
    for i in combined:
        drink_and_measurement = Drink_and_Measurement(drink_and_measurement=i, drink_id=drink.id)
        db.session.add(drink_and_measurement)
        db.session.commit()

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
                bio = ""
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

    do_logout()
    flash("You logged out successfully!", 'success')
    return redirect("/login")

@app.route('/edit-profile/<int:user>', methods=['GET','POST'])
def edit_profile(user):

    form = EditProfileForm()
    user_id = g.user.id

    if not g.user.id == user_id:
        flash('You are not authorized to view this content.', 'danger')
        return redirect('/')

    # update = User.query.get_or_404(user)
    # print(user)
    # update.username = request.form['Username']
    # update.first_name = request.form['First Name']
    # update.last_name = request.form['Last Name']
    # update.email = request.form['Email']
    # update.bio = request.form['Bio']


    if form.validate_on_submit():
        try:
            user = User.update_user(
                username=form.username.data,
                password=form.password.data,
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                email=form.email.data,
                bio=form.bio.data,
            )
            db.session.add(user)
            db.session.commit()
            flash('Profiled updated!', 'success')

        except IntegrityError:
            flash('Failed to update. Please try again.', 'danger')
   

    return render_template('edit-profile.html', user=user, form=form, user_id=user_id)


@app.route('/profile/<int:user>', methods=['GET'])
def show_profile(user):
    if not g.user:
            return redirect('/')

    user = g.user.id

    drink_names = Cocktail.query.filter('drink_name')


    return render_template('profile.html', user=user, drink_names=drink_names)
    
# ==================Drink Searches==================


@app.route('/search', methods=['GET', 'POST'])
def search():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SearchDrink()
    drinks = {}

    if request.method == 'POST':
        drinks = cocktail_api().search(form.search.data)
        return redirect(f'search/{form.search.data}')
        
    return render_template('search.html', form=form, drinks=drinks)

@app.route('/search/<drink>', methods=['GET'])
def show_drink(drink):
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = SearchDrink()
      
    converter = cocktail_api()
    drink_response = converter.search(drink)
    drinks = converter.convert(drink_response)
    cocktail = drinks

    for drink in drinks:
        rows = Favorite.query.join(Cocktail, Favorite.drink_id == Cocktail.id).add_columns(Cocktail.drink_name).filter(Favorite.user_id == g.user.id).filter(Cocktail.drink_id == drink['id']).all()

        drink['is_favorite'] = len(rows) > 0

    if form.validate_on_submit():
        try:
            cocktail = drinks 
            Cocktail.add_drink(
            drink_id = drinks.id,
            user_id = g.user.index,
            drink_name=drinks.name            )
            db.session.commit()


        except IntegrityError:
            flash('Cocktail not found. Please try another one.', 'danger')
            return render_template('/search.html', form=form)
        
    
    return render_template('search.html', drinks=drinks, converter=converter, cocktail=cocktail)



@app.route('/search/<int:drink_id>/favorite', methods=['POST'])
def add_favorite(drink_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    save_drink(drink_id)   

    rows = Favorite.query.join(Cocktail, Favorite.drink_id == Cocktail.id).add_columns(Cocktail.drink_name).filter(Favorite.user_id == g.user.id).filter(Cocktail.drink_id == drink_id).all()

    if len(rows) > 0:
        drink_name = rows[0][1]
        flash("Drink already added.", "danger")
        return redirect(f'search/{drink_name}')

    user_id = g.user.id
    drink = drink_id
    
    
    Favorite.save_drink(user_id, drink)
    flash("Added Favorite.", "success")

    return redirect("/search")
