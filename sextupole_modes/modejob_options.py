#!/usr/bin/env python

from math import pi
import synergia_workflow

opts = synergia_workflow.Options("recycler")

opts.add('kick1', None, 'orbit corrector 1 element name', str)
opts.add('kick2', None, 'orbit corrector 2 element name', str)
opts.add('kick3', None, 'orbit corrector 3 element name', str)
opts.add('target', None, 'target element name for orbit bump', str)
opts.add('offset', 0.0, 'offset for orbit bump at target element')
opts.add('adjelem', None, 'element name for k2l adjustment', str)
opts.add('adjk2l', 0.0, 'value of k2l setting for element')
opts.add('turns', 2048, 'Number of turns for simulation')

job_mgr = synergia_workflow.Job_manager("modejob.py", opts, ['../RR2020V0922FLAT_k2l_template_NoBreaks_K2L_ready', 'rr_modes.py', 'rr_setup.py', 'rrnova_qt60x.py', 'rr_sextupoles.py', 'three_bump.py', 'sext_names.pickle'])
