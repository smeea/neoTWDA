# neoTWDA

neoTWDA is a set of utilities to generate static TWDA (Tournament Winning Decks Archive) pages from separate deck files for [Vampire the Eternal Struggle (VTES)](https://www.vekn.net/what-is-v-tes) collectible card game.

## OLD (CURRENT) APPROACH
Existing [Official TWDA](http://www.vekn.fr/decks/twd.htm) is maintained (updated with new TWDs) by editing single html file which later served to the public.

### PROBLEMS WITH CURRENT APPROACH
* Target file is very big (hundreds of thousand lines) which is not very convenient to edit/navigate
* Editing require manual ordering by date
* Require manual Table of Content creation
* Relatively high bar of technical knowledge for contribution as each new deck addition requires at least to get html file from git and then careful edit it
* Prone to human errors like typos in html tags
* Prone to duplications (especially when several people commit addition of same deck)
* No simple way of changing styles (including not only visual, but also the structure of the document or deck representation)

## PROPOSED SOLUTION (AS IN neoTWDA)
* Each deck is stored as txt file of already established human-readable twd format (in `./decks` folder)
* Static files generated by running one script (`create_twd_html.py`) which uses deck files to create main part of the document + ToC, and adds html header/footer from static files (`twd_html_header.txt` and `twd_html_footer.txt`)

### DECK FILE FORMAT
File name must be event id.
First 6 lines order (Event...Player) is important, as their values used for ToC generation.
The rest may be in arbitrary order/style (i.e. script will reuse it as-is just like plain text - this allows custom style like author card comments in deck list).

### HOW TO ADD NEW DECK
* Put deck file `event-id.txt` file into `./decks`
* Re-run `python create_twd_html.py`

Similar works to edit/delete the deck.

### WHERE TO GET DECK FILE
* Deck files are standard txt files, so 'simplest' (not easiest!) way is to type it in your favorite text editor
* Deck-building software (Amaranth, VDB, etc) can to export deck to Text or TWD format, then edit header fields (Event, Date, etc) in text editor.
* To help verify deck file integrity it is possible to use (VDB Check TWD)[https://vdb.im/twd_check] page, but it's not mandatory and approach designed to avoid any format/vendor-locking and to be plain-text-driven.
* Final entry (with filled fields) could then be attached as file to TWD Report post in the forum or pasted as text, and is ready to be add to TWD with minimal overhead for TWDA maintainers.

## INSTALLATION

```
    git clone https://github.com/smeea/neotwda.git
    cd neotwda
    python -m venv venv
    source venv/bin/activate
    python -m pip install -r requirements.txt
```