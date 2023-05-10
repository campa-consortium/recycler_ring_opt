
#from mpi4py import MPI
import numpy as np
import synergia

import rr_setup

#from rr_options import opts

def print_statistics(bunch):

    parts = bunch.get_particles_numpy()
    print(parts.shape,  ", ", parts.size )
    print("shape: {0}, {1}".format(parts.shape[0], parts.shape[1]))

    mean = synergia.bunch.Core_diagnostics.calculate_mean(bunch)
    std = synergia.bunch.Core_diagnostics.calculate_std(bunch, mean)
    print("mean = {}".format(mean))
    print("std = {}".format(std))


def get_lattice_rr():
    
    lattice_file = open("rr_tuned.json", "r")
    lattice = synergia.lattice.Lattice.load_from_json(lattice_file.read())

    lattice.set_all_string_attribute("extractor_type", "libff")
    #synergia.simulation.Lattice_simulator.tune_circular_lattice(lattice)                                 
    return lattice

def run_rr():

    # Run Recyler setup in order to tune lattice
    # Run rr_setup to get covariance matrix in order to populate bunches
    rr_setup.setup()

    # Define basic parameters for the simulation
    real_particles = 1e10 #Number of real particles in simulation
    refine = 1
    gridx = 32*refine
    gridy = 32*refine
    gridz = 128*refine
    partpercell = 8 #Number of particles per cell
    num_bunches = 1 #Number of bunches to simulate

    grid = [gridx, gridy, gridz]
    print('Grid Size:')
    print(grid)
    macro_particles = gridx * gridy * gridz * partpercell
    print('Number of macroparticles:')
    print(macro_particles)
    #macro_particles = 100000 #Number of macroparticles to simulate
    spacing = 5.64526987439 #Bucket length calculated from synergia2

    seed = 4 # Random seed to use

    # Get tuned Recycler lattice and reference particle for lattice
    lattice = get_lattice_rr()
    ref_part = lattice.get_reference_particle()

    # Initiate bunch simulator (For now single bunch)
    sim = synergia.simulation.Bunch_simulator.create_bunch_train_simulator(
        ref_part, macro_particles, real_particles, num_bunches, spacing)

    # Enforce longitudinal bucket conditions (Mandatory if RF is turned on)
    sim.set_longitudinal_boundary(synergia.bunch.LongitudinalBoundary.periodic, spacing)

    # Populate particles inside bunches (For now single bunch)
    # Can introduce horizontal or vertical kick
    xkick = 0
    ykick = 0
    means = np.zeros([6], 'd')+np.array([0,xkick,0,ykick,0,0])
    covars = np.load("correlation_matrix.npy")[()]

    # Initiate parallel communication protocol
    comm = synergia.utils.parallel_utils.Commxx()

    # Initiate Random Distribution with specified seed
    dist = synergia.foundation.Random_distribution(seed, comm.get_rank())

    # Populate bunches with the random 6D distribution
    # Populate according to means and covariance parameters

    for b in range(num_bunches):
        bunch = sim.get_bunch(0, b) # Get b-th bunch at 0-th train
        synergia.bunch.populate_6d(dist, bunch, means, covars)
        print_statistics(bunch)

    # Define space-charge operator (For now no space charge)
    steps = 416 # Number of steps to use for stepper (What does this mean?)
    sc_ops = synergia.collective.Dummy_CO_options() # No space-charge option
    stepper = synergia.simulation.Split_operator_stepper(sc_ops, steps)

    # Define propagator for simulations
    propagator = synergia.simulation.Propagator(lattice, stepper)

    # Define diagnostics to run
    # For now keep options to single bunch

    # Track individual particles and save to individual files
    part_track = 1000 # Number of particles to track
    nturns_track = 1 # Number of turns between each tracking 
    diag_part = synergia.bunch.Diagnostics_particles("diag_particles.h5", part_track)
    sim.reg_diag_per_turn(diag_part, period = nturns_track)

    # Get mean diagnostics for single bunch at every turn
    diag_full2 = synergia.bunch.Diagnostics_full2("diag_full.h5")
    sim.reg_diag_per_turn(diag_full2)

    # Set maximum number of turns to simulate
    max_turns = 4000
    sim.set_max_turns(max_turns)

    # Define logs and screens to print out alarms and logs
    simlog = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.INFO_TURN)
    screen = synergia.utils.parallel_utils.Logger(0, synergia.utils.parallel_utils.LoggerV.DEBUG)

    # Propagate simulation for certain number of turns
    turns = 3999
    propagator.propagate(sim, simlog, turns)

    # Print simple timer
    synergia.utils.parallel_utils.simple_timer_print(screen)


def main():

    print("Running Recycler Ring Simulation (No Space Charge)")
    run_rr()

    
# Run simulation
main()
