""" Fichier principal """

import os

import numpy as np

from libs.distributions import check_distributions
from libs.report import make_report

res_path = "Output"
os.makedirs(res_path, exist_ok=True)  # Créer le dossier de résultat (la première fois, il n'existe pas)

N = 1000
datas = {"Normal":      np.random.normal(12.6, 4.1, N),
         "Log":         np.random.lognormal(6.4, 1.0, N),
         "Exponential": np.random.exponential(3.2, N),
         "Power":       np.random.power(2.5, N),
         "Beta":        np.random.beta(5.5, 2.2, N),
         "Gamma":       np.random.gamma(3.7, 2.0, N)}

for k, v in datas.items():
    print(f"Calcul pour la distribution {k}")
    results = check_distributions(v)
    fig = results["Figure"]
    fig.tight_layout()
    fig.savefig(os.path.join(res_path, f"{k} Distribution ({N} samples) Histograms.png"), bbox_inches="tight")
    results["Dataframe"].to_csv(os.path.join(res_path, f"{k} Distribution ({N} samples) Results.csv"), index=False)
    make_report(v, results, f"{k} Distribution ({N} samples) Report", res_path)

print("Fini")
