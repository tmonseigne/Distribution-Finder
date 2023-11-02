""" Fichier principal """

import matplotlib.pyplot as plt
import numpy as np

from libs.distributions import Exponential, Log, Normal, Power

N = 1000
data = np.random.normal(12.6, 4.1, N)

fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=200)
axes = axes.ravel()
fig.show()

distributions = [Normal, Log, Exponential, Power]
for i in range(len(distributions)):
    dist = distributions[i](data, axes[i])
    print(dist)

fig.tight_layout()
fig.show()
fig.savefig("Distributions comparison.png", bbox_inches="tight")
fig.show()
