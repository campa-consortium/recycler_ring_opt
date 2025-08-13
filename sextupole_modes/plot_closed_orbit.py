#!/usr/bin/env python3

import sys, os
import numpy as np
import matplotlib.pyplot as plt
import synergia
import h5py

#------------------------------------------------------------------------

def load_lattice():
    f = open('rr_run_lattice.json', 'r')
    latticejson = f.read()
    f.close()
    lattice = synergia.lattice.Lattice.load_from_json(latticejson)
    return lattice

#------------------------------------------------------------------------

# for this purpose, we don't need to propagate many particles
def create_simulator(refpart):
    macroparticles = 8
    realparticles = 5e10
    sim = synergia.simulation.Bunch_simulator.create_single_bunch_simulator(refpart, macroparticles, realparticles)
    # populate the bunch. Particle 0 stays as 0, particle 1 has kick in px
    # particle 2 has kick in py.
    bunch = sim.get_bunch(0, 0)
    bunch.checkout_particles()
    local_particles = bunch.get_particles_numpy()
    local_particles[:, 0:6] = 0.0
    bunch.checkin_particles()
    return sim

#------------------------------------------------------------------------

# Stepper and propagator.

def get_propagator(lattice):
    stepper = synergia.simulation.Independent_stepper_elements(1)
    propagator = synergia.simulation.Propagator(lattice, stepper)
    return propagator

#------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def register_diagnostics(sim):
    # diagnostics

    diag = synergia.bunch.Diagnostics_bulk_track("orbit.h5", 1)
    sim.reg_diag_per_step(diag)

#-------------------------------------------------------------------------------

def track():
    lattice = load_lattice()
    print(f'read lattice, len: {lattice.get_length()}, num elements: {len(lattice.get_elements())}')

    sim = create_simulator(lattice.get_reference_particle())

    register_diagnostics(sim)

    propagator = get_propagator(lattice)

    simlog = synergia.utils.parallel_utils.Logger(0, 
            synergia.utils.parallel_utils.LoggerV.INFO_TURN)

    propagator.propagate(sim, simlog, 1)

    return

def main():
    #print(sys.argv[0])
    #print(os.path.dirname(sys.argv[0]))
    track()
    h5 = h5py.File('orbit.h5', 'r')
    tracks = h5.get('track_coords')[()]
    s = h5.get('track_s')[()]
    plt.plot(s, tracks[:, 0, 0]*1000)
    plt.xlabel('s [m]')
    plt.ylabel('x [mm]')
    plt.savefig('orbit.png')
    plt.show()
    
#------------------------------------------------------------------------

if __name__ == "__main__":
    main()
    pass
