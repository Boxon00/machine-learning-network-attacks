// Generise PowerPoint prezentaciju za odbranu. Pokretanje: node defense/build_deck.js
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
// Opcioni dodatak (postoji samo u mom okruzenju); bez njega se prezentacija svejedno generise.
let applyTheme = async () => {};
try { ({ applyTheme } = require(process.env.APPLY_THEME_JS || "./apply_theme.js")); } catch (e) { /* preskoci */ }

const ROOT = path.resolve(__dirname, "..");
const M = (f) => JSON.parse(fs.readFileSync(path.join(ROOT, "results/metrics", f), "utf-8"));
const FIG = (f) => path.join(ROOT, "results/figures", f);
const dt = M("decision_tree_binary.json"), rf = M("random_forest_binary.json"),
  ln = M("linear_svm_ceo_trening_binary.json"), rb = M("svm_rbf_uzorak_binary.json"), ls = M("linear_svm_uzorak_binary.json");
const eda = M("eda_summary.json");
const models = [["Decision Tree", dt], ["Random Forest", rf], ["Linear SVM", ln], ["SVM RBF (uzorak)", rb]];
const fx = (x, d = 4) => x.toFixed(d).replace(".", ",");
const pc = (x, d = 1) => (x * 100).toFixed(d).replace(".", ",") + "%";
const nf = (x) => Math.round(x).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
const mt = (r, k) => r.test_metrics[k];

const THEME = {
  name: "SIR1 NIDS", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "14213D", lt1: "FFFFFF", dk2: "0B2545", lt2: "EEF2F7", accent1: "1B998B", accent2: "E4572E",
    accent3: "F2B134", accent4: "3A86FF", accent5: "5C6B8A", accent6: "8DA9C4", hlink: "3A86FF", folHlink: "5C6B8A" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Primena mašinskog učenja u detekciji mrežnih napada";
pres.author = "SIR1";
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "LIGHT", background: { color: "FFFFFF" },
  slideNumber: { x: 9.2, y: 5.25, w: 0.5, h: 0.3, fontSize: 10, color: "5C6B8A" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9, h: 0.8, fontSize: 30, bold: true, color: "0B2545", fontFace: "Cambria", margin: 0, valign: "middle" }, text: "" } }],
});
pres.defineSlideMaster({
  title: "DARK", background: { color: "0B2545" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.7, y: 1.5, w: 8.6, h: 1.6, fontSize: 38, bold: true, color: "FFFFFF", fontFace: "Cambria", margin: 0, valign: "top" }, text: "" } }],
});

const NAVY = "0B2545", TEAL = "1B998B", RED = "E4572E", AMBER = "F2B134", GREY = "5C6B8A", PALE = "EEF2F7";
const MODEL_COLORS = [NAVY, TEAL, AMBER, RED];

function light(title, section, notes) {
  const s = pres.addSlide({ masterName: "LIGHT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function card(s, x, y, w, h, head, body, fill = PALE, headColor = NAVY) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08, objectName: "card" });
  s.addText(head, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.4, fontSize: 19, bold: true, color: headColor, margin: 0, isTextBox: true });
  s.addText(body, { x: x + 0.2, y: y + 0.55, w: w - 0.4, h: h - 0.65, fontSize: 17, color: "14213D", margin: 0, valign: "top", paraSpaceAfter: 8, isTextBox: true });
}
function stat(s, x, y, w, big, small, color = TEAL) {
  s.addText(big, { x, y, w, h: 0.8, fontSize: 40, bold: true, color, fontFace: "Cambria", margin: 0, isTextBox: true });
  s.addText(small, { x, y: y + 0.8, w, h: 0.55, fontSize: 14, color: GREY, margin: 0, valign: "top", isTextBox: true });
}

// 1 ---------------------------------------------------------------- naslov
pres.addSection({ title: "Uvod" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Uvod" });
s.addText("Primena mašinskog učenja u detekciji mrežnih napada", { placeholder: "title" });
s.addText("Poređenje algoritama Decision Tree, Random Forest i SVM na skupu UNSW-NB15", { x: 0.7, y: 3.25, w: 8.2, h: 0.7, fontSize: 18, color: "8DA9C4", margin: 0, isTextBox: true });
s.addText("Seminarski rad iz predmeta SIR1  |  Elektronski fakultet Univerziteta u Nišu", { x: 0.7, y: 4.5, w: 8.6, h: 0.35, fontSize: 14, color: "FFFFFF", margin: 0, isTextBox: true });
s.addText("[Ime i prezime studenta]  |  Mentor: [Ime i prezime mentora]", { x: 0.7, y: 4.85, w: 8.6, h: 0.35, fontSize: 14, color: "8DA9C4", margin: 0, isTextBox: true });
s.addNotes("Predstavljanje: tema, predmet, mentor. Rad poredi tri klasična algoritma u binarnoj detekciji mrežnih napada na zvaničnoj podeli skupa UNSW-NB15.");

// 2 ---------------------------------------------------------------- cilj
s = light("Cilj i istraživačka pitanja", "Uvod", "Cilj: eksperimentalno uporediti tri klasična algoritma pod uporedivim uslovima. Bez dubokog učenja – to je svesno ostavljeno za buduće proširenje.");
card(s, 0.5, 1.3, 4.4, 3.7, "Cilj", "Utvrditi koliko uspešno Decision Tree, Random Forest i SVM razlikuju normalan saobraćaj od napada i koji nudi najbolji kompromis tačnosti, lažnih alarma i brzine.");
card(s, 5.1, 1.3, 4.4, 3.7, "Istraživačka pitanja", "IP1 Uspešnost detekcije\nIP2–IP5 Najbolji algoritam, RF naspram DT, SVM naspram stabala, balans Precision/Recall\nIP6 Vreme treniranja i predikcije\nIP7 Primenljivost klasičnih metoda", PALE);

// 3 ---------------------------------------------------------------- dataset
s = light("Skup podataka UNSW-NB15", "Uvod", "Skup su kreirali istraživači UNSW Canberra alatom IXIA PerfectStorm: hibrid realnog normalnog i sintetičkog napadačkog saobraćaja. Koristimo zvaničnu podelu na trening i test. Napomena: trening je veći od testa.");
stat(s, 0.5, 1.3, 2.2, nf(dt.n_train), "zapisa u treningu");
stat(s, 0.5, 2.8, 2.2, nf(dt.n_test), "zapisa u testu", RED);
stat(s, 0.5, 4.3, 2.2, "42", "ulazne karakteristike (39 numeričkih, 3 kategorijske)", NAVY);
const att = fs.readFileSync(path.join(ROOT, "results/metrics/eda_attack_cat_counts.csv"), "utf-8").trim().split("\n").slice(1).map((l) => l.split(","));
s.addChart(pres.charts.BAR, [{ name: "Trening", labels: att.map((r) => r[0]), values: att.map((r) => +r[1]) }, { name: "Test", labels: att.map((r) => r[0]), values: att.map((r) => +r[2]) }],
  { x: 3.0, y: 1.2, w: 6.6, h: 3.9, barDir: "bar", chartColors: [NAVY, AMBER], showTitle: true, title: "Zastupljenost kategorija saobraćaja", titleFontSize: 14, titleColor: NAVY,
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, catAxisLabelColor: "14213D", valAxisLabelColor: GREY, catAxisOrientation: "maxMin", valAxisLogScaleBase: 10,
    valGridLine: { color: "D9DEE7", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 11 });

// 4 ---------------------------------------------------------------- algoritmi
s = light("Tri algoritma", "Uvod", "Decision Tree: rekurzivne podele po pragovima (Gini/entropija). Random Forest: bagging + nasumičan izbor karakteristika. SVM: maksimalna margina, kernel trik; RBF je skup za velike skupove.");
card(s, 0.5, 1.3, 2.9, 3.7, "Decision Tree", "Hijerarhija pravila nad karakteristikama.\n+ brz, interpretabilan\n– sklon preprilagođavanju");
card(s, 3.55, 1.3, 2.9, 3.7, "Random Forest", "Ansambl stabala (bagging + nasumične karakteristike).\n+ manja varijansa\n– sporiji, manje interpretabilan", PALE);
card(s, 6.6, 1.3, 2.9, 3.7, "SVM", "Hiperravan maksimalne margine; RBF kernel za nelinearne granice.\n+ jaka teorija\n– skup za velike skupove");

// 5 ---------------------------------------------------------------- metodologija
pres.addSection({ title: "Metodologija" });
s = light("Tok eksperimenta", "Metodologija", "Test skup se koristi isključivo za završnu evaluaciju. Hiperparametri se biraju 3-fold stratifikovanom unakrsnom validacijom na uzorku treninga od 50.000 zapisa; finalni modeli se treniraju na celom treningu.");
const steps = [["1", "Učitavanje", "zvanična podela"], ["2", "Preprocesiranje", "fit samo na treningu"], ["3", "Hiperparametri", "3-fold CV, F1"], ["4", "Treniranje", "ceo trening skup"], ["5", "Evaluacija", "isti test skup"]];
steps.forEach((st, i) => {
  const x = 0.5 + i * 1.82;
  s.addShape(pres.shapes.OVAL, { x: x + 0.45, y: 1.5, w: 0.7, h: 0.7, fill: { color: i === 4 ? RED : TEAL }, line: { color: i === 4 ? RED : TEAL } });
  s.addText(st[0], { x: x + 0.45, y: 1.5, w: 0.7, h: 0.7, fontSize: 20, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
  s.addText(st[1], { x, y: 2.35, w: 1.6, h: 0.4, fontSize: 15, bold: true, color: NAVY, align: "center", margin: 0, isTextBox: true });
  s.addText(st[2], { x, y: 2.75, w: 1.6, h: 0.6, fontSize: 13, color: GREY, align: "center", margin: 0, valign: "top", isTextBox: true });
});
card(s, 0.5, 3.7, 9, 1.4, "Uporedivi uslovi", "Isto preprocesiranje, isti test skup, iste metrike, n_jobs = 1 za merenje vremena, seed 42. Binarna klasifikacija (label); višeklasna (attack_cat) nije deo rada.");

// 6 ---------------------------------------------------------------- leakage
s = light("Sprečavanje curenja podataka", "Metodologija", "Ključne tačke: Pipeline, fit samo na treningu, handle_unknown ignore zbog stanja ACC i CLO koja postoje samo u testu, label i attack_cat nikada nisu ulaz.");
card(s, 0.5, 1.3, 4.5, 3.8, "Pravila", "Pipeline: imputacija → log(1+x) → standardizacija; One-Hot sa handle_unknown=\"ignore\".\nfit samo na treningu; test samo transform.\nLabel i attack_cat nisu ulaz (get_xy).\nTest skup ne učestvuje u izboru hiperparametara.");
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.2, y: 1.3, w: 4.3, h: 3.8, fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.08 });
s.addText([
  { text: "pipe = Pipeline([", options: { breakLine: true } }, { text: "  (\"prep\", preprocessor),", options: { breakLine: true } }, { text: "  (\"clf\", estimator)])", options: { breakLine: true } },
  { text: " ", options: { breakLine: true } }, { text: "pipe.fit(X_train, y_train)", options: { breakLine: true } }, { text: "pipe.predict(X_test)", options: { breakLine: true } }, { text: " ", options: { breakLine: true } },
  { text: "# test: samo transform,", options: { breakLine: true, color: "8DA9C4" } }, { text: "# nikad fit", options: { color: "8DA9C4" } }],
  { x: 5.4, y: 1.5, w: 3.9, h: 3.4, fontSize: 17, fontFace: "Courier New", color: "FFFFFF", margin: 0, valign: "top", isTextBox: true });

// 7 ---------------------------------------------------------------- SVM i uzorak + kvalitet
s = light("Nalazi o podacima i izbor za SVM", "Metodologija", "Ključni nalazi EDA: duplikati, preklapanje trening/test, pomak raspodele klasa. RBF SVM je zbog složenosti treniran na uzorku, evaluiran na celom testu.");
const d = eda.duplikati;
stat(s, 0.5, 1.3, 2.8, nf(d.duplikati_bez_id_trening), "duplikata u treningu (bez id)", RED);
stat(s, 3.5, 1.3, 2.8, pc(eda.preklapanje.udeo_preklapanja), "test zapisa identičnih nekom iz treninga");
stat(s, 6.5, 1.3, 3.0, pc(eda.udeo_napada_trening, 0) + " / " + pc(eda.udeo_napada_test, 0), "udeo napada u treningu / testu", NAVY);
card(s, 0.5, 3.0, 9, 2.1, "SVM: tri varijante, svi evaluirani na celom testu", "Linear SVM na celom treningu (175.341)\nLinear SVM na uzorku od 20.000 (izolovanje efekta kernela)\nSVM RBF na uzorku od 20.000 – kernelski SVM je nadlinearan po složenosti");

// 8 ---------------------------------------------------------------- rezultati tabela
pres.addSection({ title: "Rezultati" });
s = light("Rezultati na test skupu", "Rezultati", "Random Forest je najbolji po F1, Accuracy, Precision, ROC-AUC i FPR. RBF SVM ima najveći Recall. Svi modeli imaju Recall preko 0,98, ali znatan FPR.");
const hdrOpts = { bold: true, color: "FFFFFF", fill: { color: NAVY }, align: "center", fontSize: 13 };
const rows = [[{ text: "Model", options: { ...hdrOpts, align: "left" } }, ...["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "FPR"].map((t) => ({ text: t, options: hdrOpts }))]];
const best = {};
["accuracy", "precision", "recall", "f1", "roc_auc"].forEach((k) => (best[k] = Math.max(...models.map((m) => mt(m[1], k)))));
best.fpr = Math.min(...models.map((m) => mt(m[1], "fpr")));
models.forEach(([name, r], i) => {
  const cell = (k) => ({ text: fx(mt(r, k)), options: { align: "center", fontSize: 13, bold: mt(r, k) === best[k], color: mt(r, k) === best[k] ? TEAL : "14213D", fill: { color: i % 2 ? "FFFFFF" : PALE } } });
  rows.push([{ text: name, options: { fontSize: 13, bold: true, align: "left", fill: { color: i % 2 ? "FFFFFF" : PALE } } }, cell("accuracy"), cell("precision"), cell("recall"), cell("f1"), cell("roc_auc"), cell("fpr")]);
});
s.addTable(rows, { x: 0.5, y: 1.3, w: 9, colW: [2.4, 1.1, 1.1, 1.0, 1.0, 1.2, 1.2], rowH: 0.5, border: { type: "solid", color: "D9DEE7", pt: 0.5 }, valign: "middle" });
s.addText("Podebljano zeleno = najbolja vrednost u koloni. SVM RBF treniran na uzorku od 20.000 zapisa; svi modeli evaluirani na svih " + nf(dt.n_test) + " test zapisa. FPR: manje je bolje.", { x: 0.5, y: 4.0, w: 9, h: 0.6, fontSize: 12, color: GREY, margin: 0, isTextBox: true });
s.addText("Random Forest: F1 " + fx(mt(rf, "f1"), 3) + ", ROC-AUC " + fx(mt(rf, "roc_auc"), 3) + ". Recall iznad 0,98 kod svih modela.", { x: 0.5, y: 4.6, w: 9, h: 0.4, fontSize: 15, bold: true, color: NAVY, margin: 0, isTextBox: true });

// 9 ---------------------------------------------------------------- chart metrika
s = light("Poređenje metrika", "Rezultati", "Razlike su veće u Precision (lažni alarmi) nego u Recall. Intervali poverenja (bootstrap) za F1 se ne preklapaju.");
const cats = ["Accuracy", "Precision", "Recall", "F1"], keys = ["accuracy", "precision", "recall", "f1"];
s.addChart(pres.charts.BAR, models.map(([n, r]) => ({ name: n, labels: cats, values: keys.map((k) => +mt(r, k).toFixed(4)) })),
  { x: 0.5, y: 1.2, w: 9, h: 3.9, barDir: "col", barGrouping: "clustered", chartColors: MODEL_COLORS, valAxisMinVal: 0.7, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.05,
    showValue: true, dataLabelFormatCode: "0.000", dataLabelFontSize: 8, dataLabelPosition: "outEnd", catAxisLabelFontSize: 13, valAxisLabelFontSize: 11, catAxisLabelColor: "14213D", valAxisLabelColor: GREY,
    valGridLine: { color: "D9DEE7", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 12 });

// 10 --------------------------------------------------------------- matrice konfuzije
s = light("Matrice konfuzije", "Rezultati", "Veoma malo propuštenih napada, ali veliki broj lažnih alarma. Normalan saobraćaj je najslabije prepoznata klasa.");
s.addImage({ path: FIG("cm_all.png"), x: 0.5, y: 1.15, w: 4.0, h: 3.55 });
card(s, 4.8, 1.3, 4.7, 3.7, "Šta pokazuju", "Propušteni napadi (FN): RF " + nf(rf.test_metrics.fn) + ", DT " + nf(dt.test_metrics.fn) + ".\nLažni alarmi (FP): od " + nf(Math.min(...models.map((m) => m[1].test_metrics.fp))) + " do " + nf(Math.max(...models.map((m) => m[1].test_metrics.fp))) + " od " + nf(dt.test_metrics.tn + dt.test_metrics.fp) + " normalnih zapisa.\nNormalan saobraćaj je najslabija klasa (specifičnost 0,61–0,73).");

// 11 --------------------------------------------------------------- ROC
s = light("ROC krive", "Rezultati", "Za niske FPR vrednosti stabla su bolja od oba SVM modela. RBF SVM ima najviši Recall na podrazumevanom pragu, ali najnižu ROC-AUC.");
s.addImage({ path: FIG("roc_curves.png"), x: 0.5, y: 1.15, w: 4.5, h: 3.75 });
card(s, 5.3, 1.3, 4.2, 3.7, "ROC-AUC", "RF  " + fx(mt(rf, "roc_auc")) + "\nDT  " + fx(mt(dt, "roc_auc")) + "\nLinear SVM  " + fx(mt(ln, "roc_auc")) + "\nSVM RBF  " + fx(mt(rb, "roc_auc")) + "\n\nROC-AUC ne zavisi od praga; Recall se meri na podrazumevanom pragu.");

// 12 --------------------------------------------------------------- vreme
s = light("Vreme izvršavanja", "Rezultati", "Vremena su jednokratna, jedno jezgro, uključuju preprocesiranje. RBF predikcija je daleko najsporija; pri udvostručenju trening skupa RBF vreme raste oko 7 puta.");
s.addChart(pres.charts.BAR, [{ name: "Treniranje (s)", labels: models.map((m) => m[0]), values: models.map((m) => +m[1].fit_time_s.toFixed(2)) }, { name: "Predikcija (s)", labels: models.map((m) => m[0]), values: models.map((m) => +m[1].predict_time_s.toFixed(2)) }],
  { x: 0.5, y: 1.2, w: 5.4, h: 3.9, barDir: "col", chartColors: [NAVY, RED], showValue: true, dataLabelFormatCode: "0.0", dataLabelFontSize: 10, dataLabelPosition: "outEnd", catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
    catAxisLabelColor: "14213D", valAxisLabelColor: GREY, valGridLine: { color: "D9DEE7", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 12 });
stat(s, 6.3, 1.4, 3.2, fx(rb.predict_time_s, 1) + " s", "predikcija RBF SVM-a za 82.332 zapisa", RED);
stat(s, 6.3, 3.0, 3.2, "< 1 s", "predikcija stabala i Linear SVM-a (ceo test skup)", TEAL);

// 13 --------------------------------------------------------------- kategorije
s = light("Detekcija po kategorijama", "Rezultati", "Većina kategorija napada se detektuje iznad 0,9 kod svih modela. Fuzzers je najteža kategorija napada, a Normal klasa je najslabije prepoznata.");
s.addImage({ path: FIG("detection_by_category.png"), x: 0.5, y: 1.15, w: 5.4, h: 3.5 });
card(s, 6.1, 1.3, 3.4, 3.7, "Nalazi", "Napadi: 0,91–1,00.\nFuzzers najteži (0,91–0,95).\nNormal: samo 0,61–0,73.\nWorms (n = 44) i Shellcode (n = 378): velika nesigurnost.");

// 14 --------------------------------------------------------------- ablacija
s = light("Ablacija: duplikati i TCP seq.", "Rezultati", "Uklanjanje duplikata smanjuje F1 za oko 0,08, a njihov sastav objašnjava deo efekta: 89% uklonjenih test duplikata su napadi, pa udeo napada u testu pada sa 55% na 39%. TCP sekvencni brojevi nemaju uticaja.");
const csvSplit = (l) => (l.match(/("([^"]*)"|[^,]+)/g) || []).map((x) => x.replace(/^"|"$/g, ""));
const abl = fs.readFileSync(path.join(ROOT, "results/metrics/ablation.csv"), "utf-8").trim().split("\n").slice(1).map(csvSplit);
const pick = (v) => abl.filter((r) => r[0] === v);
const vars_ = ["Osnovni", "Bez TCP seq. (stcpb", "Bez duplikata"];
const ablNames = ["Decision Tree", "Random Forest", "Linear SVM (ceo trening)"];
const f1Of = (v, mname) => { const r = abl.find((x) => x[0].startsWith(v) && x[1] === mname); return r ? +(+r[7]).toFixed(4) : 0; };
s.addChart(pres.charts.BAR, ["Osnovni", "Bez TCP seq.", "Bez duplikata"].map((lab, i) => ({ name: lab, labels: ["Decision Tree", "Random Forest", "Linear SVM"], values: ablNames.map((mn) => f1Of(vars_[i], mn)) })),
  { x: 0.5, y: 1.2, w: 5.6, h: 3.9, barDir: "col", chartColors: [NAVY, TEAL, RED], valAxisMinVal: 0.7, valAxisMaxVal: 0.95, showValue: true, dataLabelFormatCode: "0.000", dataLabelFontSize: 9, dataLabelPosition: "outEnd",
    showTitle: true, title: "F1-score po varijanti", titleFontSize: 14, titleColor: NAVY, catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLabelColor: "14213D", valAxisLabelColor: GREY, valGridLine: { color: "D9DEE7", size: 0.5 }, catGridLine: { style: "none" }, showLegend: true, legendPos: "b", legendFontSize: 11 });
card(s, 6.3, 1.3, 3.2, 3.7, "Zaključak", "TCP seq. brojevi: bez uticaja (ΔF1 ≤ 0,0003).\nBez duplikata: F1 pada ~0,08; redosled modela isti.\nCV na treningu (F1 ≈ 0,96) je optimističan u odnosu na test.");

// 15 --------------------------------------------------------------- hipoteze
pres.addSection({ title: "Zaključci" });
s = light("Provera hipoteza", "Zaključci", "Sve hipoteze su proverene izmerenim vrednostima; H3 ima malu razliku izmerenu jednim izvršavanjem pa je treba oprezno tumačiti.");
const hy = [["H1", "RF F1 > DT F1", "Prihvaćena"], ["H2", "Stabla > Linear SVM (F1)", "Prihvaćena"], ["H3", "RBF > Linear (isti uzorak)", "Prihvaćena (razlika " + fx(mt(rb, "f1") - mt(ls, "f1"), 4) + ")"], ["H4", "Vreme SVM-a raste brže sa n", "Za RBF da; za Linear ne"], ["H5", "Precision < Recall", "Prihvaćena"]];
hy.forEach((h, i) => {
  const y = 1.3 + i * 0.72;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 9, h: 0.6, fill: { color: i % 2 ? "FFFFFF" : PALE }, line: { color: PALE }, rectRadius: 0.06 });
  s.addText(h[0], { x: 0.7, y, w: 0.7, h: 0.6, fontSize: 18, bold: true, color: TEAL, margin: 0, valign: "middle", isTextBox: true });
  s.addText(h[1], { x: 1.5, y, w: 4.6, h: 0.6, fontSize: 15, color: "14213D", margin: 0, valign: "middle", isTextBox: true });
  s.addText(h[2], { x: 6.2, y, w: 3.2, h: 0.6, fontSize: 15, bold: true, color: NAVY, margin: 0, valign: "middle", isTextBox: true });
});

// 16 --------------------------------------------------------------- zakljucci
s = light("Zaključci istraživanja", "Zaključci", "Odgovor na centralno pitanje: klasične metode, posebno Random Forest, efikasno detektuju napade na UNSW-NB15, ali visok udeo lažnih alarma i laboratorijska priroda skupa ograničavaju zaključke o produkcionoj primeni.");
card(s, 0.5, 1.3, 4.4, 3.8, "Šta smo pokazali", "Random Forest je najbolji: F1 " + fx(mt(rf, "f1"), 3) + ", ROC-AUC " + fx(mt(rf, "roc_auc"), 3) + ".\nSvi modeli otkrivaju preko 98% napada.\nStabla i Linear SVM klasifikuju ceo test skup za manje od 1 s.\nRBF SVM je najsporiji u predikciji.");
card(s, 5.1, 1.3, 4.4, 3.8, "Ograničenja", "Jedan skup, delom sintetički; jedan seed.\nRBF SVM treniran na uzorku (20.000).\nFPR " + pc(mt(rf, "fpr")) + "–" + pc(mt(ln, "fpr")) + ": dominira praktični problem.\nPrag odlučivanja nije podešavan.\nBudući rad: višeklasna klasifikacija, više seed-ova, drugi skupovi, podešavanje praga.", PALE);

// 17 --------------------------------------------------------------- hvala
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Zaključci" });
s.addText("Hvala na pažnji", { placeholder: "title" });
s.addText("Pitanja?", { x: 0.7, y: 3.2, w: 8, h: 0.6, fontSize: 24, color: "8DA9C4", margin: 0, isTextBox: true });
s.addNotes("Pripremljena su pitanja i odgovori u dokumentu SIR1_Pitanja_i_odgovori.docx.");

(async () => {
  const out = path.join(__dirname, "SIR1_Odbrana_prezentacija.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("OK", out);
})();
