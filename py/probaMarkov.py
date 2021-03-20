#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path
import glob
from MarkovSurMots import MarkovSurMots

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.
Donne les probabilités qu'une fin de mot puisse compléter le début de mot
spécifié et inversement que le début puisse compléter la fin.

usage   : %s <fichier entrée> <début mot> <fin mot>
exemple : %s "ressources/*.txt.npy" "Arya" "nita"
"""%(script, script))

def main():
    try:
        if len(sys.argv) < 4 : raise Exception()
        nomsFichiersNpy = sys.argv[1]
        dejbutMot = sys.argv[2].strip()
        finMot = sys.argv[3].strip()
        calcule(nomsFichiersNpy, dejbutMot, finMot)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
def calcule(nomsFichiersNpy, dejbutMot, finMot):
    markovSurMots = MarkovSurMots()
    print(f'probabilités de "{finMot}" après "{dejbutMot}" : ')
    for fichierNpy in glob.glob(nomsFichiersNpy):
        nomFichier = fichierNpy[:-4]
        markovSurMots.initCorpus(nomFichier, True)
        dejbut = dejbutMot
        fin = finMot + ' '
        proba = 1.0
        for carfin in fin:
            prob = 0.0
            for (mcar, mprob) in markovSurMots.prochainsCars(dejbut):
                if mcar == carfin: prob = mprob
            #print("'{}' : {:0.3f}".format(carfin, prob))
            proba *= prob
            dejbut += carfin
        if proba != 0.0:
            print('1 chance sur {: 12d} ({:0.9f}) pour {}'.format(int(1.0/proba), proba, path.basename(nomFichier)))
        else:
            print('0 (zéro) chance pour {}'.format(path.basename(nomFichier)))
    
    print(f'probabilités de "{dejbutMot}" avant "{finMot}" : ')
    for fichierNpy in glob.glob(nomsFichiersNpy):
        nomFichier = fichierNpy[:-4]
        markovSurMots.initCorpus(nomFichier, True)
        dejbut = dejbutMot
        fin = finMot
        proba = 1.0
        for cardeb in dejbut[::-1]:
            prob = 0.0
            for (mcar, mprob) in markovSurMots.prochainsCars(fin, True):
                if mcar == cardeb: prob = mprob
            #print("'{}' : {:0.3f}".format(cardeb, prob))
            proba *= prob
            fin = cardeb + fin
        if proba != 0.0:
            print('1 chance sur {: 12d} ({:0.9f}) pour {}'.format(int(1.0/proba), proba, path.basename(nomFichier)))
        else:
            print('0 (zéro) chance pour {}'.format(path.basename(nomFichier)))
    
    
if __name__ == '__main__':
        main()
