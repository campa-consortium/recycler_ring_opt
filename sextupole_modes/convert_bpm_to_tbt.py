#!/usr/bin/env python

import sys, os
import numpy as np
import pickle
import h5py

# Convert BPM data to tbt data as described by C. Gonzalez-Ortiz
#
# Use only the horizontally deflected particle which is particle
# 1 in the BPM data.

def main():

    # Load BPM info
    BPM_info = np.load("BPM_info.npy", allow_pickle=True)[()]
    # This is a dict with the keys being the
    # names of BPMs, eg. hp318, vp319, ...

    hbpm_data = {}
    vbpm_data = {}

    for bpm in BPM_info:
        bpmfile = f'BPM_{bpm}.h5'
        h5 = h5py.File(bpmfile, 'r')
        keyname = f'R:{bpm.upper()}'
        if bpm[0:2] == 'hp':
            # horizontal data
            print('collecting horizontal BPM data for ', keyname, ' file ', bpmfile)
            hdata = h5.get('track_coords')[:, 1, 0]
            hbpm_data[keyname] = {'x_mean': hdata}
        elif bpm[0:2] == 'vp':
            # vertical data
            print('collecting vertical BPM data for ', keyname, ' file ', bpmfile)
            vdata = h5.get('track_coords')[:, 1, 2]
            vbpm_data[keyname] = {'y_mean': vdata}
        else:
            raise(RuntimeError, 'What kind of bpm is this: ', bpm)
        h5.close()

        with open('TBT_data.pickle', 'wb') as f:
            pickle.dump([hbpm_data, vbpm_data], f)

if __name__ == "__main__":
    main()

