#!/usr/bin/env python
import sys, os
import numpy as np
import matplotlib.pyplot as plt

def main():
    bigtunes = np.load('eval_test.npy')

    params = {'legend.fontsize': 'x-large',
              'axes.labelsize': '24',
              'axes.titlesize':'20',
              'xtick.labelsize':'22',
              'ytick.labelsize':'22'}
    plt.rcParams.update(params)

    f = np.arange(-2000.0, 2050.0, 100.0)

    plt.plot(f, bigtunes[:, 4], 's', label='k3l_even = 1.0')
    plt.plot(f, bigtunes[:, 2], 'o', label='k2l_even = 0.005')
    plt.plot(f, bigtunes[:, 0], 'd', label='default')
    plt.xlabel('freq offset')
    plt.ylabel('x tunes')
    plt.legend(loc='upper right')

    plt.show()

if __name__ == "__main__":
    main()
