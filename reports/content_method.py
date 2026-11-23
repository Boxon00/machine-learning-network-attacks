"""Poglavlja 6-8: opis dataseta, metodologija i implementacija (brojke se citaju iz rezultata)."""
import pandas as pd

from pathlib import Path
FIG = str(Path(__file__).resolve().parent.parent / "results" / "figures") + "/"


def n(x):
    """Ceo broj sa tackom kao separatorom hiljada (srpski zapis)."""
    return f"{int(x):,}".replace(",", ".")


def pct(x, d=2):
    return f"{x*100:.{d}f}".replace(".", ",") + "%"


def blocks(R):
    E = R["eda"]
    B = []
    a = B.append
    tr_n, te_n = E["trening_oblik"][0], E["test_oblik"][0]
    dup = E["duplikati"]; ov = E["preklapanje"]
    att = pd.read_csv(R["M"] / "eda_attack_cat_counts.csv", index_col=0)

    # ------------------------------------------------------------------ 6. DATASET
    a(("h1", "6. Opis skupa podataka UNSW-NB15"))
    a(("h2", "6.1. Nastanak skupa podataka"))
    a(("p", "Skup UNSW-NB15 kreirali su istraživači iz Australijskog centra za sajber-bezbednost (ACCS) pri Univerzitetu Novog Južnog Velsa u Kanberi. Prema zvaničnoj stranici skupa, sirovi mrežni paketi generisani su alatom IXIA PerfectStorm u laboratoriji Cyber Range kao hibrid realnih savremenih normalnih aktivnosti i sintetički generisanih savremenih napada [[cite:unswpage]], [[cite:moustafa2015]]. Saobraćaj je snimljen alatom tcpdump (oko 100 GB sirovog saobraćaja), a zatim su alatima Argus i Bro-IDS i uz dvanaest razvijenih algoritama izvedene karakteristike; ukupno 49 atributa zajedno sa oznakom klase [[cite:unswpage]]."))
    a(("p", f"Kompletan skup sadrži 2.540.044 zapisa raspoređenih u četiri CSV datoteke, a zvaničnom stranicom je dodatno ponuđena podela na trening skup ({n(tr_n)} zapisa) i test skup ({n(te_n)} zapisa) [[cite:unswpage]]. Ove dve datoteke (UNSW_NB15_training-set.csv i UNSW_NB15_testing-set.csv) korišćene su u ovom radu, i to isključivo u zvaničnoj podeli. Prema uslovima korišćenja, slobodna upotreba je dozvoljena za akademska istraživanja uz citiranje radova autora [[cite:unswpage]]. Podaci ovog rada učitani su iz datoteka i svi brojevi u ovom poglavlju izračunati su direktno iz njih (skripta eda.py)."))

    a(("h2", "6.2. Struktura i karakteristike"))
    a(("p", f"Obe datoteke imaju po 45 kolona: redni broj zapisa (id), 42 ulazne karakteristike, kategoriju saobraćaja (attack_cat) i binarnu oznaku (label). Među 42 ulazne karakteristike je {E['broj_numerickih_ulaznih']} numeričkih i {E['broj_kategorijskih_ulaznih']} kategorijske: proto (transakcioni protokol, 133 različite vrednosti u treningu), service (usluga, 13 vrednosti, uključujući vrednost „-“ kada usluga nije identifikovana) i state (stanje konekcije, 9 vrednosti u treningu, 7 u testu). U skupu nema nedostajućih ni beskonačnih vrednosti, i nema konstantnih kolona."))
    a(("p", "Karakteristike obuhvataju osnovne atribute toka (trajanje, protokol, usluga, stanje), sadržajne i vremenske atribute (broj paketa i bajtova u oba smera, TTL vrednosti, gubitke paketa, jitter, vremena između paketa, TCP veličine prozora i sekvencne brojeve, vreme uspostave TCP veze), kao i dodatno izvedene statistike povezivanja (ct_* atributi) koje opisuju broj sličnih konekcija u okviru poslednjih 100 konekcija [[cite:moustafa2015]]. Tabela 1 prikazuje izbor karakteristika koje se pominju u analizi rezultata."))
    a(("tab", "features", "Izbor karakteristika UNSW-NB15 (opis prema zvaničnoj datoteci sa opisima karakteristika)",
       ["Karakteristika", "Tip", "Opis"],
       [["dur", "float", "Ukupno trajanje zapisa (toka)"],
        ["proto / service / state", "nominalna", "Transakcioni protokol / usluga (http, ftp, dns, …) / stanje konekcije"],
        ["spkts, dpkts", "ceo broj", "Broj paketa od izvora ka odredištu i obrnuto"],
        ["sbytes, dbytes", "ceo broj", "Broj bajtova od izvora ka odredištu i obrnuto"],
        ["rate", "float", "Brzina prenosa (paketi u jedinici vremena)"],
        ["sttl, dttl", "ceo broj", "Vrednost TTL (time to live) od izvora ka odredištu i obrnuto"],
        ["sload, dload", "float", "Biti u sekundi od izvora / ka izvoru"],
        ["sloss, dloss", "ceo broj", "Broj retransmitovanih ili odbačenih paketa"],
        ["sjit, djit", "float", "Jitter izvora / odredišta (ms)"],
        ["swin, dwin", "ceo broj", "Vrednosti TCP prozora (advertisement)"],
        ["stcpb, dtcpb", "ceo broj", "TCP bazni sekvencni brojevi izvora i odredišta"],
        ["smean, dmean", "ceo broj", "Prosečna veličina paketa koje šalje izvor / odredište"],
        ["ct_srv_src, ct_dst_ltm, …", "ceo broj", "Brojači konekcija sa istom uslugom/adresom/portom u poslednjih 100 konekcija"],
        ["is_sm_ips_ports", "binarna", "1 ako su izvorna i odredišna IP adresa i port jednaki"]],
       [4.2, 2.3, 9.0], None))

    a(("h2", "6.3. Kategorije saobraćaja"))
    a(("p", "Skup sadrži normalan saobraćaj i devet kategorija napada. Zvanična dokumentacija navodi kategorije Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode i Worms [[cite:unswpage]]; u CSV datotekama se kategorija Backdoors javlja pod nazivom „Backdoor“. Opšti opis kategorija: Fuzzers šalju nasumične ili neispravne ulaze radi izazivanja grešaka u servisima; Analysis obuhvata skeniranje portova, neželjenu poštu i napade putem veb sadržaja; Backdoor zaobilazi uobičajene mehanizme autentikacije radi skrivenog pristupa; DoS (Denial of Service) ometa dostupnost usluge; Exploits iskorišćava poznate ranjivosti; Generic je tehnika koja deluje protiv kriptografskih primitiva bez obzira na implementaciju; Reconnaissance prikuplja informacije o ciljnom sistemu; Shellcode je kod za preuzimanje kontrole nad procesom; Worms su samoreplikujući programi. Tabela 2 prikazuje zastupljenost kategorija."))
    rows = []
    for cat in att.sort_values("trening", ascending=False).index:
        rows.append([cat, n(att.loc[cat, "trening"]), pct(att.loc[cat, "trening"] / tr_n), n(att.loc[cat, "test"]), pct(att.loc[cat, "test"] / te_n)])
    rows.append(["**Ukupno**", f"**{n(tr_n)}**", "**100%**", f"**{n(te_n)}**", "**100%**"])
    a(("tab", "attack_counts", "Zastupljenost kategorija saobraćaja u trening i test skupu",
       ["Kategorija", "Trening (n)", "Trening (%)", "Test (n)", "Test (%)"], rows, [4.0, 2.9, 2.9, 2.9, 2.9], None))
    a(("fig", "dist", FIG + "eda_distributions.png", f"Raspodele klasa: (a) binarna oznaka (normalan saobraćaj čini {pct(1-E['udeo_napada_trening'],1)} trening i {pct(1-E['udeo_napada_test'],1)} test skupa); (b) kategorije saobraćaja (logaritamska skala).", 15.0))
    a(("p", f"Binarna raspodela je umereno neuravnotežena i različita u dva skupa: udeo napada je {pct(E['udeo_napada_trening'])} u treningu i {pct(E['udeo_napada_test'])} u testu ([[fig:dist]]a). To je pomak raspodele između trening i test skupa, koji treba imati u vidu pri tumačenju Precision i Accuracy. Raspodela po kategorijama je mnogo neuravnoteženija ([[fig:dist]]b): kategorija Worms ima samo 130 primera u treningu i 44 u testu, dok Generic i Exploits imaju desetine hiljada."))

    a(("h2", "6.4. Analiza kvaliteta podataka"))
    a(("p", f"**Nedostajuće i beskonačne vrednosti.** Nijedan od dva skupa ne sadrži nedostajuće ni beskonačne vrednosti. Pipeline ipak sadrži zaštitne korake (zamena beskonačnih vrednosti i imputacija medijanom, naučena na treningu), pa bi radio i na izmenjenim podacima."))
    a(("p", f"**Duplikati.** Kolona id je redni broj, zbog čega nema zapisa koji su identični u svim kolonama. Ako se id izostavi, trening skup sadrži {n(dup['duplikati_bez_id_trening'])} duplikata ({n(dup['jedinstveni_bez_id_trening'])} jedinstvenih zapisa), a test skup {n(dup['duplikati_bez_id_test'])} ({n(dup['jedinstveni_bez_id_test'])} jedinstvenih). Radi se o ponovljenim tokovima sa istim statistikama (a ne o greškama u prikupljanju), pa se u glavnom eksperimentu zadržavaju, a uticaj njihovog uklanjanja ispituje se u ablacionoj studiji (poglavlje 9.8)."))
    a(("p", f"**Preklapanje trening i test skupa.** {n(ov['test_zapisa_identicnih_treningu'])} od {n(ov['test_ukupno'])} test zapisa ({pct(ov['udeo_preklapanja'])}) ima vektor karakteristika identičan nekom zapisu u treningu. U treningu postoji i {n(ov['kontradiktornih_grupa_u_treningu'])} grupa identičnih vektora sa različitim oznakama klase, što predstavlja šum u oznakama."))
    a(("p", "**Kategorijske vrednosti koje postoje samo u jednom skupu.** U test skupu postoje stanja ACC i CLO kojih nema u treningu, dok neke vrednosti postoje samo u treningu (proto: icmp, rtp; state: ECO, PAR, URN, no). Zbog toga kodiranje kategorija mora tolerisati nepoznate vrednosti u test skupu (poglavlje 7.2)."))
    a(("p", "**Asimetrija raspodela.** Većina numeričkih karakteristika ima izrazito desno asimetričnu raspodelu sa dugim repom: najveće skewness vrednosti na treningu imaju trans_depth (≈167), response_body_len (≈76) i sbytes (≈45), a maksimalne vrednosti dosežu 10⁷–10⁹ (npr. sload do ≈6·10⁹). Ovo opravdava logaritamsku transformaciju pre standardizacije za algoritme zasnovane na rastojanjima i skalarnim proizvodima, kao što je SVM."))
    a(("fig", "feat_dist", FIG + "eda_feature_distributions.png",
       "Raspodele odabranih karakteristika po klasama nakon transformacije log(1+x).", 12.0))
    a(("p", "**Povezanost sa ciljnom promenljivom.** Najjače (linearno) povezane sa oznakom klase su sttl (r ≈ 0,69) i ct_state_ttl (r ≈ 0,58), a slede dload (r ≈ −0,39), ct_dst_sport_ltm (≈ 0,36) i dmean (≈ −0,34) ([[fig:corr]]). Linearna korelacija ne obuhvata nelinearne zavisnosti koje stabla mogu da iskoriste, pa je ovo samo orijentacioni pokazatelj."))
    a(("fig", "corr", FIG + "eda_correlation_heatmap.png",
       "Pearsonova korelacija 18 numeričkih karakteristika najjače povezanih sa oznakom klase (trening).", 10.5))
    a(("h2", "6.5. Zvanična podela i njene posledice"))
    a(("p", f"Zvanična podela je zadržana jer omogućava poređenje sa drugim radovima i sprečava proizvoljnost. Treba uočiti da je trening skup veći ({n(tr_n)} zapisa) od test skupa ({n(te_n)} zapisa), da se raspodele klasa razlikuju i da test skup nije uzorkovan istom raspodelom kao trening. Rezultati na test skupu zato mere generalizaciju pod blagim pomakom raspodele, što je realnije od nasumične podele, ali otežava poređenje sa radovima koji koriste drugačije podele."))

    # ------------------------------------------------------------------ 7. METODOLOGIJA
    a(("h1", "7. Metodologija istraživanja"))
    a(("h2", "7.1. Opšti dizajn eksperimenta"))
    a(("p", "Eksperiment je dizajniran tako da se tri algoritma porede pod uporedivim uslovima: isti skup podataka i ista podela, isto preprocesiranje, ista procedura izbora hiperparametara (unakrsna validacija na trening podacima), isti test skup i iste metrike. Primarni eksperiment je binarna klasifikacija (label), a višeklasna klasifikacija (attack_cat) nije deo ovog rada i ne meša se sa njim. [[fig:design]] prikazuje tok eksperimenta."))
    a(("fig", "design", FIG + "experiment_design.png", "Tok eksperimenta: test skup se koristi samo za završnu evaluaciju.", 14.0))
    a(("h2", "7.2. Priprema podataka i obrazloženje odluka"))
    a(("bul", [
        "**Uklanjanje kolone id.** Redni broj zapisa nema informacionu vrednost i, ako bi bio korišćen, mogao bi omogućiti modelu da koristi redosled zapisa u datoteci (artefakt prikupljanja podataka).",
        "**Ciljne promenljive nikada nisu ulaz.** Funkcija get_xy uklanja i label i attack_cat iz ulaznih karakteristika, bez obzira na to koja je promenljiva cilj. Time je izbegnuto da se ciljna promenljiva (ili njen derivat, kao što je attack_cat za label) koristi za sopstvenu predikciju.",
        "**Kategorijske promenljive (proto, service, state): One-Hot kodiranje** sa opcijom handle_unknown=\"ignore\". Redno (label) kodiranje bi nametnulo veštački redosled kategorija; one-hot ga izbegava. Opcija ignore je neophodna jer test skup sadrži vrednosti stanja (ACC, CLO) kojih nema u treningu – takvi zapisi dobijaju sve nule u tim kolonama, bez greške i bez „gledanja“ test skupa.",
        "**Numeričke promenljive: imputacija medijanom → log(1+x) → standardizacija.** Imputacija je zaštitni korak (u podacima nema nedostajućih vrednosti). Logaritamska transformacija primenjuje se samo na nenegativne kolone čija je asimetrija na TRENINGU veća od 2 (prag je hiperparametar pretprocesiranja, ne rezultat testiranja); to ublažava ekstremne vrednosti i važno je za SVM. Standardizacija (srednja vrednost 0, standardna devijacija 1) je nužna za SVM, dok je za stabla neutralna (monotone transformacije ne menjaju podele).",
        "**Isto preprocesiranje za sva tri algoritma.** Time se razlike u rezultatima mogu pripisati algoritmima, a ne pripremi podataka.",
        "**Duplikati i odstupajući zapisi se ne uklanjaju** u glavnom eksperimentu. Uklanjanje bi izmenilo zvaničnu raspodelu test skupa i ne bi bilo uporedivo sa literaturom; osetljivost na ovu odluku se posebno ispituje (poglavlje 9.8). Ekstremne vrednosti se ne brišu jer mogu biti upravo znak napada.",
        "**Karakteristike stcpb i dtcpb (TCP sekvencni brojevi)** zadržane su u glavnom eksperimentu jer pripadaju zvaničnom skupu karakteristika; njihov uticaj se ispituje u ablacionoj studiji, jer sekvencni brojevi mogu biti artefakt generisanja saobraćaja, a ne bezbednosno relevantno svojstvo."]))
    a(("h2", "7.3. Sprečavanje curenja podataka"))
    a(("p", "Curenje podataka sprečeno je na sledeće načine: (1) sve transformacije (imputacija, odabir kolona za log, standardizacija, kodiranje) sastavni su deo scikit-learn objekta Pipeline, koji se uči metodom fit isključivo na trening podacima, dok test podaci prolaze samo kroz transform; (2) u unakrsnoj validaciji Pipeline se uči iznova u svakom foldu, pa validacioni fold nikada ne utiče na parametre preprocesiranja; (3) test skup se ne koristi ni za izbor hiperparametara, broja stabala, dubine stabla niti bilo koje druge odluke; (4) ciljne promenljive nisu ulazne karakteristike. Preklapanje identičnih zapisa između trening i test skupa (poglavlje 6.4) nije posledica metodologije, već svojstvo zvanične podele, i zato je transparentno prikazano i dodatno analizirano."))
    a(("h2", "7.4. Izbor hiperparametara"))
    a(("p", f"Hiperparametri se biraju pretragom po mreži (GridSearchCV) sa stratifikovanom 3-fold unakrsnom validacijom i F1-score kao kriterijumom, nad celim Pipeline-om. Zbog računskih ograničenja (jedno procesorsko jezgro), pretraga se izvodi na stratifikovanom slučajnom uzorku od 50.000 zapisa trening skupa (seed 42); konačni modeli se zatim treniraju na celom trening skupu. Pretraga po mreži je izabrana zbog transparentnosti i reproduktivnosti, a alternativa je nasumična pretraga [[cite:bergstra2012]]. Kao kriterijum je izabran F1 jer uravnotežava Precision i Recall; Recall se posebno prati i izveštava."))
    a(("tab", "grids", "Mreže hiperparametara korišćene u pretrazi",
       ["Algoritam", "Hiperparametar", "Vrednosti"],
       [["Decision Tree", "criterion", "gini, entropy"], ["", "max_depth", "5, 10, 20, None"], ["", "min_samples_leaf", "1, 5, 20"],
        ["Random Forest", "max_depth", "None, 25"], ["", "min_samples_leaf", "1, 3"], ["", "max_features", "sqrt, log2"],
        ["", "n_estimators", "kriva na validaciji: 10, 25, 50, 100, 200, 300 (u pretrazi fiksno 100)"],
        ["Linear SVM (LinearSVC)", "C", "0,01; 0,1; 1; 10"],
        ["SVM RBF (SVC)", "C × gamma", "{1, 10, 100} × {0,001; 0,01; 0,1}"]],
       [4.2, 4.0, 7.3], None))
    a(("p", "Dubina stabla odlučivanja i broj stabala u šumi dodatno se analiziraju krivama na podeli trening skupa 80/20 (stratifikovano), pri čemu se preprocesiranje uči samo na 80% delu. Test skup se ni u ovim analizama ne koristi."))
    a(("h2", "7.5. Postupak za SVM i uzorkovanje"))
    a(("p", f"Kernelski SVM ima složenost koja raste više nego kvadratno sa brojem uzoraka [[cite:pedregosa2011]], pa je treniranje RBF SVM-a na svih {n(tr_n)} zapisa na raspoloživom hardveru (jedno jezgro, 3,9 GB RAM-a) nepraktično. Zbog toga su evaluirane tri varijante: (1) **Linear SVM** (LinearSVC) treniran na **celom** trening skupu; (2) **SVM RBF** (SVC) treniran na stratifikovanom uzorku od {n(R['svm_sample'])} zapisa trening skupa (seed 42), uz pretragu C i gamma na podskupu tog uzorka od {n(R['svm_tune_sample'])} zapisa; (3) **Linear SVM treniran na istom uzorku** kao RBF, kako bi se efekat kernela razdvojio od efekta veličine trening skupa. Sve tri varijante evaluirane su na **celom** test skupu. Rezultati varijanti (2) i (3) odnose se na modele trenirane na uzorku i kao takvi se označavaju u celom radu; oni se ne predstavljaju kao rezultati na kompletnom trening skupu."))
    a(("h2", "7.6. Evaluacija i statistička analiza"))
    a(("p", "Svi modeli se evaluiraju na istom, celom test skupu. Izračunavaju se Accuracy, Precision, Recall, F1-score, ROC-AUC, PR-AUC, MCC, FPR i FNR, matrica konfuzije, kao i vreme treniranja i vreme predikcije. Pored toga: (a) 95% intervali poverenja za Accuracy, Precision, Recall i F1 procenjuju se bootstrap postupkom sa 1.000 ponovljenih uzoraka test skupa [[cite:efron1993]]; (b) parovi modela se porede McNemarovim testom [[cite:mcnemar1947]]; (c) analizira se udeo ispravno klasifikovanih zapisa po kategorijama napada; (d) poredi se uspeh na trening i test skupu radi procene preprilagođavanja. Napominje se da bootstrap uzorkovanje uzima u obzir samo varijabilnost test skupa, a ne i varijabilnost treniranja (npr. različit seed), kao i da McNemarov test pretpostavlja nezavisne primere, što zbog dupliranih tokova nije strogo ispunjeno; zato se p-vrednosti tumače kao orijentacione."))
    a(("p", "Vreme treniranja obuhvata preprocesiranje i treniranje klasifikatora; vreme predikcije obuhvata preprocesiranje i predikciju oznaka za ceo test skup. Svi modeli se treniraju i predviđaju sa jednim jezgrom (n_jobs = 1) radi uporedivosti; pretraga hiperparametara može koristiti sva raspoloživa jezgra. Apsolutna vremena zavise od hardvera, pa su značajna prvenstveno kao relativna poređenja."))
    a(("h2", "7.7. Reproduktivnost"))
    a(("p", "Svi stohastički koraci koriste isti seed (random_state = 42): stratifikovano uzorkovanje, podela na validaciju, unakrsna validacija, stabla i šuma, kao i bootstrap. Verzije softvera i hardverski parametri automatski se beleže u datoteku environment.json. Ceo eksperiment se pokreće jednom komandom (python main.py)."))

    # ------------------------------------------------------------------ 8. IMPLEMENTACIJA
    a(("h1", "8. Implementacija sistema"))
    a(("h2", "8.1. Tehnologije i organizacija koda"))
    a(("p", f"Implementacija je izvedena u jeziku Python {R['env']['python']} uz biblioteke Pandas {R['env']['pandas']}, NumPy {R['env']['numpy']}, Scikit-learn {R['env']['scikit-learn']} [[cite:pedregosa2011]], SciPy {R['env']['scipy']}, Matplotlib i Seaborn, kao i Jupyter Notebook za istraživačku analizu. Kod je organizovan modularno; svaki algoritam ima zaseban modul koji se može samostalno pokrenuti, a zajednička logika izdvojena je u zasebne module ([[tab:modules]])."))
    a(("tab", "modules", "Moduli projekta i njihova odgovornost",
       ["Datoteka", "Odgovornost"],
       [["config.py", "putanje, seed, veličine uzoraka, broj jezgara"],
        ["data_loader.py", "učitavanje zvaničnih CSV datoteka, provera seme, get_xy (izbor cilja), uzorkovanje"],
        ["preprocessing.py", "ColumnTransformer: imputacija, log1p, standardizacija, one-hot (u Pipeline-u)"],
        ["experiment.py", "zajednički postupak: GridSearchCV, treniranje, merenje vremena, čuvanje rezultata"],
        ["decision_tree.py", "Decision Tree: kriva dubine, pretraga, evaluacija, značaj karakteristika"],
        ["random_forest.py", "Random Forest: kriva broja stabala, pretraga, evaluacija, značaj karakteristika"],
        ["svm.py", "Linear SVM, Linear SVM (uzorak) i SVM RBF (uzorak)"],
        ["evaluation.py", "metrike, bootstrap, McNemar, tabela poređenja"],
        ["visualization.py", "svi grafikoni; eda.py, ablation.py, comparison.py"]],
       [4.2, 11.3], None))
    a(("h2", "8.2. Preprocesiranje bez curenja podataka"))
    a(("p", "Ključni deo implementacije je preprocesor koji se gradi na osnovu tipova kolona u trening skupu i objedinjuje se sa klasifikatorom u jedan Pipeline. Slede izvodi iz koda."))
    a(("code", '''def build_preprocessor(X_train):
    numeric, categorical = split_column_types(X_train)
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("log", SkewedLog1p()),          # kolone biraju se na TRENINGU
        ("scaler", StandardScaler()),
    ])
    cat_pipe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return ColumnTransformer([("num", num_pipe, numeric),
                              ("cat", cat_pipe, categorical)])

def make_pipeline(X_train, estimator):
    return Pipeline([("prep", build_preprocessor(X_train)), ("clf", estimator)])'''))
    a(("p", "Izbor ciljne promenljive centralizovan je u jednoj funkciji, čime se onemogućava slučajno ubacivanje cilja među ulaze:"))
    a(("code", '''def get_xy(df, task="binary", drop_columns=()):
    target = "label" if task == "binary" else "attack_cat"
    to_drop = {"id", "label", "attack_cat", *drop_columns}
    X = df.drop(columns=[c for c in to_drop if c in df.columns])
    y = df[target].copy()
    assert target not in X.columns
    return X, y'''))
    a(("h2", "8.3. Treniranje, merenje vremena i evaluacija"))
    a(("p", "Funkcija fit_and_evaluate prima nefitovan klasifikator, gradi Pipeline, trenira ga na trening skupu, meri vreme treniranja i vreme predikcije na test skupu (time.perf_counter), računa metrike na test i trening skupu, bootstrap intervale i uspešnost po kategorijama, i čuva rezultate u JSON datoteku, a predikcije i skorove u NPZ datoteku za kasnije crtanje ROC krivih:"))
    a(("code", '''pipe = make_pipeline(X_train, clone(estimator))
_, fit_t = timed(pipe.fit, X_train, y_train)
y_pred, pred_t = timed(pipe.predict, X_test)
y_score = get_scores(pipe, X_test)   # predict_proba ili decision_function
test_m = compute_binary_metrics(y_test, y_pred, y_score)'''))
    a(("p", "Pretraga hiperparametara izvodi se funkcijom tune_hyperparameters, koja nad celim Pipeline-om pokreće GridSearchCV sa StratifiedKFold(n_splits=3, shuffle=True, random_state=42) i F1 kao merom; test skup ovoj funkciji uopšte nije dostupan."))
    a(("h2", "8.4. Modul po algoritmu i pokretanje"))
    a(("p", "Svaki od modula decision_tree.py, random_forest.py i svm.py izlaže funkciju run_experiment i može se pokrenuti samostalno (npr. python -m src.decision_tree), ili preko ulazne tačke main.py (opcije --stage dt, rf, svm, ablation, compare, kao i --quick za brzu proveru ispravnosti koda sa malim uzorcima, čiji se rezultati upisuju u poseban direktorijum i nikada ne koriste u radu). Automatski se čuvaju metrike (results/metrics), grafikoni (results/figures) i tabele, a README datoteka sadrži uputstvo za preuzimanje dataseta i pokretanje."))
    a(("h2", "8.5. Verifikacija implementacije"))
    a(("p", "Ispravnost implementacije proveravana je na više načina: (1) kod je pre pravog eksperimenta pokrenut u brzom režimu na malim uzorcima; (2) proveravano je da se kolone label i attack_cat ne nalaze u ulaznim karakteristikama; (3) broj izlaznih karakteristika posle kodiranja zabeležen je u rezultatima; (4) svi brojevi u ovom radu učitavaju se direktno iz generisanih rezultata (JSON i CSV datoteke), bez ručnog prepisivanja. Sve izmerene vrednosti dolaze iz stvarnog izvršavanja koda na datom hardveru."))
    return B
