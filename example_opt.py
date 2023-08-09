import numpy as np
import evaluate

np.set_printoptions(precision=16)


Vals = np.loadtxt("tunefreq_fine.txt", skiprows=1, delimiter=",")
xtunes_target = Vals[:, 1]
ytunes_target = Vals[:, 2]

kxl_values = {
    "K1L_EVEN": 0.01,
    "K1L_ODD": -0.005,
    "K2L_EVEN": -0.005,
    "K2L_ODD": -0.00033,
    "K3L_EVEN": 0.0000129,
    "K3L_ODD": -0.0000333,
}

xtunes1, ytunes1 = evaluate.evaluate(kxl_values)

kxl_values = {
    "K1L_EVEN": 0.0,
    "K1L_ODD": 0.0,
    "K2L_EVEN": 0.0,
    "K2L_ODD": 0.0,
    "K3L_EVEN": 0.0,
    "K3L_ODD": 0.0,
}

xtunes2, ytunes2 = evaluate.evaluate(kxl_values)

print(np.linalg.norm(xtunes1 - xtunes2))
print(np.linalg.norm(ytunes1 - ytunes2))
