"""Generise seminarski rad (DOCX + PDF) iz rezultata eksperimenta. Pokretanje: python reports/build_report.py"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "reports"))
import matplotlib; matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Cm, Pt

from docbuilder import Builder
from references import REFS
import content_theory, content_method, content_results

M = ROOT / "results" / "metrics"
FIGS = ROOT / "results" / "figures"
OUT = ROOT / "reports"
J = lambda n: json.load(open(M / f"{n}.json", encoding="utf-8"))
NAMES = ["Decision Tree", "Random Forest", "Linear SVM (ceo trening)", "SVM RBF (uzorak)"]


def load_R():
    dt, rf, ln, rb, ls = (J("decision_tree_binary"), J("random_forest_binary"), J("linear_svm_ceo_trening_binary"),
                          J("svm_rbf_uzorak_binary"), J("linear_svm_uzorak_binary"))
    det = pd.read_csv(M / "detection_by_category.csv")
    return {
        "M": M, "eda": J("eda_summary"), "env": J("environment"),
        "dt": dt, "rf": rf, "lin": ln, "rbf": rb, "lins": ls,
        "table": pd.read_csv(M / "final_comparison.csv"), "ci": pd.read_csv(M / "bootstrap_ci95.csv"),
        "tvt": pd.read_csv(M / "train_vs_test.csv"), "mcnemar": pd.read_csv(M / "mcnemar.csv"),
        "abl": pd.read_csv(M / "ablation.csv"), "scaling": pd.read_csv(M / "scaling.csv"),
        "det": det[det["Model"].isin(NAMES)],
        "dt_curve": pd.read_csv(M / "dt_depth_curve.csv"), "rf_curve": pd.read_csv(M / "rf_trees_curve.csv"),
        "dt_imp": pd.read_csv(M / "dt_feature_importance_aggregated.csv"),
        "rf_imp": pd.read_csv(M / "rf_feature_importance_aggregated.csv"),
        "svm_sample": rb["n_train"], "svm_tune_sample": rb["tuning"]["n_tune"],
    }


def make_cm_panel():
    slugs = [("Decision Tree", "cm_decision_tree"), ("Random Forest", "cm_random_forest"),
             ("Linear SVM (ceo trening)", "cm_linear_svm_ceo_trening"), ("SVM RBF (uzorak)", "cm_svm_rbf_uzorak")]
    fig, axes = plt.subplots(2, 2, figsize=(9, 8))
    for ax, (_, s) in zip(axes.ravel(), slugs):
        ax.imshow(mpimg.imread(FIGS / f"{s}.png")); ax.axis("off")
    fig.tight_layout(pad=0.3); fig.savefig(FIGS / "cm_all.png", dpi=130); plt.close(fig)


def make_panels():
    def panel(files, out, w=11, h=4.6):
        fig, axes = plt.subplots(1, len(files), figsize=(w, h))
        for ax, (fn, lab) in zip(axes, files):
            ax.imshow(mpimg.imread(FIGS / fn)); ax.axis("off"); ax.set_title(lab, loc="left", fontsize=11, fontweight="bold")
        fig.tight_layout(pad=0.3); fig.savefig(FIGS / out, dpi=130); plt.close(fig)
    panel([("eda_label_distribution.png", "(a)"), ("eda_attack_cat_distribution.png", "(b)")], "eda_distributions.png", 12, 4.2)
    panel([("dt_depth_curve.png", "(a)"), ("rf_trees_curve.png", "(b)")], "tuning_curves.png", 12, 4.0)


def f(x, d=4):
    return f"{x:.{d}f}".replace(".", ",")


def front_matter(R):
    dt, rf, ln, rb = R["dt"], R["rf"], R["lin"], R["rbf"]
    m = lambda r, k: r["test_metrics"][k]
    sr = (f"U radu je ispitana efikasnost klasičnih algoritama mašinskog učenja – Decision Tree, Random Forest i Support Vector Machine (SVM) – u binarnoj detekciji mrežnih napada na zvaničnoj podeli skupa UNSW-NB15 (175.341 zapis za trening i 82.332 za test). Implementiran je reproduktivan proces u jeziku Python i biblioteci Scikit-learn, sa preprocesiranjem koje se uči samo na trening podacima (sprečavanje curenja podataka), podešavanjem hiperparametara unakrsnom validacijom i evaluacijom svih modela na istom test skupu. "
          f"Random Forest je ostvario najbolji ukupni rezultat (Accuracy {f(m(rf,'accuracy'),3)}, Precision {f(m(rf,'precision'),3)}, Recall {f(m(rf,'recall'),3)}, F1 {f(m(rf,'f1'),3)}, ROC-AUC {f(m(rf,'roc_auc'),3)}), zatim Decision Tree (F1 {f(m(dt,'f1'),3)}), dok su linearni SVM (F1 {f(m(ln,'f1'),3)}) i RBF SVM treniran na uzorku od 20.000 zapisa (F1 {f(m(rb,'f1'),3)}) bili slabiji. Svi modeli otkrivaju preko 98% napada, ali uz znatan udeo lažnih alarma na normalnom saobraćaju ({f(m(rf,'fpr')*100,1)}–{f(m(ln,'fpr')*100,1)}%). RBF SVM ima daleko najsporiju predikciju ({f(rb['predict_time_s'],1)} s naspram manje od jedne sekunde kod ostalih). Ablaciona studija pokazuje da uklanjanje dupliranih zapisa znatno smanjuje izmerene performanse, dok uklanjanje TCP sekvencnih brojeva nema uticaja. Zaključuje se da klasične metode, posebno Random Forest, efikasno detektuju napade na ovom skupu, ali da laboratorijska priroda skupa i visok udeo lažnih alarma ograničavaju zaključke o praktičnoj primeni.")
    en = (f"This paper investigates how effectively classical machine learning algorithms – Decision Tree, Random Forest and Support Vector Machine (SVM) – detect network attacks in a binary classification setting on the official training/testing split of the UNSW-NB15 dataset (175,341 and 82,332 records). A reproducible Python/Scikit-learn pipeline was implemented in which all preprocessing is fitted on training data only (preventing data leakage), hyperparameters are tuned by cross-validation, and all models are evaluated on the same test set. "
          f"Random Forest achieved the best overall results (accuracy {m(rf,'accuracy'):.3f}, precision {m(rf,'precision'):.3f}, recall {m(rf,'recall'):.3f}, F1 {m(rf,'f1'):.3f}, ROC-AUC {m(rf,'roc_auc'):.3f}), followed by Decision Tree (F1 {m(dt,'f1'):.3f}); linear SVM (F1 {m(ln,'f1'):.3f}) and an RBF SVM trained on a 20,000-record sample (F1 {m(rb,'f1'):.3f}) were weaker. All models detect more than 98% of attacks but at a considerable false-alarm rate on normal traffic ({m(rf,'fpr')*100:.1f}–{m(ln,'fpr')*100:.1f}%). The RBF SVM has by far the slowest prediction ({rb['predict_time_s']:.1f} s versus under one second for the others). An ablation study shows that removing duplicate records markedly lowers measured performance, whereas removing TCP sequence numbers has no effect. We conclude that classical methods, Random Forest in particular, detect attacks effectively on this dataset, while the laboratory origin of the data and the high false-alarm rate limit conclusions about practical deployment.")
    return sr, en


def title_page(d):
    def para(text, size=12, bold=False, after=6, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, italic=False):
        p = d.add_paragraph(); p.alignment = align
        p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text); r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    para("UNIVERZITET U NIŠU", 14, True, 2)
    para("ELEKTRONSKI FAKULTET", 14, True, 2)
    para("Master akademske studije", 12, False, 90)
    para("SEMINARSKI RAD", 16, True, 6)
    para("iz predmeta SIR1 – Studijski istraživački rad 1", 12, False, 70)
    para("PRIMENA MAŠINSKOG UČENJA U DETEKCIJI MREŽNIH NAPADA", 20, True, 10)
    para("Application of Machine Learning in Network Intrusion Detection", 13, False, 8, italic=True)
    para("Poređenje algoritama Decision Tree, Random Forest i SVM na skupu UNSW-NB15", 12, False, 130)
    for lab, val in (("Student:", "[Ime i prezime]"), ("Broj indeksa:", "[broj indeksa]"), ("Mentor:", "[Ime i prezime mentora]")):
        p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(2.0); p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"{lab} "); r.bold = True; p.add_run(val)
    para("Niš, 2026.", 12, False, 0, before=60)
    d.add_page_break()


def toc_block(entries, pages):
    def render(d):
        p = d.add_paragraph(); p.paragraph_format.space_after = Pt(10)
        r = p.add_run("Sadržaj"); r.bold = True; r.font.size = Pt(16)
        for (lvl, text), pg in zip(entries, pages):
            q = d.add_paragraph(); q.paragraph_format.line_spacing = 1.0
            q.paragraph_format.space_after = Pt(2 if lvl > 1 else 3)
            q.paragraph_format.left_indent = Cm(0 if lvl == 1 else 0.8)
            q.paragraph_format.tab_stops.add_tab_stop(Cm(15.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            r = q.add_run(f"{text}\t{pg}"); r.font.size = Pt(11 if lvl == 1 else 10.5); r.bold = (lvl == 1)
        d.add_page_break()
    return ("raw", render)


def build(pages=None, chapter_break=False, spacing=1.07):
    R = load_R()
    b = Builder(line_spacing=spacing, chapter_page_break=chapter_break)
    b.refs = REFS
    sr, en = front_matter(R)
    abstract = [("h1", "1. Apstrakt (Abstract)"), ("h2", "Apstrakt"), ("p", sr),
                ("pn", "**Ključne reči:** mašinsko učenje, detekcija mrežnih napada, NIDS, UNSW-NB15, Decision Tree, Random Forest, SVM"),
                ("h2", "Abstract"), ("p", en),
                ("pn", "**Keywords:** machine learning, network intrusion detection, NIDS, UNSW-NB15, Decision Tree, Random Forest, SVM")]
    body = content_theory.blocks() + content_method.blocks(R) + content_results.blocks(R)
    refs_h = [("h1", "13. Literatura")]
    appendix = [("h1", "Prilog A. Uputstvo za reprodukciju eksperimenta"),
                ("p", "Kompletan projekat (kod, rezultati i uputstvo) nalazi se u direktorijumu SIR1-Network-Intrusion-Detection. Dataset se preuzima sa zvanične stranice https://research.unsw.edu.au/projects/unsw-nb15-dataset i postavlja u data/raw/ (datoteke UNSW_NB15_training-set.csv i UNSW_NB15_testing-set.csv). Zatim se instaliraju zavisnosti (pip install -r requirements.txt) i pokreće ceo eksperiment komandom python main.py; pojedinačne faze pokreću se opcijom --stage (eda, dt, rf, svm, ablation, scaling, compare). Rezultati se upisuju u results/metrics i results/figures, a ovaj dokument generiše se skriptom reports/build_report.py. Zbog hardverskih i verzijskih razlika, vremena izvršavanja (a moguće i neznatno metrike) mogu odstupati od vrednosti u ovom radu.")]
    all_blocks = abstract + body
    entries = [(1 if x[0] == "h1" else 2, x[1]) for x in all_blocks if x[0] in ("h1", "h2")]
    entries += [(1, "13. Literatura"), (1, "Prilog A. Uputstvo za reprodukciju eksperimenta")]
    pages = pages or [0] * len(entries)
    b.register(all_blocks + appendix)
    title_page(b.doc)
    # numeracija poziva: prvo prolaz kroz tekst da se popuni redosled citata, pa referenca lista
    b.render([toc_block(entries, pages)])
    b.render(all_blocks)
    # lista literature u redosledu prvog pominjanja (ukljucuje i ne-pomenute ako ih ima na kraju)
    rest = [k for k in REFS if k not in b.cite_order]
    b.doc.add_page_break(); b._h1_count = 99
    b.doc.add_heading("13. Literatura", level=1)
    for i, k in enumerate(b.cite_order, 1):
        p = b.doc.add_paragraph(); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.line_spacing = 1.0; p.paragraph_format.space_after = Pt(3); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.add_run(f"[{i}]\t").bold = False; p.add_run(REFS[k]).font.size = Pt(10.5)
    b.render(appendix)
    b.add_page_numbers()
    return b, entries, rest


def _soffice():
    """Trazi LibreOffice (soffice) u PATH-u; vraca None ako ga nema."""
    import shutil
    return shutil.which("soffice") or shutil.which("libreoffice")


def to_pdf(docx):
    """Konvertuje DOCX u PDF pomocu LibreOffice-a (mora biti instaliran)."""
    exe = _soffice()
    if exe is None:
        raise RuntimeError("LibreOffice (soffice) nije pronadjen u PATH-u; PDF i brojevi strana u sadrzaju "
                           "se ne mogu generisati. Instalirajte LibreOffice ili otvorite DOCX u Word-u.")
    subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(docx)],
                   check=True, capture_output=True)
    return OUT / (Path(docx).stem + ".pdf")


def find_pages(pdf, entries):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    texts = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"], capture_output=True, text=True).stdout for i in range(1, n + 1)]
    pages, start = [], 3  # posle naslovne strane i sadrzaja
    toc_pages = [i for i, t in enumerate(texts, 1) if "Sadržaj" in t and "....." in t]
    start = (max(toc_pages) + 1) if toc_pages else 3
    for lvl, text in entries:
        found = None
        for i in range(start, n + 1):
            lines = [re.sub(r"\s+", " ", l).strip() for l in texts[i - 1].splitlines()]
            if text in lines or any(l.startswith(text[:40]) and len(text) > 40 for l in lines):
                found = i; break
        if found is None:
            found = start
        pages.append(found); start = found
    return pages, n


if __name__ == "__main__":
    make_cm_panel(); make_panels()
    name = OUT / "SIR1_Seminarski_rad.docx"
    b, entries, rest = build()
    b.doc.save(name)
    if _soffice() is None or not __import__("shutil").which("pdftotext"):
        print("UPOZORENJE: LibreOffice/poppler (pdftotext) nisu instalirani. Sacuvan je samo DOCX "
              "(brojevi strana u sadrzaju su 0; u Word-u: azurirajte sadrzaj rucno). Nema PDF-a.")
        sys.exit(0)
    pdf = to_pdf(name)
    pages, n = find_pages(pdf, entries)
    b, entries, rest = build(pages)
    b.doc.save(name)
    pdf = to_pdf(name)
    pages2, n2 = find_pages(pdf, entries)
    print("Broj strana:", n2, "| TOC stabilan:", pages == pages2)
    if pages != pages2:
        b, entries, rest = build(pages2); b.doc.save(name); pdf = to_pdf(name)
        _, n2 = find_pages(pdf, entries); print("Broj strana (3. prolaz):", n2)
    print("Nepomenute reference:", rest)
