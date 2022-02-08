import os
import sys
import math
import argparse
import random
import ROOT
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor \
    import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel \
    import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.modules import *

parser = argparse.ArgumentParser()


parser.add_argument('--isData', dest='isData',
                    action='store_true', default=False)
parser.add_argument('--isSignal', dest='isSignal',
                    action='store_true', default=False)
parser.add_argument('--nosys', dest='nosys',
                    action='store_true', default=False)
parser.add_argument('--invid', dest='invid',
                    action='store_true', default=False)
parser.add_argument('--year', dest='year',
                    action='store', type=str, default='2017', choices=['2016','2016preVFP','2017','2018'])
parser.add_argument('-i','--input', dest='inputFiles', action='append', default=[])
parser.add_argument('--maxEvents', dest='maxEvents', type=int, default=None)
parser.add_argument('output', nargs=1)

args = parser.parse_args()

print("isData:",args.isData)
print("isSignal:",args.isSignal)
print("evaluate systematics:",not args.nosys)
print("invert lepton id/iso:",args.invid)
print("inputs:",len(args.inputFiles))
print("year:", args.year)
print("output directory:", args.output[0])
if args.maxEvents:
    print('max number of events', args.maxEvents)

globalOptions = {
    "isData": args.isData,
    "isSignal": args.isSignal,
    "year": args.year
}

Module.globalOptions = globalOptions

isMC = not args.isData
isPowheg = 'powheg' in args.inputFiles[0].lower()
isPowhegTTbar = 'TTTo' in args.inputFiles[0] and isPowheg

minMuonPt =     {'2016': 25., '2016preVFP': 25., '2017': 28., '2018': 25.}
minElectronPt = {'2016': 29., '2016preVFP': 29., '2017': 34., '2018': 34.}


jesUncertaintyFilesRegrouped = {
    '2016':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/RegroupedV2_Summer19UL16_V7_MC_UncertaintySources_AK4PFchs.txt",
    '2016preVFP': "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/RegroupedV2_Summer19UL16APV_V7_MC_UncertaintySources_AK4PFchs.txt",
    '2017':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/RegroupedV2_Summer19UL17_V5_MC_UncertaintySources_AK4PFchs.txt",
    '2018':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/RegroupedV2_Summer19UL18_V5_MC_UncertaintySources_AK4PFchs.txt"
}
jerResolutionFiles = {
    '2016':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer20UL16_JRV3_MC_PtResolution_AK4PFchs.txt",
    '2016preVFP': "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer20UL16APV_JRV3_MC_PtResolution_AK4PFchs.txt",
    '2017':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer19UL17_JRV2_MC_PtResolution_AK4PFchs.txt",
    '2018':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer19UL18_JRV2_MC_PtResolution_AK4PFchs.txt"
}

jerSFUncertaintyFiles = {
    '2016':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer20UL16_JRV3_MC_SF_AK4PFchs.txt",
    '2016preVFP': "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer20UL16APV_JRV3_MC_SF_AK4PFchs.txt",
    '2017':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer19UL17_JRV2_MC_SF_AK4PFchs.txt",
    '2018':       "${CMSSW_BASE}/src/PhysicsTools/NanoAODTools/data/jme/Summer19UL18_JRV2_MC_SF_AK4PFchs.txt"
}

def leptonSequence():
    seq = [
        MuonSelection(
            inputCollection=lambda event: Collection(event, "Muon"),
            outputName="tightMuons",
            storeKinematics=[],
            storeWeights=True,
            muonMinPt=minMuonPt[args.year],
            muonMaxEta=2.4,
            triggerMatch=True,
            muonID=MuonSelection.TIGHT,
            muonIso=MuonSelection.INV if args.invid else MuonSelection.VERYTIGHT,
        ),
        SingleMuonTriggerSelection(
            inputCollection=lambda event: event.tightMuons,
            outputName="IsoMuTrigger",
            storeWeights=True,
        ),
        
        MuonVeto(
            inputCollection=lambda event: event.tightMuons_unselected,
            outputName = "looseMuons",
            muonMinPt = 10.,
            muonMaxEta = 2.4,
        ),

        ElectronSelection(
            inputCollection = lambda event: Collection(event, "Electron"),
            outputName = "tightElectrons",
            electronID = ElectronSelection.INV if args.invid else ElectronSelection.WP90,
            electronMinPt = minElectronPt[args.year],
            electronMaxEta = 2.4,
            storeKinematics=[],
            storeWeights=True,
        ),
        SingleElectronTriggerSelection(
            inputCollection=lambda event: event.tightElectrons,
            outputName="IsoElectronTrigger",
            storeWeights=True,
        ),
        ElectronVeto(
            inputCollection=lambda event: event.tightElectrons_unselected,
            outputName = "looseElectrons",
            electronMinPt = 10.,
            electronMaxEta = 2.4,
        ),
        EventSkim(selection=lambda event: (event.IsoMuTrigger_flag > 0) or (event.IsoElectronTrigger_flag > 0)),
        EventSkim(selection=lambda event: (len(event.tightMuons) + len(event.tightElectrons)) == 2),
        EventSkim(selection=lambda event: (len(event.looseMuons) + len(event.looseElectrons)) == 0),
        
    ]
    return seq
    
def jetSelection(jetDict):
    seq = []
    
    selectedJetCollections = []
    for systName,jetCollection in jetDict.items():
        seq.append(
            JetSelection(
                inputCollection=jetCollection,
                leptonCollectionDRCleaning=lambda event: event.tightMuons+event.tightElectrons,
                jetMinPt=30.,
                jetMaxEta=2.4,
                dRCleaning=0.4,
                jetId=JetSelection.TIGHT,
                storeKinematics=['pt', 'eta'],
                outputName="selectedJets_"+systName,
            )
        )
        selectedJetCollections.append(lambda event: getattr(event,"selectedJets_"+systName))
        
        seq.append(
            BTagSelection(
                inputCollection=lambda event,sys=systName: getattr(event,"selectedJets_"+sys),
                flagName="isBTagged",
                outputName="selectedBJets_"+systName,
                jetMinPt=30.,
                jetMaxEta=2.4,
                workingpoint = BTagSelection.TIGHT,
                storeKinematics=[],
                storeTruthKeys = ['hadronFlavour','partonFlavour'],
            )
        )
        
    systNames = jetDict.keys()
    
    #at least 3 AK4 jets
    seq.append(
        EventSkim(selection=lambda event, systNames=systNames: 
            any([getattr(event, "nselectedJets_"+systName) >= 3 for systName in systNames])
        )
    )
    
    #at least 2 b-tagged jets
    seq.append(
        EventSkim(selection=lambda event, systNames=systNames: 
            any([len(list(filter(lambda jet: jet.isBTagged,getattr(event,"selectedJets_"+systName)))) >= 2 for systName in systNames])
        )
    )
    
    #TODO: btagging SF producer might have a bug
    '''
    if isMC:
        jesUncertForBtag = ['jes'+syst.replace('Total','') for syst in jesUncertaintyNames]
        # to remove once breakdown available
        if args.year != '2016preVFP':
            jesUncertForBtag = ['jes']
        seq.append(
            btagSFProducer(
                era=args.year,
                jesSystsForShape = jesUncertForBtag,
                nosyst = args.nosys
            )
        )
    '''

    
            
    return seq
    


analyzerChain = [
    EventSkim(selection=lambda event: event.nTrigObj > 0),
    MetFilter(
        globalOptions=globalOptions,
        outputName="MET_filter"
    ),
]

analyzerChain.extend(leptonSequence())

if args.isData:
    analyzerChain.extend(
        jetSelection({
            "nominal": lambda event: Collection(event,"Jet")
        })
    )

else:
    analyzerChain.append(PUWeightProducer_dict[args.year]())

    if args.nosys:
        jesUncertaintyNames = []
    else:
        '''
        jesUncertaintyNames = ["Total","Absolute","EC2","BBEC1", "HF","RelativeBal","FlavorQCD" ]
        for jesUncertaintyExtra in ["RelativeSample","HF","Absolute","EC2","BBEC1"]:
            jesUncertaintyNames.append(jesUncertaintyExtra+"_"+args.year.replace("preVFP",""))
        '''
        jesUncertaintyNames = ["Total"]
            
        print("JECs: ",jesUncertaintyNames)
        
    #TODO: apply type2 corrections? -> improves met modelling; in particular for 2018
    analyzerChain.append(
        JetMetUncertainties(
            jesUncertaintyFilesRegrouped[args.year],
            jerResolutionFiles[args.year],
            jerSFUncertaintyFiles[args.year],
            jesUncertaintyNames = jesUncertaintyNames, 
            metInput = lambda event: Object(event, "MET"),
            rhoInput = lambda event: event.fixedGridRhoFastjetAll,
            jetCollection = lambda event: Collection(event,"Jet"),
            lowPtJetCollection = lambda event: Collection(event,"CorrT1METJet"),
            genJetCollection = lambda event: Collection(event,"GenJet"),
            muonCollection = lambda event: Collection(event,"Muon"),
            electronCollection = lambda event: Collection(event,"Electron"),
            propagateJER = False, #not recommended
            outputJetPrefix = 'jets_',
            outputMetPrefix = 'met_',
            jetKeys=['jetId', 'nConstituents','btagDeepFlavB','hadronFlavour','partonFlavour'],
            metKeys = [],
        )
    )

    jetDict = {
        "nominal": lambda event: event.jets_nominal,
    }
    
    if not args.nosys:
        jetDict["jerUp"] = lambda event: event.jets_jerUp
        jetDict["jerDown"] = lambda event: event.jets_jerDown
        
        for jesUncertaintyName in jesUncertaintyNames:
            jetDict['jes'+jesUncertaintyName+"Up"] = lambda event,sys=jesUncertaintyName: getattr(event,"jets_jes"+sys+"Up")
            jetDict['jes'+jesUncertaintyName+"Down"] = lambda event,sys=jesUncertaintyName: getattr(event,"jets_jes"+sys+"Down")
    
    analyzerChain.extend(
        jetSelection(jetDict)
    )


if not args.isData:
    #analyzerChain.append(GenWeightProducer())
    if isPowhegTTbar:
        analyzerChain.append(
            TopPtWeightProducer(
                mode=TopPtWeightProducer.DATA_NLO
            )
        )


storeVariables = [
    [lambda tree: tree.branch("PV_npvs", "I"), lambda tree,
     event: tree.fillBranch("PV_npvs", event.PV_npvs)],
    [lambda tree: tree.branch("PV_npvsGood", "I"), lambda tree,
     event: tree.fillBranch("PV_npvsGood", event.PV_npvsGood)],
    [lambda tree: tree.branch("fixedGridRhoFastjetAll", "F"), lambda tree,
     event: tree.fillBranch("fixedGridRhoFastjetAll",
                            event.fixedGridRhoFastjetAll)],
]


if not globalOptions["isData"]:
    storeVariables.append([lambda tree: tree.branch("genweight", "F"),
                           lambda tree,
                           event: tree.fillBranch("genweight",
                           event.Generator_weight)])

    '''
    L1prefirWeights =  ['Dn', 'Nom', 'Up', 'ECAL_Dn', 'ECAL_Nom', 'ECAL_Up',
                        'Muon_Nom', 'Muon_StatDn', 'Muon_StatUp', 'Muon_SystDn', 'Muon_SystUp']

    for L1prefirWeight in L1prefirWeights:
        storeVariables.append([
            lambda tree, L1prefirWeight=L1prefirWeight: tree.branch('L1PreFiringWeight_{}'.format(L1prefirWeight.replace('Dn','Down').replace('Nom','Nominal')), "F"),
            lambda tree, event, L1prefirWeight=L1prefirWeight: tree.fillBranch('L1PreFiringWeight_{}'.format(L1prefirWeight.replace('Dn','Down').replace('Nom','Nominal')),
                                                                               getattr(event,'L1PreFiringWeight_{}'.format(L1prefirWeight)))
        ])
    '''
    analyzerChain.append(EventInfo(storeVariables=storeVariables))

p = PostProcessor(
    args.output[0],
    args.inputFiles,
    cut="(nJet>2)&&((nElectron+nMuon)>1)", #at least 3 jets + 2 leptons
    modules=analyzerChain,
    friend=True,
    maxEntries = args.maxEvents
)

p.run()

