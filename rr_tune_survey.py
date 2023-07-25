# from mpi4py import MPI
import numpy as np
import synergia

import rr_setup

from rr_options import opts

def print_statistics(bunch):
    parts = bunch.get_particles_numpy()
    print(parts.shape, ", ", parts.size)
    print("shape: {0}, {1}".format(parts.shape[0], parts.shape[1]))

    mean = synergia.bunch.Core_diagnostics.calculate_mean(bunch)
    std = synergia.bunch.Core_diagnostics.calculate_std(bunch, mean)
    print("mean = {}".format(mean))
    print("std = {}".format(std))

# Use the template RR lattice and passed in values for kxL moments
# to construct the lattice for determining tunes vs. momentum

#-----------------------------------------------------------------------

def get_rr_lattice_for_opt(RR_template, RR_line, kxl_values):
    with open(RR_template, 'r') as template:
        template = template.read()

    # Values for K0LEVEN and K0L_ODD are set to 0 in the template itself.
    k1leven = kxl_values.get('k1l_even', 0)
    k1lodd = kxl_values.get('k1l_odd', 0)
    k2leven = kxl_values.get('k2l_even', 0)
    k2lodd = kxl_values.get('k2l_odd', 0)
    k3leven = kxl_values.get('k3l_even', 0)
    k3lodd = kxl_values.get('k3l_odd', 0)

    header = ""
    header = header + "VALUEFOR_K1L_EVEN := {:22g}\n".format(k1leven)
    header = header + "VALUEFOR_K1L_ODD := {:22g}\n".format(k1lodd)

    header = header + "VALUEFOR_K2L_EVEN := {:22g}\n".format(k2leven)
    header = header + "VALUEFOR_K2L_ODD := {:22g}\n".format(k2lodd)

    header = header + "VALUEFOR_K3L_EVEN := {:22g}\n".format(k3leven)
    header = header + "VALUEFOR_K3L_ODD := {:22g}\n".format(k3lodd)

    rr_full = header+template

    # For when I need to see what is being sent to the parser
    # f = open('xyzzy.txt', 'w')
    # f.write(rr_full)
    # f.close()

    reader = synergia.lattice.Mad8_reader()
    reader.parse_string(rr_full)

    lattice = reader.get_lattice(RR_line)

    return lattice

#-----------------------------------------------------------------------

def get_lattice_rr():
    lattice_file = open("rr_tuned.json", "r")
    lattice = synergia.lattice.Lattice.load_from_json(lattice_file.read())

    lattice.set_all_string_attribute("extractor_type", "libff")
    # synergia.simulation.Lattice_simulator.tune_circular_lattice(lattice)
    return lattice


def get_dpop_offsets():
    # We're going to create particles with momenta at frequency offsets
    # between -2000 and +2000 (Hz) at intevals of 100 Hz.
    
    # From Rob Ainsworth:
    #revtime=11.135e-6
    revtime = 1.1134653259322681e-05
    h=588.
    eta = -0.0087165
    # dpop=df*revtime/h/np.abs(eta)

    # d(1/T) = -(1/T) * (dt/T)
    #        = -(1/T) * eta * (dp/p)
    #
    # f = h * (1/T)
    # df = h * d(1/T) = h * (-1/T) * eta * (dp/p)
    #
    # dp/p = df * -T/(h * eta) 

    min_freq_off = opts.min_freq_offset
    max_freq_off = opts.max_freq_offset
    freq_step = opts.freq_offset_step
    # add half step to max so the upper frequency is included in range
    df_list = np.arange(min_freq_off, max_freq_off+0.5*freq_step, freq_step)
    dpop_list = df_list * revtime/(h*np.abs(eta))
    return dpop_list

#-----------------------------------------------------------------------

# Create the simulator object for the simulation which characteristics
# determined by the reference particle

def create_simulator(lattice, screen):
    ref_part = lattice.get_reference_particle()

    # We're only  going to propagate a small number of particles
    # each at a different momentum to determine their tunes so I
    # don't really need the grid stuff.

    dpop_offsets = get_dpop_offsets()
    print('Number of frequencies to run: ', len(dpop_offsets), file=screen)
    print('    offsets from ', dpop_offsets[0], 'to', dpop_offsets[-1], file=screen)

    macro_particles = len(dpop_offsets)
    print("Number of macroparticles:", macro_particles, file=screen)

    real_particles = 1.0e9     # propagating without space charge
    
    spacing = synergia.simulation.Lattice_simulator.get_bucket_length(lattice)
    num_bunches=1

    # Get tuned Recycler lattice and reference particle for lattice
    ref_part = lattice.get_reference_particle()

    # Initiate bunch simulator (For now single bunch)
    sim = synergia.simulation.Bunch_simulator.create_bunch_train_simulator(
        ref_part, macro_particles, real_particles, num_bunches, spacing
    )

    # Enforce longitudinal bucket conditions (Mandatory if RF is turned on)
    sim.set_longitudinal_boundary(synergia.bunch.LongitudinalBoundary.aperture, spacing)

    bunch = sim.get_bunch()
    bunch.checkout_particles()
    lp = bunch.get_particles_numpy()
    np = macro_particles
    
    # we can start all the particles at 0
    lp[:, 0:5] = 0.0
    # The total size of the array is padded for alignment so I limit the
    # the index of particle number to match the size of dpop_offsets
    lp[:np, 5] = dpop_offsets

    bunch.checkin_particles()

    return sim

#-----------------------------------------------------------------------

def create_propagator(comm, lattice):
    # this next block shows propagation with space charge.
    # Define space-charge operator (For now no space charge)
    # steps = 416  # Number of steps to use for stepper (What does this mean?)
    # sc_ops = synergia.collective.Dummy_CO_options()  # No space-charge option
    # stepper = synergia.simulation.Split_operator_stepper(sc_ops, steps)

    # Define propagation without space charge
    sc_ops = synergia.collective.Dummy_CO_options()   # No space-charge option
    stepper = synergia.simulation.Split_operator_stepper(sc_ops, 1)

    # Define propagator for simulations
    propagator = synergia.simulation.Propagator(lattice, stepper)

    return propagator

#-----------------------------------------------------------------------

# register the diagnostics needed to get the tune data
# into the simulator which is passed in.

def register_diagnostics(sim):
# Define diagnostics to run
    # For now keep options to single bunch

    # we don't need no steenkin particles, we're only interested in tracks
    # Track individual particles and save to individual files
    #part_track = macro_particles  # Number of particles to track
    #nturns_track = 1  # Number of turns between each tracking
    #diag_part = synergia.bunch.Diagnostics_particles("particles.h5", part_track)
    # bunch statistics aren't useful for this purpose so we skip them
    # Get mean diagnostics for single bunch at every turn
    #diag = synergia.bunch.Diagnostics_full2("diag.h5")
    #sim.reg_diag_per_turn(diag)

    # Save tracking data for all 41 particles
    npart = sim.get_bunch().size()
    diagtrk = synergia.bunch.Diagnostics_bulk_track("tracks.h5", npart)
    sim.reg_diag_per_turn(diagtrk)

    return sim

#-----------------------------------------------------------------------

# run a set of off-momentum particles for 2000 turns through the lattice
# previously set up.

def run_rr(lattice, turns):

    screen = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.DEBUG)

    sim = create_simulator(lattice, screen)

    # Initiate parallel communication protocol
    comm = synergia.utils.parallel_utils.Commxx()

    propagator = create_propagator(comm, lattice)

    register_diagnostics(sim)
        
    # Set maximum number of turns to simulate
    max_turns = turns
    sim.set_max_turns(turns)

    # Define logs and screens to print out alarms and logs
    simlog = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.INFO_TURN)
    #simlog = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.INFO)

    # Propagate simulation for certain number of turns
    propagator.propagate(sim, simlog, turns)


#-----------------------------------------------------------------------

def main():
    print("Running Recycler Ring Simulation (No Space Charge)")
    run_rr()


if __name__ == "__main__":
    main()
