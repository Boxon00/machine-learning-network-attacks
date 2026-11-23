# SIR1 – Primena mašinskog učenja u detekciji mrežnih napada

*Application of Machine Learning in Network Intrusion Detection*
Master akademske studije, Elektronski fakultet Univerziteta u Nišu – predmet SIR1.

Projekat poredi tri klasična algoritma (**Decision Tree, Random Forest, SVM**) na skupu
**UNSW-NB15** (zvanična podela na trening i test skup) u zadatku **binarne klasifikacije**
(`label`: 0 = normalan saobraćaj, 1 = napad). Priprema za višeklasnu klasifikaciju (`attack_cat`)
postoji u kodu (`get_xy(df, task="multiclass")`), ali višeklasni eksperiment nije deo ovog rada.

## 1. Preuzimanje i postavljanje dataseta
1. Preuzmite UNSW-NB15 sa zvanične stranice: <https://research.unsw.edu.au/projects/unsw-nb15-dataset>
   (sekcija sa „training and testing sets“).
2. Datoteke postavite u `data/raw/`:
   - `UNSW_NB15_training-set.csv` (175.341 zapis)
   - `UNSW_NB15_testing-set.csv` (82.332 zapisa)
   - `UNSW-NB15_features.csv` (opis karakteristika; nije obavezan za eksperiment)
3. Dataset se ne uključuje u Git (`.gitignore`). Za akademsku upotrebu važe uslovi citiranja sa zvanične stranice.

## 2. Instalacija
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Testirano sa Python 3.12, scikit-learn 1.9, pandas 3.0 (tačne verzije: `results/metrics/environment.json`).

## 3. Pokretanje
```bash
python main.py                    # ceo eksperiment: EDA -> DT -> RF -> SVM -> ablacija -> skaliranje -> poređenje
python main.py --stage eda        # samo EDA
python main.py --stage dt         # samo Decision Tree (isto: python -m src.decision_tree)
python main.py --stage rf         # samo Random Forest (python -m src.random_forest)
python main.py --stage svm        # samo SVM (python -m src.svm)
python main.py --stage ablation   # analiza osetljivosti (ablacija)
python main.py --stage scaling    # skaliranje vremena treniranja
python main.py --stage compare    # završna tabela i grafikoni
python main.py --quick            # SAMO provera koda (mali uzorci, upis u results_quick/)
jupyter notebook notebooks/exploratory_analysis.ipynb
```
Pun eksperiment traje oko 12 minuta na jednom jezgru (izmereno u ovom radu: DT ~1,5 min, RF ~4,5 min, SVM ~3 min, ablacija ~2 min).
Redosled faza je bitan: `compare` i `ablation` čitaju rezultate koje prethodne faze upisuju.

## 3a. Testovi ispravnosti
```bash
python -m unittest discover -s tests -v     # 15 testova; "skipped" znaci da nema dataseta/rezultata
```
Proveravaju: zvanične dimenzije i broj klasa, da `id`/`label`/`attack_cat` nisu ulaz, da se preprocesor uči samo na treningu,
obradu nepoznatih kategorija (`ACC`, `CLO`), tačnost metrika na ručno izračunatom primeru, reproduktivnost,
i da se sačuvana tabela rezultata poklapa sa sačuvanim predikcijama.

## 3b. Generisanje dokumenata (opciono)
```bash
python reports/build_report.py     # seminarski rad (DOCX; PDF ako su instalirani LibreOffice i poppler-utils)
python defense/build_qa.py         # pitanja i odgovori za odbranu (DOCX)
npm install pptxgenjs && node defense/build_deck.js   # prezentacija (PPTX)
```
Dokumenti se generišu iz `results/metrics` i `results/figures`, pa prvo pokrenite `python main.py`.
Ime studenta, indeks i mentora na naslovnoj strani zamenite u `reports/build_report.py` (funkcija `title_page`) i `defense/build_deck.js`.

## 4. Struktura projekta
```
data/raw/            sirove CSV datoteke (ne ulaze u Git)
data/processed/      rezervisano za međuproizvode
notebooks/           exploratory_analysis.ipynb
src/config.py        putanje, seed (42), veličine uzoraka, broj jezgara
src/data_loader.py   učitavanje, provera seme, get_xy (izbor cilja), uzorkovanje
src/preprocessing.py imputacija -> log1p -> StandardScaler; OneHotEncoder (sve u Pipeline-u)
src/experiment.py    zajedničko: tuning (GridSearchCV), treniranje, merenje vremena, čuvanje
src/decision_tree.py, random_forest.py, svm.py   po jedan modul za svaki algoritam
src/evaluation.py    metrike, bootstrap CI, McNemar, tabela poređenja
src/visualization.py svi grafikoni
src/eda.py, ablation.py, comparison.py
results/metrics/     JSON/CSV rezultati;   results/figures/  PNG grafikoni
reports/             seminarski rad (DOCX/PDF) i skripta za generisanje
defense/             prezentacija i pitanja za odbranu
main.py, requirements.txt, README.md, .gitignore
```

## 5. Ključne metodološke odluke
- **Zvanična podela** trening/test se ne menja. Test skup se ne koristi za izbor hiperparametara ni preprocesiranja.
- **Bez curenja podataka:** preprocesiranje je deo `Pipeline`-a i uči se samo na treningu (u unakrsnoj validaciji
  ponovo u svakom foldu). `id`, `label` i `attack_cat` nikada nisu ulazne karakteristike (`get_xy`).
- **Nepoznate kategorije:** test sadrži vrednosti `state` (`ACC`, `CLO`) kojih nema u treningu → `handle_unknown="ignore"`.
- **Hiperparametri:** `GridSearchCV` (stratifikovani 3-fold, F1) na stratifikovanom uzorku od 50.000 zapisa treninga;
  konačni modeli se treniraju na celom treningu. Broj stabala RF i dubina DT biraju se na podeli 80/20 unutar treninga.
- **SVM:** `LinearSVC` na celom treningu; RBF `SVC` na stratifikovanom uzorku od 20.000 zapisa (računska zahtevnost).
  Rezultati RBF modela odnose se na model treniran na uzorku, ali su evaluirani na **celom** test skupu.
  Dodatno se evaluira `LinearSVC` na istom uzorku radi izolovanja efekta kernela.
- **Vremena:** fitovanje i predikcija se mere sa jednim jezgrom (`N_JOBS_FIT=1`); uključuju preprocesiranje.
- **Duplikati** se u glavnom eksperimentu zadržavaju (zvanična podela); uticaj uklanjanja je u ablacionoj studiji,
  zajedno sa uklanjanjem `stcpb`/`dtcpb`.
- **Reproduktivnost:** `random_state=42` svuda; verzije softvera u `results/metrics/environment.json`.
  Rezultati mogu neznatno odstupati na drugoj verziji biblioteka ili broju jezgara (vremena zavise od hardvera).

## 6. Literatura i dataset
Dataset: Moustafa & Slay (2015, 2016) – vidi seminarski rad, poglavlje „Literatura“. Zvanična stranica:
<https://research.unsw.edu.au/projects/unsw-nb15-dataset>. Pre predaje rada proverite svaki DOI iz liste literature.
