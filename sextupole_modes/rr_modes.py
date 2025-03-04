#!/usr/bin/env python
import sys, os
import pickle
import numpy as np
import re

import synergia

import mpi4py.MPI as MPI
myrank = MPI.COMM_WORLD.rank

import rr_setup

lattice_file = '../RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready'
RR_line = "ring605_fodo"

RR_xtune = 0.42
RR_ytune = 0.46
RR_xchrom = -4.44 # from C. Ortiz-Gonzalez 2025-02-18
RR_ychrom = -9.1 # from C. Ortiz-Gonzalez 2025-02-18

#------------------------------------------------------------------------

# Read parameter names here so they are globally available
with open('sext_names.pickle', 'rb') as f:
    sext_names = pickle.load(f)




#------------------------------------------------------------------------

# Edit the multipole moment parameters 
def prepare_lattice(params):
    f = open(lattice_file, 'r')
    lattice_txt = f.read()

    for p in params.keys():
        # The pattern to look for this name
        mp_pattern = f'{p}_K2L_offset:= 0.0'
        rep_pattern = f'{p}_K2L_offset:= {repr(params[p])}'
        subs = lattice_txt = re.sub(mp_pattern, rep_pattern, lattice_txt)
        if not subs:
            raise RuntimeError(f'error, no match for requested pattern {mp_pattern}')

    # write out the modified lattice text on rank 0
    if myrank == 0:
        with open("RR_modified.txt", "w") as f:
            f.write(lattice_txt)
    # 
    reader = synergia.lattice.Mad8_reader()
    reader.parse_string(lattice_txt)
    lattice_org1 = reader.get_lattice(RR_line)

    lattice_org2 = rr_setup.convert_rbends_to_sbends(lattice_org1)

    rr_setup.keep_qt(lattice_org2)

    # set tune with phase trombone (qt60x)
    # first need to get current tunes
    (xtune, ytune, cdt) = synergia.simulation.Lattice_simulator.calculate_tune_and_cdt(lattice_org2)

    rrnova_qt60x.adjust_rr60_trim_quads(lattice_org2,
                                        RR_xtune-xtune, RR_ytune-ytune)


    # set chromaticity
    rr_setup.set_chromaticity(RR_chromx, RR_chromy):

    return lattice

#------------------------------------------------------------------------

# run modes with the parameters given as a dict with element names as keys with the multipole offset as the value
def run_modes(params):

    # start with getting the lattice set up to use the requested
    # settings.
    lattice = prepare_lattice(params)

    if myrank == 0:
        print("read lattice, length: ", lattice.get_length(), len(lattice.get_elements()), "elements")

    return

#------------------------------------------------------------------------

# Just running the script will generate spectra with the default settings
def main():

    nparams = len(sext_names)

    # Generate the default settings dict
    default_params = {}
    for mn in sext_names:
        default_params[mn] = 0.0

    # test some settings
    # default_params['MPS109AD'] = -99.0
    # default_params['MP100AS'] = 3.14159
    # yes setting these parameters modifies the lattice

    # run it
    run_modes(default_params)


#------------------------------------------------------------------------

if __name__ == "__main__":
    main()
