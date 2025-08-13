#!/usr/bin/env python

# numproc variable refers to the number of 16 core nodes that will
# be allocated and run with 16 threads each.

# The local_options file must be named local_opts.py and placed
# in the Synergia2 job manager search path.

from synergia_workflow import options

# Any instance of the Options class will be added as a suboption.
opts = options.Options('local')
#opts.add("ompnumthreads",2,"number of openmp threads")

# Any instance of the Override class will be used to override
#   the defaults of the existing options.
override = options.Override()
override.account = "accelsim"
override.numproc = 1
override.procspernode=1
# The location of the setup.sh for your synergia build
override.setupsh="/work1/accelsim/egstern/devel3-cpu/install/bin/setup.sh"
override.template="job"
override.resumetemplate="resume"
#override.templatepath="full path to template file"
override.queue="cpu_gce"
override.walltime="24:00:00"
