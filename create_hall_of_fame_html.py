import re
import calendar
import datetime
import glob
import math
from unidecode import unidecode
from num2words import num2words


def format_deck(id, entry):
    rows = [row.strip() for row in entry.splitlines()]

    month_text, day_text, year = rows[2].split(" ")
    month = f"{list(calendar.month_name).index(month_text):02}"
    day = f"{int(re.findall('[0-9]+', day_text)[0]):02}"

    deck = {
        "id": id,
        "event": rows[0],
        "location": rows[1],
        "year": year,
        "month_text": month_text,
        "winner": rows[5],
        "date": f"{year}-{month}-{day}",
    }
    return deck


def get_stars(decks):
    stars = 0
    for deck in decks:
        if re.search(
            r"(NAC|NC|EC|RESAC|SAC|ACC|Continental Championship) \d{4}( -- |$)",
            deck["event"],
        ):
            stars += 1
        if re.search(r"(NAC|NC|EC) \d{4} Day 2$", deck["event"]):
            stars += 1
    return stars


def generate_listed_players_hidden(badly_sorted_names):
    rows = []
    rows.append(f"<!-- {len(badly_sorted_names)} players listed")
    for name in sorted(badly_sorted_names):
        rows.append(name)

    all_players = "\n".join(rows) + " -->\n"
    return all_players


def generate_top_players_list(sorted_names, players_twd):
    rows_per_column = math.ceil(len(sorted_names) / 5)
    column = 1
    row = 1
    rows = []
    rows.append("<table>")
    for i in range(len(sorted_names)):
        if column == 1:
            rows.append("<tr>")
        name = sorted_names[(column - 1) * rows_per_column + row - 1]
        stars = get_stars(players_twd[name])  # TODO list of star-tournaments
        rows.append(
            f"<td>({len(players_twd[name])}) <a href=\"#{name.replace(' ', '')}\">{name}<sup>{'★'*stars}</sup></a></td>"
        )
        if column == 5:
            rows.append("</tr>")
            column = 1
            row += 1
        else:
            column += 1

    rows.append("</table>")
    top_players = "\n".join(rows) + "\n"
    return top_players


def generate_top_players_decks(sorted_names, players_twd):
    rows = []
    current_qty = 0
    for name in sorted_names:
        decks_qty = len(players_twd[name])
        if current_qty != decks_qty:
            rows.append(
                f"<h2>{num2words(decks_qty).capitalize()} tournament winning decks</h2>"
            )
            current_qty = decks_qty

        rows.append(f"<h3><a id={name.replace(' ', '')}>{name}</a></h3>")
        rows.append("<ul>")
        for deck in sorted(players_twd[name], key=lambda x: x["date"], reverse=True):
            rows.append(
                f"<li><a href=http://www.vekn.fr/decks/twd.htm#{deck['id']}>{deck['event']}: {deck['location']} {deck['month_text']} {deck['year']}</a><br/></li>"
            )
        rows.append("</ul>")
    toc = "\n".join(rows) + "\n"
    return toc


players_twd = {}
for file in glob.glob("decks" + "/*.txt"):
    with open(file, "r") as deck_file:
        id = file.removeprefix("decks/").removesuffix(".txt")
        deck_entry = deck_file.read()
        deck = format_deck(id, deck_entry)
        if deck["winner"] not in players_twd:
            players_twd[deck["winner"]] = [deck]
        else:
            players_twd[deck["winner"]].append(deck)

for name in [n for n in players_twd.keys()]:
    if len(players_twd[name]) < 5:
        del players_twd[name]

sorted_top_players = sorted(players_twd, key=lambda x: unidecode(x))
sorted_top_players.sort(key=lambda x: len(players_twd[x]), reverse=True)

with open("hall_of_fame.htm", "w") as hall_of_fame_file, open(
    "hall_of_fame_html_header.txt", "r"
) as html_header_file, open("hall_of_fame_html_footer.txt", "r") as html_footer_file:
    hall_of_fame_file.truncate(0)
    hall_of_fame_file.seek(0)

    html_header = html_header_file.read()
    html_footer = html_footer_file.read()
    html_listed_players_hidden = generate_listed_players_hidden(sorted_top_players)
    html_top_players_list = generate_top_players_list(sorted_top_players, players_twd)
    html_top_players_decks = generate_top_players_decks(sorted_top_players, players_twd)
    html_update_date = (
        f"<address>Last updated {datetime.datetime.now():%B %d, %Y}</address>"
    )

    hall_of_fame_file.write(html_header)
    hall_of_fame_file.write(html_listed_players_hidden)
    hall_of_fame_file.write(html_top_players_list)
    hall_of_fame_file.write("</blockquote></center>")
    hall_of_fame_file.write(html_top_players_decks)
    hall_of_fame_file.write(html_update_date)
    hall_of_fame_file.write(html_footer)
