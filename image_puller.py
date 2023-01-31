import requests
import os
import json
from fast_autocomplete import AutoComplete
from string import ascii_lowercase
import shutil
from pyrate_limiter import Duration, RequestRate, Limiter
from PIL import Image
from glob import glob
import sys

min_rate = RequestRate(100, Duration.MINUTE)

limiter = Limiter(min_rate)

EXCLUDED_WORDS = ["The", "the", "A", "a", "of", "Grid"]


@limiter.ratelimit("identity", delay=True)
def get_card_image(id):
    return requests.get(f"https://static.nrdbassets.com/v1/large/{id}.jpg").content


def update_cards():
    if not os.path.isdir("cardimages"):
        os.mkdir("cardimages")
    cards = requests.get("https://netrunnerdb.com/api/2.0/public/cards").json()["data"]
    for card in cards:
        if os.path.exists(f"cardimages/{card['code']}.jpg"):
            continue
        print(card["code"])
        with open(f"cardimages/{card['code']}.jpg", "wb") as f:
            f.write(get_card_image(card["code"]))


def card_dictionary(refresh: bool = False) -> dict:
    if os.path.exists("cards.json") and not refresh:
        print("Pre-load successful")
        with open("cards.json", "r") as f:
            cards = json.load(f)
        return cards

    cards = requests.get("https://netrunnerdb.com/api/2.0/public/cards").json()["data"]
    cards = {c["title"]: c["code"] for c in cards}

    with open("cards.json", "w") as f:
        f.write(json.dumps(cards))

    update_cards()
    return cards


def card_pull(cards: dict, project_folder: str, overwrite: bool = True):
    search_list = {key: {} for key in cards.keys()}
    synonyms = {key: str(key).split() for key in search_list.keys()}
    for key, syn in synonyms.items():
        for word in EXCLUDED_WORDS:
            if word in syn:
                syn.remove(word)
        synonyms[key] = syn
    # print(synonyms)
    auto = AutoComplete(search_list, synonyms=synonyms)
    while True:
        card_search = input("Search Card: ")
        results = auto.search(word=card_search, size=10)
        results = {str(num): r for num, r in enumerate(results)}
        print(results)
        check_result = input("Choose result (or type any letter to restart): ")
        if check_result.lower() in ascii_lowercase:
            continue
        # else:
        id = cards[results[check_result][0]]

        if overwrite:
            destination = "display.jpg"
        else:
            destination = os.path.abspath(project_folder + "/" + str(id) + ".jpg")
            print(destination)
        shutil.copyfile(f"cardimages/{id}.jpg", destination)


def convert_images(dir: str):
    g = glob(f"{dir}/*.png")
    for file in g:
        image = Image.open(file)
        rgb_image = image.convert("RGB")
        rgb_image.save(file.replace(".png", ".jpg"))


if __name__ == "__main__":
    cards = card_dictionary()
    card_pull(
        cards=cards,
        project_folder="C:/Users/jeffp/Videos/Streaming/Parhelion/CBI_Numbers",
        overwrite=False,
    )
    # convert_images("ParhelionImages")
