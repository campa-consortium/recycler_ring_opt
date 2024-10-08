#!/usr/bin/env python

from math import pi

from synergia_workflow import options

opts = options.Options("rr")

opts.add("seed", 4, "Pseudorandom number generator seed", int)
opts.add("radius", 0.1, "aperture radius [m]", float)
opts.add("macroparticles", 1000, "Number of macro particles")
opts.add("real_particles", 1e10, "Number of real particles", float)
opts.add("verbose", 1, "Verbose propagation", int)

opts.add("num_bunches", 1, "number of bunches")
opts.add("generate_bunch", True, "whether to generate the bunch", bool)
opts.add("particles_file", "mi_particles.h5", "Particles to read {.txt|.mxtxt|.h5}", str)

opts.add("bucket_length", 5.64526987439, "bucket length calculated from synergia2", float)

opts.add("start_element", None, "which element in the lattice to start with", str)
opts.add("matching", "nfgaussian", "6dmoments|nftorus|nfgaussian", str)
# diagnostics saving options
opts.add("turn_tracks", 0, "Number of particles to track each turn", int)
opts.add("step_basic", False, "Whether to do basic diagnostics each step", bool)
opts.add("turn_full2", True, "Whether to do full2 diagnostics each turn", bool)
opts.add("turn_particles", True, "Whether to save all particles each turn", bool)
opts.add("particles_period", 100, "dump particles every n turns", int)
opts.add("checkpoint_period", 200, "checkpoint every n turns", int)
opts.add("concurrent_io", 1, "number of procs doing checkpoint concurrently")
opts.add("septa_dump", False, "whether to dump particles hitting the septa", bool)
opts.add("septa_period", 1, "period between septa particle dump", int)
opts.add("step_full2", False, "Whether to do full2 diagnostics each step", bool)
opts.add("steps", 416, "Number of steps per turn", int)
opts.add("turns", 1024, "Number of turns total", int)
opts.add("max_turns", 2048, "Maximum number of turns this run", int)
opts.add("map_order", 5, "Map order", int)
opts.add("quad_maps", False, "Use MAPS for quadrupoles", bool)
opts.add("partpercell", 8, "macro particles per grid cell", int)
# normalized geometric emittance of 19.09e-6 mm-mr at beta*gamma=9.4855
# gives a beam spot with a half width of 14 mm at the ipm location with beta_x
# is 51.67.
opts.add("norm_emit", 50e-6 / 5.99, "95% normalized horizontal and vertical emittance [pi m rad]", float)
opts.add("stdz", 0.001, "RMS longitudinal length [m]", float)
# opts.add("rf_voltage", 0.08, "RF cavity voltage in MV", float)
opts.add("rf_voltage", 0.0, "RF cavity voltage in MV", float)

# with RF on, buckets should be periodic
opts.add("periodic", True, "Enforce longitudinal bucket periodicity", bool)

opts.add("x_offset", 0.0, "Bunch offset in x", float)
# opts.add("xp_offset, 0.0, "Bunch momentum in x", float)
opts.add("y_offset", 0.0, "Bunch offset in y", float)
# opts.add("yp_offset, 0.0, "Bunch momentum in y", float)
opts.add("z_offset", 0.0, "Bunch offset in z", float)
opts.add("start_energy", None, "Start energy", float)

opts.add("comm_avoid", True, "Use communication avoidance", bool)
opts.add("comm_divide", 0, "Comm divider factor", int)
opts.add("autotune", False, "Autotune collective communication algorithm", bool)
opts.add("spacecharge", False, "Use a space charge solver", bool)
opts.add("comm_group_size", 1, "Communication group size for space charge solvers (must be 1 on GPUs)", int)

# solver choices are 3dopen-hockney, 2dbassetti-erskine, 2dopen-hockney,
#    rectangular
opts.add("solver", "rectangular", "which space charge solver to use", str)
# if spacecharge is off, we can either use the splitoperator stepper with
# a dummy collective, or an independent stepper
opts.add(
    "stepper",
    "splitoperator",
    "the stepper to use with no space charge sither independent, elements, or splitoperator",
    str,
)

# impedance options
opts.add("impedance", True, "activate impedance")
opts.add("wake_file", "Wakes_MI.dat", "data file for wake(impedance) calculation")
opts.add("wake_grid", 1000, "grid for intrabunch wake calculation")
opts.add("wave_number", [0, 0, 0], "wave number for multibunch instability")
opts.add("wake_turns", 1, "number of turns to consider for wake")
opts.add("wake_type", "XZ_Elliptical_coeff", "type of wake to apply")
opts.add("full_machine", False, "consider every bucket occupied")

# options for whether to add multipole fields
# opts.add("add_multipoles", True, "Add multipole fields", bool)

# lambertson aperture option
opts.add("lam52", False, "Apply aperture at lam52 elements", bool)
# MI orbit bumps
opts.add("orbit_bumps", False, "Enable orbit bumps", bool)
opts.add("magnet_moves", False, "Move magnets for lambertson", bool)

opts.add("pipe_size", [60.26e-3, 23.69e-3], "dimensions of rectangular pipe")
opts.add("gridx", 32, "size of transverse grid for solver", int)
opts.add("gridy", 32, "size of transverse grid for solver", int)
opts.add("gridz", 128, "size of longitudinal grid for solver", int)

# tune adjustments
# These starting tunes come from the file tunefreq_fine.txt and are the values
# at 0 frequency offset
opts.add("xtune_adjust", 0.4126, "adjust x tune", float)
opts.add("ytune_adjust", 0.3560, "adjust y tune", float)

# chromaticity adjustments
opts.add("xchrom_adjust", None, "adjust x chromaticity", float)
opts.add("ychrom_adjust", None, "adjust y chromaticity", float)

opts.add("xml_save_lattice", False, "Save the lattice in xml form", bool)
opts.add("add_multipoles", True, "add multipoles", bool)

opts.add("lattice_simplify", True, "apply lattice simplification", bool)
opts.add("scratch", None, "directory for temporary diagnostic files", str)
# job_mgr = synergia_workflow.Job_manager("mi_multibunch.py", opts, ["mi20-egs-thinrf.lat","multipoles.npy","mi_orbit_bumps.py","mi_ila_aperture.py","read_bunch.py", "Wakes_MI.dat"])
# job_mgr = synergia_workflow.Job_manager("mi.py", opts, ["mi20.lsx", "covars.txt"])

# tune survey options
opts.add("min_freq_offset", -2000, "minimum frequency offset (MHz)")
opts.add("max_freq_offset", 2000, "maximum frequency offset (MHz)")
opts.add("freq_offset_step", 100, "step size between frequency measurements")
