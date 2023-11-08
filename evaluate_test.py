import numpy as np
import evaluate



kxl_values = {
    "k1l_even": 0.001,
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

xtunes1, ytunes1 = evaluate.evaluate(kxl_values)

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

