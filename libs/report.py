""" Fonctions permettant de créer un rapport """

import os
import numpy as np

##################################################
def _get_distribution_types(analysis: dict):
    """
    Récupère la liste des distributions testées
    :param analysis: Résultat de l'analyse
    :return: liste des distributions
    """
    types = []
    for a in analysis['Analysis']:
        types.append(a.type)
    return types

##################################################
def _add_fig(fig, name, path):
    fig.tight_layout()
    fig.savefig(os.path.join(path, name), bbox_inches="tight")
    return f"![Comparaison]({name})\n"

##################################################
def make_distribution_report(distribution: np.ndarray, analysis: dict, name: str = "Report", path: str = ""):
    """
    Créé un rapport markdown
    :param distribution: Distribution originale
    :param analysis: Résultat de l'analyse
    :param name: Nom du rapport
    :param path: Chemin du rapport
    """
    dist_types = _get_distribution_types(analysis)
    md_txt = f"# Analyse de la distribution\n\n"
    md_txt += (f"Distribution de {len(distribution)} samples ({type(distribution[0])}) "
               f"comparé avec {len(dist_types)} distributions : {', '.join(t for t in dist_types)}\n")

    # Ajout de la figure
    md_txt += f"\n## Figures de comparaison entre la distribution actuelle et celles générées\n\n"
    md_txt += _add_fig(analysis["Figure"], f"{name.replace(' ', '_')}-001.png", path)

    # Ajout du dataframe sous format de tableau
    md_txt += f"\n## Récapitulatif des comparaisons entre la distribution actuelle et celles générées\n\n"
    md_txt += analysis["Dataframe"].to_markdown(index=False) + "\n"

    # Ajout du blabla Box Cox
    md_txt += f"\n## Transformation de Box-Cox\n\n"
    if analysis['Box-Cox'] is None:
        md_txt += ("La transformation de Box-Cox n'a pu être effectué, car des données négatives étaient présentes dans la distrbution"
                   " ou celle-ci est constante.\n")
    else:
        md_txt += (f"Avec la transformation de Box-Cox on trouve un lambda λ ≈ {np.round(analysis['Box-Cox']['Lambda'], 3)}, "
                   f"une nouvelle moyenne μ ≈ {np.round(analysis['Box-Cox']['Mu'], 3)} "
                   f"et un nouvel écart-type σ ≈ {np.round(analysis['Box-Cox']['Sigma'], 3)} \n")

    # Ajout du blabla pour chaque distribution
    md_txt += f"\n## Comparaison distribution par distribution.\n\n"
    for i in range(len(dist_types)):
        md_txt += f"\n### Distribution Originale VS {dist_types[i]}\n\n"
        a = analysis['Analysis'][i]
        md_txt += f"Paramètres de la distribution {dist_types[i]} : {a.params}\n\n"
        md_txt += f"Resultats : \n\n"
        for test, value in a.results.items():
            md_txt += f"* {test} : {value}\n"
        md_txt += f"\n"

    # Enregistrement en .md
    with open(os.path.join(path, name+".md"), 'w', encoding='utf-8') as f:
        f.write(md_txt)
    # Enregistrement du md en pdf ?

##################################################
def make_normality_report(distribution: np.ndarray, analysis: dict, name: str = "Report", path: str = ""):
    """
    Créé un rapport markdown
    :param distribution: Distribution originale
    :param analysis: Résultat de l'analyse
    :param name: Nom du rapport
    :param path: Chemin du rapport
    """
    valid_transform = list(analysis['Distribution'].keys())
    md_txt = f"# Analyse de la normalité\n\n"
    md_txt += (f"Distribution de {len(distribution)} samples ({type(distribution[0])}) "
               f"comparé avec {len(valid_transform)} transformations : {', '.join(t for t in valid_transform)}\n")

    # Ajout de la figure
    md_txt += f"\n## Figures de comparaison entre la distribution normale et celles transformées\n\n"
    md_txt += _add_fig(analysis["Figure"], f"{name.replace(' ', '_')}-001.png", path)

    # Ajout du dataframe sous format de tableau
    md_txt += f"\n## Récapitulatif des comparaisons entre la distribution normale et celles transformées\n\n"
    md_txt += analysis["Dataframe"].to_markdown(index=False) + "\n"

    # Ajout du blabla pour chaque distribution
    md_txt += f"\n## Comparaison distribution par distribution.\n\n"
    for i in range(len(valid_transform)):
        md_txt += f"\n### Distribution Normale VS {valid_transform[i]}\n\n"
        a = analysis['Analysis'][i]
        md_txt += f"Paramètres de la transformation {valid_transform[i]} : {a.params}\n\n"
        md_txt += f"Resultats : \n\n"
        for test, value in a.results.items():
            md_txt += f"* {test} : {value}\n"
        md_txt += f"\n"

    # Enregistrement en .md
    with open(os.path.join(path, name+".md"), 'w', encoding='utf-8') as f:
        f.write(md_txt)
    # Enregistrement du md en pdf ?

# Liste des symboles à exporter (pour limiter les accès)
__all__ = ["make_distribution_report", "make_normality_report"]
