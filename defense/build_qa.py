"""Generise dokument sa pitanjima komisije i odgovorima (DOCX). Brojke se citaju iz rezultata."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reports"))
from docbuilder import Builder
from references import REFS
import pandas as pd

M = ROOT / "results" / "metrics"
J = lambda n: json.load(open(M / f"{n}.json", encoding="utf-8"))
dt, rf, ln, rb, ls = (J("decision_tree_binary"), J("random_forest_binary"), J("linear_svm_ceo_trening_binary"), J("svm_rbf_uzorak_binary"), J("linear_svm_uzorak_binary"))
eda = J("eda_summary"); sc = pd.read_csv(M / "scaling.csv"); abl = pd.read_csv(M / "ablation.csv")
f = lambda x, d=4: f"{x:.{d}f}".replace(".", ",")
pc = lambda x, d=1: f"{x*100:.{d}f}".replace(".", ",") + "%"
nf = lambda x: f"{int(x):,}".replace(",", ".")
m = lambda r, k: r["test_metrics"][k]
d = eda["duplikati"]
base = abl[abl.Varijanta == "Osnovni"].set_index("Model"); dd = abl[abl.Varijanta == "Bez duplikata"].set_index("Model")

QA = [
("Zašto ste izabrali UNSW-NB15, a ne KDD'99 ili NSL-KDD?",
 "KDD'99 potiče iz 1999. godine i ima dokumentovane nedostatke, pre svega veliki broj redundantnih zapisa koji favorizuje algoritme koji „pamte“ (Tavallaee i sar.). UNSW-NB15 sadrži savremenije napade i normalan saobraćaj, ima zvaničnu podelu na trening i test skup i često se koristi u literaturi. Treba priznati da ni on nije savršen: delom je sintetički, a naši rezultati o duplikatima pokazuju da i on ima slične probleme kao KDD'99 (67.601 duplikat u treningu)."),
("Zašto upravo Decision Tree, Random Forest i SVM?",
 "To su tri algoritma koje je predložio profesor i pokrivaju tri različita pristupa: jedno interpretabilno stablo, ansambl stabala i metodu zasnovanu na marginama. Svesno nisu uvođeni XGBoost, neuronske mreže ni duboko učenje, jer je istraživačko pitanje koliko su efikasne klasične metode; ostali algoritmi su navedeni kao buduće proširenje."),
("Zašto ste koristili zvaničnu podelu na trening i test, a ne nasumičnu?",
 "Zvanična podela omogućava poređenje sa drugim radovima i sprečava proizvoljnost (autor ne bira podelu koja mu odgovara). Posledica je da test skup ima drugačiju raspodelu klasa (55% napada naspram 68% u treningu), što je realnije od nasumične podele, ali i razlog zašto rezultati unakrsne validacije na treningu (F1 ≈ 0,96) nisu predviđanje test rezultata (F1 " + f(m(dt,'f1'),3) + "–" + f(m(rf,'f1'),3) + ")."),
("Šta je curenje podataka (data leakage) i kako ste ga sprečili?",
 "Curenje je situacija u kojoj informacija koja ne bi bila dostupna pri stvarnoj primeni utiče na treniranje ili izbor modela, što daje preoptimistične rezultate. Sprečeno je na četiri načina: (1) sve transformacije su u scikit-learn Pipeline-u i uče se samo na treningu; (2) u unakrsnoj validaciji Pipeline se uči iznova u svakom foldu; (3) test skup se ne koristi ni za izbor hiperparametara; (4) label i attack_cat nikada nisu ulazne karakteristike (funkcija get_xy). Preklapanje identičnih zapisa između trening i test skupa (" + pc(eda['preklapanje']['udeo_preklapanja']) + " test zapisa) nije curenje iz metodologije, već svojstvo zvanične podele, i transparentno je prikazano."),
("Zašto One-Hot kodiranje i šta znači handle_unknown=\"ignore\"?",
 "Kolone proto, service i state su nominalne; redno kodiranje bi nametnulo veštački redosled. One-Hot ga izbegava. Test skup sadrži vrednosti state (ACC, CLO) kojih nema u treningu; sa handle_unknown=\"ignore\" takvi zapisi dobijaju nule u tim kolonama, bez greške i bez „gledanja“ test skupa. Kodiranje posebno na trening i test skupu (npr. get_dummies) bi dalo različit broj kolona i bilo bi pogrešno."),
("Zašto log(1+x) i standardizacija, ako stablima to ne treba?",
 "Stablima nije potrebno jer monotone transformacije ne menjaju podele. SVM jeste osetljiv na skalu, a podaci imaju ekstremne vrednosti (npr. sload do ≈6·10⁹). Isto preprocesiranje je primenjeno na sva tri algoritma da bi razlike u rezultatima bile posledica algoritama, a ne pripreme. Kolone za log transformaciju biraju se na treningu (nenegativne sa asimetrijom > 2)."),
("Zašto je F1 kriterijum za izbor hiperparametara, a zašto je Recall važan?",
 "F1 je harmonijska sredina Precision i Recall i sprečava da se model optimizuje samo za jedno. Recall je u bezbednosti posebno važan jer propušten napad (FN) obično košta više od lažnog alarma. Zato je Recall izveštavan posebno: svi modeli imaju Recall između " + f(m(dt,'recall'),3) + " i " + f(m(rb,'recall'),3) + ". Ali sam Recall nije dovoljan, jer bi klasifikator koji sve proglasi napadom imao Recall 1; zato se prate Precision, FPR i F1."),
("Zašto Accuracy nije dovoljna metrika?",
 "Accuracy zavisi od raspodele klasa i ne pokazuje vrstu grešaka. U našem skupu udeo napada se razlikuje između trening (68%) i test skupa (55%), a posle uklanjanja duplikata pada na 39%. Dva modela sa istom Accuracy mogu imati sasvim različit odnos FN i FP. Zato se koriste matrica konfuzije, Precision, Recall, F1, FPR, MCC i ROC/PR-AUC."),
("Šta je ROC-AUC i zašto ste dodali PR-AUC?",
 "ROC kriva prikazuje TPR u zavisnosti od FPR za sve pragove, a AUC je verovatnoća da napad dobije viši skor od normalnog toka; ne zavisi od praga. Kod neuravnoteženih podataka ROC-AUC može biti optimističan, pa se dodaje PR-AUC koja se zasniva na Precision i Recall (Saito i Rehmsmeier). U našem slučaju RBF SVM ima najviši Recall (" + f(m(rb,'recall')) + ") a najnižu ROC-AUC (" + f(m(rb,'roc_auc')) + "): Recall se meri na podrazumevanom pragu, a AUC na svim pragovima."),
("Zašto je RBF SVM treniran na uzorku i da li je poređenje fer?",
 "Kernelski SVM ima nadlinearnu složenost: u našem eksperimentu skaliranja, udvostručenje trening skupa sa 20.000 na 40.000 zapisa povećalo je vreme treniranja RBF SVM-a oko 7,2 puta (naspram 1,9–2,5 puta kod ostalih modela). Na raspoloživom hardveru (jedno jezgro, 3,9 GB RAM) trening na 175.341 zapis nije praktičan. Poređenje nije potpuno simetrično i to je jasno navedeno kao ograničenje. Da bi se kontrolisao efekat veličine uzorka, dodat je Linear SVM treniran na istom uzorku (F1 " + f(m(ls,'f1')) + ") i na celom skupu (F1 " + f(m(ln,'f1')) + "): razlika je zanemarljiva, pa veličina trening skupa nije ključni faktor za linearni model. Za RBF to nismo mogli da proverimo na celom skupu."),
("Zašto je Random Forest bolji od Decision Tree?",
 "Pojedinačno duboko stablo ima visoku varijansu. Random Forest usrednjava veliki broj stabala treniranih na bootstrap uzorcima sa nasumičnim podskupom karakteristika, čime smanjuje varijansu bez velikog povećanja pristrasnosti. U našim rezultatima F1 je " + f(m(rf,'f1')) + " naspram " + f(m(dt,'f1')) + ", a broj propuštenih napada pada sa " + nf(m(dt,'fn')) + " na " + nf(m(rf,'fn')) + ". Razlika je statistički značajna (McNemar p < 0,001), a cena je oko " + f(rf['fit_time_s']/dt['fit_time_s'],1) + " puta duže treniranje."),
("Kako tumačite razliku između CV rezultata na treningu (F1 ≈ 0,96) i rezultata na testu (F1 ≈ 0,85–0,89)?",
 "To je pomak između trening i test raspodele, a ne greška u implementaciji. Unakrsna validacija deli iste podatke iste raspodele, uključujući duplirane tokove koji se mogu naći u trening i validacionom foldu. Test skup ima drugačiji udeo napada i drugačiji sastav, a i ACC/CLO stanja koja trening nema. Pokazano je da je razlika trening–test slična i za linearni SVM (" + f(abs(ln['train_metrics']['accuracy']-m(ln,'accuracy')),3) + ") koji ima malu kapacitivnost, što ukazuje da ne potiče pre svega od preprilagođavanja. Tačan uzrok nije izolovan u eksperimentu i to bi trebalo reći otvoreno. Praktična poruka je da CV na treningu ne sme da se navodi kao procena generalizacije na UNSW-NB15."),
("Zašto su lažni alarmi tako visoki (FPR " + pc(m(rf,'fpr')) + "–" + pc(m(ln,'fpr')) + ") i kako bi se smanjili?",
 "Modeli su sa podrazumevanim pragom optimizovani za visok Recall, a normalan saobraćaj test skupa je najslabije prepoznata klasa (specifičnost 0,61–0,73). Moguće mere: podešavanje praga odlučivanja na posebnom validacionom skupu prema ciljanom FPR, težine klasa, dodatne karakteristike, ansambl sa drugim modelima i višeslojna arhitektura. To nije ispitivano u ovom radu i navedeno je kao buduće istraživanje; nije smelo da se podešava na test skupu."),
("Zašto niste uklonili duplikate i šta pokazuje ablaciona studija?",
 "Duplikati su svojstvo zvanične podele i uklanjanje bi izmenilo test skup, pa ne bi bilo uporedivo sa literaturom. Zato je uklanjanje ispitano kao analiza osetljivosti: F1 pada sa " + f(base.loc['Random Forest','F1'],3) + " na " + f(dd.loc['Random Forest','F1'],3) + " (RF), sa " + f(base.loc['Decision Tree','F1'],3) + " na " + f(dd.loc['Decision Tree','F1'],3) + " (DT), a redosled modela ostaje isti. Deo efekta je promena raspodele klasa: napadi čine " + pc(eda['duplikati']['udeo_napada_medju_duplikatima_test']) + " uklonjenih test zapisa pa udeo napada u testu pada sa " + pc(eda['udeo_napada_test']) + " na " + pc(eda['duplikati']['udeo_napada_posle_dedup_test']) + ". Zaključak: apsolutne vrednosti zavise od pripreme, relativni redosled je stabilan."),
("Zašto sttl dominira u Decision Tree modelu? Da li je to artefakt?",
 "Značaj sttl (TTL vrednost od izvora) iznosi oko 80% ukupnog smanjenja nečistoće u stablu, a u EDA je i najjače linearno korelisana karakteristika sa oznakom (r ≈ 0,69). Mogući razlog je da su napadi i normalan saobraćaj u laboratoriji generisani sa različitih izvora sa različitim TTL vrednostima, što je artefakt generisanja skupa, a ne univerzalno svojstvo napada. To nismo eksperimentalno proverili (npr. uklanjanjem sttl), pa je to hipoteza i ograničenje. Random Forest raspoređuje značaj ravnomernije."),
("Kako ste kontrolisali preprilagođavanje?",
 "Za Decision Tree: kriva dubine na podeli 80/20 unutar treninga (trening F1 raste do 0,9988 za neograničenu dubinu, a validacioni F1 stagnira) i ograničavanje dubine i min_samples_leaf pretragom po mreži. Za Random Forest: izbor broja stabala na validaciji i parametri max_depth, min_samples_leaf. Za SVM: parametar C. Preprilagođavanje se proverava poređenjem trening i test metrika; napominjem da RF ima gotovo savršen trening rezultat (" + f(rf['train_metrics']['accuracy']) + ") a najbolji test rezultat, što je uobičajeno za ansamble."),
("Šta je McNemarov test i zašto p < 0,001 nije dovoljno?",
 "McNemarov test poredi dva klasifikatora na istim primerima koristeći samo primere gde se razlikuju (A tačan/B pogrešan i obrnuto). Sa preko 80.000 test primera i male razlike postaju statistički značajne, pa značajnost ne govori o praktičnoj važnosti. Dodatno, test pretpostavlja nezavisne primere, a duplirani tokovi to narušavaju, pa se p-vrednosti tumače orijentaciono. Praktičnu važnost procenjujem prema veličini razlike (npr. ΔF1 ≈ 0,02 između RF i DT) i ceni grešaka."),
("Šta su bootstrap intervali poverenja i šta ne obuhvataju?",
 "Test skup se 1.000 puta uzorkuje sa vraćanjem i za svaki uzorak se računaju metrike; 2,5. i 97,5. percentil čine 95% interval. Na primer, F1 Random Foresta je " + f(rf['test_ci95']['f1'][0],3) + "–" + f(rf['test_ci95']['f1'][1],3) + ". Intervali obuhvataju samo varijabilnost test skupa, a ne varijabilnost treniranja (različiti seed-ovi, različiti trening uzorci), koja nije kvantifikovana jer je eksperiment izveden sa jednim seed-om."),
("Zašto je pretraga hiperparametara rađena na uzorku od 50.000 zapisa?",
 "Zbog računskih ograničenja (jedno jezgro). Pretraga je 3-fold stratifikovana CV nad celim Pipeline-om, a finalni modeli se treniraju na celom treningu. Rizik je da bi pretraga na celom skupu mogla dati drugačije parametre; razlike među najboljim kombinacijama u CV rezultatima su male, pa je uticaj verovatno mali, ali to nije proveravano. Navedeno je kao ograničenje."),
("Zašto ste vremena merili sa n_jobs=1 i koliko su pouzdana?",
 "Da bi poređenje bilo fer (Random Forest bi sa više jezgara bio nepravedno brži). Merenja su jednokratna na jednom računaru i uključuju preprocesiranje. Ponovljeno treniranje RBF SVM-a na 20.000 zapisa trajalo je 5,9 s naspram 6,8 s, pa razlike manje od 15–20% ne treba tumačiti. Relativni odnosi (npr. RBF predikcija " + f(rb['predict_time_s'],1) + " s naspram < 1 s kod ostalih) su robusni, apsolutne vrednosti zavise od hardvera."),
("Zašto LinearSVC, a ne SVC(kernel=\"linear\")?",
 "LinearSVC koristi LIBLINEAR, čije treniranje skalira približno linearno sa brojem uzoraka, dok SVC (LIBSVM) skalira nadlinearno. Za 175.341 zapis SVC je nepraktičan. Razlike u formulaciji (LinearSVC koristi kvadratni hinge loss i penalizuje i slobodan član) su male i ne utiču na zaključke, ali je to detalj koji treba znati."),
("Koliko su rezultati generalizabilni i koja su glavna ograničenja?",
 "Odnose se samo na UNSW-NB15 u zvaničnoj podeli, koji je delom sintetički. Glavna ograničenja: jedan skup podataka, jedan seed, RBF SVM na uzorku (11,4% treninga), uska mreža hiperparametara, podrazumevani prag, pomak raspodele i duplikati, nesigurnost za retke kategorije (Worms n = 44) i izostanak višeklasne klasifikacije. Zaključci se zato odnose na ovaj skup i ne dokazuju produkcionu spremnost."),
("Da li bi se ovakav model mogao primeniti u realnom NIDS sistemu?",
 "Kao komponenta ili baseline, da; sam, ne. Problem je base-rate fallacy (Axelsson): u realnom saobraćaju napadi su retki, pa bi pri FPR od " + pc(m(rf,'fpr')) + " većina alarma bila lažna. Ilustracija po Bayesovoj formuli: pri 1% napada u saobraćaju i izmerenom Recall/FPR za RF, Precision bi bio oko 3,5% (to je izračun, a ne izmeren rezultat). Potrebni su podešavanje praga, dodatni filtri, rad sa realnim saobraćajem i izdvajanje karakteristika u realnom vremenu."),
("Kako je obezbeđena reproduktivnost?",
 "Svi stohastički koraci koriste random_state = 42, podaci se koriste u zvaničnoj podeli, verzije softvera i hardver se beleže u environment.json, a ceo eksperiment se pokreće komandom python main.py. Napominjem da druga verzija biblioteka ili broj jezgara mogu dati neznatno drugačije metrike, a vremena zavise od hardvera."),
("Šta ste mogli da uradite drugačije ili šta bi bio sledeći korak?",
 "Višeklasna klasifikacija (attack_cat) sa makro metrikama, podešavanje praga na validacionom skupu, ponavljanje sa više seed-ova i stratifikovane unakrsne validacije radi kvantifikacije varijabilnosti, provera uticaja sttl, evaluacija na drugim skupovima (npr. CIC-IDS), i dodatni algoritmi (gradijentno pojačavanje, neuronske mreže) kao proširenje u master radu."),
("Zašto je binarna klasifikacija primarni eksperiment, a višeklasna nije rađena?",
 "Binarna detekcija odgovara osnovnom zadatku NIDS-a (napad ili ne) i omogućava jasnu evaluaciju; mešanje sa višeklasnim eksperimentom bi zamutilo zaključke. Kod je pripremljen za višeklasni slučaj (get_xy sa task=\"multiclass\" koristi attack_cat kao cilj i odbacuje label), ali on nije izveden niti se njegovi rezultati navode."),
]

b = Builder(line_spacing=1.1, chapter_page_break=False)
b.refs = REFS
blocks = [("h1", "Pitanja komisije i odgovori – SIR1"),
          ("pn", "__Primena mašinskog učenja u detekciji mrežnih napada.__ Brojke u odgovorima preuzete su iz rezultata eksperimenta (results/metrics). Kod pitanja koja se tiču tumačenja jasno je označeno šta je izmereno, a šta hipoteza.")]
for i, (q, a) in enumerate(QA, 1):
    blocks += [("h3", f"{i}. {q}"), ("pn", a)]
b.register(blocks)
b.render(blocks)
out = ROOT / "defense" / "SIR1_Pitanja_i_odgovori.docx"
b.doc.save(out)
print("OK", out, len(QA), "pitanja")
