import ROOT
import sys
#can only load this once
if (ROOT.gSystem.Load("libPhysicsToolsNanoAODTools.so")!=0):
    print("Cannot load 'libPhysicsToolsNanoAODTools'")
    sys.exit(1)

#muons
from PhysicsTools.NanoAODTools.modules.SingleMuonTriggerSelection import SingleMuonTriggerSelection
from PhysicsTools.NanoAODTools.modules.MuonSelection import MuonSelection
from PhysicsTools.NanoAODTools.modules.MuonVeto import MuonVeto

#electrons
from PhysicsTools.NanoAODTools.modules.SingleElectronTriggerSelection import SingleElectronTriggerSelection
from PhysicsTools.NanoAODTools.modules.ElectronSelection import ElectronSelection
from PhysicsTools.NanoAODTools.modules.ElectronVeto import ElectronVeto

#aux
from PhysicsTools.NanoAODTools.modules.EventSkim import EventSkim
from PhysicsTools.NanoAODTools.modules.MetFilter import MetFilter
from PhysicsTools.NanoAODTools.modules.EventInfo import EventInfo

#jets
from PhysicsTools.NanoAODTools.modules.JetMetUncertainties import JetMetUncertainties
from PhysicsTools.NanoAODTools.modules.JetSelection import JetSelection
from PhysicsTools.NanoAODTools.modules.BTagSelection import BTagSelection
from PhysicsTools.NanoAODTools.modules.btagSFProducer import btagSFProducer

#event
from PhysicsTools.NanoAODTools.modules.PUWeightProducer import puWeightProducer, PUWeightProducer_dict
from PhysicsTools.NanoAODTools.modules.GenWeightProducer import GenWeightProducer
from PhysicsTools.NanoAODTools.modules.TopPtWeightProducer import TopPtWeightProducer

#reco
from PhysicsTools.NanoAODTools.modules.EventObservables import EventObservables

