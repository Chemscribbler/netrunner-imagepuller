import requests
import fast_autocomplete
from fast_autocomplete.misc import read_single_keypress

NRDB_API = "https://netrunnerdb.com/api/2.0/public/"

request = requests.get(NRDB_API+"cards")

cards = {c['title']: {} for c in request.json()['data']}
# print(cards)
auto = fast_autocomplete.AutoComplete(words=cards)

# print(auto.search(word='Mut'))


word_list = []
while True:
    pressed = read_single_keypress()
    if pressed == '\x7f':
        if word_list:
            word_list.pop()
    elif pressed == '\x03':
        break
    else:
        word_list.append(pressed)
    
    joined = ''.join(word_list)
    print(chr(27) + "[2J")
    print(joined)
    results = {}
    for module_name, module in auto.items():
        results[module_name] = module.search(word=joined, max_cost=3, size=5)
    print(results)
    print('')