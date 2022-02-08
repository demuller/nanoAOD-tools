from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import ROOT
import math
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.modules.gen_helper import isLastCopy

class TopPtWeightProducer(Module):
    DATA_NLO = 0 #data/NLO
    DATA_NNLO = 1 #data/NNLO
    NNLO_NLO = 2 #NNLO/NLO


    def __init__(self, mode=DATA_NLO):
        self.mode = mode
        if not mode in [
            TopPtWeightProducer.DATA_NLO,
            TopPtWeightProducer.DATA_NNLO,
            TopPtWeightProducer.NNLO_NLO
        ]:
            raise ValueError('top pt reweighting mode {} not supported: please check'.format(mode))
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch('TopPtWeight','F')

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        tt_cand = []
        genParts = Collection(event,'GenPart')
        for part in genParts:
            if abs(part.pdgId) == 6 and isLastCopy(part):
                tt_cand.append(part)

        weight = 1.
        if len(tt_cand) != 2:
            print('WARNING: {} top quarks found. No pt reweighting applied'.format(len(tt_cand)))
        elif tt_cand[0].pdgId*tt_cand[1].pdgId > 0:
            print('WARNING: the two top quark candidated have the same charge. No pt reweighting applied')
        else:
            weight = self.getEventWeight(tt_cand)

        self.out.fillBranch('TopPtWeight',weight)

        return True


    def getEventWeight(self,tt_cand):
        if len(tt_cand) != 2:
            raise ValueError('exactly two top quarks required, {} given'.format(len(tt_cand)))
        weight = 1.
        for t_cand in tt_cand:
            weight *= self.getParticleWeight(t_cand)
        return weight **.5

    def getParticleWeight(self, t_cand):
        if self.mode == TopPtWeightProducer.DATA_NLO:
            return math.exp(.0615-.0005*t_cand.pt)
        elif self.mode == TopPtWeightProducer.DATA_NNLO:
            return math.exp(.0416-.0003*t_cand.pt)
        elif self.mode == TopPtWeightProducer.NNLO_NLO:
            return .103 * math.exp(-.0118*t_cand.pt) - .000134*t_cand.pt + .973
        else:
            raise ValueError('top pt reweighting mode {} not supported: please check'.format(self.mode))



        
        
