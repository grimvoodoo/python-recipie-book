import datetime
import os
from bson import ObjectId
import dotenv
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient

dotenv.load_dotenv()

# Connect to MongoDB
client = MongoClient(
    os.getenv("MONGO_URI")
)  # Replace with your connection string later
db = client.cookbook  # Use 'cookbook' database
recipes_collection = db.recipes  # Use 'recipes' collection

app = Flask(__name__)


@app.route("/")
def index():
    recipes = list(
        recipes_collection.find({}, {"_id": 1, "name": 1, "image": 1, "score": 1, "serves": 1})
    )
    print(recipes)
    return render_template("index.html", recipes=recipes)


@app.route("/recipe/<recipe_id>", methods=["GET", "POST"])
def recipe(recipe_id):
    if request.method == "POST":
        # Get form data
        comment = request.form.get("comment")

        # Validate required fields
        if not comment:
            return "comment is required.", 400

        # Create a new comment document
        new_comment = {
            "_id": ObjectId(),
            "timestamp": datetime.datetime.now(),
            "text": comment,
        }

        # Update the recipe document with the new comment
        recipes_collection.update_one(
            {"_id": recipe_id}, {"$push": {"comments": new_comment}}
        )

        return redirect(url_for("recipe", recipe_id=recipe_id))

    recipe = recipes_collection.find_one({"_id": recipe_id})
    if not recipe:
        return "Recipe not found", 404
    return render_template("recipe.html", recipe=recipe)


@app.route("/delete_comment/<recipe_id>/<comment_id>", methods=["GET", "POST"])
def delete_comment(recipe_id, comment_id):
    recipes_collection.update_one(
        {"_id": recipe_id}, {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}
    )
    return redirect(url_for("recipe", recipe_id=recipe_id))


@app.route("/edit_comment/<recipe_id>/<comment_id>", methods=["GET", "POST"])
def edit_comment(recipe_id, comment_id):
    if request.method == "POST":
        # Get form data
        comment = request.form.get("comment")

        # Validate required fields
        if not comment:
            return "Comment is required.", 400

        # Update the comment
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
def add_recipe():
    if request.method == 'POST':
        # Get form data
        recipe_name = request.form.get('name')
        recipe_description = request.form.get('description')
        recipe_image = request.form.get('image')
        recipe_score = request.form.get('score')
        recipe_serves = request.form.get('serves')

        # Collect ingredients
        ingredient_names = request.form.getlist('ingredient_name')
        ingredient_quantities = request.form.getlist('ingredient_quantity')
        ingredient_measurements = request.form.getlist('ingredient_measurement')

        # Create a list of dictionaries for ingredients
        ingredients = [
            {
                "name": name,
                "quantity": quantity,
                "measurement": measurement
            }
            for name, quantity, measurement in zip(ingredient_names, ingredient_quantities, ingredient_measurements)
        ]

        # Collect instructions (if applicable)
        instructions = request.form.get('instructions')

        # Create the new recipe document
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

        # Insert into the database
        recipes_collection.insert_one(new_recipe)

        return redirect(url_for('index'))

    return render_template('add_recipe.html')



@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    # Handle form submission
    if request.method == 'POST':
        # Get updated data from the form
        recipe_name = request.form.get('name')
        recipe_description = request.form.get('description')

        # Handle ingredients
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

        # Update the recipe in the database
        recipes_collection.update_one(
            {"_id": recipe_id},
            {"$set": {
                "name": recipe_name,
                "description": recipe_description,
                "ingredients": ingredients
            }}
        )
        return redirect(url_for('recipe', recipe_id=recipe_id))

    # Fetch recipe data for the edit form
    recipe = recipes_collection.find_one({"_id": recipe_id})
    if not recipe:
        return "Recipe not found", 404
    
    return render_template('edit_recipe.html', recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)
