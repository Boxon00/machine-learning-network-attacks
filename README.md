# SIR1 – Primena mašinskog učenja u detekciji mrežnih napada

## O projektu

Ovaj projekat se bavi primenom i uporednom analizom algoritama mašinskog učenja u oblasti detekcije mrežnih napada (Network Intrusion Detection).

Cilj istraživanja je implementacija, evaluacija i poređenje odabranih algoritama mašinskog učenja radi utvrđivanja njihove efikasnosti u razlikovanju normalnog i zlonamernog mrežnog saobraćaja.

Za eksperimentalni deo koristi se UNSW-NB15 skup podataka, koji sadrži primere normalnog mrežnog saobraćaja i različitih kategorija sajber napada.

**Osnovni podaci o projektu:**

- Predmet: Studijsko-istraživački rad 1 (SIR1)
- Institucija: Elektronski fakultet Univerziteta u Nišu
- Oblast: Mašinsko učenje i sajber bezbednost
- Tip problema: Binarna klasifikacija

## Ciljevi istraživanja

- Analiza UNSW-NB15 skupa podataka.
- Priprema i obrada podataka za primenu algoritama mašinskog učenja.
- Implementacija odabranih algoritama klasifikacije.
- Evaluacija performansi primenjenih modela.
- Analiza uticaja karakteristika na rezultate klasifikacije.
- Uporedna analiza algoritama na osnovu evaluacionih metrika.
- Ispitivanje pouzdanosti eksperimentalnih rezultata.

## Korišćeni algoritmi

U okviru istraživanja implementirana su tri pristupa mašinskom učenju:

| Algoritam | Opis |
|---|---|
| Decision Tree | Klasifikacija zasnovana na stablu odlučivanja |
| Random Forest | Ansambl algoritam koji kombinuje više stabala odlučivanja |
| Support Vector Machine (SVM) | Klasifikacija pomoću optimalne granice razdvajanja klasa |

Kod SVM algoritma razmatraju se dve implementacije:

- LinearSVC – linearni pristup klasifikaciji.
- SVC sa RBF kernelom – nelinearni pristup klasifikaciji.

## Skup podataka – UNSW-NB15

Za potrebe istraživanja koristi se UNSW-NB15 skup podataka, razvijen za istraživanja u oblasti detekcije mrežnih napada.

Skup sadrži normalne mrežne aktivnosti i više kategorija napada, kao što su Fuzzers, DoS, Exploits, Generic i Reconnaissance.

**Zvanični izvor:**

https://research.unsw.edu.au/projects/unsw-nb15-dataset

Osnovne karakteristike korišćenih podataka:

| Podskup | Broj zapisa |
|---|---:|
| Trening skup | 175.341 |
| Test skup | 82.332 |
| Ukupno | 257.673 |

U glavnim eksperimentima koristi se zvanična podela na trening i test skup.

### Definisanje klasifikacionog problema

Glavni eksperimentalni zadatak predstavlja binarnu klasifikaciju:

- `0` – normalan mrežni saobraćaj.
- `1` – mrežni napad.

Originalne CSV datoteke nisu uključene u GitHub repozitorijum zbog njihove veličine.

Potrebno ih je preuzeti sa zvaničnog izvora i smestiti u direktorijum `data/raw/`.

Potrebne datoteke:

- `UNSW_NB15_training-set.csv`
- `UNSW_NB15_testing-set.csv`
- `UNSW-NB15_features.csv` (opciono).

## Tehnologije i alati

| Tehnologija | Namena |
|---|---|
| Python | Glavni programski jezik |
| Pandas | Obrada i analiza podataka |
| NumPy | Numeričke operacije |
| Scikit-learn | Implementacija algoritama i evaluacija |
| Matplotlib | Grafički prikaz rezultata |
| Jupyter Notebook | Istraživačka analiza podataka |

## Metodologija i priprema podataka

Priprema podataka predstavlja važan deo istraživanja jer kvalitet ulaznih podataka direktno utiče na performanse modela mašinskog učenja.

U okviru projekta primenjuju se sledeći postupci:

1. Učitavanje i provera integriteta podataka.
2. Razdvajanje ulaznih karakteristika i ciljne promenljive.
3. Obrada nedostajućih vrednosti.
4. Logaritamska transformacija odabranih numeričkih karakteristika.
5. Kodiranje kategoričkih karakteristika pomoću OneHotEncoder.
6. Standardizacija numeričkih karakteristika pomoću StandardScaler.
7. Formiranje pipeline strukture za pripremu i treniranje modela.

### Sprečavanje Data Leakage problema

Posebna pažnja posvećena je sprečavanju curenja podataka (Data Leakage), koje može dovesti do nerealno visokih rezultata evaluacije.

Primenjene su sledeće mere:

- Transformatori se prilagođavaju isključivo na trening podacima.
- Predobrada podataka realizovana je unutar Scikit-learn Pipeline strukture.
- Tokom unakrsne validacije predobrada se nezavisno prilagođava unutar svakog fold-a.
- Test skup se ne koristi za izbor hiperparametara.
- Identifikacione i ciljne kolone isključuju se iz ulaznih karakteristika.
- Nepoznate kategoričke vrednosti obrađuju se pomoću odgovarajućeg OneHotEncoder podešavanja.

Originalna podela na trening i test skup zadržava se tokom glavnih eksperimenata.

## Eksperimentalna evaluacija

Performanse algoritama analiziraju se primenom sledećih evaluacionih metrika:

- **Accuracy** – ukupna tačnost klasifikacije.
- **Precision** – preciznost pozitivnih predikcija.
- **Recall** – sposobnost prepoznavanja pozitivnih primera.
- **F1-score** – harmonijska sredina preciznosti i odziva.
- **Confusion Matrix** – matrica konfuzije koja prikazuje rezultate klasifikacije.

Pored osnovnih metrika, projekat obuhvata dodatne eksperimentalne analize:

- Optimizaciju hiperparametara pomoću GridSearchCV.
- Stratifikovanu unakrsnu validaciju.
- Bootstrap intervale poverenja.
- McNemar statistički test za poređenje modela.
- Ablation analizu radi ispitivanja uticaja odabranih karakteristika.
- Merenje vremena treniranja i predikcije.
- Uporednu analizu rezultata algoritama.

## Struktura projekta

```text
machine-learning-network-attacks/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── experiment.py
│   ├── decision_tree.py
│   ├── random_forest.py
│   ├── svm.py
│   ├── evaluation.py
│   ├── visualization.py
│   ├── eda.py
│   ├── ablation.py
│   └── comparison.py
│
├── results/
│   ├── metrics/
│   └── figures/
│
├── reports/
├── defense/
├── logs/
├── tests/
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Opis najvažnijih direktorijuma

- `data/` – originalni i obrađeni podaci.
- `notebooks/` – istraživačka analiza podataka.
- `src/` – implementacija algoritama, predobrada, treniranje i evaluacija.
- `results/metrics/` – rezultati eksperimenata u JSON i CSV formatima.
- `results/figures/` – grafikoni i vizuelni prikazi rezultata.
- `reports/` – generisanje seminarskog rada.
- `defense/` – materijali za pripremu odbrane.
- `logs/` – zapisi o izvršavanju eksperimenata.
- `tests/` – automatski testovi ispravnosti.

## Instalacija i podešavanje okruženja

### 1. Kloniranje repozitorijuma

```bash
git clone https://github.com/Boxon00/machine-learning-network-attacks.git

cd machine-learning-network-attacks
```

### 2. Kreiranje virtuelnog okruženja

Za Windows:

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### 3. Instalacija potrebnih biblioteka

```bash
pip install -r requirements.txt
```

Nakon preuzimanja UNSW-NB15 skupa podataka, potrebno je smestiti odgovarajuće CSV datoteke u direktorijum `data/raw/`.

## Pokretanje projekta

Glavni eksperimentalni proces pokreće se komandom:

```bash
python main.py
```

### Pokretanje pojedinačnih faza

```bash
python main.py --stage eda
python main.py --stage dt
python main.py --stage rf
python main.py --stage svm
python main.py --stage ablation
python main.py --stage scaling
python main.py --stage compare
```

Za brzu proveru ispravnosti programa:

```bash
python main.py --quick
```

Brza provera koristi manje uzorke i rezultate upisuje u `results_quick/`, bez zamene glavnih eksperimentalnih rezultata.

Za pokretanje istraživačke Jupyter sveske:

```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

**Napomena:** Za kompletno izvršavanje eksperimenta potrebno je prethodno pripremiti dataset. Završna faza poređenja i dodatne analize zavise od rezultata prethodno izvršenih faza.

## Testiranje ispravnosti

Projekat sadrži automatizovane testove kojima se proveravaju različiti aspekti implementacije.

Pokretanje testova:

```bash
python -m unittest discover -s tests -v
```

Testovi obuhvataju:

- Proveru dimenzija i broja klasa u datasetu.
- Proveru isključivanja identifikacionih i ciljnih kolona iz ulaznih karakteristika.
- Proveru pravilnog prilagođavanja predprocesora na trening podacima.
- Obradu nepoznatih kategoričkih vrednosti.
- Proveru evaluacionih metrika.
- Reproduktivnost eksperimentalnih rezultata.
- Usklađenost sačuvanih rezultata i predikcija.

Za generisanje dokumenata i prezentacije potrebno je prethodno izvršiti glavni eksperimentalni proces.

## Reproduktivnost eksperimenata

Radi obezbeđivanja ponovljivosti rezultata, u projektu se koristi fiksirana vrednost slučajnog semena:

`random_state = 42`

Verzije softverskih biblioteka i informacije o eksperimentalnom okruženju čuvaju se u:

`results/metrics/environment.json`

Rezultati mogu neznatno odstupati u različitim softverskim i hardverskim okruženjima, naročito kada je reč o vremenu izvršavanja.

## Literatura i izvori podataka

Moustafa, N. i Slay, J. (2015, 2016). UNSW-NB15 – A comprehensive data set for network intrusion detection systems.

Zvanična stranica skupa podataka:

https://research.unsw.edu.au/projects/unsw-nb15-dataset

Dodatna naučna literatura i korišćeni izvori navedeni su u seminarskom radu.

---

## Autor

**Boxon00**

GitHub: https://github.com/Boxon00

**Projekat:** Primena mašinskog učenja u detekciji mrežnih napada  
**Predmet:** Studijsko-istraživački rad 1 (SIR1)  
**Institucija:** Elektronski fakultet Univerziteta u Nišu