"""Poglavlja 1-5 (uvod i teorijske osnove) - ne zavise od eksperimentalnih rezultata."""


def blocks():
    B = []
    a = B.append

    # ------------------------------------------------------------------ 2. UVOD
    a(("h1", "2. Uvod"))
    a(("h2", "2.1. Motivacija i predmet istraživanja"))
    a(("p", "Računarske mreže su osnova savremenog poslovanja, javne uprave i svakodnevnog života, pa je zaštita mrežne infrastrukture od neovlašćenog pristupa, zloupotrebe i napada jedan od centralnih zadataka informacione bezbednosti. Sistemi za detekciju upada (Intrusion Detection Systems – IDS) prate saobraćaj ili aktivnosti na računarima i generišu upozorenja kada uoče znake zlonamernog ponašanja [[cite:scarfone2007]]. Tradicionalni sistemi zasnovani na potpisima prepoznaju samo unapred opisane obrasce napada, dok se anomalijski pristupi oslanjaju na model „normalnog“ ponašanja i često koriste metode mašinskog učenja [[cite:buczak2016]]."))
    a(("p", "Mašinsko učenje omogućava da se granica između normalnog i zlonamernog saobraćaja nauči direktno iz označenih primera, bez ručnog pisanja pravila. Pri tom se postavlja praktično pitanje: koliko su efikasni klasični, relativno jednostavni i dobro razumljivi algoritmi, bez primene dubokog učenja? Odgovor je važan jer su klasični modeli brzi, interpretabilni i primenljivi na skromnijem hardveru, što je u operativnim okruženjima često presudno."))
    a(("p", "Predmet ovog istraživanja je eksperimentalno poređenje tri klasična algoritma nadgledanog učenja – stabla odlučivanja (Decision Tree), nasumične šume (Random Forest) i metode potpornih vektora (Support Vector Machine – SVM) – u zadatku binarne klasifikacije mrežnog saobraćaja na skupu podataka UNSW-NB15."))

    a(("h2", "2.2. Cilj i istraživačka pitanja"))
    a(("p", "Cilj istraživanja je da se, pod kontrolisanim i uporedivim uslovima, utvrdi koliko uspešno klasični algoritmi mašinskog učenja detektuju mrežne napade i koji od tri razmatrana algoritma ostvaruje najbolji kompromis između tačnosti detekcije, broja lažnih alarma i vremena izvršavanja. Istraživanje je vođeno sledećim pitanjima:"))
    a(("num", [
        "**IP1:** Koliko uspešno klasični algoritmi mašinskog učenja detektuju mrežne napade na skupu UNSW-NB15?",
        "**IP2:** Koji od tri algoritma ostvaruje najbolje rezultate prema Accuracy, Precision, Recall i F1-score?",
        "**IP3:** Da li Random Forest ostvaruje bolje rezultate od pojedinačnog stabla odlučivanja?",
        "**IP4:** Kako se SVM (linearni i RBF) ponaša u poređenju sa algoritmima zasnovanim na stablima?",
        "**IP5:** Koji algoritam ostvaruje najbolji balans između Precision i Recall?",
        "**IP6:** Koliko vremena zahteva treniranje i predikcija svakog modela?",
        "**IP7:** Mogu li klasične metode predstavljati efikasno rešenje za detekciju mrežnih napada?"]))

    a(("h2", "2.3. Hipoteze"))
    a(("p", "Na osnovu opšteg poznavanja algoritama formulisane su sledeće radne hipoteze. One nisu unapred prihvaćene činjenice, već tvrdnje koje se proveravaju eksperimentima u poglavlju 10 (u kome se prihvataju ili odbacuju na osnovu izmerenih vrednosti):"))
    a(("bul", [
        "**H1:** Random Forest postiže veći F1-score na test skupu od pojedinačnog Decision Tree modela.",
        "**H2:** Modeli zasnovani na stablima postižu veći F1-score od linearnog SVM modela.",
        "**H3:** SVM sa RBF kernelom postiže veći F1-score od linearnog SVM modela pod jednakim uslovima (isti trening uzorak).",
        "**H4:** Vreme treniranja SVM modela raste znatno brže sa brojem uzoraka nego vreme treniranja modela zasnovanih na stablima.",
        "**H5:** Visoka stopa detekcije napada (Recall) postiže se uz primetan broj lažnih alarma, tj. Precision je nižim od Recall."]))

    a(("h2", "2.4. Doprinos i organizacija rada"))
    a(("p", "Doprinos rada je (1) reproduktivna implementacija kompletnog procesa – od analize podataka do evaluacije – sa striktnom kontrolom curenja podataka, (2) uporedna evaluacija tri algoritma na zvaničnoj podeli skupa UNSW-NB15 uz merenje vremena i intervale poverenja, i (3) dodatne analize osetljivosti (uticaj dupliranih zapisa i TCP sekvencnih brojeva) i analiza detekcije po kategorijama napada."))
    a(("p", "Rad je organizovan na sledeći način. Poglavlje 3 uvodi osnove sajber-bezbednosti i detekcije upada, poglavlje 4 daje pregled primene mašinskog učenja u toj oblasti, a poglavlje 5 izlaže teorijske osnove tri algoritma i evaluacionih metrika. Poglavlje 6 opisuje skup UNSW-NB15, poglavlje 7 metodologiju, a poglavlje 8 implementaciju. Rezultati su u poglavlju 9, diskusija u poglavlju 10, ograničenja u poglavlju 11, a zaključak u poglavlju 12."))

    # ------------------------------------------------------------------ 3. OSNOVE
    a(("h1", "3. Osnove sajber-bezbednosti i detekcije mrežnih napada"))
    a(("h2", "3.1. Pojam napada i ciljevi bezbednosti"))
    a(("p", "Informaciona bezbednost se tradicionalno opisuje kroz tri cilja: poverljivost (podaci su dostupni samo ovlašćenima), integritet (podaci i sistemi se ne menjaju neovlašćeno) i dostupnost (usluge su na raspolaganju kada su potrebne). Mrežni napad je namerna aktivnost kojom se narušava bar jedan od ovih ciljeva, a odvija se preko mrežne komunikacije: skeniranjem i izviđanjem ciljnog sistema, iskorišćavanjem ranjivosti, postavljanjem zadnjih vrata, preplavljivanjem resursa i slično."))
    a(("p", "Napadi na mreže razlikuju se po fazi, cilju i tehnici, ali se u mrežnim podacima ispoljavaju kroz izmenjene statistike komunikacije: neuobičajen broj paketa, trajanje veze, veličinu prenetih podataka, retke protokole ili usluge, učestalost povezivanja ka istom odredištu itd. Upravo se na tim statistikama zasniva primena mašinskog učenja koja se razmatra u ovom radu."))

    a(("h2", "3.2. Sistemi za detekciju upada"))
    a(("p", "Prema NIST-ovom vodiču, detekcija upada je proces praćenja događaja u računarskom sistemu ili mreži i njihove analize radi uočavanja znakova incidenata; sistemi koji to automatizuju nazivaju se IDS, a oni koji dodatno pokušavaju da zaustave incident – IPS (Intrusion Prevention Systems) [[cite:scarfone2007]]. Prema mestu posmatranja razlikuju se:"))
    a(("bul", [
        "**Host-based IDS (HIDS):** nadgleda aktivnosti na jednom računaru (sistemski pozivi, log-datoteke, integritet fajlova);",
        "**Network-based IDS (NIDS):** posmatra mrežni saobraćaj na jednoj ili više tačaka u mreži; to je kontekst ovog rada;",
        "**Hibridni sistemi** kombinuju oba pristupa."]))
    a(("p", "Prema metodi detekcije, razlikuju se detekcija zasnovana na potpisima (misuse detection), koja poredi saobraćaj sa bazom poznatih obrazaca napada, i detekcija zasnovana na anomalijama (anomaly detection), koja formira profil normalnog ponašanja i prijavljuje odstupanja [[cite:scarfone2007]], [[cite:sommer2010]]. Potpisi su pouzdani za poznate napade, ali ne pokrivaju nove; anomalijski pristupi teorijski mogu otkriti i nepoznate napade, ali uz veći rizik od lažnih alarma. U ovom radu koristi se nadgledano učenje na označenom skupu, što odgovara detekciji poznatih klasa napada, a ne otkrivanju potpuno novih."))

    a(("h2", "3.3. Zašto je detekcija napada težak zadatak mašinskog učenja"))
    a(("p", "Sommer i Paxson ukazuju da se detekcija upada suštinski razlikuje od uobičajenih primena mašinskog učenja: cena greške je visoka, saobraćaj je veoma raznolik i promenljiv, ne postoji pouzdan „zatvoren svet“ poznatih klasa, a rezultate je teško pretvoriti u akcije za administratora [[cite:sommer2010]]. Axelsson je pokazao da zbog niske učestalosti pravih napada u realnom saobraćaju (tzv. base-rate fallacy) čak i mala stopa lažnih alarma može dovesti do toga da većina alarma bude lažna [[cite:axelsson2000]]."))
    a(("p", "Ove činjenice imaju direktne posledice za interpretaciju rezultata u ovom radu. Prvo, skup UNSW-NB15 je „uravnotežen“ u odnosu na realan saobraćaj (napadi čine oko polovine test skupa), pa vrednosti Precision i Accuracy ne treba direktno prenositi na produkcione uslove. Drugo, rezultati se odnose na unapred zadate klase napada iz laboratorijskog okruženja i ne govore o otpornosti na nove napade. Ova ograničenja se razmatraju u poglavlju 11."))

    a(("h2", "3.4. Skupovi podataka za evaluaciju NIDS-a"))
    a(("p", "Dugo godina su se za evaluaciju koristili skupovi KDD'99 i njegova prečišćena verzija NSL-KDD. Tavallaee i saradnici ukazali su na ozbiljne nedostatke KDD'99 skupa, pre svega veliki broj redundantnih zapisa koji pogoduje algoritmima koji „pamte“ ponovljene primere [[cite:tavallaee2009]]. Zbog starosti i ograničene reprezentativnosti ovih skupova, Moustafa i Slay su kreirali UNSW-NB15, koji sadrži savremenije napade i savremeniji normalan saobraćaj [[cite:moustafa2015]], [[cite:moustafa2016]]. Taj skup je predmet poglavlja 6."))

    # ------------------------------------------------------------------ 4. ML U IDS
    a(("h1", "4. Mašinsko učenje u detekciji mrežnih napada"))
    a(("h2", "4.1. Nadgledano učenje i formulacija zadatka"))
    a(("p", "Nadgledano učenje polazi od skupa označenih primera {(x₁, y₁), …, (xₙ, yₙ)}, gde je xᵢ vektor karakteristika jednog mrežnog toka (npr. trajanje, broj paketa, broj bajtova, protokol), a yᵢ oznaka klase. Cilj je pronaći funkciju f koja za nov, neviđen tok predviđa oznaku. U binarnoj klasifikaciji, yᵢ ∈ {0, 1}, pri čemu 0 označava normalan saobraćaj, a 1 napad. U višeklasnoj klasifikaciji oznaka je kategorija napada (npr. DoS, Exploits, Fuzzers). Ovaj rad se bavi binarnom klasifikacijom, dok je kod pripremljen i za višeklasni slučaj."))
    a(("p", "Mrežni tok (flow) je skup paketa sa istim identifikatorima komunikacije (izvorna i odredišna adresa i port, protokol) u određenom vremenskom intervalu. Karakteristike se izvode iz zaglavlja paketa i statistike toka; one ne zahtevaju uvid u sadržaj poruka, pa su primenljive i na šifrovan saobraćaj."))

    a(("h2", "4.2. Pregled literature"))
    a(("p", "Buczak i Guven daju sistematičan pregled metoda data mining-a i mašinskog učenja za detekciju upada, uključujući stabla odlučivanja, nasumične šume, SVM, neuronske mreže i druge pristupe, uz diskusiju o njihovim prednostima i ograničenjima [[cite:buczak2016]]. Ističu da ne postoji jedna „najbolja“ metoda i da izbor zavisi od vrste napada, skupa podataka i zahteva za brzinom."))
    a(("p", "Na skupu UNSW-NB15 više radova poredi klasične algoritme. Kasongo i Sun, na primer, primenjuju selekciju karakteristika zasnovanu na XGBoost algoritmu i evaluiraju SVM, k-NN, logističku regresiju, veštačku neuronsku mrežu i stablo odlučivanja za binarnu i višeklasnu klasifikaciju; u njihovom radu tačnost stabla odlučivanja na testu u binarnoj klasifikaciji raste sa 88,13% na 90,85% nakon selekcije karakteristika [[cite:kasongo2020]]. Rezultati u literaturi se, međutim, teško direktno porede jer se razlikuju u pretprocesiranju, izboru karakteristika, korišćenoj podeli podataka i izboru metrika; zbog toga u ovom radu sopstveni rezultati nisu poređeni sa tuđim brojkama, već se sva tri algoritma evaluiraju na identičan način."))

    a(("h2", "4.3. Tipični izazovi u primeni"))
    a(("bul", [
        "**Neuravnoteženost klasa:** retke kategorije napada (npr. Worms) imaju vrlo malo primera, što otežava njihovo učenje i interpretaciju ukupne tačnosti.",
        "**Pomak raspodele (distribution shift):** raspodela u treningu i testu može se razlikovati, a u produkciji se saobraćaj vremenom menja.",
        "**Curenje podataka:** neispravno preprocesiranje (npr. skaliranje na celom skupu) vodi optimističnim rezultatima [[cite:kaufman2012]].",
        "**Redundantni i duplirani zapisi:** mogu veštački povećati rezultate ako se isti zapis nađe i u treningu i u testu [[cite:tavallaee2009]].",
        "**Cena grešaka:** propušten napad (False Negative) i lažni alarm (False Positive) imaju različite posledice, pa Accuracy nije dovoljna metrika."]))

    # ------------------------------------------------------------------ 5. TEORIJA
    a(("h1", "5. Teorijske osnove algoritama i evaluacionih metrika"))
    a(("h2", "5.1. Stablo odlučivanja (Decision Tree)"))
    a(("p", "Stablo odlučivanja je hijerarhijski model u kome svaki unutrašnji čvor primenjuje test nad jednom karakteristikom (npr. „sbytes ≤ 1 500“), grane predstavljaju ishode testa, a listovi sadrže predikciju klase. Algoritmi za izgradnju stabala, kao što su ID3 [[cite:quinlan1986]] i CART [[cite:cart1984]], rekurzivno biraju test koji najviše smanjuje nečistoću (impurity) skupa primera u čvoru. Biblioteka Scikit-learn koristi optimizovanu verziju CART algoritma [[cite:pedregosa2011]]."))
    a(("p", "Za čvor t sa udelima klasa pₖ, dve najčešće mere nečistoće su Gini indeks i entropija:"))
    a(("eq", "Gini(t) = 1 − Σₖ pₖ²          Entropy(t) = − Σₖ pₖ · log₂ pₖ"))
    a(("p", "Za svaki kandidat-podelu računa se smanjenje nečistoće (informaciona dobit), pa se bira najbolja podela. Proces se zaustavlja kada se dostignu zadati kriterijumi (maksimalna dubina, minimalan broj uzoraka u listu i slično) ili kada je čvor čist."))
    a(("p", "**Prednosti:** model je interpretabilan (putanja kroz stablo je skup pravila), ne zahteva skaliranje karakteristika, prirodno obrađuje različite skale i nelinearne odnose i veoma je brz u treniranju i predikciji. **Nedostaci:** duboko stablo lako preprilagođava podatke (visoka varijansa), osetljivo je na male promene u podacima, a granice odlučivanja su paralelne osama. Preprilagođavanje se kontroliše ograničavanjem dubine (max_depth), minimalnim brojem uzoraka u listu (min_samples_leaf) ili orezivanjem stabla [[cite:hastie2009]]."))

    a(("h2", "5.2. Nasumična šuma (Random Forest)"))
    a(("p", "Random Forest je ansambl metod koji gradi veliki broj stabala odlučivanja i kombinuje njihove predikcije glasanjem [[cite:breiman2001]]. Zasniva se na dve ideje. Prva je bagging (bootstrap aggregating): svako stablo se trenira na bootstrap uzorku trening skupa, tj. na slučajnom uzorku sa vraćanjem iste veličine [[cite:breiman1996]]. Druga je nasumičan izbor karakteristika: pri svakoj podeli razmatra se samo slučajni podskup karakteristika (parametar max_features), što smanjuje korelaciju između stabala."))
    a(("p", "Usrednjavanjem velikog broja nekorelisanih stabala visoke varijanse i niske pristrasnosti dobija se model sa znatno manjom varijansom od pojedinačnog stabla, bez značajnog povećanja pristrasnosti. Greška ansambla se obično stabilizuje kako broj stabala raste, pa dodatna stabla povećavaju samo računski trošak [[cite:breiman2001]], [[cite:hastie2009]]. Zbog toga se u ovom radu broj stabala bira empirijski (poglavlje 9.3)."))
    a(("p", "Značaj karakteristika u Random Forest modelu najčešće se procenjuje kao srednje smanjenje nečistoće (Mean Decrease in Impurity) po svim stablima. Ta mera je jednostavna, ali može biti pristrasna ka karakteristikama sa mnogo različitih vrednosti [[cite:strobl2007]], pa se tumači oprezno i kao pokazatelj korišćenja karakteristike u modelu, a ne kao dokaz uzročnosti. **Prednosti:** visoka tačnost, otpornost na preprilagođavanje u odnosu na pojedinačno stablo, rad sa velikim brojem karakteristika. **Nedostaci:** manja interpretabilnost, veći utrošak memorije i vremena u odnosu na jedno stablo."))

    a(("h2", "5.3. Metoda potpornih vektora (SVM)"))
    a(("p", "SVM traži hiperravan koja razdvaja dve klase sa maksimalnom marginom, tj. maksimalnim rastojanjem do najbližih primera obe klase, koji se nazivaju potporni vektori [[cite:cortes1995]]. Za linearno razdvojive podatke hiperravan je određena jednačinom wᵀx + b = 0, a klasifikacija znakom funkcije f(x) = wᵀx + b. Kod podataka koji nisu savršeno razdvojivi koristi se meka margina (soft margin) sa promenljivama popuštanja ξᵢ:"))
    a(("eq", "min  ½‖w‖² + C · Σᵢ ξᵢ      uz   yᵢ (wᵀxᵢ + b) ≥ 1 − ξᵢ,   ξᵢ ≥ 0"))
    a(("p", "Parametar C kontroliše kompromis između širine margine i broja prekršaja: veliko C kažnjava greške strože (rizik preprilagođavanja), a malo C dozvoljava širu marginu uz više grešaka. Nelinearne granice dobijaju se „trikom jezgra“ (kernel trick) – skalarni proizvod se zamenjuje kernel funkcijom, što implicitno preslikava podatke u prostor veće dimenzije [[cite:boser1992]]. Najčešći je RBF (Gaussov) kernel:"))
    a(("eq", "K(x, x′) = exp(−γ ‖x − x′‖²)"))
    a(("p", "Parametar γ određuje „domet“ jednog primera: veliko γ daje vrlo lokalne i složene granice, a malo γ glatke granice. Zbog osetljivosti na skalu karakteristika, SVM zahteva standardizaciju ulaza [[cite:hsu2003]]."))
    a(("p", "**Računska zahtevnost.** Treniranje kernelskog SVM-a (npr. LIBSVM, na kome se zasniva klasa SVC u Scikit-learn biblioteci) ima složenost koja raste više nego kvadratno sa brojem uzoraka, a predikcija zavisi od broja potpornih vektora [[cite:chang2011]], [[cite:pedregosa2011]]. Za velike skupove zato se koriste linearni SVM-ovi (LIBLINEAR, klasa LinearSVC), čije treniranje skalira približno linearno sa brojem uzoraka [[cite:fan2008]]. U ovom radu je zbog toga linearni SVM treniran na celom trening skupu, a RBF SVM na stratifikovanom uzorku (poglavlje 7.5)."))
    a(("p", "**Prednosti:** dobra generalizacija u prostorima visoke dimenzije, mogućnost nelinearnih granica kroz kernele. **Nedostaci:** osetljivost na skaliranje i izbor hiperparametara, veliki računski trošak za velike skupove, nema direktnu interpretaciju značaja karakteristika (osim za linearni model)."))

    a(("h2", "5.4. Evaluacione metrike"))
    a(("p", "Evaluacija se zasniva na matrici konfuzije za binarnu klasifikaciju, u kojoj se napad smatra pozitivnom klasom: TP (napad ispravno detektovan), TN (normalan saobraćaj ispravno prepoznat), FP (lažni alarm) i FN (propušten napad). Metrike korišćene u radu su:"))
    a(("eq", "Accuracy = (TP + TN) / (TP + TN + FP + FN)          Precision = TP / (TP + FP)"))
    a(("eq", "Recall = TP / (TP + FN)          F1 = 2 · Precision · Recall / (Precision + Recall)"))
    a(("eq", "FPR = FP / (FP + TN)          FNR = FN / (FN + TP)"))
    a(("p", "**Recall** (stopa detekcije) pokazuje koji udeo stvarnih napada je otkriven; u bezbednosti je posebno važan jer propušten napad može imati ozbiljne posledice. **Precision** pokazuje koji udeo alarma su pravi napadi; nizak Precision znači mnogo lažnih alarma i opterećenje analitičara. **F1-score** je harmonijska sredina Precision i Recall i koristi se kao sažeta mera njihovog balansa. **FPR** je udeo normalnog saobraćaja koji je pogrešno označen kao napad."))
    a(("p", "**ROC-AUC** je površina ispod ROC krive, koja prikazuje zavisnost stope detekcije (TPR) od stope lažnih alarma (FPR) za sve moguće pragove odlučivanja; ne zavisi od izabranog praga i može se tumačiti kao verovatnoća da slučajno izabran napad dobije viši skor od slučajno izabranog normalnog toka [[cite:fawcett2006]]. Pošto ROC-AUC može biti optimističan kod neuravnoteženih skupova, uz njega se prikazuje i površina ispod Precision–Recall krive (PR-AUC) [[cite:saito2015]]. Pored toga, izračunat je Matthewsov koeficijent korelacije (MCC) kao uravnotežena mera koja uzima u obzir sve četiri vrednosti matrice konfuzije."))
    a(("p", "Za statističko poređenje dva klasifikatora na istom test skupu koristi se McNemarov test, koji se zasniva samo na primerima na kojima se dva modela razlikuju [[cite:mcnemar1947]], [[cite:dietterich1998]]. Nesigurnost metrika procenjuje se neparametarskim bootstrap postupkom [[cite:efron1993]]."))

    a(("h2", "5.5. Curenje podataka i preprilagođavanje"))
    a(("p", "Curenje podataka (data leakage) nastaje kada informacija koja ne bi bila dostupna u trenutku stvarne primene dospe u proces treniranja ili izbora modela, što vodi preoptimističnoj proceni performansi [[cite:kaufman2012]]. Dva tipična izvora u ovom zadatku su: (a) ciljna promenljiva ili njen derivat među ulaznim karakteristikama (u UNSW-NB15 to bi bile kolone label i attack_cat), i (b) transformacije naučene na celom skupu pre podele, npr. skaliranje ili kodiranje kategorija koje „vidi“ test podatke. U ovom radu se oba izvora izbegavaju konstrukcijom (poglavlja 7 i 8), a test skup se ne koristi ni za izbor hiperparametara."))
    a(("p", "Preprilagođavanje (overfitting) je pojava da model veoma dobro opisuje trening podatke, uključujući šum, ali slabo generalizuje. Indikator je velika razlika između performansi na treningu i na neviđenim podacima. Kontroliše se ograničavanjem složenosti modela, regularizacijom i izborom hiperparametara unakrsnom validacijom [[cite:hastie2009]]."))
    return B
