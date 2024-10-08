#!/usr/bin/env python
#

import synergia
import rr_tune_survey
import rr_setup
from rr_options import opts

RR_template_file = "RR2020V0922_TEMPLATE_fixed"
#RR_template_file = "RR2020V0922_TEMPLATE_wip"
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


#----------------------------------------------------------------------

def evaluate(kxl_values):

    lattice = generate_lattice(kxl_values)
    
    print("read lattice, ", len(lattice.get_elements()), ", length: ", lattice.get_length())

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

    return

#----------------------------------------------------------------------

# main() run evaluate() for representative set of KxL values
def main():

    # test unaltered lattice
    kxl_values = {
        'K1L_EVEN': 0.0112332575,
        'K1L_ODD': -0.00024562271,
        'K2L_EVEN': -0.0050223296,
        'K2L_ODD': -0.0331316105,
        'K3L_EVEN': 0.1297873,
        'K3L_ODD': -0.2137673
        }

    kxl_values = {}

    return evaluate(kxl_values)

#----------------------------------------------------------------------

if __name__ == "__main__":
    main()
