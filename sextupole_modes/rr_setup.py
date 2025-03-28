#!/usr/bin/env python

import os
import re
import sys

# import mpi4py.MPI as MPI
import numpy as np
import synergia
import synergia.simulation as SIM
MT = synergia.lattice.marker_type
ET = synergia.lattice.element_type

import rr_sextupoles
import rrnova_qt60x


# quick and dirty twiss parameter calculator from 2x2 courant-snyder map array
def map2twiss(csmap):
    cosmu = 0.5 * (csmap[0, 0] + csmap[1, 1])
    asinmu = 0.5 * (csmap[0, 0] - csmap[1, 1])

    if abs(cosmu) > 1.0:
        raise RuntimeError("map is unstable")

    mu = np.arccos(cosmu)

    # beta is positive
    if csmap[0, 1] < 0.0:
        mu = 2.0 * np.pi - mu

    beta = csmap[0, 1] / np.sin(mu)
    alpha = asinmu / np.sin(mu)
    tune = mu / (2.0 * np.pi)

    return (alpha, beta, tune)


def convert_rbends_to_sbends(orig_lattice):
    lattice = synergia.lattice.Lattice("rrnova")
    for elem in orig_lattice.get_elements():
        if elem.get_type_name() == "rbend":
            new_elem = synergia.lattice.Lattice_element("sbend", elem.get_name())

            new_elem.copy_attributes_from(elem)

            ang = elem.get_double_attribute("angle")
            length = elem.get_double_attribute("l")
            arclength = ang * length / (2.0 * np.sin(ang / 2.0))
            new_elem.set_double_attribute("l", arclength)
            new_elem.set_double_attribute("e1", ang / 2.0)
            new_elem.set_double_attribute("e2", ang / 2.0)
            lattice.append(new_elem)
        else:
            lattice.append(elem)
    lattice.set_reference_particle(orig_lattice.get_reference_particle())
    return lattice


def keep_qt(lattice):
    valid_trim_name_regex = "qt60([1-9])[a-d]"
    trimobj = re.compile(valid_trim_name_regex)
    for elem in lattice.get_elements():
        if elem.get_type_name() == "quadrupole":
            qname = elem.get_name()
            mo = trimobj.match(elem.get_name())
            if mo:
                elem.set_string_attribute("no_simplify", "save me!")
    return lattice


# Reorder the lattice if needed
def reorder_lattice(lattice, start_element=None):
    if start_element:
        new_lattice = synergia.lattice.Lattice("mi", lattice.get_element_adaptor_sptr())

        elements = lattice.get_elements()
        names = [e.get_name() for i in elements]
        if opts.start_element not in names:
            raise RuntimeError("start element "+opts.start_element+" not in lattice")

        start_i = names.index(start_element)
        reorder_alements = elements[start_i:] + elements[0:start_i]

        for elem in reorder_elements:
            new_lattice.append(elem)

        new_lattice.set_design_reference_particle(lattice.get_design_reference_particle())
        new_lattice.set_reference_particle(lattice.get_reference_particle())

        return new_lattice
    else:
        return lattice

#----------------------------------------------------------------------------------

#
#From: Eric G Stern
#Sent: Tuesday, February 18, 2025 11:25 AM
#To: Cristhian E. Gonzalez-Ortiz
#Cc: Jason Michael St.John
#Subject: RE: RF cavity settings for TBT BPM data 
#
#Thanks! In the lattice file would that be the first RFCAV53MHz element in line HC607?
# 
#    Eric
# 
#From: Cristhian E. Gonzalez-Ortiz <gonza839@fnal.gov>
#Sent: Tuesday, February 18, 2025 11:18 AM
#To: Eric G Stern <egstern@fnal.gov>
#Cc: Jason Michael St.John <stjohn@fnal.gov>
#Subject: Re: RF cavity settings for TBT BPM data
# 
#Hi Eric,
# 
#The RF cavity (53 MHz) Station A should be close to 80 kV. I don't recall the specific number, but 80 kV should pretty close.
 #
#Best,
# 
#Cris

# lattice is input lattice
# rf_voltage is the voltage in GV
# harmno is the harmonic number
# modifies elements in lattice in-place

def setup_rf_cavities(lattice, rf_voltage, harmno):

    # rf cavity voltage, is in GV.
    # expects cavities voltages in  units of MV.

    num_cavities = 0
    rfcav53mhz = None
    # First turn off all RF cavities except for one
    for elem in lattice.get_elements():
        if elem.get_type() == ET.rfcavity:
            num_cavities = num_cavities + 1
            elem.set_double_attribute("volt", 0.0)
            elem.set_double_attribute("harmon", harmno)
            elem.set_double_attribute("freq", 0.0)
            # is this the first rfcav53mhz (all names or lowercase)
            if (elem.get_name() == "rfcav53mhz") and (rfcav53mhz is None):
                rfcav53mhz = elem
                elem.set_double_attribute("volt", rf_voltage*1.0e3)

    if num_cavities < 1:
        raise RuntimeError("error: set_rf_cavities: no RF cavities found")
    if not rfcav53mhz:
        raise RuntimeError("error: the 53 MHz RF cavity was not found.")

    return

#----------------------------------------------------------------------------------

def setup():
    raise RuntimeError("Do not call setup anymore, call individual setup routines!")

    try:
        logger = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.DEBUG)

        # logger = synergia.utils.Logger(0)

        # tjob_0 = MPI.Wtime()

        # memlogger = synergia.utils.Logger("memlog")

        # ============================================
        # get parameters for run

        rf_voltage = opts.rf_voltage

        print("==== Run Summary ====", file=logger)
        print("RF Voltage: ", rf_voltage, file=logger)

        if opts.xtune_adjust:
            print("x tune adjustment: ", opts.xtune_adjust, file=logger)
        else:
            print("x tune adjustment: NONE", file=logger)
        if opts.ytune_adjust:
            print("y tune adjustment: ", opts.ytune_adjust, file=logger)
        else:
            print("y tune adjustment: NONE", file=logger)

        if opts.xchrom_adjust:
            print("x chromaticity adjustment: ", opts.xchrom_adjust, file=logger)
        else:
            print("x chromaticity adjustment: NONE", file=logger)

        if opts.ychrom_adjust:
            print("y chromaticity adjustment: ", opts.ychrom_adjust, file=logger)
        else:
            print("y chromaticity adjustment: NONE", file=logger)

        # ============================================

        # read the lattice and
        # turn on the RF by setting voltage, frequency and phase in RF cavities

        lattice_file = "RR2020V0922FLAT_fixed"

        ring_name = "ring605_fodo"
        lattice = synergia.lattice.Mad8_reader().get_lattice(ring_name, lattice_file)

        """
        lsexpr = synergia.utils.pylsexpr.read_lsexpr_file("mi20_raw.lsx")
        lattice = synergia.lattice.Lattice(lsexpr)
        """
        lattice = convert_rbends_to_sbends(lattice)

        print("lattice # elements: ", len(lattice.get_elements()))
        print("lattice length: ", lattice.get_length())

        harmno = 588

        if opts.start_element:
            print("reordering lattice to start at ", opts.start_element, file=logger)
            new_lattice = synergia.lattice.Lattice("mi", lattice.get_element_adaptor_sptr())
            copying = False
            start_i = -1
            elements = lattice.get_elements()
            for i in range(len(elements)):
                if elements[i].get_name() == opts.start_element:
                    start_i = i
                    break
            reorder_elements = elements[start_i:] + elements[:start_i]
            for elem in reorder_elements:
                new_lattice.append(elem)

            new_lattice.set_reference_particle(lattice.get_reference_particle())
            print("new lattice length: ", new_lattice.get_length(), file=logger)
            lattice = new_lattice

        if opts.lattice_simplify:
            lattice = keep_qt(lattice)
            lattice = synergia.lattice.simplify_all(lattice)
            print("lattice # elements after simplification: ", len(lattice.get_elements()))
            print("lattice length after simplification: ", lattice.get_length())

        # ============================================

        lattice.set_all_string_attribute("extractor_type", "libff")

        # turn on the RF cavities
        reference_particle = lattice.get_reference_particle()
        energy = reference_particle.get_total_energy()
        beta = reference_particle.get_beta()
        gamma = reference_particle.get_gamma()

        print("energy: ", energy, file=logger)
        print("beta: ", beta, file=logger)
        print("gamma: ", gamma, file=logger)

        # set rf cavity frequency
        # harmno * beta * c/ring_length
        freq = harmno * beta * synergia.foundation.pconstants.c / lattice.get_length()
        # only for informational purposes
        print("RF frequency: ", freq, file=logger)

        print("Begin setting RF voltage...", file=logger)

        # rf cavity voltage, is 1.0 MV total distributed over 18 cavities.  MAD8
        # expects cavities voltages in  units of MV.
        num_cavities = 0
        for elem in lattice.get_elements():
            if elem.get_type() == synergia.lattice.element_type.rfcavity:
                # set the harmonic number so the frequency is set
                elem.set_double_attribute("harmon", harmno)
                # set the first pass frequency so I can get the bucket length
                elem.set_double_attribute("freq", freq * 1.0e-6)
                if num_cavities < 1:
                    elem.set_double_attribute("volt", rf_voltage)
                    num_cavities += 1
                else:
                    elem.set_double_attribute("volt", 0.0)

        print("Finish setting RF voltage...", file=logger)

        # ============================================
        # adjust the tune and chromaticity of requested

        SIM.Lattice_simulator.set_closed_orbit_tolerance(1.0e-6)
        SIM.Lattice_simulator.tune_circular_lattice(lattice)

        tunes = SIM.Lattice_simulator.calculate_tune_and_cdt(lattice)
        xtune = tunes[0]
        ytune = tunes[1]

        chroms = SIM.Lattice_simulator.get_chromaticities(lattice)
        xchrom = chroms.horizontal_chromaticity
        ychrom = chroms.vertical_chromaticity

        # adjust the tunes
        print("Unadjusted x tune: ", xtune, file=logger)
        print("Unadjusted y tune: ", ytune, file=logger)

        if opts.xtune_adjust or opts.ytune_adjust:
            if opts.xtune_adjust:
                delta_xtune = opts.xtune_adjust - xtune
            else:
                delta_xtune = 0.0
            if opts.ytune_adjust:
                delta_ytune = opts.ytune_adjust - ytune
            else:
                delta_ytune = 0.0

            print("Adjusting tunes to:", file=logger)
            print("xtune: ", opts.xtune_adjust, file=logger)
            print("ytune: ", opts.ytune_adjust, file=logger)

            rrnova_qt60x.adjust_rr60_trim_quads(lattice, delta_xtune, delta_ytune)

            tunes = SIM.Lattice_simulator.calculate_tune_and_cdt(lattice)
            xtune = tunes[0]
            ytune = tunes[1]

            print("adjusted xtune: ", xtune, file=logger)
            print("adjusted ytune: ", ytune, file=logger)

        print("Unadjusted x chromaticity: ", xchrom, file=logger)
        print("Unadjusted y chromaticity: ", ychrom, file=logger)

        if opts.xchrom_adjust or opts.ychrom_adjust:
            if opts.xchrom_adjust:
                xchrom = opts.xchrom_adjust

            if opts.ychrom_adjust:
                ychrom = opts.ychrom_adjust

            print("Adjusting chromaticities to:", file=logger)
            print("x chrom: ", xchrom, file=logger)
            print("y chrom: ", ychrom, file=logger)

            f_sext, d_sext = rr_sextupoles.get_fd_sextupoles(lattice)
            print("There are ", len(f_sext), " focussing sextupoles", file=logger)
            print("There are ", len(d_sext), " defocussing sextupoles", file=logger)

            SIM.Lattice_simulator.adjust_chromaticities(lattice, xchrom, ychrom, 1.0e-6, 20)

            chroms = SIM.Lattice_simulator.get_chromaticities(lattice)
            xchrom = chroms.horizontal_chromaticity
            ychrom = chroms.vertical_chromaticity

            print("adjusted x chrom: ", xchrom, file=logger)
            print("adjusted y chrom: ", ychrom, file=logger)

        # The lattice is tuned now, write it out
        # synergia.utils.write_lsexpr_file(lattice.as_lsexpr(), "mi20_ra_08182020_tuned.lsx")

        # Get the covariance matrix
        map = SIM.Lattice_simulator.get_linear_one_turn_map(lattice)
        print("one turn map from synergia2.5 infrastructure", file=logger)
        print(np.array2string(map, max_line_width=200), file=logger)

        [l, v] = np.linalg.eig(map)

        # print "l: ", l
        # print "v: ", v

        print("eigenvalues: ", file=logger)
        for z in l:
            print("|z|: ", abs(z), " z: ", z, " tune: ", np.log(z).imag / (2.0 * np.pi), file=logger)

        [ax, bx, qx] = map2twiss(map[0:2, 0:2])
        [ay, by, qy] = map2twiss(map[2:4, 2:4])
        [az, bz, qz] = map2twiss(map[4:6, 4:6])
        stdz = opts.stdz
        dpop = stdz / bz

        print("Lattice parameters (assuming uncoupled map)", file=logger)
        print("alpha_x: ", ax, " alpha_y: ", ay, file=logger)
        print("beta_x: ", bx, " beta_y: ", by, file=logger)
        print("q_x: ", qx, " q_y: ", qy, file=logger)
        print("beta_z: ", bz, file=logger)
        print("delta p/p: ", dpop, file=logger)

        emitx = opts.norm_emit / (beta * gamma)
        emity = opts.norm_emit / (beta * gamma)

        stdx = np.sqrt(emitx * bx)
        stdy = np.sqrt(emity * by)

        print("emitx: ", emitx, file=logger)
        print("emity: ", emity, file=logger)
        print("target stdx: ", stdx, file=logger)
        print("target stdy: ", stdy, file=logger)

        # =========================================
        #
        # get the correlation matrix for bunch generation

        correlation_matrix = synergia.bunch.get_correlation_matrix(map, stdx, stdy, stdz / beta, beta, (0, 2, 4))

        np.save("correlation_matrix.npy", correlation_matrix)
        print(np.array2string(correlation_matrix, max_line_width=200), file=logger)

        # write the lattice in json
        lattice_file = open("rr_tuned.json", "w")
        lattice_file.write(lattice.as_json())
        lattice_file.close()

    except Exception as e:
        sys.stdout.write(str(e) + "\n")
        # MPI.COMM_WORLD.Abort(777)


if __name__ == "__main__":
    setup()

# main()
