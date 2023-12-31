""" Classes des distributions """

import math
import warnings
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize

from libs.utils import get_kde, get_kde_curve_mse, get_kde_mse, box_cox_test

# ==================================================
# region Combine Functions
# ==================================================
##################################################
def get_values(analysis, head, columns):
    """
    Récupère les informations de l'analyse
    :param analysis: Analyse effectuée.
    :param head: Première valeur de la liste (le nom de la dsitribution do'rigine ou le nom de l'analyse par exemple).
    :param columns: Colonnes à enregistrer
    :return: une liste de chaine de caractères
    """
    res = [f"{head}"]
    tmp = ""
    for key, value in analysis.params.items():
        tmp += f"{key} ({value}) "
    res.append(tmp)
    for i in range(2, len(columns)):
        tmp = analysis.results[columns[i]]
        if isinstance(tmp, dict):   res.append(analysis.results[columns[i]]["P"])
        else:                       res.append(analysis.results[columns[i]])
    return res

##################################################
def check_distributions(data: np.ndarray, distributions: list = None):
    """
    Lance une analyse sur toutes les distributions et renvoie une figure des histogrammes et le résultat des analyses
    :param distributions: Liste des distributions à tester (par Défaut None signifie toutes)
    :param data: Distribution à analyser
    :return: Un dictionnaire contennant les éléments suivants
    - Figure : La figure contenant tous les histogrammes
    - Analysis : Le résultat de toutes les distributions
    - Dataframe : Dataframe récapitulatif (trié et arrondi à 10e-5)
    """
    if len(data) == 0: raise ValueError("Empty array is not allowed.")
    if distributions is None: distributions = [Normal, Log, Exponential, Power]

    n_dist = len(distributions)
    rows = round(math.sqrt(n_dist))         # Arrondir au lieu d'un cast en int car ça évite trop de différence entre le nombre de lignes et colonnes
    columns = (n_dist + rows - 1) // rows   # Arrondir vers le haut

    fig, axes = plt.subplots(rows, columns, figsize=(16, 10), dpi=200)
    axes = axes.ravel()
    analysis = []
    for i in range(n_dist):
        analysis.append(distributions[i](data, axes[i]))

    return {"Figure": fig, "Analysis": analysis, "Dataframe": combine_distributions(analysis), "Box-Cox": box_cox_test(data)}

##################################################
def combine_distributions(distributions: list):
    """
    Combine les différentes analyses de distributions en un seul dataframe
    :param distributions: liste des analyses
    :return: Dataframe contenant les informations calculées lors de l'analyse.
    Les éléments sont triés par MSE puis kurtosis et skewness en cas d'égalité et arrondi à 10e-5 pour faciliter la lecture.
    """
    if len(distributions) == 0: raise ValueError("Empty list is not allowed.")
    res = []
    columns = ["Distribution", "Parameters", "MSE", "MSE Scale", "MSE Curve", "Delta Kurtosis", "Delta Skewness",
               "Kolmogorov-Smirnov Test", "Shapiro-Wilk Test", "Wasserstein Distance",
               "Pearson Correlation Test on values", "Pearson Correlation Test on KDE",
               "Anderson-Darling Test on values", "Anderson-Darling Test on KDE"]
    for d in distributions: res.append(get_values(d, d.type, columns))
    return pd.DataFrame(res, columns=columns).sort_values(by=["MSE", "MSE Scale", "MSE Curve", "Delta Kurtosis", "Delta Skewness"]).round(5)

##################################################
def check_normality(distributions: dict):
    """
    Calcule pour chacune des distributions sa proximité avec une distribution normale
    :param distributions: liste des dsitributions (normalement plusieurs transformations d'une distribution d'origine)
    :return: Dictionnaire contenant les informations calculées lors de l'analyse.
    """
    if len(distributions) == 0: raise ValueError("Empty dictionnary is not allowed.")
    original_std = np.std(distributions["Original"])
    valid_distributions = dict()
    for name, array in distributions.items():
        # Si le tableau est valide (pas null et contenant des élémemnts non fini) et si son écart-type n'est pas aberrant par rapport à l'original
        if array is None or not np.isfinite(array).all() or original_std/np.std(array) < 1e-6: continue
        valid_distributions[name] = array
    if len(valid_distributions) == 0: raise ValueError("No valid array in dictionnary.")

    table = []
    cols_name = ["Distribution", "Parameters", "MSE Curve", "MSE", "MSE Scale", "Delta Kurtosis", "Delta Skewness",
                 "Kolmogorov-Smirnov Test", "Shapiro-Wilk Test", "Wasserstein Distance",
                 "Pearson Correlation Test on values", "Pearson Correlation Test on KDE",
                 "Anderson-Darling Test on values", "Anderson-Darling Test on KDE"]

    n_dist = len(valid_distributions)
    rows = round(math.sqrt(n_dist))  # Arrondir au lieu d'un cast en int car ça évite trop de différence entre le nombre de lignes et colonnes
    columns = (n_dist + rows - 1) // rows  # Arrondir vers le haut

    fig, axes = plt.subplots(rows, columns, figsize=(16, 10), dpi=200)
    axes = axes.ravel()
    analysis = []
    i = 0
    for name, array in valid_distributions.items():
        normal_analysis = Normal(array, axes[i])
        axes[i].set_title(f"{name} transformation (MSE: {np.round(normal_analysis.results['MSE Curve'], 3)})")
        table.append(get_values(normal_analysis, name, cols_name))
        analysis.append(normal_analysis)
        i += 1

    dataframe = pd.DataFrame(table, columns=cols_name).sort_values(by=["MSE Curve", "MSE", "MSE Scale", "Delta Kurtosis", "Delta Skewness"]).round(5)
    return dict(Figure=fig, Distribution=valid_distributions, Analysis=analysis, Dataframe=dataframe)

# ==================================================
# endregion Combine Functions
# ==================================================

# ==================================================
# region Base Distribution Class
# ==================================================
class _BaseDistribution(ABC):
    """ Classe mère des distributions """

    ##################################################
    def __init__(self, data: np.ndarray = None, ax: plt.axes = None):
        self.type = self._get_type()
        self.data, self.data_gen = None, None
        self.params = dict()
        self.results = dict()
        if data is not None: self.fit(data, ax)

    ##################################################
    @staticmethod
    def _get_type(): return "Generic"

    ##################################################
    def __str__(self): return (f"Distribution : {self.type}\n"
                               f"Parameters : {self.params}\n"
                               f"Results : \n{self.print_result()}")

    ##################################################
    def fit(self, data: np.ndarray, ax=None):
        """
        Ajoute un tableau de nombre à la classe qui sera la distribution à analyser
        :param ax: Axe sur lequel dessiner nos histogrammes
        :param data: Tableau des nombres à ajouter
        """
        if len(data) < 10: raise ValueError("Distribution must have at least 10 values.")
        self.data = data.copy()
        self._find_parameters()
        self._make_distribution()
        self.get_results()
        if ax is not None:
            self.plot(ax)

    ##################################################
    def plot(self, ax: plt.axes):
        """
        Dessine les distributions originales et généré
        :param ax: Axe
        """
        sns.histplot(self.data, kde=True, ax=ax)
        sns.histplot(self.data_gen, kde=True, ax=ax)
        ax.set_title(f"{self.type} Distribution (MSE: {np.round(self.results['MSE'], 3)})")
        ax.legend(["data", f"{self.type} Distribution"], title="Distribution")
        ax.set_xlabel("Values")

    @abstractmethod
    def _cost(self, params: np.ndarray):
        """
        Fonction de coût pour l'ajustement des paramètres de distributions
        :param params: Paramètres à trouver
        :return: MSE entre la distribution originale et celle calculée avec ces paramètres
        """
        pass

    ##################################################
    @abstractmethod
    def _find_parameters(self):
        """ Trouve les paramètres de la distribution """
        pass

    ##################################################
    @abstractmethod
    def _make_distribution(self):
        """ Créé une distribution à partir des paramètres """
        pass

    ##################################################
    def get_results(self):
        """ Calcule différentes métriques de comparaison de distributions """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            """ Calcule la différence entre la distribution stockée et la distribution générée """
            kde, kde_gen = get_kde(self.data), get_kde(self.data_gen)  # Récupération des courbes
            # Basic Tests
            self.results["MSE"] = get_kde_mse(self.data, self.data_gen, 1)
            self.results["MSE Scale"] = get_kde_mse(self.data, self.data_gen, 0)
            self.results["MSE Curve"] = get_kde_curve_mse(self.data, self.data_gen)
            self.results["Delta Kurtosis"] = np.fabs(stats.kurtosis(self.data) - stats.kurtosis(self.data_gen))
            self.results["Delta Skewness"] = np.fabs(stats.skew(self.data) - stats.skew(self.data_gen))
            # Kolmogorov-Smirnov (KS) Test
            ks = np.round(stats.kstest(self.data, self.data_gen), 3)
            self.results["Kolmogorov-Smirnov Test"] = dict(P=ks[0], S=ks[1])
            # Shapiro-Wilk Test
            s, p = stats.shapiro(self.data)
            s_gen, p_gen = stats.shapiro(self.data_gen)
            self.results["Shapiro-Wilk Test"] = dict(P=np.fabs(p - p_gen), S=np.fabs(s - s_gen))
            # Wasserstein Test
            self.results["Wasserstein Distance"] = stats.wasserstein_distance(kde[1], kde_gen[1])
            # Pearson Correlation Test
            s, p = stats.pearsonr(self.data, self.data_gen)
            self.results["Pearson Correlation Test on values"] = dict(P=p, S=s)
            s, p = stats.pearsonr(kde[1], kde_gen[1])
            self.results["Pearson Correlation Test on KDE"] = dict(P=p, S=s)
            # Anderson-Darling Test
            r = stats.anderson_ksamp([self.data, self.data_gen])
            self.results["Anderson-Darling Test on values"] = dict(P=r.significance_level, S=r.statistic)
            r = stats.anderson_ksamp([kde[1], kde_gen[1]])
            self.results["Anderson-Darling Test on KDE"] = dict(P=r.significance_level, S=r.statistic)

    ##################################################
    def print_result(self):
        """
        Mets en forme les résultats.
        :return: Les résultats sous forme d'une chaine de caractère
        """
        res = ""
        for test, value in self.results.items():
            res += f"\t{test} : {value}\n"
        return res

# ==================================================
# endregion Base Distribution Class
# ==================================================

# ==================================================
# region Normal Distribution Class
# ==================================================
class Normal(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Normal"

    ##################################################
    def _cost(self, params: np.ndarray): return 0.0

    ##################################################
    def _find_parameters(self):
        self.params = dict(Mu=np.mean(self.data), Sigma=np.std(self.data))

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.normal(self.params["Mu"], self.params["Sigma"], len(self.data))

# ==================================================
# endregion Normal Distribution Class
# ==================================================

# ==================================================
# region Log Distribution Class
# ==================================================
class Log(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Log"

    ##################################################
    def _cost(self, params: np.ndarray):
        self.params["Shape"] = params[0]
        # self._make_distribution()
        # return get_kde_mse(self.data, self.data_gen)
        return -np.sum(np.log(stats.lognorm(s=self.params["Shape"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0, 1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.lognormal(self.params["Shape"], 1.0, len(self.data))

# ==================================================
# endregion Log Distribution Class
# ==================================================

# ==================================================
# region Exponential Distribution Class
# ==================================================
class Exponential(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Exponential"

    ##################################################
    def _cost(self, params: np.ndarray):
        self.params["Scale"] = params[0]
        # self._make_distribution()
        # return get_kde_mse(self.data, self.data_gen)
        return -np.sum(np.log(stats.expon(scale=self.params["Scale"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.exponential(self.params["Scale"], len(self.data))

# ==================================================
# endregion Exponential Distribution Class
# ==================================================

# ==================================================
# region Power Distribution Class
# ==================================================
class Power(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Power"

    ##################################################
    def _cost(self, params: np.ndarray):
        self.params["Alpha"] = params[0]
        return -np.sum(np.log(stats.powerlaw(self.params["Alpha"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        if self.params["Alpha"] == 0:
            self.data_gen = np.full(len(self.data), self.params["Alpha"])
        elif self.params["Alpha"] > 0:
            self.data_gen = np.random.power(self.params["Alpha"], len(self.data))
        else:
            self.data_gen = 1 / np.random.power(-self.params["Alpha"], len(self.data))

# ==================================================
# endregion Power Distribution Class
# ==================================================

# ==================================================
# region Beta Distribution Class
# ==================================================
class Beta(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Beta"

    ##################################################
    def _cost(self, params: np.ndarray):
        self.params["A"] = params[0]
        self.params["B"] = params[1]
        return -np.sum(np.log(stats.beta(self.params["A"], self.params["B"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0, 1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.beta(self.params["A"], self.params["B"], len(self.data))

# ==================================================
# endregion Beta Distribution Class
# ==================================================

# ==================================================
# region Gamma Distribution Class
# ==================================================
class Gamma(_BaseDistribution):
    ##################################################
    @staticmethod
    def _get_type(): return "Gamma"

    ##################################################
    def _cost(self, params: np.ndarray):
        self.params["Shape"] = params[0]
        return -np.sum(np.log(stats.gamma(self.params["Shape"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.gamma(self.params["Shape"], 1.0, len(self.data))

# ==================================================
# endregion Gamma Distribution Class
# ==================================================

# # ==================================================
# # region Chi-Square Distribution Class
# # ==================================================
# class ChiSquare(_BaseDistribution):
#     ##################################################
#     @staticmethod
#     def _get_type(): return "Chi-Square"
#
#     ##################################################
#     def _cost(self, params: np.ndarray):
#         self.params["Degrees of freedom"] = params[0]
#         return -np.sum(np.log(stats.chi2(self.params["Degrees of freedom"]).pdf(self.data)))
#
#     ##################################################
#     def _find_parameters(self):
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
#             # On ajoute une limite pour que les degrés de liberté soient forcément positifs
#             minimize(self._cost, np.array([1.0]), method='Nelder-Mead', bounds=[(1e-6, None)])
#         self._make_distribution()
#
#     ##################################################
#     def _make_distribution(self):
#         self.data_gen = np.random.chisquare(self.params["Degrees of freedom"], len(self.data))
#
# # ==================================================
# # endregion Chi-Square Distribution Class
# # ==================================================
#
# # ==================================================
# # region Geometric Distribution Class
# # ==================================================
# class Geometric(_BaseDistribution):
#     ##################################################
#     @staticmethod
#     def _get_type(): return "Geometric"
#
#     ##################################################
#     def _cost(self, params: np.ndarray):
#         self.params["Probability"] = params[0]
#         return -np.sum(np.log(stats.geom(self.params["Probability"]).cdf(self.data)))
#
#     ##################################################
#     def _find_parameters(self):
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
#             # On ajoute une limite pour que la probabilité soit entre 0 et 1.
#             minimize(self._cost, np.array([1.0, 1.0]), method='Nelder-Mead', bounds=[(0.0, 1.0)])
#         self._make_distribution()
#
#     ##################################################
#     def _make_distribution(self):
#         self.data_gen = np.random.geometric(self.params["Probability"], len(self.data))
#
# # ==================================================
# # endregion Geometric Distribution Class
# # ==================================================
#
# # ==================================================
# # region Laplace Distribution Class
# # ==================================================
# class Laplace(_BaseDistribution):
#     ##################################################
#     @staticmethod
#     def _get_type(): return "Laplace"
#
#     ##################################################
#     def _cost(self, params: np.ndarray):
#         self.params["Position"] = params[0]
#         return -np.sum(np.log(stats.laplace(self.params["Position"]).pdf(self.data)))
#
#     ##################################################
#     def _find_parameters(self):
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
#             minimize(self._cost, np.array([1.0]), method='Nelder-Mead')
#         self._make_distribution()
#
#     ##################################################
#     def _make_distribution(self):
#         self.data_gen = np.random.laplace(self.params["Position"], 1.0, len(self.data))
#
# # ==================================================
# # endregion Laplace Distribution Class
# # ==================================================

# ==================================================
# region Tests
# ==================================================
if __name__ == "__main__":
    sizes = [10, 100, 1000]
    # Normal Distribution
    print("\n**************************************************")
    print("********** Normal Distribution : **********")
    mu, sigma = 12.6, 4.1
    for n in sizes:
        dist = Normal(np.random.normal(mu, sigma, n))
        print(f"Normal Distribution with {n} sample : Original mu ({mu}) VS Founded mu ({dist.params['Mu']}), "
              f"Original sigma ({sigma}) VS Founded sigma ({dist.params['Sigma']})")
        print(dist)

    # Log-Normal Distribution
    print("\n**************************************************")
    print("********** Log-Normal Distribution : **********")
    mu, sigma = 6.4, 1.0
    for n in sizes:
        dist = Log(np.random.lognormal(mu, sigma, n))
        print(f"Log-Normal Distribution with {n} sample : Original mu ({mu}) VS Founded mu ({dist.params['Shape']})")
        print(dist)

    # Exponential Distribution
    print("\n**************************************************")
    print("********** Exponential Distribution : **********")
    scale = 3.2
    for n in sizes:
        dist = Exponential(np.random.exponential(scale, n))
        print(f"Exponential Distribution with {n} sample : Original Scale ({scale}) VS Founded Scale ({dist.params['Scale']})")
        print(dist)

    # Power Distribution
    print("\n**************************************************")
    print("********** Power Distribution : **********")
    alpha = 2.5
    for n in sizes:
        dist = Power(np.random.power(alpha, n))
        print(f"Power Distribution with {n} sample : Original Alpha ({alpha}) VS Founded Alpha ({dist.params['Alpha']})")
        print(dist)

    # Beta Distribution
    print("\n**************************************************")
    print("********** Beta Distribution : **********")
    a, b = 2.5, 3.1
    for n in sizes:
        dist = Beta(np.random.beta(a, b, n))
        print(f"Beta Distribution with {n} sample : Original A ({a}) VS Founded A ({dist.params['A']}), "
              f"Original B ({b}) VS Founded B ({dist.params['B']})")
        print(dist)

    # Beta Distribution
    print("\n**************************************************")
    print("********** Gamma Distribution : **********")
    shape = 3.1
    for n in sizes:
        dist = Gamma(np.random.gamma(a, b, n))
        print(f"Gamma Distribution with {n} sample : Original Shape ({shape}) VS Founded Shape ({dist.params['Shape']})")
        print(dist)

    # Check Distributions
    for n in sizes:
        results = check_distributions(np.random.normal(mu, sigma, n))
        print(results["Dataframe"])
# ==================================================
# endregion Tests
# ==================================================

ALL_DISTRIBUTIONS = [Normal, Log, Exponential, Power, Beta, Gamma]

# Liste des symboles à exporter (pour limiter les accès)
# __all__ = ["check_distributions", "Normal", "Exponential", "Power", "Log"]
