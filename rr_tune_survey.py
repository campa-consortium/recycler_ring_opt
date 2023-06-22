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
    revtime=11.135e-6
    h=588.
    eta=-8.7e-3
    # dpop=df*revtime/h/np.abs(eta)

    min_freq_off = opts.min_freq_offset
    max_freq_off = opts.max_freq_offset
    freq_step = opts.freq_offset_step
    # add half step to max so the upper frequency is included in range
    df_list = np.arange(min_freq_off, max_freq_off+0.5*freq_step, freq_step)
    dpop_list = df_list * revtime/(h*np.abs(eta))
    return dpop_list

def run_rr():
    screen = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.DEBUG)

    # Run Recyler setup in order to tune lattice
    # Run rr_setup to get covariance matrix in order to populate bunches
    rr_setup.setup()

    # We're only  going to propagate a small number of particles
    # each at a different momentum to determine their tunes so I
    # don't really need the grid stuff.

    dpop_offsets = get_dpop_offsets()
    print('Number of frequencies to run: ', len(dpop_offsets), file=screen)
    print('    offsets from ', dpop_offsets[0], 'to', dpop_offsets[-1], file=screen)

    macro_particles = len(dpop_offsets)
    print("Number of macroparticles:", macro_particles, file=screen)

    real_particles = 1.0e9     # propagating without space charge
    
    spacing = 5.64526987439  # Bucket length calculated from synergia2
    num_bunches=1

    # Get tuned Recycler lattice and reference particle for lattice
    lattice = get_lattice_rr()
    ref_part = lattice.get_reference_particle()

    # Initiate bunch simulator (For now single bunch)
    sim = synergia.simulation.Bunch_simulator.create_bunch_train_simulator(
        ref_part, macro_particles, real_particles, num_bunches, spacing
    )

    # Enforce longitudinal bucket conditions (Mandatory if RF is turned on)
    sim.set_longitudinal_boundary(synergia.bunch.LongitudinalBoundary.periodic, spacing)

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

    # Initiate parallel communication protocol
    comm = synergia.utils.parallel_utils.Commxx()

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

    # Define diagnostics to run
    # For now keep options to single bunch

    # Track individual particles and save to individual files
    part_track = macro_particles  # Number of particles to track
    nturns_track = 1  # Number of turns between each tracking
    # we don't need no steenkin particles, we're only interested in tracks
    #diag_part = synergia.bunch.Diagnostics_particles("particles.h5", part_track)
    #sim.reg_diag_per_turn(diag_part, period=nturns_track)

    # Get mean diagnostics for single bunch at every turn
    diag = synergia.bunch.Diagnostics_full2("diag.h5")
    sim.reg_diag_per_turn(diag)

    # Save tracking data for all 41 particles
    diagtrk = synergia.bunch.Diagnostics_bulk_track("tracks.h5", macro_particles)
    sim.reg_diag_per_turn(diagtrk)

    # Set maximum number of turns to simulate
    max_turns = 2000
    sim.set_max_turns(max_turns)

    # Define logs and screens to print out alarms and logs
    simlog = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.INFO_TURN)
    screen = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.DEBUG)

    # Propagate simulation for certain number of turns
    turns = 2000
    propagator.propagate(sim, simlog, turns)

    # Print simple timer
    synergia.utils.parallel_utils.simple_timer_print(screen)


def main():
    print("Running Recycler Ring Simulation (No Space Charge)")
    run_rr()


# Run simulation
main()
