# Analiza meteoritov in kraterjev

## Opis
Cilj tega projekta je analiza podatkov o meteoritih in kraterjih iz spletne strani [Mednarodnega društva za meteorite in planetarno znanost](https://www.lpi.usra.edu/meteor/metbull.php).
Vsebovani so programi, ki opravijo celoten postopek dela, vse od zajemanja podatkov in shranjevanja do analize v Jupyter Notebook.

Projekt je razdeljen na dva dela, pridobivanje podatkov in njihovo analizo.

Podatki so dobljeni s programi napisani v jeziku Python, z glavno datoteko `main.py`, ki ob zagonu opravi vse potrebne korake.
Sprva z danimi parametri požene prvotno iskanje števila strani in jih začne večnitno nalagati v `data/html`.
Potem iz vsake strani posebej izloči željene podatke in jih zapiše v oblikah csv in json v datoteki `data/output.csv` in `data/output.json`.
S tem se pridobivanje podatkov zaključi in program se ustavi.
Za natančnejša navodila uporabe se obrnite na [Navodila za uporabo]().

Analiza podatkov poteka datoteki `jupyter/analysis.ipynb` oziroma v `jupyter/analysis.ju.py`, če vam je ljubši JupyText.
Hkrati se v tej mapi nahajajo vse zunanje datoteke, ki jih uporabimo pri analizi podatkov razen `data/output.*` datotek.
Program je kot večina Jupyter Notebookov razdeljen na postopno poganjanje in analizo z obrazloženimi idejami implementacije.
Za več informacij lahko direktno pogledate datoteko [`jupyter/analysis.ipynb`](https://github.com/LesbianLemon/uvp-projektna/blob/726db6d28f177848de125ee515211734beb431c1/jupyter/analysis.ipynb).

## Navodila za uporabo

