import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

BASE_URL = "https://api.edamam.com/api/recipes/v2"

# function returns a list of 20(?) random dishes according to a query (q)
def getRandomRecipeList(q):
    params = {
        "type": "public",
        "app_id": os.getenv("APP_ID"),
        "app_key": os.getenv("APP_KEY"),
        "q": q,
        "random": True,
    }

    response = requests.get(BASE_URL, params=params).json()["hits"]

    randomRecipeList = []

    for hit in response:
        randomRecipeList.append(
            {
                "label": hit["recipe"]["label"],
                "image": hit["recipe"]["image"],
                "source": hit["recipe"]["source"],
                "url": hit["recipe"]["url"],
                # split the uri in two at the target ("_") to get id at the end
                "id": hit["recipe"]["uri"].split("_", 1)[1],
            }
        )

    return randomRecipeList


def getRecipeList(q):
    params = {
        "type": "public",
        "app_id": os.getenv("APP_ID"),
        "app_key": os.getenv("APP_KEY"),
        "q": q,
        "random": False,
    }

    response = requests.get(BASE_URL, params=params).json()["hits"]

    recipeList = []

    for hit in response:
        recipeList.append(
            {
                "label": hit["recipe"]["label"],
                "image": hit["recipe"]["image"],
                "source": hit["recipe"]["source"],
                "url": hit["recipe"]["url"],
                # split the uri in two at the target ("_") to get id at the end
                "id": hit["recipe"]["uri"].split("_", 1)[1],
            }
        )

    return recipeList


def getRecipeDetails(id):
    newUrl = BASE_URL + "/" + id

    params = {
        "type": "public",
        "app_id": os.getenv("APP_ID"),
        "app_key": os.getenv("APP_KEY"),
        "id": id,
    }

    response = requests.get(newUrl, params=params).json()["recipe"]

    return response
