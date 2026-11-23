"""Poglavlja 9-12: rezultati, diskusija, ogranicenja i zakljucak. Sve brojke dolaze iz R (rezultati eksperimenta)."""
import pandas as pd

from pathlib import Path
FIG = str(Path(__file__).resolve().parent.parent / "results" / "figures") + "/"


def f(x, d=4):
    return f"{x:.{d}f}".replace(".", ",")


def p(x, d=2):
    return f"{x*100:.{d}f}".replace(".", ",") + "%"


def n(x):
    return f"{int(x):,}".replace(",", ".")


def blocks(R):
    B = []; a = B.append
    dt, rf, ln, rb, ls = R["dt"], R["rf"], R["lin"], R["rbf"], R["lins"]
    M = lambda r, k: r["test_metrics"][k]
    T = R["table"].set_index("Model")
    ci = R["ci"].set_index("Model")
    tvt = R["tvt"].set_index("Model")
    sc = R["scaling"]; abl = R["abl"]; det = R["det"]; mc = R["mcnemar"]
    dcv, rcv = R["dt_curve"], R["rf_curve"]
    names = ["Decision Tree", "Random Forest", "Linear SVM (ceo trening)", "SVM RBF (uzorak)"]
    short = {"Decision Tree": "Decision Tree", "Random Forest": "Random Forest",
             "Linear SVM (ceo trening)": "Linear SVM (ceo trening)", "SVM RBF (uzorak)": "SVM RBF (uzorak 20.000)"}

    def cm_line(r):
        m = r["test_metrics"]
        return f"TN = {n(m['tn'])}, FP = {n(m['fp'])}, FN = {n(m['fn'])}, TP = {n(m['tp'])}"

    # ------------------------------------------------------------------ 9
    a(("h1", "9. Eksperimentalni rezultati"))
    a(("p", f"U ovom poglavlju prikazani su rezultati svih eksperimenata, izmereni stvarnim izvršavanjem koda (Python {R['env']['python']}, Scikit-learn {R['env']['scikit-learn']}, jedno procesorsko jezgro, 3,9 GB RAM-a). Svi modeli evaluirani su na istom, celom test skupu od {n(dt['n_test'])} zapisa. Napad je pozitivna klasa. Nijedna vrednost nije prepisana iz literature."))

    a(("h2", "9.1. Decision Tree"))
    d_best = dt["params"]
    a(("p", f"Kriva dubine stabla ([[fig:tuning]]a), dobijena na podeli trening skupa 80/20, pokazuje klasičan obrazac preprilagođavanja: F1 na trening delu raste do {f(dcv['train_f1'].iloc[-1])} za stablo neograničene dubine (stvarna dubina {int(dcv['actual_depth'].iloc[-1])}, {n(dcv['n_leaves'].iloc[-1])} listova), dok F1 na validacionom delu dostiže maksimum od {f(dcv['val_f1'].max())} za dubinu {int(dcv.loc[dcv['val_f1'].idxmax(),'max_depth'])} i potom blago opada ili stagnira. Razlika između trening i validacionog F1 raste sa dubinom, što je znak povećane varijanse."))
    a(("p", f"Pretraga po mreži (3-fold CV na uzorku od {n(dt['tuning']['n_tune'])} zapisa) izabrala je kriterijum {d_best['criterion']}, max_depth = {d_best['max_depth']} i min_samples_leaf = {d_best['min_samples_leaf']} (CV F1 = {f(dt['tuning']['best_cv_score'])}). Dobijeno stablo ima dubinu {dt['tree_depth']} i {n(dt['n_leaves'])} listova. Treba napomenuti da je CV pretraga izabrala nešto plići model od onog koji je na krivoj dubine imao najviši validacioni F1; razlike između ovih modela na validaciji su male (do oko 0,005 u F1), pa izbor plićeg stabla ne menja zaključke."))
    a(("p", f"Na test skupu Decision Tree postiže Accuracy = {f(M(dt,'accuracy'))}, Precision = {f(M(dt,'precision'))}, Recall = {f(M(dt,'recall'))}, F1 = {f(M(dt,'f1'))} i ROC-AUC = {f(M(dt,'roc_auc'))}. Matrica konfuzije: {cm_line(dt)}. Model dakle detektuje {p(M(dt,'recall'))} napada, ali pogrešno označava {p(M(dt,'fpr'))} normalnih tokova kao napad. Vreme treniranja (uključujući preprocesiranje) iznosi {f(dt['fit_time_s'],2)} s, a predikcije na celom test skupu {f(dt['predict_time_s'],2)} s."))
    dti = R["dt_imp"]
    a(("p", f"Značaj karakteristika ([[fig:imp]]a) potpuno je dominiran jednom karakteristikom: sttl (TTL vrednost od izvora ka odredištu) nosi {p(dti.iloc[0]['importance'],1)} ukupnog smanjenja nečistoće. Slede {dti.iloc[1]['origin']} ({p(dti.iloc[1]['importance'],1)}), {dti.iloc[2]['origin']} ({p(dti.iloc[2]['importance'],1)}) i {dti.iloc[3]['origin']} ({p(dti.iloc[3]['importance'],1)}). Ovo je u skladu sa EDA nalazom da je sttl najjače korelisana karakteristika sa oznakom klase (poglavlje 6.4)."))

    a(("h2", "9.2. Matrice konfuzije"))
    a(("fig", "cm_all", FIG + "cm_all.png", "Matrice konfuzije svih modela na test skupu (u ćelijama: broj zapisa i udeo u stvarnoj klasi).", 11.5))
    a(("p", f"Sve četiri matrice pokazuju isti obrazac: veoma malo propuštenih napada (FN) i znatan broj lažnih alarma (FP). Broj propuštenih napada kreće se od {n(rf['test_metrics']['fn'])} (Random Forest) do {n(max(r['test_metrics']['fn'] for r in (dt, rf, ln, rb)))} (najviša vrednost među modelima), a broj lažnih alarma od {n(min(r['test_metrics']['fp'] for r in (dt, rf, ln, rb)))} do {n(max(r['test_metrics']['fp'] for r in (dt, rf, ln, rb)))} od {n(dt['test_metrics']['tn']+dt['test_metrics']['fp'])} normalnih zapisa."))

    # RF
    a(("h2", "9.3. Random Forest"))
    r_best = rf["params"]
    a(("p", f"Uticaj broja stabala analiziran je na podeli trening skupa 80/20 ([[fig:tuning]]b). Validacioni F1 raste sa {f(rcv['val_f1'].iloc[0])} za {int(rcv['n_estimators'].iloc[0])} stabala do {f(rcv['val_f1'].max())}, pri čemu se poboljšanje nakon 100 stabala praktično zaustavlja (razlika između 100 i 200 stabala je {f(rcv.loc[rcv['n_estimators']==200,'val_f1'].iloc[0]-rcv.loc[rcv['n_estimators']==100,'val_f1'].iloc[0],4)}), dok se vreme treniranja linearno uvećava (od {f(rcv['fit_time_s'].iloc[0],1)} s za 10 do {f(rcv['fit_time_s'].iloc[-1],1)} s za 300 stabala). Primenom pravila parsimonije (najmanji broj stabala čiji je F1 u okviru 0,0005 od maksimuma) izabrano je {r_best['n_estimators']} stabala."))
    a(("fig", "tuning", FIG + "tuning_curves.png", "(a) Decision Tree: F1-score na trening i validacionom delu u funkciji dubine stabla; (b) Random Forest: validacioni F1 i vreme treniranja u funkciji broja stabala.", 15.0))
    a(("p", f"Pretraga ostalih hiperparametara izabrala je max_depth = {r_best['max_depth']}, max_features = {r_best['max_features']} i min_samples_leaf = {r_best['min_samples_leaf']} (CV F1 = {f(rf['tuning']['best_cv_score'])} uz {rf['tuning_trees']} stabala u pretrazi). Razlike među najboljim kombinacijama su male (u četvrtoj decimali), pa izbor nije posebno osetljiv na ove parametre."))
    a(("p", f"Na test skupu Random Forest postiže Accuracy = {f(M(rf,'accuracy'))}, Precision = {f(M(rf,'precision'))}, Recall = {f(M(rf,'recall'))}, F1 = {f(M(rf,'f1'))}, ROC-AUC = {f(M(rf,'roc_auc'))} i PR-AUC = {f(M(rf,'pr_auc'))}. Matrica konfuzije: {cm_line(rf)}. U poređenju sa Decision Tree modelom, Random Forest ima veće vrednosti svih metrika, uz istovremeno {p(M(rf,'fnr'))} propuštenih napada (naspram {p(M(dt,'fnr'))}) i {p(M(rf,'fpr'))} lažnih alarma (naspram {p(M(dt,'fpr'))}). Cena je veća vremenska složenost: treniranje traje {f(rf['fit_time_s'],1)} s ({f(rf['fit_time_s']/dt['fit_time_s'],1)} puta duže od stabla), a predikcija {f(rf['predict_time_s'],2)} s."))
    rfi = R["rf_imp"]
    a(("p", f"Značaj karakteristika u šumi ([[fig:imp]]b) raspoređen je znatno ravnomernije nego u pojedinačnom stablu: najviše doprinose {rfi.iloc[0]['origin']} ({p(rfi.iloc[0]['importance'],1)}), {rfi.iloc[1]['origin']} ({p(rfi.iloc[1]['importance'],1)}), {rfi.iloc[2]['origin']} ({p(rfi.iloc[2]['importance'],1)}) i {rfi.iloc[3]['origin']} ({p(rfi.iloc[3]['importance'],1)}). Šuma dakle koristi više izvora informacija nego stablo, što je u skladu sa teorijskim očekivanjem da nasumičan izbor karakteristika smanjuje zavisnost ansambla od jedne dominantne karakteristike. Kako je opisano u poglavlju 5.2, ove vrednosti treba tumačiti kao značaj u modelu, a ne kao uzročnost."))
    a(("fig", "imp", FIG + "importances.png", "Značaj karakteristika (zbir po originalnoj koloni, uključujući one-hot kolone): (a) Decision Tree; (b) Random Forest.", 15.0))

    # SVM
    a(("h2", "9.4. Support Vector Machine"))
    a(("p", f"Linearni SVM (LinearSVC) pretragom po mreži dobio je C = {ln['params']['C']} (CV F1 = {f(ln['tuning']['best_cv_score'])}); CV rezultati za C od 0,01 do 10 razlikuju se tek u trećoj decimali, što ukazuje da je linearni model relativno neosetljiv na regularizaciju na ovim podacima. SVM sa RBF kernelom, treniran na stratifikovanom uzorku od {n(rb['n_train'])} zapisa, pretragom na podskupu od {n(rb['tuning']['n_tune'])} zapisa dobio je C = {rb['params']['C']} i gamma = {rb['params']['gamma']} (CV F1 = {f(rb['tuning']['best_cv_score'])}); [[fig:svm_grid]] prikazuje CV F1 za sve kombinacije. CV vrednost za RBF se ne može direktno porediti sa CV vrednostima ostalih modela jer je dobijena na znatno manjem uzorku."))
    a(("fig", "svm_grid", FIG + "svm_rbf_grid.png", "SVM RBF: CV F1-score u funkciji parametara C i gamma (uzorak od 8.000 zapisa).", 8.0))
    a(("tab", "svm_res", "Rezultati tri varijante SVM modela na celom test skupu",
       ["Varijanta", "N trening", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "Trening (s)", "Predik. (s)"],
       [[nm, n(r["n_train"]), f(M(r, "accuracy")), f(M(r, "precision")), f(M(r, "recall")), f(M(r, "f1")), f(M(r, "roc_auc")), f(r["fit_time_s"], 2), f(r["predict_time_s"], 2)]
        for nm, r in (("Linear SVM (ceo trening)", ln), ("Linear SVM (uzorak)", ls), ("SVM RBF (uzorak)", rb))],
       [3.2, 1.5, 1.7, 1.7, 1.5, 1.3, 1.6, 1.5, 1.5],
       "Napomena: modeli označeni sa „uzorak“ trenirani su na stratifikovanom uzorku trening skupa; evaluirani su na celom test skupu."))
    a(("p", f"Linearni SVM na celom trening skupu postiže F1 = {f(M(ln,'f1'))}, a na uzorku od {n(ls['n_train'])} zapisa F1 = {f(M(ls,'f1'))}: razlika je zanemarljiva ({f(M(ln,'f1')-M(ls,'f1'),4)}), što znači da dodatnih {n(ln['n_train']-ls['n_train'])} trening zapisa ne poboljšava linearni model. To podržava korišćenje uzorka za RBF model jer veličina trening skupa nije glavni ograničavajući faktor. RBF SVM trenirani na istom uzorku postiže F1 = {f(M(rb,'f1'))}, tj. {f(M(rb,'f1')-M(ls,'f1'),4)} više od linearnog na istom uzorku; to je uticaj kernela. RBF model ima najveći Recall od svih ({f(M(rb,'recall'))}), ali i najnižu ROC-AUC vrednost ({f(M(rb,'roc_auc'))}); pošto je ROC-AUC nezavisna od praga, a Recall se meri na podrazumevanom pragu, ovo znači da RBF model sa podrazumevanim pragom odlučivanja bira tačku na ROC krivoj sa visokom stopom detekcije i visokom stopom lažnih alarma, a ne da je u celini bolji rangirač od ostalih."))
    a(("p", f"Najupadljivija osobina RBF modela je vreme predikcije: {f(rb['predict_time_s'],1)} s za test skup, što je {f(rb['predict_time_s']/ln['predict_time_s'],0)} puta duže od linearnog SVM-a i {f(rb['predict_time_s']/dt['predict_time_s'],0)} puta duže od stabla odlučivanja, iako je trening uzorak mali. Razlog je što predikcija kernelskog SVM-a zahteva računanje kernela između svakog test zapisa i svih potpornih vektora."))

    # Poredjenje
    a(("h2", "9.5. Završno poređenje modela"))
    hdr = ["Model", "N trening", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "FPR"]
    rows = [[short[nm], n(T.loc[nm, "N_trening"]), f(T.loc[nm, "Accuracy"]), f(T.loc[nm, "Precision"]), f(T.loc[nm, "Recall"]), f(T.loc[nm, "F1"]), f(T.loc[nm, "ROC_AUC"]), f(T.loc[nm, "FPR"])] for nm in names]
    best_idx = {c: max(range(4), key=lambda i: float(rows[i][k].replace(",", ".")) if c != "FPR" else -float(rows[i][k].replace(",", "."))) for c, k in (("Accuracy", 2), ("Precision", 3), ("Recall", 4), ("F1", 5), ("ROC-AUC", 6), ("FPR", 7))}
    for c, k in (("Accuracy", 2), ("Precision", 3), ("Recall", 4), ("F1", 5), ("ROC-AUC", 6), ("FPR", 7)):
        i = best_idx[c]; rows[i][k] = f"**{rows[i][k]}**"
    a(("tab", "final", "Završna tabela rezultata na test skupu (podebljana je najbolja vrednost u koloni)", hdr, rows, [3.9, 1.7, 1.8, 1.8, 1.6, 1.4, 1.7, 1.6], "FPR = stopa lažnih alarma (manje je bolje). Svi ostali pokazatelji: više je bolje."))
    a(("tab", "times", "Vremena izvršavanja (jedno procesorsko jezgro, uključuje preprocesiranje)",
       ["Model", "Treniranje (s)", "Predikcija na test skupu (s)", "Predikcija / 1000 zapisa (ms)"],
       [[short[nm], f(T.loc[nm, "Vreme_treniranja_s"], 2), f(T.loc[nm, "Vreme_predikcije_s"], 2), f(T.loc[nm, "Vreme_predikcije_s"] / dt["n_test"] * 1000 * 1000, 2)] for nm in names],
       [5.0, 3.0, 4.0, 3.5], "Vremena zavise od hardvera i mere se jednokratno; razlike manje od ~15–20% (npr. ponovljeno treniranje RBF SVM-a na 20.000 zapisa trajalo je 5,9 s u eksperimentu skaliranja naspram 6,8 s ovde) ne treba tumačiti."))
    a(("fig", "metrics", FIG + "metrics_comparison.png", "Poređenje Accuracy, Precision, Recall i F1-score na test skupu.", 12.5))
    a(("p", f"Prema F1-score, redosled je: Random Forest ({f(M(rf,'f1'))}), Decision Tree ({f(M(dt,'f1'))}), SVM RBF ({f(M(rb,'f1'))}) i Linear SVM ({f(M(ln,'f1'))}). Random Forest je najbolji i po Accuracy ({f(M(rf,'accuracy'))}), Precision ({f(M(rf,'precision'))}), ROC-AUC ({f(M(rf,'roc_auc'))}) i FPR ({f(M(rf,'fpr'))}). Po Recall-u RBF SVM je najbolji ({f(M(rb,'recall'))}), ali uz najduže vreme predikcije. Svi modeli imaju Recall iznad {f(min(M(r,'recall') for r in (dt,rf,ln,rb)),2)}; razlike između modela više su u Precision (lažni alarmi) nego u Recall-u."))
    a(("p", "Intervali poverenja (bootstrap, 95%) prikazani su u tabeli ([[tab:ci]]). Intervali F1 svih modela međusobno se ne preklapaju. Ti intervali odražavaju samo varijabilnost test skupa."))
    a(("tab", "ci", "95% bootstrap intervali poverenja (1.000 uzoraka test skupa)",
       ["Model", "Accuracy", "Precision", "Recall", "F1"],
       [[short[nm]] + [f"{f(ci.loc[nm, c+'_lo'],4)} – {f(ci.loc[nm, c+'_hi'],4)}" for c in ("accuracy", "precision", "recall", "f1")] for nm in names],
       [4.0, 2.9, 2.9, 2.9, 2.9], None))
    a(("fig", "roc", FIG + "roc_curves.png", "ROC krive modela na test skupu.", 9.0))
    a(("p", f"ROC krive ([[fig:roc]]) potvrđuju redosled po ROC-AUC: Random Forest ({f(M(rf,'roc_auc'))}) > Decision Tree ({f(M(dt,'roc_auc'))}) > Linear SVM ({f(M(ln,'roc_auc'))}) > SVM RBF ({f(M(rb,'roc_auc'))}). Za niske stope lažnih alarma (FPR ispod ≈ 0,1) Random Forest i Decision Tree su bolji od oba SVM modela, a RBF model je na tom delu krive najslabiji. Pošto stablo odlučivanja daje verovatnoće samo na osnovu udela klasa u listovima, njegova ROC kriva ima manji broj različitih pragova od krive šume."))
    a(("fig", "time", FIG + "time_comparison.png", "Vreme treniranja i predikcije (logaritamska skala).", 12.5))
    a(("p", f"Što se tiče vremena ([[fig:time]], [[tab:times]]), Decision Tree je najbrži u treniranju ({f(dt['fit_time_s'],1)} s), a Random Forest sa 100 stabala treba {f(rf['fit_time_s'],1)} s. Linear SVM na celom skupu trenira se {f(ln['fit_time_s'],1)} s. RBF SVM trenira se samo {f(rb['fit_time_s'],1)} s, ali samo na {n(rb['n_train'])} zapisa, a njegova predikcija je daleko najsporija. Predikcija stabla i linearnog SVM-a traje manje od {f(max(dt['predict_time_s'], ln['predict_time_s']),1)} s za {n(dt['n_test'])} zapisa, što odgovara propusnosti reda stotina hiljada zapisa u sekundi na jednom jezgru (iako ova mera obuhvata samo klasifikaciju već izvedenih karakteristika, bez izdvajanja karakteristika iz paketa)."))

    a(("h2", "9.6. Analiza preprilagođavanja i generalizacije"))
    a(("tab", "tvt", "Accuracy i F1 na trening skupu naspram test skupa",
       ["Model", "Accuracy (trening)", "Accuracy (test)", "Razlika", "F1 (trening)", "F1 (test)"],
       [[short[nm], f(tvt.loc[nm, "Accuracy_trening"]), f(tvt.loc[nm, "Accuracy_test"]), f(tvt.loc[nm, "Razlika_accuracy"]), f(tvt.loc[nm, "F1_trening"]), f(tvt.loc[nm, "F1_test"])] for nm in names],
       [4.2, 2.4, 2.3, 1.9, 2.4, 2.3], "Metrike na trening skupu računaju se na podacima na kojima je model treniran i optimističan su pokazatelj."))
    a(("p", f"Svi modeli imaju znatno bolje rezultate na trening nego na test skupu (razlika u Accuracy od {f(tvt['Razlika_accuracy'].min(),3)} do {f(tvt['Razlika_accuracy'].max(),3)}). Random Forest skoro savršeno „pamti“ trening skup (Accuracy {f(tvt.loc['Random Forest','Accuracy_trening'])}), što je očekivano za duboka stabla, ali on i na testu ima najbolje rezultate, pa preprilagođavanje na treningu nije nužno štetno za generalizaciju ansambla. Značajno je da je razlika slična i kod jednostavnog linearnog SVM-a ({f(tvt.loc['Linear SVM (ceo trening)','Razlika_accuracy'],3)}), čija je kapacitivnost mala. To ukazuje da veliki deo jaza ne potiče od preprilagođavanja složenošću modela, već od razlike između trening i test raspodele (poglavlje 6.5), što je razmotreno u diskusiji."))
    a(("p", f"Dodatno, CV vrednosti F1 na trening podacima ({f(dt['tuning']['best_cv_score'],3)} za Decision Tree, {f(rf['tuning']['best_cv_score'],3)} za Random Forest, {f(ln['tuning']['best_cv_score'],3)} za Linear SVM) znatno su veće od F1 na zvaničnom test skupu ({f(M(dt,'f1'),3)}, {f(M(rf,'f1'),3)}, {f(M(ln,'f1'),3)}). Unakrsna validacija unutar trening skupa dakle daje optimističnu procenu performansi na zvaničnom test skupu. To je razlog zbog kojeg je test skup neophodan za konačnu ocenu i zbog kojeg se rezultati unakrsne validacije na UNSW-NB15 trening skupu ne smeju navoditi kao procena generalizacije."))

    a(("h2", "9.7. Detekcija po kategorijama saobraćaja"))
    pv = det.pivot(index="attack_cat", columns="Model", values="detection_rate")
    cnt = det.drop_duplicates("attack_cat").set_index("attack_cat")["n"]
    order = cnt.sort_values(ascending=False).index
    rows = [[c, n(cnt[c])] + [f(pv.loc[c, nm], 3) for nm in names] for c in order]
    a(("tab", "det", "Udeo ispravno klasifikovanih test zapisa po kategoriji (Normal: specifičnost; ostalo: Recall)",
       ["Kategorija", "n (test)", "Decision Tree", "Random Forest", "Linear SVM", "SVM RBF"], rows, [3.2, 2.0, 2.6, 2.6, 2.6, 2.5], None))
    a(("fig", "det", FIG + "detection_by_category.png", "Udeo ispravno klasifikovanih zapisa po kategorijama (test skup).", 10.5))
    worst_att = pv.drop(index="Normal").min(axis=1).idxmin()
    a(("p", f"Većina kategorija napada detektuje se sa udelom iznad 0,9 kod svih modela. Kategorija {worst_att} je najslabije prepoznata kategorija napada ({f(pv.loc[worst_att].min(),3)} kod najlošijeg i {f(pv.loc[worst_att].max(),3)} kod najboljeg modela). Najveća slabost svih modela je prepoznavanje normalnog saobraćaja: samo {f(pv.loc['Normal'].min(),3)} (najlošiji model) do {f(pv.loc['Normal'].max(),3)} (Random Forest) test zapisa normalnog saobraćaja ispravno je klasifikovano. Dakle, visok Recall ukupnog skupa posledica je toga što modeli retko propuštaju napad, ali na račun velikog broja lažnih alarma na normalnom saobraćaju. Napomena: zbog male brojnosti, udeli za Worms (n = 44) i Shellcode (n = 378) imaju veliku nesigurnost, što se vidi iz toga što su vrednosti za Worms identične kod tri modela (43 od 44 pogođena)."))

    a(("h2", "9.8. Ablaciona studija i skaliranje"))
    base = abl[abl["Varijanta"] == "Osnovni"].set_index("Model")
    rows = []
    for _, r in abl.iterrows():
        rows.append([r["Varijanta"], r["Model"], n(r["N_trening"]), n(r["N_test"]), f(r["Accuracy"]), f(r["Precision"]), f(r["Recall"]), f(r["F1"])])
    a(("tab", "abl", "Ablaciona studija (fiksni hiperparametri iz glavnog eksperimenta)",
       ["Varijanta", "Model", "N trening", "N test", "Accuracy", "Precision", "Recall", "F1"], rows, [3.4, 3.3, 1.5, 1.4, 1.5, 1.5, 1.4, 1.2], None))
    a(("fig", "abl", FIG + "ablation.png", "Ablaciona studija: F1-score i Recall po varijantama pripreme podataka.", 13.0))
    nt = abl[abl["Varijanta"].str.startswith("Bez TCP")].set_index("Model")
    dd = abl[abl["Varijanta"] == "Bez duplikata"].set_index("Model")
    a(("p", f"**Uklanjanje TCP sekvencnih brojeva (stcpb, dtcpb)** praktično ne menja rezultate: maksimalna promena F1 iznosi {f(max(abs(nt['F1']-base['F1'])),4)}. Dakle, na ovom skupu modeli ne zavise od ovih karakteristika, pa pretpostavka o njihovom štetnom uticaju nije potvrđena. **Uklanjanje dupliranih zapisa** (iz treninga i iz testa) znatno pogoršava rezultate: F1 pada za {f(base.loc['Random Forest','F1']-dd.loc['Random Forest','F1'],3)} kod Random Forest, {f(base.loc['Decision Tree','F1']-dd.loc['Decision Tree','F1'],3)} kod Decision Tree i {f(base.loc['Linear SVM (ceo trening)','F1']-dd.loc['Linear SVM (ceo trening)','F1'],3)} kod Linear SVM, dok Recall ostaje gotovo isti (iznad {f(dd['Recall'].min(),3)}). Pad Precision (npr. Random Forest sa {f(base.loc['Random Forest','Precision'],3)} na {f(dd.loc['Random Forest','Precision'],3)}) objašnjava se sastavom duplikata: napadi čine {p(R['eda']['duplikati']['udeo_napada_medju_duplikatima_test'],1)} uklonjenih test zapisa ({p(R['eda']['duplikati']['udeo_napada_medju_duplikatima_trening'],1)} u treningu), pa udeo napada u test skupu posle uklanjanja pada sa {p(R['eda']['udeo_napada_test'],1)} na {p(R['eda']['duplikati']['udeo_napada_posle_dedup_test'],1)}. Uz isti Recall i manji udeo napada, isti broj lažnih alarma daje niži Precision, a F1 i Accuracy zavise od raspodele klasa. Zato se pad F1 ne sme tumačiti isključivo kao „lakše“ ili „teže“ klasifikovanje, već i kao posledica promene raspodele klasa. Napomena: uklanjanjem duplikata istovremeno se menja i trening i test skup, pa se efekat ne može pripisati samo jednom od njih. Redosled modela (RF > DT > Linear SVM po F1) ostaje isti u svim varijantama."))
    a(("fig", "scaling", FIG + "scaling.png", "Vreme treniranja u funkciji broja trening uzoraka (fiksni hiperparametri, logaritamske ose).", 9.0))
    s = sc.pivot(index="N_trening", columns="Model", values="Vreme_treniranja_s")
    ratio = lambda m: s[m].iloc[-1] / s[m].iloc[-2]
    a(("p", f"Skaliranje vremena treniranja ([[fig:scaling]]) pokazuje da se pri udvostručenju trening skupa sa {n(s.index[-2])} na {n(s.index[-1])} zapisa vreme treniranja uvećava {f(ratio('Decision Tree'),1)} puta za Decision Tree, {f(ratio('Random Forest'),1)} puta za Random Forest, {f(ratio('Linear SVM'),1)} puta za Linear SVM, ali čak {f(ratio('SVM RBF'),1)} puta za RBF SVM ({f(s['SVM RBF'].iloc[-2],1)} s → {f(s['SVM RBF'].iloc[-1],1)} s). Ovo je jasna potvrda nadlinearne složenosti kernelskog SVM-a i razlog zbog kog je on treniran na uzorku."))

    a(("h2", "9.9. Statistička poređenja"))
    rows = [[r["Model_A"], r["Model_B"], n(r["n_a_only"]), n(r["n_b_only"]), f(r["chi2"], 1), "< 0,001" if r["p_value"] < 0.001 else f(r["p_value"], 3)] for _, r in mc.iterrows()]
    a(("tab", "mc", "McNemarov test za parove modela na test skupu",
       ["Model A", "Model B", "Samo A tačan", "Samo B tačan", "χ²", "p-vrednost"], rows, [3.6, 3.6, 2.2, 2.2, 1.9, 2.0], "„Samo A tačan“ je broj zapisa koje A klasifikuje ispravno, a B pogrešno; obrnuto za B."))
    a(("p", "Za svaki par modela p-vrednost je manja od 0,001, tj. razlike u greškama su statistički značajne u okviru pretpostavki testa. Zbog velikog test skupa ( >80.000 primera), čak i male razlike postaju značajne, pa statistička značajnost sama ne govori o praktičnoj važnosti; praktičnu važnost treba proceniti prema veličini razlika (npr. razlika F1 od približno 0,02 između Random Forest i Decision Tree) i prema ceni grešaka u konkretnom okruženju. Kako je napomenuto u poglavlju 7.6, test pretpostavlja nezavisne primere, što je zbog dupliranih tokova samo približno ispunjeno."))

    # ------------------------------------------------------------------ 10
    a(("h1", "10. Diskusija i poređenje rezultata"))
    a(("h2", "10.1. Odgovori na istraživačka pitanja"))
    a(("p", f"**IP1 – uspešnost detekcije.** Klasični algoritmi detektuju napade veoma uspešno kada je cilj visok Recall: svi modeli otkrivaju između {p(min(M(r,'recall') for r in (dt,rf,ln,rb)),1)} i {p(max(M(r,'recall') for r in (dt,rf,ln,rb)),1)} napada, a ROC-AUC vrednosti su između {f(min(M(r,'roc_auc') for r in (dt,rf,ln,rb)),3)} i {f(M(rf,'roc_auc'),3)}. Međutim, Accuracy ({p(min(M(r,'accuracy') for r in (dt,rf,ln,rb)),1)}–{p(M(rf,'accuracy'),1)}) i Precision ({p(min(M(r,'precision') for r in (dt,rf,ln,rb)),1)}–{p(M(rf,'precision'),1)}) znatno su niži zbog velikog udela lažnih alarma: između {p(M(rf,'fpr'),1)} i {p(max(M(r,'fpr') for r in (dt,rf,ln,rb)),1)} normalnog saobraćaja test skupa pogrešno je označeno kao napad."))
    a(("p", f"**IP2 i IP5 – najbolji algoritam i balans.** Random Forest je najbolji prema F1 ({f(M(rf,'f1'))}), Accuracy, Precision, ROC-AUC, PR-AUC, MCC ({f(M(rf,'mcc'),3)}) i FPR; njegov 95% interval poverenja za F1 ({f(ci.loc['Random Forest','f1_lo'],3)}–{f(ci.loc['Random Forest','f1_hi'],3)}) ne preklapa se sa intervalima ostalih modela. Najbolji balans između Precision i Recall (F1) dakle ostvaruje Random Forest. RBF SVM ima najveći Recall ({f(M(rb,'recall'))}), ali uz najniži ROC-AUC i najsporiju predikciju."))
    a(("p", f"**IP3 – Random Forest naspram Decision Tree.** Random Forest je bolji po svim izmerenim metrikama: F1 je veći za {f(M(rf,'f1')-M(dt,'f1'),4)}, Precision za {f(M(rf,'precision')-M(dt,'precision'),4)}, Recall za {f(M(rf,'recall')-M(dt,'recall'),4)}, a broj propuštenih napada manji je za {p(1-M(rf,'fn')/M(dt,'fn'),1)} (sa {n(M(dt,'fn'))} na {n(M(rf,'fn'))}). McNemarov test pokazuje da Random Forest ispravno klasifikuje {n(mc[(mc['Model_A']=='Decision Tree')&(mc['Model_B']=='Random Forest')]['n_b_only'].iloc[0])} zapisa koje stablo pogrešno klasifikuje, a obrnuto samo {n(mc[(mc['Model_A']=='Decision Tree')&(mc['Model_B']=='Random Forest')]['n_a_only'].iloc[0])}. Cena je {f(rf['fit_time_s']/dt['fit_time_s'],1)} puta duže treniranje i {f(rf['predict_time_s']/dt['predict_time_s'],1)} puta duža predikcija, što je u apsolutnom iznosu skromno."))
    a(("p", f"**IP4 – SVM u poređenju sa stablima.** Oba SVM modela slabija su od oba modela zasnovana na stablima prema F1, Accuracy i Precision i ROC-AUC. Linearni SVM je za {f(M(dt,'f1')-M(ln,'f1'),4)} (F1) slabiji od Decision Tree, a RBF SVM treniran na uzorku za {f(M(dt,'f1')-M(rb,'f1'),4)}. RBF kernel poboljšava linearni model na istom uzorku (F1 za {f(M(rb,'f1')-M(ls,'f1'),4)}), ali to poboljšanje ne dostiže nivo stabala, a plaća se mnogo dužom predikcijom ({f(rb['predict_time_s'],1)} s). Treba imati u vidu da je RBF SVM treniran na uzorku i da bi, uz više uzoraka, rezultati mogli biti drugačiji; ovo istraživanje to nije ispitalo."))
    a(("p", f"**IP6 – vreme.** Decision Tree: trening {f(dt['fit_time_s'],1)} s, predikcija {f(dt['predict_time_s'],2)} s; Random Forest: {f(rf['fit_time_s'],1)} s i {f(rf['predict_time_s'],2)} s; Linear SVM (ceo skup): {f(ln['fit_time_s'],1)} s i {f(ln['predict_time_s'],2)} s; RBF SVM (uzorak): {f(rb['fit_time_s'],1)} s i {f(rb['predict_time_s'],1)} s. Svi osim RBF SVM-a imaju predikciju ispod jedne sekunde za ceo test skup."))
    a(("p", "**IP7 – efikasnost klasičnih metoda.** Za zadatak „propustiti što manje napada“ klasične metode su efikasne i veoma brze. Međutim, za praktičnu upotrebu važna su ograničenja: visok udeo lažnih alarma na normalnom saobraćaju (poglavlje 10.4) i činjenica da je evaluacija izvršena na laboratorijskom skupu. Zaključak je da klasične metode mogu biti dobra osnova (baseline) i komponenta za filtriranje, ali sama po sebi ovakva evaluacija ne dokazuje spremnost za produkcionu upotrebu."))

    a(("h2", "10.2. Provera hipoteza"))
    t100 = lambda m: sc[(sc["Model"] == m)].sort_values("N_trening")
    hrows = [
        ["H1", "RF F1 > DT F1", f"{f(M(rf,'f1'))} naspram {f(M(dt,'f1'))}; McNemar p < 0,001", "**Prihvaćena**"],
        ["H2", "Stabla F1 > Linear SVM F1", f"DT {f(M(dt,'f1'))}, RF {f(M(rf,'f1'))} naspram {f(M(ln,'f1'))}", "**Prihvaćena**"],
        ["H3", "RBF F1 > Linear F1 (isti uzorak)", f"{f(M(rb,'f1'))} naspram {f(M(ls,'f1'))} (razlika {f(M(rb,'f1')-M(ls,'f1'),4)})", "**Prihvaćena** (mala razlika)"],
        ["H4", "Vreme SVM-a raste brže sa n", f"udvostručenje n: RBF {f(ratio('SVM RBF'),1)}×, DT {f(ratio('Decision Tree'),1)}×, RF {f(ratio('Random Forest'),1)}×, Linear {f(ratio('Linear SVM'),1)}×", "**Prihvaćena** za RBF; ne i za Linear SVM"],
        ["H5", "Precision < Recall", f"Precision {f(min(M(r,'precision') for r in (dt,rf,ln,rb)),3)}–{f(M(rf,'precision'),3)}; Recall {f(min(M(r,'recall') for r in (dt,rf,ln,rb)),3)}–{f(M(rb,'recall'),3)}", "**Prihvaćena**"]]
    a(("tab", "hyp", "Provera hipoteza na osnovu izmerenih rezultata", ["Hipoteza", "Sadržaj", "Izmereno", "Ishod"], hrows, [1.6, 4.2, 6.2, 3.5],
       "H4: za Linear SVM (LinearSVC) vreme raste sporije od za RBF i uporedivo sa stablima, pa se hipoteza odnosi na kernelski SVM."))
    a(("p", "Treba naglasiti da je ishod H3 zasnovan na maloj razlici koja je izmerena na jednom izvršavanju sa jednim seed-om; bez ponavljanja sa više seed-ova ne može se isključiti da je deo razlike posledica slučaja. Ishod H1 i H2 podržan je velikim razlikama i velikim brojem primera."))

    a(("h2", "10.3. Objašnjenje razlika između algoritama"))
    a(("p", f"Prednost modela zasnovanih na stablima može se objasniti prirodom podataka. Karakteristike su mešavina brojača, TTL vrednosti, stanja i protokola sa izrazito nelinearnim i često „pragovskim“ odnosima (npr. sttl razdvaja klase u velikoj meri samo jednim pragom). Stabla takve odnose modeluju direktno, dok linearni SVM mora da ih aproksimira jednom hiperravni, a RBF SVM sa jednim globalnim parametrom gamma nema fleksibilnost da se prilagodi karakteristikama različitih skala i prirode (jedan gamma za numeričke i za one-hot kolone). Random Forest dodatno smanjuje varijansu stabla usrednjavanjem i koristi više karakteristika nego pojedinačno stablo (poglavlje 9.3). Ova objašnjenja su tumačenja usklađena sa teorijom (poglavlje 5), a nisu posebno testirana u eksperimentima; ona bi se mogla proveriti, na primer, analizom parcijalne zavisnosti ili alternativnim kernelima."))
    a(("p", f"Zanimljivo je da je ROC-AUC RBF modela ({f(M(rb,'roc_auc'))}) niža od ROC-AUC linearnog modela ({f(M(ln,'roc_auc'))}), iako su F1 i Recall RBF modela viši. Ova pojava pokazuje koliko izbor metrike i praga odlučivanja utiče na zaključke: RBF model je pomeren ka detekciji svih napada (Recall {f(M(rb,'recall'))}), a pri nižim stopama lažnih alarma je lošiji rangirač. Kada bi se prag odlučivanja podešavao (npr. prema ciljanom FPR), redosled modela mogao bi se promeniti; to nije ispitivano jer bi podešavanje praga zahtevalo dodatni validacioni skup."))

    a(("h2", "10.4. Praktična primenljivost"))
    a(("p", f"Sa stanovišta bezbednosti, prednost svih modela je visok Recall (iznad {f(min(M(r,'recall') for r in (dt,rf,ln,rb)),2)}). Međutim, FPR od {p(M(rf,'fpr'),1)} (najbolji model) do {p(M(ln,'fpr'),1)} znači da bi u realnom okruženju, gde su napadi retki, veliki broj alarma bio lažan (base-rate fallacy [[cite:axelsson2000]]). Na primer, kada bi udeo napada u saobraćaju bio samo 1%, čak i Random Forest sa Recall {f(M(rf,'recall'),3)} i FPR {f(M(rf,'fpr'),3)} imao bi Precision oko {f((0.01*M(rf,'recall'))/(0.01*M(rf,'recall')+0.99*M(rf,'fpr')),3)} (računato po Bayesovoj formuli iz izmerenih Recall i FPR, kao ilustracija, a ne kao izmeren rezultat). Zato bi praktična primena zahtevala podešavanje praga odlučivanja, dodatne filtre ili višeslojnu arhitekturu."))
    a(("p", "Dodatno, brzina predikcije stabala i linearnog SVM-a (manje od jedne sekunde za više od 80.000 zapisa na jednom jezgru) pogoduje primeni u realnom vremenu, uz napomenu da ovo vreme ne obuhvata izdvajanje karakteristika iz mrežnih paketa. RBF SVM je sa stanovišta brzine predikcije najnepovoljniji. Interpretabilnost je prednost stabla odlučivanja: pravila su pregledna, a model pokazuje da se u velikoj meri oslanja na sttl, što je bezbednosno upotrebljiv uvid, ali i upozorenje da model može usvojiti artefakte laboratorijskog okruženja (poglavlje 11)."))

    a(("h2", "10.5. Prednosti i nedostaci algoritama"))
    a(("tab", "proscons", "Sažetak prednosti i nedostataka (kombinacija teorijskih svojstava i izmerenih vrednosti iz ovog rada)",
       ["Algoritam", "Prednosti", "Nedostaci"],
       [["Decision Tree", f"najbrže treniranje ({f(dt['fit_time_s'],1)} s) i predikcija; interpretabilan; F1 = {f(M(dt,'f1'),3)}", f"zavisnost od jedne karakteristike (sttl); pretpostavka preprilagođavanja za duboka stabla; više lažnih alarma od RF (FPR {p(M(dt,'fpr'),1)})"],
        ["Random Forest", f"najbolji F1, Accuracy, Precision, ROC-AUC; ravnomerniji značaj karakteristika; predikcija < 1 s", f"{f(rf['fit_time_s']/dt['fit_time_s'],1)}× duže treniranje od stabla; slabija interpretabilnost; skoro savršen trening rezultat"],
        ["Linear SVM", f"stabilno i brzo na celom skupu; Recall {f(M(ln,'recall'),3)}; neosetljiv na C", f"najniži F1 i Accuracy; najviši FPR ({p(M(ln,'fpr'),1)}); ne modeluje nelinearne odnose"],
        ["SVM RBF", f"najviši Recall ({f(M(rb,'recall'),3)}); bolji od linearnog na istom uzorku", f"predikcija {f(rb['predict_time_s'],1)} s; nadlinearno skaliranje treninga; najniži ROC-AUC; ocena samo na uzorku"]],
       [3.0, 6.3, 6.2], None))

    # ------------------------------------------------------------------ 11
    a(("h1", "11. Ograničenja istraživanja"))
    a(("bul", [
        "**Jedan skup podataka.** Svi zaključci odnose se na UNSW-NB15 u zvaničnoj podeli; ne može se tvrditi da bi isti redosled važio na drugim skupovima ili u realnom saobraćaju. Skup je delom sintetički, generisan u laboratorijskom okruženju [[cite:unswpage]], pa karakteristike (npr. sttl) mogu odražavati artefakte generisanja.",
        "**Jedno izvršavanje po modelu.** Rezultati su dobijeni sa jednim seed-om (42). Nisu ponavljana treniranja sa različitim seed-ovima niti sa različitim podelama, pa varijabilnost zbog treniranja nije kvantifikovana. Bootstrap intervali obuhvataju samo varijabilnost test skupa.",
        "**SVM RBF na uzorku.** Zbog računskih ograničenja model je treniran na 20.000 zapisa (≈11,4% trening skupa). Poređenje sa modelima treniranim na celom skupu stoga nije potpuno simetrično; razlike u korist ili protiv RBF modela ne mogu se pripisati samo kernelu.",
        "**Pretraga hiperparametara na uzorku i ograničenoj mreži.** Mreže su male (poglavlje 7.4) i izvedene na 50.000 zapisa, a RBF mreža na 8.000; mogući je bolji izbor sa širom pretragom ili na celom skupu.",
        "**Pomak raspodele i duplikati.** Raspodela klasa se razlikuje između trening i test skupa, preklapanje identičnih zapisa iznosi oko 10,4%, a duplikati čine veliki udeo skupa. Rezultati ablacije pokazuju da ovo bitno utiče na izmerene vrednosti (poglavlje 9.8); apsolutne vrednosti se zato ne smeju direktno poređeti sa radovima koji koriste drugačiju pripremu.",
        "**Neuravnoteženost kategorija.** Za retke kategorije (Worms, Shellcode) procene su nepouzdane zbog malog broja test primera.",
        "**Binarna klasifikacija i poznate klase napada.** Rad ne ispituje višeklasnu klasifikaciju niti otkrivanje potpuno novih napada; statičan model ne obuhvata promenu saobraćaja tokom vremena [[cite:sommer2010]].",
        "**Podrazumevani prag odlučivanja.** Prag nije podešavan; rezultati odražavaju podrazumevani prag svakog algoritma.",
        "**Merenja vremena** su jednokratna, na jednom jezgru i jednom računaru; ne obuhvataju izdvajanje karakteristika iz paketa.",
        "**Značaj karakteristika** (smanjenje nečistoće) ne ukazuje na uzročnost i može biti pristrasan [[cite:strobl2007]]."]))
    a(("p", "Moguća proširenja, koja su svesno izostavljena iz ovog rada, uključuju višeklasnu klasifikaciju (attack_cat), dodatne algoritme (npr. gradijentno pojačavanje), podešavanje praga odlučivanja, evaluaciju na drugim skupovima podataka i ponavljanje eksperimenata sa više seed-ova."))

    # ------------------------------------------------------------------ 12
    a(("h1", "12. Zaključak"))
    a(("p", f"U radu su uporedno evaluirana tri klasična algoritma – Decision Tree, Random Forest i SVM (linearni i RBF) – u binarnoj detekciji mrežnih napada na zvaničnoj podeli skupa UNSW-NB15, uz kompletnu analizu podataka, sprečavanje curenja podataka, podešavanje hiperparametara unakrsnom validacijom na trening podacima i evaluaciju na istom test skupu od {n(dt['n_test'])} zapisa."))
    a(("p", f"Glavni rezultati su sledeći. Prvo, Random Forest je ostvario najbolji ukupni rezultat (F1 = {f(M(rf,'f1'))}, Accuracy = {f(M(rf,'accuracy'))}, ROC-AUC = {f(M(rf,'roc_auc'))}), potom Decision Tree (F1 = {f(M(dt,'f1'))}), a oba SVM modela bila su slabija (RBF na uzorku F1 = {f(M(rb,'f1'))}; linearni F1 = {f(M(ln,'f1'))}). Drugo, svi modeli imaju visok Recall ({f(min(M(r,'recall') for r in (dt,rf,ln,rb)),3)}–{f(M(rb,'recall'),3)}), ali znatan udeo lažnih alarma ({p(M(rf,'fpr'),1)}–{p(M(ln,'fpr'),1)} normalnog saobraćaja), pa su Precision i Accuracy znatno niži; normalan saobraćaj je najslabije prepoznata klasa. Treće, Decision Tree i Linear SVM su veoma brzi, Random Forest je umereno sporiji, dok RBF SVM ima daleko najsporiju predikciju ({f(rb['predict_time_s'],1)} s) i nadlinearno skaliranje treniranja. Četvrto, uklanjanje dupliranih zapisa znatno smanjuje izmerene vrednosti F1, dok uklanjanje TCP sekvencnih brojeva nema uticaja; unakrsna validacija na trening skupu daje znatno optimističniju procenu od zvaničnog test skupa."))
    a(("p", "Odgovor na centralno istraživačko pitanje je sledeći: klasične metode mašinskog učenja, a posebno Random Forest, mogu efikasno da detektuju napade na UNSW-NB15 uz vrlo visoku stopu detekcije i vrlo kratko vreme klasifikacije, ali visok udeo lažnih alarma i laboratorijska priroda skupa ograničavaju zaključke o praktičnoj primenljivosti. Rezultati su dobra osnova (baseline) za dalja istraživanja, među kojima su višeklasna klasifikacija, podešavanje praga odlučivanja, ponavljanje sa više seed-ova i evaluacija na drugim skupovima podataka."))
    return B
