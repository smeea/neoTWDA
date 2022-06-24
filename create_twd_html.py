import re
import calendar
import glob
import textwrap


def format_deck(id, entry):
    STRING_LIMIT = 90

    rows = [row.strip() for row in entry.splitlines()]

    month_text, day_text, year = rows[2].split(" ")
    month = f"{list(calendar.month_name).index(month_text):02}"
    day = f"{int(re.findall('[0-9]+', day_text)[0]):02}"
    good_rows = []

    for row in rows:
        if row == "-- Unknown" or row == "Unknown":
            if good_rows[-1] == "":
                good_rows.pop(-1)
            continue

        if row == "" and good_rows[-1] == "":
            continue

        if len(row) > STRING_LIMIT:
            good_rows.append("\n".join(textwrap.wrap(row, STRING_LIMIT)))
        else:
            good_rows.append(row)

    entry = "\n".join(good_rows)

    deck = {
        "id": id,
        "event": rows[0],
        "location": rows[1],
        "year": year,
        "month_text": month_text,
        "winner": rows[5],
        "date": f"{year}-{month}-{day}",
        "entry": entry,
    }
    return deck


def generate_toc(decks):
    rows = []
    current_year = None
    for deck in decks:
        if current_year != deck["year"]:
            current_year = deck["year"]
            rows.append(f"\n<h3><a id=\"Year{deck['year']}\">{deck['year']}</a></h3>\n")

        rows.append(
            f"<a href=#{deck['id']}>{deck['winner']}'{'s' if deck['winner'][-1] != 's' else ''} {deck['event']}: {deck['location']} {deck['month_text']} {deck['year']}</a><br>"
        )

    toc = "\n".join(rows) + "\n</center>\n"
    return toc


decks = []
for file in glob.glob("decks" + "/*.txt"):
    with open(file, "r") as deck_file:
        id = file.removeprefix("decks/").removesuffix(".txt")
        deck_entry = deck_file.read()
        decks.append(format_deck(id, deck_entry))

sorted_decks = sorted(decks, key=lambda x: x["date"], reverse=True)


with open("twd.htm", "w") as twd_file, open(
    "twd_html_header.txt", "r"
) as html_header_file, open("twd_html_footer.txt", "r") as html_footer_file:
    twd_file.truncate(0)
    twd_file.seek(0)

    html_header = html_header_file.read()
    html_footer = html_footer_file.read()
    html_toc = generate_toc(sorted_decks)
    twd_file.write(html_header)
    twd_file.write(html_toc)

    for deck in sorted_decks:
        twd_file.write(f"<a id={deck['id']} href=#>Top</a>\n")
        twd_file.write("<hr><pre>\n")
        twd_file.write(deck["entry"])
        twd_file.write("\n</pre>\n")

    twd_file.write(html_footer)
