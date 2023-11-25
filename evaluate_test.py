import numpy as np
import evaluate



kxl_values = {
    "k1l_even": 0.001, # this value causes an unstable lattice
    "k1l_odd": 0.0,
    "k2l_even": 0.0,
    "k2l_odd": 0.0,
    "k3l_even": 0.0,
    "k3l_odd": 0.0,
    "k4l_even": 0.0,
    "k4l_odd": 0.0,
    "k5l_even": 0.0,
    "k5l_odd": 0.0
}

eval = evaluate.evaluate(kxl_values, chatty=True, adjust_tunes=True)
if eval is None:
    print(f'Lattice with values: {kxl_values}, is not stable or evaluatable')
else:
    xtunes1, ytunes1 = eval
    print('xtunes: ', xtunes1)
    print('ytunes: ', ytunes1)

# kxl_values2 = {
#     "k1l_even": 0.0,
#     "k1l_odd": 0.0,
#     "k2l_even": 0.0,
#     "k2l_odd": 0.0,
#     "k3l_even": 0.0,
#     "k3l_odd": 0.0,
#     "k4l_even": 0.0,
#     "k4l_odd": 0.0,
#     "k5l_even": 0.0,
#     "k5l_odd": 0.0
# }

# xtunes2, ytunes2 = evaluate.evaluate(kxl_values2)

