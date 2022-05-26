from app import app, db
import os

import flask
from flask_login import login_user, current_user, LoginManager, logout_user
from flask_login.utils import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import RecipeData, User

import recipe
import random

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_name):
    return User.query.get(user_name)


@app.route("/")
def landing():
    if current_user.is_authenticated:
        return flask.redirect("index")
    return flask.redirect("login")


@app.route("/signup")
def signup():
    return flask.render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup_post():
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if len(username) < 3:
        flask.flash("Username must be at least 3 characters in length.")
        return flask.redirect(flask.url_for("signup"))
    if user:
        flask.flash("Username already in use.")
        return flask.redirect(flask.url_for("signup"))
    if len(password) < 6:
        flask.flash("Password must be at least 6 characters in length.")
        return flask.redirect(flask.url_for("signup"))
    else:
        user = User(
            username=username,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        flask.flash("Successfully registered.")
        return flask.redirect(flask.url_for("login"))


@app.route("/login")
def login():
    return flask.render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flask.flash("Please check your login details and try again.")
        return flask.redirect(flask.url_for("login"))

    else:
        login_user(user)
        return flask.redirect(flask.url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    flask.flash("Successfully logged out.")
    return flask.redirect("login")


@app.route("/search", methods=["GET", "POST"])
def search_recipe():
    if flask.request.method == "POST":
        data = flask.request.form.get("keyword")
    recipes = recipe.getRecipeList(data)
    return flask.render_template(
        "search.html", recipes=recipes, len_recipes=len(recipes)
    )


@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    if flask.request.method == "POST":
        data = flask.request.form
    recipes = recipe.getRandomRecipeList(data["keyword"])
    return flask.render_template(
        "recommendations.html",
        recipes=recipes,
        len_recipes=len(recipes),
        category=data["category"],
        keyword=data["keyword"],
        original_label=data["original_label"],
        original_id=data["original_id"],
    )


# route for homepage
@app.route("/index")
@login_required
def index():
    q = ["chicken", "salad", "soup", "pasta", "curry", "sandwich"]
    r = random.randrange(0, 6, 1)
    recipes = recipe.getRandomRecipeList(q[r])

    return flask.render_template(
        "index.html",
        username=current_user.username,
        q=q[r],
        recipes=recipes,
        len_recipes=len(recipes),
    )


@app.route("/details", methods=["GET", "POST"])
@login_required
def details():
    id = flask.request.form.get("id")
    label = flask.request.form.get("label")
    image = flask.request.form.get("image")
    url = flask.request.form.get("url")

    recipeDetails = recipe.getRecipeDetails(id)
    mealReco = recipeDetails["mealType"]
    cuisineReco = recipeDetails["cuisineType"]
    ingReco = recipeDetails["ingredients"]
    ingReco = ingReco[0]["food"]
    ingcatReco = recipeDetails["ingredients"]
    ingcatReco = ingcatReco[0]["foodCategory"]
    healthReco = recipeDetails["healthLabels"]

    calories = int(recipeDetails["calories"])
    dailyValue = int(recipeDetails["totalDaily"]["ENERC_KCAL"]["quantity"])

    # for comments:
    comments = RecipeData.query.filter_by(recipeid=id).all()

    return flask.render_template(
        "details.html",
        recipeDetails=recipeDetails,
        original_id=id,
        mealReco=mealReco,
        cuisineReco=cuisineReco,
        ingReco=ingReco,
        ingcatReco=ingcatReco,
        healthReco=healthReco,
        len_ing=len(recipeDetails["ingredientLines"]),
        label=label,
        image=image,
        url=url,
        calories=calories,
        dailyValue=dailyValue,
        comments=comments,
        len_comments=len(comments),
    )


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    userid = current_user.id
    recipes = RecipeData.query.filter_by(userid=userid).all()

    return flask.render_template(
        # display database information here
        "favorite.html",
        recipes=recipes,
        len_recipes=len(recipes),
    )


@app.route("/favorite", methods=["POST"])
@login_required
def favorite():
    recipeLabel = flask.request.form.get("recipeLabel")
    recipeImage = flask.request.form.get("recipeImage")
    recipeURL = flask.request.form.get("recipeURL")
    recipeID = flask.request.form.get("recipeID")
    checkDouble = RecipeData.query.filter_by(label=recipeLabel).first()

    new_saved = RecipeData(
        label=recipeLabel,
        image=recipeImage,
        url=recipeURL,
        userid=current_user.id,
        recipeid=recipeID,
    )

    if recipeLabel == checkDouble:
        return flask.redirect("/profile")

    else:
        db.session.add(new_saved)
        db.session.commit()
        return flask.redirect("/profile")


@app.route("/savefromdetails", methods=["POST"])
def savefromdetails():
    recipeImage = flask.request.form.get("recipeImage")
    recipeLabel = flask.request.form.get("recipeLabel")
    recipeURL = flask.request.form.get("recipeURL")
    recipeID = flask.request.form.get("recipeID")

    checkDouble = RecipeData.query.filter_by(label=recipeLabel).first()

    new_saved = RecipeData(
        label=recipeLabel,
        image=recipeImage,
        url=recipeURL,
        userid=current_user.id,
        recipeid=recipeID,
    )

    if recipeLabel == checkDouble:
        return flask.redirect("/profile")

    else:
        db.session.add(new_saved)
        db.session.commit()

        recipeDetails = recipe.getRecipeDetails(recipeID)
        mealReco = recipeDetails["mealType"]
        cuisineReco = recipeDetails["cuisineType"]
        ingReco = recipeDetails["ingredients"]
        ingReco = ingReco[0]["food"]
        ingcatReco = recipeDetails["ingredients"]
        ingcatReco = ingcatReco[0]["foodCategory"]
        healthReco = recipeDetails["healthLabels"]

        calories = int(recipeDetails["calories"])
        dailyValue = int(recipeDetails["totalDaily"]["ENERC_KCAL"]["quantity"])

        # for comments:
        comments = RecipeData.query.filter_by(recipeid=recipeID).all()

        return flask.render_template(
            "details.html",
            recipeDetails=recipeDetails,
            original_id=recipeID,
            mealReco=mealReco,
            cuisineReco=cuisineReco,
            ingReco=ingReco,
            ingcatReco=ingcatReco,
            healthReco=healthReco,
            len_ing=len(recipeDetails["ingredientLines"]),
            calories=calories,
            dailyValue=dailyValue,
            comments=comments,
            len_comments=len(comments),
        )


@app.route("/deletesaved", methods=["POST", "GET"])
def deletesaved():
    data = flask.request.form.get("reviewid")
    commdata = RecipeData.query.filter_by(recipeid=data).first()
    db.session.delete(commdata)
    db.session.commit()

    return flask.redirect("/profile")


@app.route("/rating", methods=["POST"])
def rating():
    if flask.request.method == "POST":
        rating = flask.request.form.get("rate", type=int)
        comment = flask.request.form.get("comment")
        image = flask.request.form.get("image")
        label = flask.request.form.get("label")
        url = flask.request.form.get("url")
        id = flask.request.form.get("id")

        rate_saved = RecipeData(
            rating=rating,
            comment=comment,
            image=image,
            label=label,
            url=url,
            userid=current_user.id,
            recipeid=id,
        )
        db.session.add(rate_saved)
        db.session.commit()

        recipeDetails = recipe.getRecipeDetails(id)
        mealReco = recipeDetails["mealType"]
        cuisineReco = recipeDetails["cuisineType"]
        ingReco = recipeDetails["ingredients"]
        ingReco = ingReco[0]["food"]
        ingcatReco = recipeDetails["ingredients"]
        ingcatReco = ingcatReco[0]["foodCategory"]
        healthReco = recipeDetails["healthLabels"]

        calories = int(recipeDetails["calories"])
        dailyValue = int(recipeDetails["totalDaily"]["ENERC_KCAL"]["quantity"])

        # for comments:
        comments = RecipeData.query.filter_by(recipeid=id).all()

        return flask.render_template(
            "details.html",
            recipeDetails=recipeDetails,
            original_id=id,
            mealReco=mealReco,
            cuisineReco=cuisineReco,
            ingReco=ingReco,
            ingcatReco=ingcatReco,
            healthReco=healthReco,
            len_ing=len(recipeDetails["ingredientLines"]),
            label=label,
            image=image,
            url=url,
            calories=calories,
            dailyValue=dailyValue,
            comments=comments,
            len_comments=len(comments),
        )


@app.route("/deletecomment", methods=["POST", "GET"])
def delete():
    data = flask.request.form.get("reviewid")
    commdata = RecipeData.query.filter_by(id=data).first()
    db.session.delete(commdata)
    db.session.commit()

    return flask.redirect("index")


@app.route("/comments")
@login_required
def comments():
    reviewInfo = RecipeData.query.filter_by(userid=current_user.id).all()
    reviewlen = len(reviewInfo)
    reviewlist = []
    for i in range(reviewlen):
        reviewlist.append(
            {
                "id": reviewInfo[i].id,
                "label": reviewInfo[i].label,
                "rating": reviewInfo[i].rating,
                "comment": reviewInfo[i].comment,
                "url": reviewInfo[i].url,
                "image": reviewInfo[i].image,
            }
        )
    return flask.render_template(
        "comments.html", review=reviewlist, name=current_user.id, length=reviewlen
    )


@app.route("/editcomment", methods=["POST"])
def editcomments():
    reviewid = flask.request.form.get("reviewid")
    editcomm = flask.request.form.get("comminput")
    editrate = flask.request.form.get("rateinput")
    commdata = RecipeData.query.filter_by(id=reviewid).first()
    commdata.comment = editcomm
    commdata.rating = editrate
    db.session.commit()
    return flask.redirect("/comments")


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"),
        port=int(os.getenv("PORT", 8080)),
        debug=True,
    )
