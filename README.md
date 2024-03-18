# About

Uses the Python Google Sheets API to implement backends for spreadsheets to track and update both personal spending and gaming data including achievement checklists and speedrun records over time

# Pokémon

[Spreadsheet](https://docs.google.com/spreadsheets/d/1NBl-bWTtXo95KjDnMBOIGQ-dd6_YvRBdQkRfUQMmSUU/edit#gid=109308367) keeps track of my Pokémon Home live dex as well as a database sheet with any relevant information needed for live dex.

Backend exists to have more custom logic around which forms I want to include and where as well as for validation when I make errors during manual entry for things like forgetting an OT, or hidden abilities not aligning, or duplicate family lines in the same ball. :grin:

[pokehome_main.py](https://github.com/leahfortier/spreadsheets/blob/main/main/pokehome/pokehome_main.py) outputs a fresh copy of the live dex with any new rules I may have added or changed while preserving all of the existing tracking information I have already included so I can just copy/paste the new sheet. :relaxed:

## Sources

- Abilities, evolutions, and gender ratio are from [Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Ability)
- Images are from [pokemondb](https://img.pokemondb.net/sprites/home/normal/1x/bulbasaur.png)
- Arceus sheet was taken from [this lovely post](https://www.reddit.com/r/pokemon/comments/ut2o7y/the_only_living_dex_spread_sheet_you_will_ever/)

# Celeste

[Spreadsheet](https://docs.google.com/spreadsheets/d/1Sj8JsgVGipsAsHq5V4AIrLnBf_vzHmUbSWN2WnZAiZI/) keeps track of our fastest times and minimum deaths for each chapter and category.  It also includes separate tabs for data from isolated races.

Backend exists to compare new runs against best runs to easily let you know when a new record is set.  It also exists to keep track of progress over time.

# Budget Tracking

[Spreadsheet](https://docs.google.com/spreadsheets/d/1OYUwwr_GJCRnByd-m_2BMh4HZGVSiyldyiXiiaGLXZc/#gid=1360394288) keeps track of all spending transactions history. Categories and notes can then easily be edited inside of the Google sheet.

Transaction history needs to be manually downloaded each time from [Mint](https://mint.intuit.com/transactions) (which will soon be deprecated RIP).

Backend exists to take new transaction history and translate into the format used in Google sheet, while preserving previously added notes and categories.  Occasionally recent transactions will change metadata within the first couple of days while being processed, and so these outdated rows will then be tagged with "MINTLESS" in spreadsheet which is clearly highlighted.  The corresponding transaction is generally nearby and information can be copied over before removing these rows.
