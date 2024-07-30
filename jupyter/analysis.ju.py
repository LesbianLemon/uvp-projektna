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

import matplotlib as plt
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
Hkrati pa hočemo stolpec "(Lat,Long)" razdeliti na dva nova stolpca "Latitude" in "Longitude" za lažjo uporabo.
Potem lahko originalnega izbrišemo in stolpce preuredimo kot hočemo.
"""
# %%
df = df.sort_values(by="Name", key=lambda c: c.str.lower())
clean_ll_df = df["(Lat,Long)"].dropna()
df[["Latitude", "Longitude"]] = pd.DataFrame(clean_ll_df.to_list(), index=clean_ll_df.index)
col_order = ["Name", "Abbrev", "Status", "Year", "Type", "Mass", "Place",
             "Latitude", "Longitude", "Fall", "Antarctic", "MetBull", "Notes"]
df = df[col_order]
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
pd.set_option("display.max_rows", 20)
crt_df
# %% [markdown]
"""
#### Lepši izpis
Napišemo pomožno funkcijo, ki nam polepša izpis nekaterih tabel.
"""
# %%
def pretty_table(table_df):
    return HTML(table_df.to_html(index=False))
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
pretty_table(top10_mass)
# %% [markdown]
"""
Vidimo, da je zgornja polovica tabele tudi več kot dvakrat težja od spodnje, kar pomeni, da so meteoriti takih velikosti zelo redek pojav.
Le štirje presegajo mejo 50 ton.
Osupljiv je tudi najtežji meteorit, ki tehta približno toliko kot 12 afriških slonov ali 37 dvotonskih avtomobilov.

Našteti meteoriti so torej 2000-krat do 7000-krat težji od povprečnega meteorita.
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
pretty_table(top10_met_age)
# %% [markdown]
"""
Kot bi lahko predvidevali, nam tabela razkrije, da meteoritov iz tisoč ali več let nazaj ni veliko, saj takrat teh dogodkov niso bili sposobni beležiti tako dobro kot danes.
Vselej pa najdemo kar tri meteorite iz časa pred našim štetjem in pet pred letom 1000.

Tabela desetih najstarejših kraterjev, s krajem in starostjo:
"""
# %%
pretty_table(top10_crt_age)
# %% [markdown]
"""
V tabeli očitno odstopa "najstarejši" krater med vsemi, saj je starejši od vesolja samega (po mojem znanju je to nemogoče).
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
pretty_table(top10_types)
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
pretty_table(top10_years)
# %% [markdown]
"""
Vidimo, da so leta z največ meteoriti naključna.
Predvidevali bi lahko, da bodo imela poznejša leta več meteoritov zaradi boljših merskih sposobnosti, vendar so leta na seznamu nepovezana in nobeno od njih ni v zadnjem desetletju.
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
get_met_counts_min_year(1800, decades=True).plot.bar(xlabel="Decade", ylabel="Amount");
# %% [markdown]
"""
Očitno je, da so skoraj vsi meteoriti v podatkovni bazi iz zadnjih 50 let, zato moramo časovno obdobje skrajšati, da dobimo boljšo predstavo.

Graf števila padlih meteoritov v desetletju od leta 1950 dalje:
"""
# %%
get_met_counts_min_year(1950, decades=True).plot.bar(xlabel="Decade", ylabel="Amount");
# %% [markdown]
"""
Graf števila padlih meteoritov v letu od leta 1950 dalje:
"""
# %%
get_met_counts_min_year(1950, decades=False).plot(ylabel="Amount");
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
col_interval_trans.value_counts().sort_index().plot.bar();
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
Te podatke potem še pretvorimo v enote, ki nam najbolje pokažejo vrednosti, v tem primeru kilograme.
"""
# %%
mean_mass_year = met_df[met_df["Year"] > 1900][["Year", "Mass"]].groupby("Year").mean()/10**3
# %% [markdown]
"""
Graf povprečne mase meteorita skozi leta:
"""
# %%
mean_mass_year.plot(legend=False, ylabel="Mean mass [kg]");
# %% [markdown]
"""
Opazimo gromozanske skoke v povprečni masi meteorita.
Te podatke lahko primerjamo s prej dobljeno tabelo najtežjih meteoritov.

Tabela desetih najtežjih meteoritov za primerjavo:
"""
# %%
pretty_table(top10_mass)
# %% [markdown]
"""
Opazimo lahko močno korelacijo, saj so leta 1911, 1920 in 1947 hkrati leta z vrhunci povprečne mase in leta, ko je padel eden od desetih najtežjih meteoritov.
Predvsem odstopa leto 1920, zato si podrobneje poglejmo meteorite, ki so padli takrat.

Tabelo omejimo na leto 1920 in na stolpce, ki nas zanimajo.
Potem jo razvrstimo po masi in pretvorimo ter dodamo enote za lepši izgled.
"""
# %%
met_1920_df = met_df[met_df["Year"] == 1920][["Name", "Year", "Mass"]].sort_values("Mass", ascending=False)
met_1920_df["Mass"] = (met_1920_df["Mass"]/10**3).apply(lambda m: f"{round(m, 1)} kg")
# %% [markdown]
"""
Tabela vseh meteoritov leta 1920, razvrščena po masi:
"""
# %%
pretty_table(met_1920_df)
# %% [markdown]
"""
Vidimo, da je to leto, ko je padel drugi najtežji zabeležen meteorit in hkrati zelo malo drugih, lažjih meteoritov.
Posledica tega je, da najtežji meteorit zelo močno vpliva na povprečno maso.
To obrazloži vrh, ki smo ga videli na grafu in je verjetno razlog za vse podobne vrhove.

Naslednje si lahko pogledamo povezavo med maso in tipom meteorita, da vidimo katere vrste meteorita so najtežje.

To storimo podobno kot prej, kjer tabelo meteoritov omejimo na tip in maso in združimo vrstice glede na tip meteorita.
Iz tega razberemo povprečne vrednosti mas in jih pretvorimo v kilograme.
Pri risanju pa izberemo samo 20 največjih povprečnih mas, saj imamo tipov meteoritov preveč za en graf.
"""
# %%
mean_mass_type = met_df[["Type", "Mass"]].groupby("Type").mean()/10**3
# %% [markdown]
"""
Graf dvajsetih tipov z največjo povprečno maso na tip:
"""
# %%
mean_mass_type.sort_values("Mass", ascending=False).head(20).plot.bar(legend=False, ylabel="Mean mass [kg]");
# %% [markdown]
"""
Tukaj mogočno prevlada en tip meteorita "Iron, IIIE-an", kateremu z mnogo manjšima povprečnima masama sledita "Iron, IVB" in "Iron, IAB Complex".
Ostali tipi meteoritov pa v primerjavi s temi skoraj ne obstajajo.

Pogledamo lahko meteorite s temi tremi tipi in odkrijemo zakaj tako močno odstopajo.
Napišemo pomožno funkcijo, ki vrne tabelo vseh meteoritov nekega tipa, urejeno po masi in zapisano v kilogramih.
"""
# %%
def get_table_of_type(met_type):
    met_type_df = met_df[met_df["Type"] == met_type][["Name", "Type", "Mass"]].sort_values("Mass", ascending=False)
    met_type_df["Mass"] = (met_type_df["Mass"]/10**3).apply(lambda m: f"{round(m, 2)} kg")
    return met_type_df
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IIIE-an" urejena po masi:
"""
# %%
pretty_table(get_table_of_type("Iron, IIIE-an"))
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IVB" urejena po masi:
"""
# %%
pretty_table(get_table_of_type("Iron, IVB"))
# %% [markdown]
"""
Tabela vseh meteoritov tipa "Iron, IAB Complex" urejena po masi:
"""
# %%
pretty_table(get_table_of_type("Iron, IAB Complex"))
# %% [markdown]
"""
Takoj lahko opazimo zakaj je prišlo do takšnih odstopanj.
To so tipi najtežjih meteoritov, ki so zelo nepogosti.
To pomeni, da bo povprečna masa bila odvisna večinoma samo od najtežjega meteorita zaradi gromozanske razlike v teži in majhne količine normalno velikih meteoritov.
"""
# %% [markdown]
"""
## Zemljevidi
Uporabimo lahko tudi podatke o lokacijah, ki jih imamo shranjene v tabelah.
Pred tem moramo pa pripraviti okolje za risanje zemljevidov.

Uvozimo zemljevide iz lokalno shranjenih datotek z uporabo geopandas.
Poskrbeti moramo tudi, da se v novi tabeli meteoritov ne pojavijo vnosi, ki niso na Zemlji, saj ne želimo risati meteoritov na drugih planetih.
"""
# %%
world_gdf = gpd.read_file("world.zip")
world_accurate_gdf = gpd.read_file("world-accurate.zip")
earth_met_df = met_df[(met_df["Place"] != "Mars") & (met_df["Place"] != "Moon")]
# %% [markdown]
"""
Na koncu to pretvorimo v geopandas tabelo z uporabo "Latitude" in "Longitude" stolpcev.
"""
# %%
met_gdf = gpd.GeoDataFrame(earth_met_df, geometry=gpd.points_from_xy(earth_met_df["Longitude"], earth_met_df["Latitude"]), crs="EPSG:4326")
# %%
crt_gdf = gpd.GeoDataFrame(crt_df, geometry=gpd.points_from_xy(crt_df["Longitude"], crt_df["Latitude"]), crs="EPSG:4326")
# %% [markdown]
"""
Za začetek naredimo pomožne funkcije, ki nam bodo olajšale delo pri risanju zemljevidov.
Eno funkcijo, ki doda opis osi in drugo, ki nariše zemljevid sveta, na katerega bomo potem vrisali podatke.
"""
# %%
def set_labels(ax):
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
# %%
def get_world_map():
    ax = world_gdf.plot(color="white", edgecolor="black")
    set_labels(ax)
    return ax
# %% [markdown]
"""
#### Vsi meteoriti in kraterji
Prvo si bomo pogledali kako izgledajo naši padci meteoritov in kraterji na svetovnem zemljevidu.

Zemljevid vseh meteoritov:
"""
# %%
met_gdf.plot(ax=get_world_map(), markersize=0.5);
# %% [markdown]
"""
Iz števila pikic bi z lahkoto sklepali na območja z največjim šetvilom padcev meteoritov, vendar kot bomo videli v prihodnje pri analizi glede na državo ta zemljevid ne pove celotne zgodbe.
Veliko meteoritov na enem območju se z lahkoto skrije pred našimi očmi.

Zemljevid vseh kraterjev:
"""
# %%
crt_gdf.plot(ax=get_world_map(), markersize=3);
# %% [markdown]
"""
Pri obeh zemljevidih lahko opazimo, da je največja gostota ravno na najbolje poseljenih območjih sveta.
Severna območja kot so Kanada, Grenlandija, Sibirija in težko dostopna območja kot so džungle in puščave pa so bolj prazna.
"""
# %% [markdown]
"""
#### Glede na državo
Poskusimo lahko podatke narisati tudi glede na državo padca.
Za to bomo potrebovali vedeti kam je meteorit padel oziroma kje se krater nahaja.

Zaradi nekonstantnosti stolpca "Place", iz tega ne moremo dobiti države padca.
Lahko pa točke padcev presekamo z natančnim zemljevidom sveta, da ugotovimo v katero državo je padel.
S tem bomo dobili novo tabelo samo kraterjev in meteoritov, ki so pristali na kopnem v državi, skupaj z državo kjer so pristali.
Na žalost pa so te operacije za velike količine podatkov zelo počasne, vendar se za točnost podatkov splača potrpeti.
"""
# %%
met_country_gdf = gpd.overlay(met_gdf, world_accurate_gdf, how="intersection")
met_country_gdf = met_country_gdf.rename(columns={ "ADMIN": "Country" })
# %%
crt_country_gdf = gpd.overlay(crt_gdf, world_accurate_gdf, how="intersection")
crt_country_gdf = crt_country_gdf.rename(columns={ "ADMIN": "Country" })
# %% [markdown]
"""
Sedaj lahko naredimo novo tabelo z istimi podatki kot tabela vseh držav, le z dodanima stolpcema števila meteoritov in kraterjev.
"""
# %%
world_extra_gdf = world_gdf.set_index("admin")
world_extra_gdf["Meteorites"] = met_country_gdf["Country"].value_counts()
world_extra_gdf["Craters"] = crt_country_gdf["Country"].value_counts()
world_extra_gdf = world_extra_gdf.reset_index(names="Country")
# %% [markdown]
"""
Napišemo pomožno funkcijo, da nam ni potrebno vsakič dajati istih parametrov:
"""
# %%
def draw_map(gdf, column):
    set_labels(gdf.plot(
        column=column,
        legend=True,
        legend_kwds={ "orientation": "horizontal" },
        missing_kwds={
            "color": "lightgrey",
        }
    ))
# %% [markdown]
"""
Zemljevid števila meteoritov na državo:
"""
# %%
draw_map(world_extra_gdf, "Meteorites")
# %% [markdown]
"""
Vidimo, da je v nasprotju z našimi pričakovanji, ki jih je postavil zemljevid vseh meteoritov na svetovnem zemljevidu, skoraj cel svet zanemarljiv v primerjavi z Antarktiko.
Tam je bilo najdenih več kot 30000 meteoritov, kar je zelo blizu številu vseh meteoritov, ki smo jih dobili z analizo države padca.

Število vseh meteoritov, za katere smo določili državo padca:
"""
# %%
len(met_country_gdf)
# %% [markdown]
"""
Izven Antarktike je po celem svetu le polovica toliko meteoritov kot na Antarktiki sami.
Zato lahko poskusimo narisati še svet brez Antarktike.

Zemljevid števila meteoritov na državo brez Antarktike:
"""
# %%
draw_map(world_extra_gdf[world_extra_gdf["Country"] != "Antarctica"], "Meteorites")
# %% [markdown]
"""
Tudi brez Antarktike prevladuje zelo majhno število držav.
Poglejmo si katere države to so.

Izberemo stolpce, ki jih želimo prikazati in jih razvrstimo po številu meteoritov.
Vzamemo vrhnjih deset držav in na koncu še zapišemo števila meteoritov kot cela števila.
"""
# %%
top10_countries_met = world_extra_gdf[["Country", "Meteorites"]].sort_values("Meteorites", ascending=False).head(10)
top10_countries_met = top10_countries_met.astype({ "Meteorites": int })
# %% [markdown]
"""
Tabela desetih držav z največ meteoriti:
"""
# %%
pretty_table(top10_countries_met)
# %% [markdown]
"""
Tabela in zemljevid nam potrdita, da je največ meteoritov zapisanih kot padlih na Antarktiki.
Sledijo Oman, Čile, Združene države Amerike in Libija.
Vse ostale države pa imajo pod 1000 meteoritov.

Poglejmo si še kako izgleda zemljevid kraterjev.

Zemljevid števila kraterjev na državo:
"""
# %%
draw_map(world_extra_gdf, "Craters")
# %% [markdown]
"""
Tukaj je bolj očitno katere države prevladujejo, vendar lahko vseeno pogledamo tabelo desetih držav z največ kraterji.

Izberemo stolpce, ki jih želimo prikazati in jih razvrstimo po številu kraterjev.
Vzamemo vrhnjih deset držav in na koncu še zapišemo števila kraterjev kot cela števila.
"""
# %%
top10_countries_crt = world_extra_gdf[["Country", "Craters"]].sort_values("Craters", ascending=False).head(10)
top10_countries_crt = top10_countries_crt.astype({ "Craters": int })
# %% [markdown]
"""
Tabela desetih držav z največ meteoriti:
"""
# %%
pretty_table(top10_countries_crt)
# %% [markdown]
"""
Kot je razvidno iz zemljevida so države z največ kraterji Kanada, Združene države Amerike, Avstralija in Rusija.
Mogoče presenetljivo pa vidimo, da je naslednja Finska, ki je mnogokrat manjša od prej naštetih držav, a z njimi vseeno konkurira.

Za zaključek pa si poglejmo še povprečno maso meteorita glede na državo padca, da vidimo, če opazimo kakšna odstopanja.

Tabeli držav dodamo stolpec povprečne mase meteorita.
"""
# %%
world_extra_gdf = world_extra_gdf.set_index("Country")
world_extra_gdf["Mean meteorite mass"] = met_country_gdf[["Country", "Mass"]].groupby("Country").mean()/10**3
world_extra_gdf = world_extra_gdf.reset_index()
# %% [markdown]
"""
Zemljevid povprečne mase meteorita na državo v kg:
"""
# %%
draw_map(world_extra_gdf, "Mean meteorite mass")
# %% [markdown]
"""
Že takoj vidimo, da so močna odstopanja, zato si poglejmo še tabelo desetih najvišjih vrednosti.

Izberemo stolpce, ki jih želimo prikazati in jih razvrstimo po povprečni masi meteorita.
Vzamemo vrhnjih deset držav in na koncu še zapišemo povprečno maso meteorita v lepšem formatu, z enoto.
"""
# %%
top10_countries_mass = world_extra_gdf[["Country", "Mean meteorite mass"]].sort_values("Mean meteorite mass", ascending=False).head(10)
top10_countries_mass["Mean meteorite mass"] = top10_countries_mass["Mean meteorite mass"].apply(lambda m: f"{round(m, 1)} kg")
# %% [markdown]
"""
Tabela desetih držav z najvišjo povprečno maso meteorita:
"""
# %%
pretty_table(top10_countries_mass)
# %% [markdown]
"""
Imamo tri države, ki močno prevladujejo nad ostalimi.
To so Somalija, Namibija in Tanzanija.
Pogledamo si lahko tabele meteoritov, ki so padli na ozemlje teh držav, da bomo lažje ugotovili zakaj točno te prevladujejo.

Naredimo novo tabelo z stolpci, ki jih hočemo prikazati in že na začetku razvrstimo po masi.
Potem stolpec mase polepšamo s pretvorbo enot in dodatkom enote.
Na koncu pa vsaki državi priredimo svojo tabelo, ki vsebuje samo elemente, ki so iz te države.
"""
# %%
mass_sorted_df = met_country_gdf[["Name", "Country", "Mass"]].sort_values("Mass", ascending=False)
mass_sorted_df["Mass"] = (mass_sorted_df["Mass"]/10**3).apply(lambda m: f"{round(m, 1)} kg")
# %%
somalia_df = mass_sorted_df[mass_sorted_df["Country"] == "Somalia"]
# %%
namibia_df = mass_sorted_df[mass_sorted_df["Country"] == "Namibia"]
# %%
tanzania_df = mass_sorted_df[mass_sorted_df["Country"] == "United Republic of Tanzania"]
# %% [markdown]
"""
Tabela vseh meteoritov Somalije, urejena po masi:
"""
# %%
pretty_table(somalia_df)
# %% [markdown]
"""
Tabela desetih najtežjih meteoritov Namibije, urejena po masi:
"""
# %%
pretty_table(namibia_df.head(10))
# %% [markdown]
"""
Tabela vseh meteoritov Tanzanije, urejena po masi:
"""
# %%
pretty_table(tanzania_df)
# %% [markdown]
"""
Naleteli smo na isto težavo kot pri grafičnih prikazih.
Močno odstopanje teh treh držav je povzročil padec treh zelo težkih meteoritov, ki se uvrščajo med ene najtežjih na svetu.
Manjše kot povprečno število meteoritov v teh državah pa vodi v močno prevladovanje teh najtežjih meteoritov pri izračunu povprečne mase.
"""
# %% [markdown]
"""
## Zaključek
Videli smo torej različne zanimivosti o meteoritih in kraterjih kot so najtežji, najstarejši in najpogostejši meteoriti in kraterji.
Različna področja smo analizirali tudi tako, da smo iskali povezave med spremenljivkami.
Recimo število meteoritov skozi leta, povprečna masa meteorita skozi leta in še več.
Končali pa smo še z geografsko analizo in prikazom, kjer smo obravnavali število meteoritov na državo in povprečno maso meteorita na državo ter drugo.

Odkrili smo, da je večina meteoritov iz zadnjih 50 let, da je največ meteoritov padlo leta 2000 in desetletja 2000-2010, da je večina kraterjev starih manj kot 600 milijonov let še veliko več.
Pri analizi mase pa so nam vedno pred oči skakali podatki v povezavi z najtežjimi meteoriti.
Recimo leta, ko je bila povprečna masa meteorita največja so bila ravno ta, ko je padel eden izdem najtežjih meteoritov.
Tip meteorita z najvišjo povprečno maso je bil tip enega izmed najtežjih meteoritov in države z najvišjo povprečno maso meteoritov so bile ravno tiste, v katere je padel eden takih meteoritov.

Podatki in rezultati, ki smo jih dobili so zanimivi, ampak ali so uporabni je pa druga zgodba.
Med analizo smo odkrili meteorit starejši od vesolja samega, ki je bil posledica napake v podatkovni bazi, zato ne moremo garantirati pravilnosti vseh podatkov.
Lahko se še kje skriva napaka takšne vrste, le tokrat malo manj očitna.
Je pa smešna ideje meteorita, dvakrat starejšega od vesolja, zato je tudi to nekaj vredno.
"""
