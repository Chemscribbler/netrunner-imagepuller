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
def get_card_image(card: dict):
    return requests.get(card["attributes"]["images"]["nrdb_classic"]["large"]).content


def update_cards(
    printings_url: str = "https://api-preview.netrunnerdb.com/api/v3/public/printings",
):
    if not os.path.isdir("cardimages"):
        os.mkdir("cardimages")
    response = requests.get(printings_url)
    if response.status_code != 200:
        print("Error: ", response.status_code)
        sys.exit(1)
    page = response.json()
    cards = page["data"]
    for card in cards:
        if os.path.exists(f"cardimages/{card['id']}.jpg"):
            continue
        print(card["id"])
        with open(f"cardimages/{card['id']}.jpg", "wb") as f:
            f.write(get_card_image(card))
    if "next" in page["links"].keys():
        update_cards(page["links"]["next"])


def card_dictionary(refresh: bool = False) -> dict:
    if os.path.exists("cards.json") and not refresh:
        print("Pre-load successful")
        with open("cards.json", "r") as f:
            cards = json.load(f)
        return cards

    cards = requests.get("https://netrunnerdb.com/api/2.0/public/cards").json()["data"]
    cards = {c["stripped_title"]: c["code"] for c in cards}

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
    overwrite_mode = input("Enable Overwrite Mode (T/F)?")
    overwrite_mode = overwrite_mode.lower() == "t"
    card_pull(
        cards=cards,
        project_folder="C:/Users/jeffp/Videos/Streaming/AutomataInitiative/SpoilerVid",
        overwrite=overwrite_mode,
    )
    # convert_images("ParhelionImages")
