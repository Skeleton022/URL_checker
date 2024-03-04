# URL_checker
Egy webtartalom változást figyelő program, a defacement típusú támadások gyors észrevételére.

# Program részei
A projektben 3 python file van: `init.py`, `scan.py` és `modify.py`.

## init.py
Az init.py az első futáskor kell, megcsinálja a konfigokat, a db-t, majd lescanneli az első kört, hogy meglegyen a baseline.<br>
**FONTOS!** Az init megkérdezi, hogy akarunk-e baselineolni? Mielőtt igent nyomunk állítsuk be a konfig fájlokat úgy, ahogy azt használni akarjuk, különben nem fog rendesen működni!

## scan.py
A scan.py az a fájl amit cronnal meg kell hívni periodikusan, megnézi a konfigokat scannel majd ellenőriz, és ha hash error van akkor riaszt.

## modify.py
A modify.py a konfigmódosításkor lefuttatandó fájl, hozzáadja a dbhez azt ami kell, meg ha úgy akarjuk le baselineolja az újjonnan hozzáadott tageket

# Config files
2 konfig fájl van a projektben: `sites.json`, `tags.json` <br>
Mindkét konfig fájl json formátumban van és 1-1 tömböt tartalmaz. <br>
A `sites.json` a website-ok URL-jeit tartalmazza. <br>
A `tags.json` a site-okon keresendő tageket tartalmazza. <br>
**FONTOS!** Jelenleg a kód nem tud meta tagekre keresni, valamiért nem akar működni vele :(
Viszont képes `class`, és `id` alapján keresni, a használata hasonló mint a CSS során használandó szelektorok esetében.

### Class példa
Keresünk egy `<div class="cl_test">szöveg</div>`-et, akkor a config fájlba a következőt kell írnunk: `div.cl_test`

### ID példa
Keresünk egy `<div id="id_test">szöveg</div>`-et, akkor a config fájlba a következőt kell írnunk: `div#id_test`

### Példa:

`sites.json:`
```json
[
    "https://tryhackme.com/",
    "https://google.com",
    "https://thehackernews.com/"
]
```

`tags.json:`
```json
[
    "title",
    "div.navbar-item-text",
    "div#navbarSupportedContent",
    "di