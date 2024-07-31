# Analiza meteoritov in kraterjev

## Opis
Cilj tega projekta je analiza podatkov o meteoritih in kraterjih iz spletne strani [Mednarodnega društva za meteorite in planetarno znanost](https://www.lpi.usra.edu/meteor/metbull.php).
Vsebovani so programi, ki opravijo celoten postopek dela, vse od zajemanja podatkov in shranjevanja do analize v Jupyter Notebook.

Projekt je razdeljen na dva dela, pridobivanje podatkov in njihovo analizo.

Podatki so dobljeni s programi napisani v jeziku Python, z glavno datoteko `main.py`, ki ob zagonu opravi vse potrebne korake.
Sprva z danimi parametri požene prvotno iskanje števila strani in jih začne večnitno nalagati v `data/html/`.
Potem iz vsake strani posebej izloči željene podatke in jih zapiše v oblikah csv in json v datoteki `data/output.csv` in `data/output.json`.
S tem se pridobivanje podatkov zaključi in program se ustavi.
Za natančnejša navodila uporabe se obrnite na [Navodila za uporabo](https://github.com/LesbianLemon/uvp-projektna/blob/726db6d28f177848de125ee515211734beb431c1/jupyter/analysis.ipynb).

Analiza podatkov poteka datoteki `jupyter/analysis.ipynb` oziroma v `jupyter/analysis.ju.py`, če vam je ljubši JupyText.
Hkrati se v tej mapi nahajajo vse zunanje datoteke, ki jih uporabimo pri analizi podatkov razen `data/output.*` datotek.
Program je kot večina Jupyter Notebookov razdeljen na postopno poganjanje in analizo z obrazloženimi idejami implementacije.
Za več informacij lahko direktno pogledate datoteko [`jupyter/analysis.ipynb`](https://github.com/LesbianLemon/uvp-projektna/blob/726db6d28f177848de125ee515211734beb431c1/jupyter/analysis.ipynb).

## Navodila za uporabo
Prvo naložite repozitorij na željeno lokacijo.
Zdaj lahko nadaljujete s koraki namestitve ostalih potrebnih knjižnic in programov.

Prvo preverite verzijo naloženega programa Python:
```console
python -V
```
Če vam javi napako poskusite še:
```console
python3 -V
```
Če ne dela niti to, morate najprej naložiti Python.

Željen izpis:
```console
python -V
Python 3.12.4
```
**NUJNO:** Če je dobljena verzija nižja od 3.12, si najprej nadgradite Python.

Zdaj lahko naložimo potrebne knjižnice:
```console
pip install requests beautifulsoup4
```
oziroma
```console
pip3 install requests beautifulsoup4
```
S tem lahko poganjamo kodo za pridobivanje podatkov.
Če pa želite poganjati tudi Jupyter Notebook in si ga ne samo ogledovati, si naložite še naslednje knjižnice:
```console
pip install jupyter matplotlib pandas geopandas
```
oziroma
```console
pip3 install jupyter matplotlib pandas geopandas
```
Za drugačne načine poganjanja Jupyter Notebooka (npr. JupyterLab), si potrebne knjižnice naložite sami.

S tem imamo pripravljeno okolje za pogon `main.py`, ki ga poženemo z na naslednje načine iz mape repozitorija.
Če želimo navaden zagon:
```console
python main.py
```
oziroma
```console
python3 main.py
```

Če želimo spreminjati nastavitve programa lahko podamo argumente pri klicu `main.py`.
Več nam o tem pove naslednja komanda:
```console
python main.py -h
```
oziroma
```console
python3 main.py -h
```
Dobimo nekaj takega:
```console
python main.py -h
usage: main.py [-h] [--thread-count THREADS] [--no-force] [--clear] [--search SEA]
               [--search-for {names,text,places,classes,years}] [--valids]
               [--search-type {contains,starts,exact,sounds}] [--listings LREC]
               [--map {gg,ge,ww,ll,dm,none}]

options:
  -h, --help            show this help message and exit
  --thread-count THREADS, -c THREADS
                        number of threads used for saving the HTML files
  --no-force            will not download HTML files again if they already exist
  --clear               will clear the entire `data/html/` directory before downloading
  --search SEA, -s SEA  the string to use for search the database
  --search-for {names,text,places,classes,years}, -f {names,text,places,classes,years}
                        what to search for with the search string
  --valids, -v          restrict search to only valid meteorites
  --search-type {contains,starts,exact,sounds}, -t {contains,starts,exact,sounds}
                        what type of search to perform
  --listings LREC, -l LREC
                        number of listings per page
  --map {gg,ge,ww,ll,dm,none}, -m {gg,ge,ww,ll,dm,none}
                        type of location data to return
```

Navaden zagon kot smo ga videli zgoraj je enakovreden:
```console
python main.py -c 8 -s * -f names -t contains -l 5000 -m ll
```
oziroma
```console
python3 main.py -c 8 -s * -f names -t contains -l 5000 -m ll
```
Za več informacij kako delajo te nastavitve si poglejte spletno stran [Mednarodnega društva za meteorite in planetarno znanost](https://www.lpi.usra.edu/meteor/metbull.php).

Ko se program zaključi, se bosta v `data/` shranili datoteki `data/output.json` in `data/output.csv`, ki vsebujeta vse zapise meteoritov, ki smo jih poiskali.
