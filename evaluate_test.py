import numpy as np
import evaluate



kxl_values = {
    "k1l_even": 0.0,
    "k1l_odd": 0.0,
    "k2l_even": 0.005,
    "k2l_odd": 0.0,
    "k3l_even": 0.0,
    "k3l_odd": 0.0
}

kxl_values2 = {
    "k1l_even": 0.0,
    "k1l_odd": 0.0,
    "k2l_even": 0.0,
    "k2l_odd": 0.0,
    "k3l_even": 1.0,
    "k3l_odd": 0.0
}

xtunes2, ytunes2 = evaluate.evaluate(kxl_values2)

xtunes1, ytunes1 = evaluate.evaluate(kxl_values)

xtunes0, ytunes0 = evaluate.evaluate({})

n = xtunes0.shape[0]

bigtunes = np.hstack((xtunes0.reshape(n, 1),
                      ytunes0.reshape(n, 1),
                      xtunes1.reshape(n, 1),
                      ytunes1.reshape(n, 1),
                      xtunes2.reshape(n, 1),
                      ytunes2.reshape(n, 1))
                     )

np.save('eval_test.npy', bigtunes)
