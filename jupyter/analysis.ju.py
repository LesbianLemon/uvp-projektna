# %% [markdown]
"""
# Analiza meteoritov in kraterjev
"""
# %% [markdown]
"""
## Uvod
V tem dokumentu bomo izvedli analizo podatkov o meteoritih in kraterjih z uporabo podatkov baze Mednarodnega društva za meteorite in planetarno znanost (https://www.lpi.usra.edu/meteor/metbull.php).
Iskali bomo zanimive in uporabne povezave med podatki, ki so navedeni na prej omenjeni povezavi.
"""
# %% [markdown]
"""
## Priprava okolja
Najprej želimo pripraviti okolje, v katerem lahko podatke obdelujemo tako kot hočemo.
To naredimo tako, da uvozimo željene knjižnice, ki nam bodo olajšale delo in pripravimo podatke za obdelavo.
"""
# %% [markdown]
"""
#### Knjižnice
Nenujne knjižnice (samo za lepši izgled):
"""
# %%
# Prettier tables
from IPython.display import HTML
# %% [markdown]
"""
Knjjižnice za obdelavo podatkov:
"""
# %%
import pandas as pd
import geopandas as gpd

import matplotlib
# %% [markdown]
"""
#### Uvoz podatkov
Uvozimo podatke dobljene iz programa v pandas tabelo:
"""
# %%
df = pd.read_json("../data/output.json", precise_float=True)
df.index.names = ["id"]
# %% [markdown]
"""
Tabelo vseh podatkov uredimo po imenih po abecedi, kjer zanemarimo prednost velikih črk pred malimi.
"""
# %%
df = df.sort_values(by="Name", key=lambda col: col.str.lower())
# %% [markdown]
"""
Tabela vseh podatkov:
"""
# %%
df
# %% [markdown]
"""
#### Meteoriti
Ločimo uradne meteorite od ostalih, saj nas zanimajo neketere lastnosti, ki jih imajo le meteoriti.
Stolpec leto spremenimo v tip pd.Int64Dtype(), saj tabela ne vsebuje več kraterjev, ki imajo v stolpcu let podatke z decimalkami.
"""
# %%
met_df = df[df["Status"] == "Official"]
met_df = met_df.astype({ "Year": pd.Int64Dtype() })
# %% [markdown]
"""
Tabela vseh uradno priznanih meteoritov:
"""
# %%
met_df
# %% [markdown]
"""
#### Kraterji
Ločimo uradne kraterje od ostalih, saj nas zanimajo nekatere lastnosti, ki jih imajo le kraterji.
Prav tako preimenujemo stolpec let v starost, saj so podatki sestavljeni tako, da se starost kraterja vpiše pod leto.
"""
# %%
crt_df = df[df["Status"] == "Crater"]
crt_df = crt_df.rename(columns={ "Year": "Age" })
# %% [markdown]
"""
Tabela vseh uradno priznanih kraterjev:
"""
# %%
crt_df
# %% [markdown]
"""
## Deset najboljših

Pogledali si bomo deset najboljših vnosov po naslednjih kriterijih:
* najtežji
* najstarejši
* najpogostejši tip
* najpogostejše leto
"""
# %% [markdown]
"""
#### Deset najtežjih meteoritov
Iz tabele meteoritov izberemo stolpce, ki jih želimo prikazati in dobljene vrstice razvrstimo po masi.
Potem lahko preberemo deset vrhnjih vrstic, kar bo predstavljalo naših deset najtežjih meteoritov.
Na koncu podatke še preoblikujemo v bolj berljivo obliko.
"""
# %%
top10_mass = met_df[["Name", "Year", "Place", "Mass"]].sort_values("Mass", ascending=False).head(10)
top10_mass["Mass"] = (top10_mass["Mass"]/10**6).apply(lambda m: f"{m} ton")
# %% [markdown]
"""
Povprečna masa meteorita v gramih:
"""
# %%
round(float(met_df["Mass"][met_df["Mass"].notna()].mean()), 3)
# %% [markdown]
"""
Povprečen meteorit torej tehta približno 10 kg.

Tabela desetih najtežjih meteoritov, s krajem in letom padca ter maso:
"""
# %%
HTML(top10_mass.to_html(index=False))
# %% [markdown]
"""
Vidimo, da je zgornja polovica tabela tudi več kot dvakrat težja od spodnje, kar pomeni, da so meteoriti takih velikosti zelo redek pojav.
Le štirje presegajo mejo 50 ton.
Osupljiv je tudi najtežji meteorit, ki tehta približno toliko kot 12 afriških slonov ali 37 dvotonskih avtomobilov.

Vsi našteti meteoriti so torej 2000-krat do 7000-krat težji od povprečnega meteorita.
"""
# %% [markdown]
"""
#### Deset najstarejših meteoritov in kraterjev
Iz tabele meteoritov ali kraterjev izberemo stolpce, ki jih želimo prikazati in dobljene vrstice razvrstimo po letu oziroma starosti.
Potem lahko preberemo deset vrhnjih vrstic, kar bo predstavljalo naših deset najstarejših meteoritov ali kraterjev.
Na koncu podatke še preoblikujemo v bolj berljivo obliko.
"""
# %%
top10_met_age = met_df[["Name", "Place", "Year"]].sort_values("Year", ascending=True).head(10)
top10_met_age["Year"] = top10_met_age["Year"].apply(lambda y: f"{abs(y)} pr. n. št." if y < 0 else str(y))
# %%
top10_crt_age = crt_df[["Name", "Place", "Age"]].sort_values("Age", ascending=False).head(10)
top10_crt_age["Age"] = (top10_crt_age["Age"]/10**9).apply(lambda a: f"{round(a, 1)} milijard let")
# %% [markdown]
"""
Tabela desetih najstarejših meteoritov, s krajem in letom padca:
"""
# %%
HTML(top10_met_age.to_html(index=False))
# %% [markdown]
"""
Kot bi lahko predvidevali, nam tabela razkrije, da meteoritov iz tisoč ali več let nazaj ni veliko, saj takrat teh dogodkov niso bili sposobni beležiti tako kot danes.
Vselej pa najdemo kar tri meteorite iz časa pred našim štetjem in kar pet pred letom 1000.

Tabela desetih najstarejših kraterjev, s krajem in starostjo:
"""
# %%
HTML(top10_crt_age.to_html(index=False))
# %% [markdown]
"""
V tabeli očitno odstopa "najstarejši" krater med vsemi, saj je starejši od vesolja samega.
Potrdimo lahko, da je to napaka v podatkovni bazi in ne v naših programih, saj je starost navedena kot 34759 Ma (Ma = mega-annum) ali 34759 milijonov let.

Sicer pa lahko vidimo, da imamo kraterje, ki dosegajo starosti do polovice starosti Zemlje.
"""
# %% [markdown]
"""
#### Deset najpogostejših tipov
V tabeli meteoritov dobimo tabelo pojavitev vseh tipov meteorita, ki je že razvrščena po velikosti.
Iz tega izberemo vrhnjih deset vrstic, kar bo predstavljalo naših deset najpogostejših tipov meteorita.
Tabelo še preoblikujemo tako, da bo prikaz lepši.
"""
# %%
top10_types = met_df["Type"].value_counts().head(10)
top10_types = top10_types.to_frame(name="Occurances").reset_index()
# %% [markdown]
"""
Legenda tipov meteoritov, ki so našteti v tabeli (več na: https://en.wikipedia.org/wiki/Chondrite):
* LL\<št.\> - skupina "low-iron, low-metal"
* L\<št.\> - skupina "low-iron"
* H\<št.\> - skupina "high-iron"
* \<št.\> - stopnja homogenosti meteorita

Tabela desetih najpogostejših tipov meteoritov:
"""
# %%
HTML(top10_types.to_html(index=False))
# %% [markdown]
"""
#### Deset najpogostejših let padca
V tabeli meteoritov dobimo tabelo pojavitev vseh let, ki je že razvrščena po velikosti.
Iz tega izberemo vrhnjih deset vrstic, kar bo predstavljalo naših deset najpogostejših let padca.
Tabelo še preoblikujemo tako, da bo prikaz lepši.
"""
# %%
top10_years = met_df["Year"].value_counts().head(10)
top10_years = top10_years.to_frame(name="Amount").reset_index()
# %% [markdown]
"""
Tabela desetih let z največ meteoriti:
"""
# %%
HTML(top10_years.to_html(index=False))
# %% [markdown]
"""
Vidimo, da število meteoritov narašča skoraj naključno z naključnimi leti.
Predvidevali bi lahko, da bodo imela poznejša leta več meteoritov zaradi boljših merskih sposobnosti, vendar so leta na seznamu povsem naključna in nobeno od njih ni v zadnjem desetletju.
"""
# %% [markdown]
"""
## Grafični prikazi
Pogledali bomo povezave med različnimi spremenljivkami z uporabo grafov.
"""
# %% [markdown]
"""
#### Meteoriti in kraterji skozi čas
Poskusimo narisati grafe števila meteoritov skozi zgodovino.
Zaradi ponavljanja prehodno naredimo funkcijo, kateri podamo željene pogoje za risanje grafa.
"""
# %%
def get_met_counts_min_year(min_year, decades=False):
    col_min_year = met_df[met_df["Year"] >= min_year]["Year"]

    if decades:
        col_min_year = (col_min_year//10)*10

    return col_min_year.value_counts().sort_index()
# %% [markdown]
"""
Graf števila padlih meteoritov v desetletju od leta 1700 dalje:
"""
# %%
get_met_counts_min_year(1800, decades=True).plot.bar(xlabel="Decade", ylabel="Amount")
# %% [markdown]
"""
Očitno je, da so skoraj vsi meteoriti v podatkovni bazi iz zadnjih 50 let, zato moramo časovno obdobje skrajšati, da dobimo boljšo predstavo.

Graf števila padlih meteoritov v desetletju od leta 1950 dalje:
"""
# %%
get_met_counts_min_year(1950, decades=True).plot.bar(xlabel="Decade", ylabel="Amount")
# %% [markdown]
"""
Graf števila padlih meteoritov v letu od leta 1950 dalje:
"""
# %%
get_met_counts_min_year(1950, decades=False).plot(ylabel="Amount")
# %% [markdown]
"""
Podatki delujejo zelo naključni, z zelo velikimi skoki in padci iz leta v leto.
To bi lahko bila posledica, da ob prodoru meteorja v atmosfero ta ponavadi razpade na več manjših.
Torej bi lahko ob padcu velikega meteorita, ki se razbije na tisoče delov graf močno poskočil.

Ko pogledamo graf po desetletjih, zgleda ta že manj naključen, vendar še vedno vidimo velike razlike med desetletji.

Če želimo obravnavati še kraterje, je potrebno prvo izločiti "najstarejši" krater, za keterega smo v prejšnjem poglavju odkrili, da je napaka v podatkovni bazi.
Namesto, da ga odstranimo iz tabele, lahko najdemo raje naslednji najstarejši krater in tvorimo intervale po 200 milijonov let do njegove starosti.
Potem vnosom v tabeli pripišemo interval in za konec intervale še preimenujemo, da se pojavijo lepše na grafu.
"""
# %%
real_max = crt_df.drop(crt_df["Age"].idxmax())["Age"].max()
intervals = pd.interval_range(start=0, end=real_max, freq=2*10**8, closed="left")

col_interval = pd.cut(crt_df["Age"], bins=intervals, include_lowest=True).dropna()
col_interval_trans = col_interval.apply(lambda i: f"{int(i.left/10**6)} mil.")
# %% [markdown]
"""
Graf števila kraterjev glede na starost:
"""
# %%
col_interval_trans.value_counts().sort_index().plot.bar()
# %% [markdown]
"""
Očitno je, da se skoraj vsi kraterji nahajajo v starostnem razredu do 600 milijonov let.
To je logično, saj starejše kot so naravne značilnosti, večje so možnosti, da so te do sedaj že izginile.
"""
# %% [markdown]
"""
#### Povezave z maso meteorita
Pogledali si bomo še različne povezave med maso meteorita in različnimi faktorji, ki bi nanjo lahko vplivali.
Sprva si lahko pogledamo graf povprečne mase meteorita skozi leta, da vidimo, če najdemo velika odstopanja od povprečja.

Dobimo ga tako, da sprva tabelo omejimo na časovno obdobje, kjer imamo več vnosov (npr. po 1900) in na podatke, ki nas zanimajo, tj. leto in masa.
Potem lahko združimo vrstice glede na leto padca in izračunamo povprečno vrednost mase.
Te podatke potem še pretvorimo v enote, ki nam najbolje pokažejo vrednosti, v tem primeru kilogrami.
"""
# %%
avg_mass_year = met_df[met_df["Year"] > 1900][["Year", "Mass"]].groupby("Year").mean()/10**3
# %% [markdown]
"""
Graf povprečne mase meteorita skozi leta:
"""
# %%
avg_mass_year.plot(legend=False, ylabel="Mean mass [kg]")
# %% [markdown]
"""
Opazimo gromozanske skoke v povprečni masi meteorita.
Te podatke lahko primerjamo s prej dobljeno tabelo najtežjih meteoritov.
Opazimo lahko močno korelacijo, saj so leta 1911, 1920 in 1947 hkrati leta z vrhunci povprečne mase in leta, ko je padel eden od desetih najtežjih meteoritov.
Predvsem odstopa leto 1920, ko je padel drugi največji meteorit in hkrati iz tega leta ni zelo veliko manjših meteoritov, ki bi povprečje znižali.

Naslednje si lahko pogledamo povezavo med maso in tipom meteorita, da vidimo katere vrste meteorita so najtežje.

To storimo podobno kot prej, kjer tabelo meteoritov omejimo na tip in maso in združimo vrstice glede na tip meteorita.
Iz tega razberemo povprečne vrednosti mas in jih pretvorimo v kilograme.
Pri risanju pa izberemo samo 20 največjih povprečnih mas, saj imamo tipov meteoritov preveč za en graf.
"""
# %%
avg_mass_type = met_df[["Type", "Mass"]].groupby("Type").mean()/10**3
# %% [markdown]
"""
Graf dvajsetih tipov z največjo povprečno maso na tip:
"""
# %%
avg_mass_type.sort_values("Mass", ascending=False).head(20).plot.bar(legend=False, ylabel="Mean mass [kg]")
# %% [markdown]
"""
Tukaj mogočno prevlada en tip meteorita "Iron, IIIE-an", kateremu z mnogo manjšima povprečnima masama sledita "Iron, IVB" in "Iron, IAB Complex".
Ostali tipi meteoritov pa v primerjavi s temi skoraj ne obstajajo.

Pogledamo lahko meteorite s temi tremi tipi in odkrijemo zakaj tako močno odstopajo.
Napišemo pomožno funkcijo, ki vrne tabelo vseh meteoritov nekega tipa, urejeno po masi.
"""
# %%
def get_table_of_type(met_type):
    return met_df[met_df["Type"] == met_type][["Name", "Type", "Mass"]].sort_values("Mass", ascending=False)
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IIIE-an" urejena po masi:
"""
# %%
HTML(get_table_of_type("Iron, IIIE-an").to_html(index=False))
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IVB" urejena po masi:
"""
# %%
HTML(get_table_of_type("Iron, IVB").to_html(index=False))
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IAB Complex" urejena po masi:
"""
# %%
HTML(get_table_of_type("Iron, IAB Complex").to_html(index=False))
# %% [markdown]
"""
Takoj lahko opazimo zakaj je prišlo do takšnih odstopanj.
To so tipi najtežjih meteoritov, ki so zelo nepogosti.
To pomeni, da bo povprečno vrednost bila odvisna večinoma samo od najtežjega meteorita zaradi gromozanske razlike v teži in majhne količine normalno velikih meteoritov.
"""
