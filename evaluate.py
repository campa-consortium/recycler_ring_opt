#!/usr/bin/env python
#

import synergia
import rr_tune_survey
import rr_setup
from rr_options import opts
import rrnova_qt60x
import tune_suite
import h5py
import numpy as np

RR_template_file = "RR2020V0922_TEMPLATE_fixed"
#RR_template_file = "RR2020V0922FLAT_fixed"
RR_ring_name = "ring605_fodo"


"""
   Given input dict with parameters { 'kxl_even': xxx , ... 
                                      'kxl_odd': xxx, ...
                                    }
      given x in [1, 2, 3]
   propagate particles at a set of momenta in the Recycler ring and
   return the spectra or tunes.
"""


#----------------------------------------------------------------------

def generate_lattice(kxl_values):
    lattice = rr_tune_survey.get_rr_lattice_for_opt(RR_template_file, RR_ring_name, kxl_values)

    #  replacing old rr_setup.setup() do-it-all,
    if opts.start_element:
        lattice_tmp1 = rr_setup.reorder_lattice(lattice, opts.start_element)
    else:
        lattice_tmp1 = lattice

    lattice_tmp1a = rr_setup.convert_rbends_to_sbends(lattice_tmp1)

    if opts.lattice_simplify:
        lattice_tmp2 = rr_setup.keep_qt(lattice_tmp1a)
    else:
        lattice_tmp2 = lattice_tmp1a

    (xtune, ytune, cdt) = synergia.simulation.Lattice_simulator.calculate_tune_and_cdt(lattice_tmp2)

    print('generate_lattice, initial xtune: ', xtune, ', ytune: ', ytune)

    if opts.xtune_adjust or opts.ytune_adjust:
        print("Adjusting tunes to:")
        print("xtune: ", opts.xtune_adjust)
        print("ytune: ", opts.ytune_adjust)

        if opts.xtune_adjust:
            delta_xtune = opts.xtune_adjust - xtune
            print('delta_xtune: ', delta_xtune)
        else:
            delta_xtune = 0.0
        if opts.ytune_adjust:
            delta_ytune = opts.ytune_adjust - ytune
            print('delta_ytune: ', delta_ytune)
        else:
            delta_ytune = 0.0

        rrnova_qt60x.adjust_rr60_trim_quads(lattice_tmp2, delta_xtune, delta_ytune)

    lattice_tmp2.set_all_string_attribute("extractor_type", "libff")

    harmno = 588 # harmonic number

    # cavities in lattice_tmp2 are modified in-place
    rr_setup.setup_rf_cavities(lattice_tmp2, opts.rf_voltage, harmno)

    synergia.simulation.Lattice_simulator.tune_circular_lattice(lattice_tmp2)

    return lattice_tmp2

#----------------------------------------------------------------------

def save_lattice_txt(lattice, filename):
    if synergia.utils.Commxx().get_rank() == 0:
        with open(filename, 'w') as f:
            print(lattice, file=f)

#----------------------------------------------------------------------

def run_particles(lattice):
    # We're only  going to propagate a small number of particles
    # each at a different momentum to determine their tunes so I
    # don't really need the grid stuff.

    rr_tune_survey.run_rr(lattice, opts.turns)

#----------------------------------------------------------------------

# calculate the x and y tunes for each particle
def analyze_propagation():
    h5 = h5py.File('tracks.h5', 'r')
    trks = h5.get('track_coords')[()]
    npart = trks.shape[1]
    xtunes = np.zeros(npart)
    ytunes = np.zeros(npart)
    for n in range(npart):
        # calculate tunes this particle
        t = tune_suite.interp_tunes(trks[:, n, 0:6].transpose())
        xtunes[n] = t[0]
        ytunes[n] = t[1]
    return xtunes, ytunes

#----------------------------------------------------------------------

def evaluate(kxl_values, chatty=False):

    lattice = generate_lattice(kxl_values)
    
    if chatty:
        print("read lattice, ", len(lattice.get_elements()), ", length: ", lattice.get_length())

        save_lattice_txt(lattice, 'rr_lattice.out')

        (nux, nuy, cdT) = synergia.simulation.Lattice_simulator.calculate_tune_and_cdt(lattice)
        print('tune x: ', nux)
        print('tune y: ', nuy)
        print('cdT: ', cdT)
        print('T: ', cdT/synergia.foundation.pconstants.c)

        chrom_t = synergia.simulation.Lattice_simulator.get_chromaticities(lattice)

        print('horizontal chromaticity: ', chrom_t.horizontal_chromaticity)
        print('vertical chromaticity: ', chrom_t.vertical_chromaticity)
        print('compaction factor: ', chrom_t.momentum_compaction)
        print('slip factor: ', chrom_t.slip_factor)

    run_particles(lattice)

    return analyze_propagation()

#----------------------------------------------------------------------

# main() run evaluate() for representative set of KxL values
def main():

    # sample settings
    #kxl_values = {} # this one uses the unmodified multipole settings
                     # from the lattice file


    kxl_values = {         # this one has slight changes
        'K1L_EVEN': 0.01,
        'K1L_ODD': -0.005,
        'K2L_EVEN': -0.005,
        'K2L_ODD': -0.00033,
        'K3L_EVEN': 0.0000129,
        'K3L_ODD': -0.0000333,
        'K4L_EVEN': 0.0,
        'K4L_ODD':  0.0
        }

    return evaluate(kxl_values, True)

#----------------------------------------------------------------------

if __name__ == "__main__":
    main()
