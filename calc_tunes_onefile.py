#!/usr/bin/env python

import os
import sys
import re
import glob
import mpi4py
import mpi4py.MPI as MPI
import numpy as np
import h5py
from  tune_suite import *

# window is the size of the fft to get the tunes
window = 2000

# step is the step between tune determinations along the track
step = 100

DEBUG=1

# return type of file (single track or multitrack)
def track_filetype(hfname):
    partid_re = re.compile(basefile + "_([0-9]+).h5")
    partid_mo = partid_re.match(hfname)
    if not partid_mo:
        raise RuntimeError("filename regular expression match did not include particle ID or rank")
    h5 = h5py.File(hfname, 'r')
    if "coords" in h5.keys():
        # this is a single track file.
        h5.close()
        return partid_mo.group(1)
    elif "track_coords" in h5.keys():
        # this is a multi track file
        ntracks = h5.get("track_coords").shape[1]
        h5.close()
        return -ntracks
    else:
        h5.close()
        raise RuntimeError("track_filetype couldn't determine type of file %s"%hfname)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("usage: calc_tunes.py tracks-filename")

    os.environ["HDF5_DISABLE_VERSION_CHECK"] = "2"

    commsize = MPI.COMM_WORLD.Get_size()
    myrank = MPI.COMM_WORLD.Get_rank()

    tracks_file = sys.argv[1]
    if DEBUG and myrank == 0:
        print("Reading tracks from file ", tracks_file)

    tunes_file = os.path.splitext(tracks_file)[0]+"_tunes"
    h5 = h5py.File(tracks_file, 'r')

    # collect tunes in a dictionary indexed by particle ID containing
    # a tuple of ([starting turn], [xtunes], [ytunes], [ltunes])

    ntracks = h5.get("track_coords").shape[1]
    if DEBUG: print("rank: ", myrank, ", ntracks: ", ntracks)

    tunelist = {}
    # divide track processing up by processor
    tracks_per_proc = int((ntracks+commsize-1)/commsize)
    if DEBUG and myrank == 0: print("tracks per proc: ", tracks_per_proc)

    my_first_track = myrank*tracks_per_proc
    my_last_track = min( (myrank+1)*tracks_per_proc, ntracks )
    if DEBUG>1: print("proc: ", myrank,", first track: ", my_first_track,", last  track: ", my_last_track)

    for do_track in range(my_first_track, my_last_track):
        if DEBUG>1: print("proc: ", myrank,", working on track: ", do_track)

        # this is a file of bulk tracks.  This will contain an array
        #[turn_number, trknum, coords] with shape
        # nturns x ntracks x 7

        coords = h5.get("track_coords")[:, do_track,0:6].transpose()
        nturns = coords.shape[1]
        # the tune finding routine expects data in the format of 6xn
        tune_starts = list(range(0, nturns-window+1, step))
        xtunes = []
        ytunes = []
        ltunes = []
        for tstart in tune_starts:
            if DEBUG>2:
                print("proc: ", myrank, ", track: ", do_track, ", turn: ", tstart)
            #tunes = interp_tunes(coords[:, tstart:tstart+1024])
            tunes = interp_tunes(coords[:, tstart:tstart+window])
            xtunes.append(tunes[0])
            ytunes.append(tunes[1])
            ltunes.append(tunes[2])

        tunelist[do_track] = (tune_starts, xtunes, ytunes, ltunes)
        #tunelist[trknum] = basic_tunes(coords)
        #tunelist[trknum] = cft_tunes(coords)
        if DEBUG>1: print("tunes for particle ", do_track,": ", tunelist[do_track])
                                                                    
    h5.close()
    # send my tunes to rank 0 for writing out
 
    # rank 0 will collect all the tune data and write it out
    if myrank == 0:
        for r in range(1,commsize):
            rtunes = MPI.COMM_WORLD.recv(source=r)
            if DEBUG: print("Receiving tune data for %d tracks from rank %d"%(len(rtunes),r))
            tunelist.update(rtunes)

        if myrank == 0: print("Saving data for ",len(tunelist), " particles")
        np.save(tunes_file, tunelist)
    else:
        # send my data to rank 0
        MPI.COMM_WORLD.send(tunelist,dest=0)
