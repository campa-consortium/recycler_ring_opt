#!/usr/bin/env python
import os
import sys

import numpy as np
import synergia
MT = synergia.lattice.marker_type

# manipulate the chromaticity RR trim sextupole magnets

# In the lattice file, the sextupole currents are set by two
# parameters SF_I for "focussing" sextupole currents and SD_I
# for "defocussing" sextupole currents.  In turn, these are fanned
# out to other parametrized currents:

# Focussing:
focussing_currents = ["s112_i", "s128_i", "s330_i", "s412_i", "s428_i", "s630_i"]
defocussing_currents = ["s111_i", "s113_i", "s119_i", "s207_i", "s411_i", "s413_i", "s419_i", "s507_i", "s633_i"]

# S331_I is set to 0 because this magnets aren't installed meiqin@fnal.gov 2014-09-10

# list of focussing sextupoles
SF = [
    "s112",
    "s114",
    "s116",
    "s118",  # these magnets depend on s112_i
    "s128",
    "s130",
    "s202",
    "s204",  # these magnets depend on s128_i
    "s330",
    "s332",
    "s334",
    "s336",  # these magnets depend on s330_i
    "s412",
    "s414",
    "s416",
    "s418",  # these magnets depend on s412_i
    "s428",
    "s430",
    "s502",
    "s504",  # these magnets depend on s428_i
    # "s630", "s632", "s634", "s636"]  # these magnets depend on s630_i
    "s634",
    "s636",
]  # these magnets depend on s630_i

# list of defocussing sextupoles
SD = [
    "s111",  # this magnet depends on s111_i
    "s113",
    "s115",
    "s117",  # these magnets depend on s113_i
    "s119",
    "s121",
    "s123",
    "s125",
    "s127",
    "s129",  # these magnets depend on s119_i
    "s203",
    "s205",
    "s207",
    "s209",
    "s211",
    "s213",  # these magnets depend on s207_i
    # "s331", "s333", these magnets depend on s331_i which is set to 0
    "s411",  # this magnet depends on s411_i
    "s413",
    "s415",
    "s417",  # these magnets depend on s413_i
    "s419",
    "s421",
    "s423",
    "s425",
    "s427",
    "s429",  # these magnets depend on s419_i
    "s501",
    "s503",
    "s507",
    "s509",
    "s511",
    "s513",  # these magnets depend on s507_i
    "s633",
    "s635",
]  # these magnets depend on s633_i


# Mark focussing and defocussing sextupoles for chromaticity adjustment.
# return ( [list of focussing], [list of defocussing])
def mark_fd_sextupoles(lattice):
    f_sext = []
    d_sext = []
    for elem in lattice.get_elements():
        ename = elem.get_name()
        # print elem.as_string()
        in_f = False
        in_d = False
        if ename in SF:
            f_sext.append(elem)
            # print "elem in SF"
            in_f = True
            elem.set_marker(MT.h_chrom_corrector)
        if ename in SD:
            d_sext.append(elem)
            # print "elem in SD"
            in_d = True
            elem.set_marker(MT.v_chrom_corrector)
        if in_f and in_d:
            print("Error: element %s is in both focussing and defocussing sextupoles" % ename)

    return (f_sext, d_sext)


def print_focussing():
    print(len(SF), " focussing sextupoles: ", SF)


def print_defocussing():
    print(len(SD), "defocussing sextupoles: ", SD)


if __name__ == "__main__":
    # print_focussing()
    # print_defocussing()
    lattice = synergia.lattice.Lattice()
    synergia.lattice.xml_load_lattice(lattice, "rrnova_flat_fixed.xml")
    f_sext, d_sext = get_fd_sextupoles(lattice)
    print(len(f_sext), " focussing sextupoles")
    for elem in f_sext:
        print(elem.as_string())
    print(len(d_sext), " defocussing sextupoles")
    for elem in d_sext:
        print(elem.as_string())
