""" Fichier principal """

import os

import numpy as np
import pandas as pd


N = 1000
datas = {"Normal":      np.random.normal(12.6, 4.1, N),
         "Log":         np.random.lognormal(6.4, 1.0, N),
         "Exponential": np.random.exponential(3.2, N),
         "Power":       np.random.power(2.5, N)}

df = pd.DataFrame(datas)
df.to_csv("data.csv", index=False)
print("Fini")
