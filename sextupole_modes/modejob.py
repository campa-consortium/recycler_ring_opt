#!/usr/bin/env python

import synergia
from modejob_options import opts

from rr_modes import run_modes
import mpi4py.MPI as MPI

myrank = MPI.COMM_WORLD.rank

def main():

    turns = opts.turns
    kick1 = opts.kick1
    kick2 = opts.kick2
    kick3 = opts.kick3
    target = opts.target
    offset = opts.offset
    adjelem = opts.adjelem
    adjk2l = opts.adjk2l
    
    if myrank == 0:
        print(f'Setting orbit bump with kickers {kick1}, {kick2}, {kick3}')
        print(f'  Aiming for offset {offset} at element {target}')
        print(f'  Setting element {adjelem} k2l moment to {adjk2l}')
        print(f'Running simulation for {turns} turns')
        pass

    params = {}
    if adjelem is not None:
        if adjk2l is None:
            raise RuntimeError('no value set for element k2l')

        params[adjelem] = adjk2l
        pass

    if kick1 is None or kick2 is None or kick3 is None:
        correctors = None
    else:
        correctors = (kick1, kick2, kick3)
        if target is None or offset is None:
            raise RuntimeError('orbit bump corrector elements are defined but no offset or target element')
        pass

    run_modes(params, turns=turns, correctors=correctors, target=target, offset=offset)

    pass

if __name__ == "__main__":
    main()
    pass


