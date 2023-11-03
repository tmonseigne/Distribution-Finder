""" Fichier principal """

import matplotlib.pyplot as plt
import numpy as np

from libs.distributions import check_distributions

N = 1000
data = np.random.normal(12.6, 4.1, N)

results = check_distributions(data)
print(results["Analysis"][0])
fig = results["Figure"]
fig.tight_layout()
fig.savefig("Distributions comparison.png", bbox_inches="tight")
fig.show()

results["Dataframe"].round(5).to_csv("Distributions comparison.csv", index=False)
print(results["Dataframe"])
