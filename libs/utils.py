""" Diverses fonctions utiles """

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats

# ==================================================
# region KDE Functions
# ==================================================
##################################################
def get_kde(d: np.ndarray):
    """
    Calcul de la courbe KDE (Kernel Density Estimation) de la distribution
    :param d: Distribution
    :return: Les données du tracé de la courbe
    """
    if len(d) == 0: raise ValueError("Empty distribution is not allowed.")
    fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
    h = sns.kdeplot(d, ax=ax)                                            # Dessin du KDE de la seconde distribution
    return h.get_lines()[0].get_data()                                   # Récupération des courbes

##################################################
def get_kde_mse(d1: np.ndarray, d2: np.ndarray, axis: int = 1):
    """
    Calcul de la MSE (Mean Square Error) entre les coordonnées X ou Y des courbes KDE (Kernel Density Estimation) de deux distributions
    :param d1: Première Distribution
    :param d2: Seconde Distribution
    :param axis: Axe du calcul (0 pour X 1 pour Y), 1 par défaut
    :return: valeur de la MSE
    """
    if len(d1) == 0 or len(d2) == 0: raise ValueError("Empty distribution is not allowed.")
    kde1, kde2 = get_kde(d1), get_kde(d2)                                # Récupération des courbes
    return np.mean((kde1[axis] - kde2[axis]) ** 2)                       # Calcul du MSE entre les coordonnées Y des courbes

##################################################
def get_kde_curve_mse(d1: np.ndarray, d2: np.ndarray):
    """
    Calcul de la MSE (Mean Square Error) entre les courbes KDE (Kernel Density Estimation) de deux distributions
    :param d1: Première Distribution
    :param d2: Seconde Distribution
    :return: valeur de la MSE
    """
    if len(d1) == 0 or len(d2) == 0: raise ValueError("Empty distribution is not allowed.")
    kde1, kde2 = get_kde(d1), get_kde(d2)                                # Récupération des courbes
    return np.mean((kde1[0] - kde2[0]) ** 2 + (kde1[1] - kde2[1]) ** 2)  # Calcul du MSE entre les points des courbes

# ==================================================
# endregion KDE Functions
# ==================================================

# ==================================================
# region Transform Functions
# ==================================================
##################################################
def box_cox_test(data: np.ndarray):
    """
    Lance un calcul d'une transformation de Box Cox.
    :param data: Distribution à analyser
    :return: Retourne un dictionnaire contenant les données transformées, le lambda de la transformation ainsi que la nouvelle moyenne et ecart-type.
    """
    if len(data) == 0: raise ValueError("Empty array is not allowed.")
    if np.all(data == data[0]) or np.any(data <= 0): return None
    transformed, lambda_ = stats.boxcox(data)
    return dict(Transformed=transformed, Lambda=lambda_, Mu=np.mean(transformed), Sigma=np.std(transformed))

##################################################
def transform(data: np.ndarray):
    """
    Utilise plusieurs transformations modifiant la forme de la distribution sur le tableau en entrée
    :param data: Distribution à transformer
    :return: Retourne un dictionnaire contenant les données transformées avec :
    le logarithme, l'exponentiel, la puissance carrée, la racine carrée et la transformation inverse.
    """
    if len(data) == 0: raise ValueError("Empty array is not allowed.")
    return dict(Original=data,
                Log=np.log(data + 1) if np.all(data >= 0) else None,        # Seulement des valeurs positives pour le log (le + 1 pour éviter le gap du log)
                Exponential=np.exp(data) if np.all(data < 1234) else None,  # Overflow Exponential
                Square=np.power(data, 2),
                Root=np.power(data, 0.5) if np.all(data >= 0) else None,    # Seulement des valeurs positives pour la racine carrée
                Inverse=1 / data if np.all(data != 0) else None)            # Aucune division par 0.

# ==================================================
# endregion Transform Functions
# ==================================================

# ==================================================
# region Tests
# ==================================================
if __name__ == "__main__":
    print('TODO')
# ==================================================
# endregion Tests
# ==================================================
