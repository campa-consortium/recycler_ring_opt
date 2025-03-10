#!/usr/bin/env python
import sys, os
import pickle
import numpy as np
import re

import synergia
import synergia.simulation as SIM

import mpi4py.MPI as MPI
myrank = MPI.COMM_WORLD.rank

import rr_setup
import rrnova_qt60x
import rr_sextupoles

lattice_file = '../RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready'
RR_line = "ring605_fodo"

RR_xtune = 0.42
RR_ytune = 0.46
RR_chromx = -4.44 # from C. Ortiz-Gonzalez 2025-02-18
RR_chromy = -9.1 # from C. Ortiz-Gonzalez 2025-02-18

RF_voltage = 80.0e3 * 1.0e-9 # 80 KV


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


    f_sext, d_sext = rr_sextupoles.mark_fd_sextupoles(lattice_org2)
    print(f'There are {len(f_sext)} focussing sextupoles')
    print(f'There are {len(d_sext)} defocussing sextupoles')
    SIM.Lattice_simulator.adjust_chromaticities(lattice_org2, RR_chromx, RR_chromy, 1.0e-6, 20)

    rr_setup.setup_rf_cavities(lattice_org2, RF_voltage, 84)

    SIM.Lattice_simulator.set_closed_orbit_tolerance(1.0e-6)
    SIM.Lattice_simulator.tune_circular_lattice(lattice_org2)

    return lattice_org2

#------------------------------------------------------------------------

# run modes with the parameters given as a dict with element names as keys with the multipole offset as the value
def run_modes(params):

    # start with getting the lattice set up to use the requested
    # settings.
    lattice = prepare_lattice(params)

    if myrank == 0:
        print("read lattice, length: ", lattice.get_length(), len(lattice.get_elements()), "elements")

    tunes = SIM.Lattice_simulator.calculate_tune_and_cdt(lattice)
    xtune = tunes[0]
    ytune = tunes[1]

    if myrank == 0:
        print("adjusted xtune: ", xtune)
        print("adjusted ytune: ", ytune)

    chroms = SIM.Lattice_simulator.get_chromaticities(lattice)
    xchrom = chroms.horizontal_chromaticity
    ychrom = chroms.vertical_chromaticity


    if myrank == 0:
        print('adjusted horizontal chromaticity: ', xchrom)
        print('adjust vertical chromaticity: ', ychrom)

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
