""" Classes des distributions """

import warnings
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.optimize import minimize

# ==================================================
# region Misc Functions
# ==================================================
##################################################
def get_kde(d):
    """
    Calcul de la courbe KDE (Kernel Density Estimation) de la distribution
    :param d: Distribution
    :return: Les données du tracé de la courbe
    """
    fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
    h = sns.kdeplot(d, ax=ax)                                            # Dessin du KDE de la seconde distribution
    return h.get_lines()[0].get_data()                                   # Récupération des courbes

##################################################
def get_kde_mse(d1, d2):
    """
    Calcul de la MSE (Mean Square Error) entre les coordonnées Y des courbes KDE (Kernel Density Estimation) de deux distributions
    :param d1: Première Distribution
    :param d2: Seconde Distribution
    :return: valeur de la MSE
    """
    kde1, kde2 = get_kde(d1), get_kde(d2)                                # Récupération des courbes
    return np.mean((kde1[1] - kde2[1]) ** 2)                             # Calcul du MSE entre les coordonnées Y des courbes

##################################################
def get_kde_curve_mse(d1, d2):
    """
    Calcul de la MSE (Mean Square Error) entre les courbes KDE (Kernel Density Estimation) de deux distributions
    :param d1: Première Distribution
    :param d2: Seconde Distribution
    :return: valeur de la MSE
    """
    kde1, kde2 = get_kde(d1), get_kde(d2)                                # Récupération des courbes
    return np.mean((kde1[0] - kde2[0]) ** 2 + (kde1[1] - kde2[1]) ** 2)  # Calcul du MSE entre les points des courbes

##################################################
def check_distributions(data):
    """
    Lance une analyse sur toutes les distributions et renvoie une figure des histogrammes et le résultat des analyses
    :param data: Distribution à analyser
    :return: Un dictionnaire contennant les éléments suivants
    - Figure : La figure contenant tous les histogrammes
    - Analysis : Le résultat de toutes les distributions
    - Dataframe : Dataframe récapitulatif (trié et arrondi à 10e-5)
    """
    distributions = [Normal, Log, Exponential, Power]
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=200)
    axes = axes.ravel()
    analysis = []
    for i in range(len(distributions)):
        analysis.append(distributions[i](data, axes[i]))
    res = combine_distributions(analysis)
    return dict(Figure=fig, Analysis=analysis, Dataframe=res)

##################################################
def combine_distributions(distributions):
    """
    Combine les différentes analyses de distributions en un seul dataframe
    :param distributions: liste des analyses
    :return: Dataframe contenant les informations calculées lors de l'analyse.
    Les éléments sont triés par MSE puis kurtosis et skewness en cas d'égalité et arrondi à 10e-5.
    """
    res = []
    columns = ["Distribution", "Parameters", "MSE", "Delta Kurtosis", "Delta Skewness",
               "Kolmogorov-Smirnov Test", "Shapiro-Wilk Test", "Wasserstein Distance",
               "Pearson Correlation Test on values", "Pearson Correlation Test on KDE",
               "Anderson-Darling Test on values", "Anderson-Darling Test on KDE"]
    for d in distributions:
        row = [f"{d.type}"]
        tmp = ""
        for k, v in d.params.items():
            tmp += f"{k} ({v}) "
        row.append(tmp)
        for i in range(2, len(columns)):
            tmp = d.results[columns[i]]
            if isinstance(tmp, dict):   row.append(d.results[columns[i]]["P"])
            else:                       row.append(d.results[columns[i]])
        res.append(row)
    return pd.DataFrame(res, columns=columns).sort_values(by=["MSE", "Delta Kurtosis", "Delta Skewness"]).round(5)

# ==================================================
# endregion Misc Functions
# ==================================================

# ==================================================
# region Base Distribution Class
# ==================================================
class _BaseDistribution(ABC):
    """ Classe mère des distributions """

    ##################################################
    def __init__(self, data=None, ax=None):
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
    def fit(self, data, ax=None):
        """
        Ajoute un tableau de nombre à la classe qui sera la distribution à analyser
        :param ax: Axe sur lequel dessiner nos histogrammes
        :param data: Tableau des nombres à ajouter
        """
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

    @abstractmethod
    def _cost(self, params):
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
            self.results["MSE"] = get_kde_mse(self.data, self.data_gen)
            # self.results["MSE Curve"] = get_kde_curve_mse(self.data, self.data_gen)
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
    def __init__(self, data=None, ax=None):
        super().__init__(data, ax)

    ##################################################
    @staticmethod
    def _get_type(): return "Normal"

    ##################################################
    def _cost(self, params): return 0.0

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
    def __init__(self, data=None, ax=None):
        super().__init__(data, ax)

    ##################################################
    @staticmethod
    def _get_type(): return "Log"

    ##################################################
    def _cost(self, params):
        self.params["Scale"] = params[0]
        # self._make_distribution()
        # return get_kde_mse(self.data, self.data_gen)
        return -np.sum(np.log(stats.lognorm(s=self.params["Scale"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0, 1.0]), method='Nelder-Mead')
        self._make_distribution()

    ##################################################
    def _make_distribution(self):
        self.data_gen = np.random.lognormal(self.params["Scale"], 1.0, len(self.data))

# ==================================================
# endregion Log Distribution Class
# ==================================================

# ==================================================
# region Exponential Distribution Class
# ==================================================
class Exponential(_BaseDistribution):

    ##################################################
    def __init__(self, data=None, ax=None):
        super().__init__(data, ax)

    ##################################################
    @staticmethod
    def _get_type(): return "Exponential"

    ##################################################
    def _cost(self, params):
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
    def __init__(self, data=None, ax=None):
        super().__init__(data, ax)

    ##################################################
    @staticmethod
    def _get_type(): return "Power"

    ##################################################
    def _cost(self, params):
        self.params["Alpha"] = params[0]
        return -np.sum(np.log(stats.powerlaw(self.params["Alpha"]).pdf(self.data)))

    ##################################################
    def _find_parameters(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Désactiver temporairement l'affichage des avertissements
            minimize(self._cost, np.array([1.0, 1.0]), method='Nelder-Mead')
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
        print(f"Log-Normal Distribution with {n} sample : Original mu ({mu}) VS Founded mu ({dist.params['Scale']})")
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

    # Check Distributions
    for n in sizes:
        results = check_distributions(np.random.normal(mu, sigma, n))
        print(results["Dataframe"])
# ==================================================
# endregion Tests
# ==================================================

# Liste des symboles à exporter (pour limiter les accès)
# __all__ = ["check_distributions", "Normal", "Exponential", "Power", "Log"]
