import re
import json
from sys import argv, exit


if len(argv) <= 1:
    exit("USAGE: python check_deck.py FILE...")


with open("cardbase_crypt.json", "r") as crypt_file, open(
    "cardbase_lib.json", "r"
) as library_file:
    cardbase_crypt = {}
    cardbase_library = {}

    for card in list(json.load(crypt_file).values()):
        adv = True if card["Adv"] and card["Adv"][0] else False
        card_name = card["Name"] if not adv else f"{card['Name']} (ADV)"

        if card_name not in cardbase_crypt:
            cardbase_crypt[card_name] = {card["Group"]: card}
        else:
            cardbase_crypt[card_name][card["Group"]] = card

    for card in list(json.load(library_file).values()):
        cardbase_library[card["Name"]] = card


def check_banned(cards):
    for card in cards:
        if card["Banned"]:
            print(f" > BANNED CARD: {card['Name']}")


def check_min_max_size(cards, min, max):
    total = 0
    for card in cards:
        total += card["q"]

    if not min <= total <= max:
        print(f" > CARDS Q-TY: {total}")


def check_groups(cards):
    group_min = None
    group_max = None
    for card in cards:
        if card["Group"] == "ANY":
            continue

        group = int(card["Group"])
        if not group_min or group_min > group:
            group_min = group

        if not group_max or group_max < group:
            group_max = group

    if group_max - group_min > 1:
        print(f" > BAD GROUPS: G{group_min} + G{group_max}")


for file in argv[1:]:
    with open(file, "r") as deck_file:
        event_id = re.sub(r".*\/", "", file.rstrip(".txt"))
        lines = deck_file.readlines()
        event = lines[0].rstrip()
        location = lines[1].rstrip()
        date = lines[2].rstrip()
        format = lines[3].rstrip()
        players = lines[4].rstrip()
        winner = lines[5].rstrip()
        link = lines[6].rstrip()
        score = lines[8].rstrip().replace("-- ", "")
        deck_name = None
        description = []
        crypt = []
        library = []

        deck_name_offset = 10
        description_offset = deck_name_offset
        crypt_offset = 0
        library_offset = 0

        for i, line in enumerate(lines[deck_name_offset:]):
            if re.match(r"^Description:\n$", line):
                description_offset += i + 1
                break

            if m := re.match(r"^Deck Name: (.*)\n", line):
                deck_name = m.group(1)

        for i, line in enumerate(lines[description_offset:]):
            if re.match(r"^Crypt \(\d+ cards.*\)", line):
                crypt_offset = description_offset + i
                break

            description.append(line.rstrip())

        description = "\n".join(description).rstrip() if description else None

        for i, line in enumerate(lines[crypt_offset:]):
            if re.match(r"^Library \(\d+ cards.*\)", line):
                library_offset = crypt_offset + i
                break

            if m := re.match(r"^(\d+)x (.*)  \d+  .*:(\d|ANY).*$", line):
                q = int(m.group(1))
                card_name = m.group(2).strip()
                group = m.group(3)
                card = None
                card = cardbase_crypt[card_name][group]
                card["q"] = q
                crypt.append(card)

        for line in lines[library_offset:]:
            if m := re.match(r"^(\d+)x (.*?)( -- .*)?$", line):
                q = int(m.group(1))
                card_name = m.group(2).rstrip()
                card = cardbase_library[card_name]
                card["q"] = q
                library.append(card)

        print(f"CHECKED: {event_id}")
        check_groups(crypt)
        check_banned([*crypt, *library])
        check_min_max_size(crypt, 12, float("inf"))
        check_min_max_size(library, 60, 90)
        if not deck_name:
            print(" > NO DECK NAME")
        if not description:
            print(" > NO DESCRIPTION")
