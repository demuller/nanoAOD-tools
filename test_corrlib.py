import numpy as np
import os
import correctionlib

sf = "data/btagSF/btagging.json.gz"

btvjson = correctionlib.CorrectionSet.from_file(sf)


jet_pt = np.random.exponential(50.,20)
jet_eta = np.random.uniform(0.0,2.5,20)
jet_flav = np.random.choice([0, 4, 5],20)
jet_discr = np.random.uniform(0.0,1.0,20)

light_jets = np.where(jet_flav == 0)
bc_jets = np.where(jet_flav != 0)

bc_jet_sf = btvjson["deepJet_mujets"].evaluate("central", "M", jet_flav[bc_jets], jet_eta[bc_jets], jet_pt[bc_jets])

print(bc_jet_sf)
