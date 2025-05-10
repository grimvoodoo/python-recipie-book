import os
import random
import string
from datetime import timedelta
from bson import ObjectId
from flask import Flask, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from pymongo import MongoClient
import dotenv

dotenv.load_dotenv()

# ——— App setup ———
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=90)
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=90)

bcrypt = Bcrypt(app)

# ——— Database ———
client = MongoClient(os.getenv("MONGO_URI"))
db = client.cookbook
users_collection = db.users
recipes_collection = db.recipes


# ——— Flask-Login setup ———
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, password_hash, _id):
        self.id = str(_id)
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    u = users_collection.find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    return User(u["username"], u["password"], u["_id"])

# ——— Default admin on startup ———
@app.before_request
def create_default_admin():
    if users_collection.count_documents({}) == 0:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        users_collection.insert_one({
            "username": "admin",
            "password": bcrypt.generate_password_hash(pwd).decode(),
        })
        print("Default admin:", pwd)

# ——— Routes ———
@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users_collection.find_one({"username": username}):
            return "Username exists", 400
        users_collection.insert_one({
            "username": username,
            "password": bcrypt.generate_password_hash(password).decode()
        })
        return redirect(url_for("index"))
    return render_template("register.html")  # <-- re-add this

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = bool(request.form.get("remember"))
        record = users_collection.find_one({"username": username})
        # — typo fixed: record, not rrecord
        if not record or not bcrypt.check_password_hash(record["password"], password):
            error = "Invalid username or password."
        else:
            user = User(record["username"], record["password"], record["_id"])
            login_user(user, remember=remember)
            return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", error=error)  # <-- re-add this

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# Existing Routes
@app.route("/")
@login_required
def index():
    recipes = list(
        recipes_collection.find({}, {"_id": 1, "name": 1, "image": 1, "score": 1, "serves": 1})
    )
    return render_template("index.html", recipes=recipes)


@app.route("/recipe/<recipe_id>", methods=["GET", "POST"])
@login_required
def recipe(recipe_id):
    if request.method == "POST":
        comment = request.form.get("comment")

        if not comment:
            return "comment is required.", 400

        new_comment = {
            "_id": ObjectId(),
            "timestamp": datetime.datetime.now(),
            "text": comment,
        }

        recipes_collection.update_one(
            {"_id": recipe_id}, {"$push": {"comments": new_comment}}
        )

        return redirect(url_for("recipe", recipe_id=recipe_id))

    recipe = recipes_collection.find_one({"_id": recipe_id})
    if not recipe:
        return "Recipe not found", 404
    return render_template("recipe.html", recipe=recipe)


@app.route("/delete_comment/<recipe_id>/<comment_id>", methods=["GET", "POST"])
@login_required
def delete_comment(recipe_id, comment_id):
    recipes_collection.update_one(
        {"_id": recipe_id}, {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}
    )
    return redirect(url_for("recipe", recipe_id=recipe_id))


@app.route("/edit_comment/<recipe_id>/<comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(recipe_id, comment_id):
    if request.method == "POST":
        comment = request.form.get("comment")

        if not comment:
            return "Comment is required.", 400

        recipes_collection.update_one(
            {"_id": recipe_id, "comments._id": ObjectId(comment_id)},
            {"$set": {"comments.$.text": comment}},
        )

        return redirect(url_for("recipe", recipe_id=recipe_id))

    recipe = recipes_collection.find_one({"_id": recipe_id})
    comment = next(
        comment for comment in recipe["comments"] if str(comment["_id"]) == comment_id
    )
    return render_template("edit_comment.html", recipe=recipe, comment=comment)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        recipe_name = request.form.get('name')
        recipe_description = request.form.get('description')
        recipe_image = request.form.get('image')
        recipe_score = request.form.get('score')
        recipe_serves = request.form.get('serves')

        ingredient_names = request.form.getlist('ingredient_name')
        ingredient_quantities = request.form.getlist('ingredient_quantity')
        ingredient_measurements = request.form.getlist('ingredient_measurement')

        ingredients = [
            {
                "name": name,
                "quantity": quantity,
                "measurement": measurement
            }
            for name, quantity, measurement in zip(ingredient_names, ingredient_quantities, ingredient_measurements)
        ]

        instructions = request.form.get('instructions')

        new_recipe = {
            "_id": recipe_name.replace(" ", "-").lower(),
            "name": recipe_name,
            "image": recipe_image,
            "description": recipe_description,
            "ingredients": ingredients,
            "instructions": instructions,
            "score": recipe_score,
            "serves": recipe_serves
        }

        recipes_collection.insert_one(new_recipe)

        return redirect(url_for('index'))

    return render_template('add_recipe.html')


@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    if request.method == 'POST':
        recipe_name = request.form.get('name')
        recipe_description = request.form.get('description')

        ingredient_names = request.form.getlist('ingredient_name')
        ingredient_quantities = request.form.getlist('ingredient_quantity')
        ingredient_measurements = request.form.getlist('ingredient_measurement')
        ingredients = [
            {
                "name": name,
                "quantity": quantity,
                "measurement": measurement
            }
            for name, quantity, measurement in zip(ingredient_names, ingredient_quantities, ingredient_measurements)
        ]

        recipes_collection.update_one(
            {"_id": recipe_id},
            {"$set": {
                "name": recipe_name,
                "description": recipe_description,
                "ingredients": ingredients
            }}
        )
        return redirect(url_for('recipe', recipe_id=recipe_id))

    recipe = recipes_collection.find_one({"_id": recipe_id})
    if not recipe:
        return "Recipe not found", 404

    return render_template('edit_recipe.html', recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)
