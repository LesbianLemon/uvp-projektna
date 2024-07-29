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
#### Meteoriti skozi čas
Poskusimo narisati grafe števila meteoritov skozi zgodovino.
"""
# %% [markdown]
"""
Graf števila padlih meteoritov v desetletju od leta 1700 dalje:
"""
# %%
((met_df[met_df["Year"] > 1800]["Year"]//10)*10).value_counts().sort_index().plot.bar(ylabel="Amount")
# %% [markdown]
"""
Očitno je, da so skoraj vsi meteoriti v podatkovni bazi iz zadnjih 50 let, zato moramo časovno obdobje skrajšati, da dobimo boljšo predstavo.

Graf števila padlih meteoritov v desetletju od leta 1950 dalje:
"""
# %%
((met_df[met_df["Year"] > 1950]["Year"]//10)*10).value_counts().sort_index().plot.bar(ylabel="Amount")
# %% [markdown]
"""
Graf števila padlih meteoritov v letu od leta 1950 dalje:
"""
# %%
met_df[met_df["Year"] > 1950]["Year"].value_counts().sort_index().plot(ylabel="Amount")
# %% [markdown]
"""
Podatki delujejo zelo naključni, z zelo velikimi skoki in padci iz leta v leto.
To bi lahko bila posledica, da ob prodoru meteorja v atmosfero ta ponavadi razpade na več manjših.
Torej bi lahko ob padcu velikega meteorita, ki se razbije na tisoče delov graf močno poskočil.

Ko pogledamo graf po desetletjih, zgleda ta že manj naključen, vendar še vedno vidimo velike razlike med desetletji.
"""
