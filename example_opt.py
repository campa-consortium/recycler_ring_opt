import numpy as np
import evaluate

np.set_printoptions(precision=16)


Vals = np.loadtxt("tunefreq_fine.txt", skiprows=1, delimiter=",")
xtunes_target = Vals[:, 1]
ytunes_target = Vals[:, 2]

kxl_values = {
    "k1l_even": 0.01,
    "k1l_odd": -0.005,
    "k2l_even": -0.005,
    "k2l_odd": -0.00033,
    "k3l_even": 0.0000129,
    "k3l_odd": -0.0000333,
}

xtunes1, ytunes1 = evaluate.evaluate(kxl_values)

kxl_values = {
    "k1l_even": 0.0,
    "k1l_odd": 0.0,
    "k2l_even": 0.0,
    "k2l_odd": 0.0,
    "k3l_even": 0.0,
    "k3l_odd": 0.0,
}

xtunes2, ytunes2 = evaluate.evaluate(kxl_values)

print(np.linalg.norm(xtunes1 - xtunes2))
print(np.linalg.norm(ytunes1 - ytunes2))
