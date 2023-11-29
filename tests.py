""" Fichier principal """

import os

import numpy as np

from libs.distributions import check_distributions, check_normality, ALL_DISTRIBUTIONS
from libs.utils import transform
from libs.report import make_distribution_report, make_normality_report

res_path = "Output Tests"
os.makedirs(res_path, exist_ok=True)  # Créer le dossier de résultat (la première fois, il n'existe pas)

sizes = [10, 100, 1000]

for n in sizes:
    datas = {"Normal":      np.random.normal(12.6, 4.1, n),
             "Log":         np.random.lognormal(6.4, 1.0, n),
             "Exponential": np.random.exponential(3.2, n),
             "Power":       np.random.power(2.5, n),
             "Beta":        np.random.beta(5.5, 2.2, n),
             "Gamma":       np.random.gamma(3.7, 2.0, n)}

    for k, v in datas.items():
        print(f"Calcul pour la distribution {k} avec {n} samples")
        print(f"  Vérification avec toutes les distributions")
        # Vérification avec toutes les distributions
        result_dist = check_distributions(v, ALL_DISTRIBUTIONS)
        # Enregistrement de la figure
        fig = result_dist["Figure"]
        fig.tight_layout()
        fig.savefig(os.path.join(res_path, f"{k} Distribution ({n} samples) Histograms.png"), bbox_inches="tight")
        # Enregistrement du tableau récapitualtif
        result_dist["Dataframe"].to_csv(os.path.join(res_path, f"{k} Distribution ({n} samples) Results.csv"), index=False)
        # Enregistrement du Rapport Complet
        make_distribution_report(v, result_dist, f"{k} Distribution ({n} samples) Report", res_path)

        print(f"  Vérification de normalité avec ses versions transformées")
        # Vérification de normalité avec ses versions transformées
        result_norm = check_normality(transform(v))
        # Enregistrement de la figure
        fig = result_norm["Figure"]
        fig.tight_layout()
        fig.savefig(os.path.join(res_path, f"{k} Distribution ({n} samples) Normality Histogramm.png"), bbox_inches="tight")
        # Enregistrement du tableau récapitualtif
        result_norm["Dataframe"].to_csv(os.path.join(res_path, f"{k} Distribution ({n} samples) Normality Results.csv"), index=False)
        # Enregistrement du Rapport Complet
        make_normality_report(v, result_norm, f"{k} Distribution ({n} samples) Normality Report", res_path)

print("Fini")
