from flask import Flask, render_template

recipes = {
    "toad-in-the-hole": {
        "title": "Toad in the Hole",
        "image": "https://realfood.tesco.com/media/images/RFO-472x310-ToadInTheHole-a18fb881-11b0-4205-9a35-f7de8568e72e-0-472x310.jpg",
        "ingredients": [
            "8 pork sausages",
            "2 tbsp vegetable oil",
            "200g plain flour",
            "4 large eggs",
            "300ml milk",
            "Salt and pepper to taste",
        ],
        "score": 10,
        "serves": 4,
        "instructions": [
            "Preheat your oven to 220°C (200°C fan) or 425°F.",
            "Place the sausages in a large ovenproof dish, drizzle with oil, and bake for 15 minutes until they start to brown.",
            "While the sausages are cooking, prepare the batter. Whisk together the flour, eggs, milk, and a pinch of salt and pepper until smooth.",
            "Carefully remove the dish from the oven and pour the batter evenly over the sausages.",
            "Return to the oven and bake for 25-30 minutes until the batter is golden and risen.",
            "Serve immediately with onion gravy and vegetables of your choice.",
        ],
    },
    # Add more recipes here
}

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', recipes=recipes)

@app.route("/recipe/<recipe_id>")
def recipe(recipe_id):
    recipe = recipes.get(recipe_id)
    if not recipe:
        return "Recipe not found", 404
    return render_template("recipe.html", recipe=recipe)

if __name__ == "__main__":
    app.run(debug=True)