# URL_checker

A projektben 3 python file van: **init.py**, **scan.py**, **modify.py**

Mind 3 script a `sites.json` fájlban megadott url-eket ellenőrzi, a `tags.json` fájlban megadott tageket keresve.

## init.py
Az `init.py` az első futáskor kell, megcsinálja a konfigokat, a db-t, majd lescanneli az első kört, hogy meglegyen a baseline.

## scan.py
A `scan.py` az a fájl amit cronnal meg kell hívni periodikusan, megnézi a konfigokat scannel majd ellenőriz, és ha hash error van akkor riaszt.

## modify.py
A `modify.py` a konfigmódosításkor lefuttatandó fájl, hozzáadja a dbhez azt ami kell, meg ha úgy akarjuk le baselineolja az újjonnan hozzáadott tageket

## Dependencies:
`pip install requests bs4 pytz`
