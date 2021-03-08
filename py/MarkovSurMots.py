#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path
import codecs
import re
import numpy

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.
Programme de test de la classe MarkovSurMots.
Complète de 10 façons 1) un mot vide, 2) un mot spécifié par son début

usage   : %s <fichier entrée> <début mot>
exemple : %s MadameBovary.txt "d'"
"""%(script, script))

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        nomFichier = sys.argv[1]
        dejbutMot = sys.argv[2]

        markovSurMots = MarkovSurMots()
        markovSurMots.initCorpus(nomFichier, True)
        mots = []
        for fois in range(20):
            mots.append(markovSurMots.complehteMot(''))
        print(', '.join(mots))
        mots = []
        for fois in range(20):
            mots.append(markovSurMots.complehteMot(dejbutMot))
        print(', '.join(mots))
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
class MarkovSurMots():
    def __init__(self):
        pass

    # init le corpus
    def initCorpus(self, nomFichier, bavard = False):
        # si le corpus n'a pas dejjah ejté traitej, le fait
        if not path.isfile(nomFichier + '.npy'): 
            self.traiteCorpus(nomFichier, bavard)
        # init le corpus ah partir de la sauvegarde
        self.markov = numpy.load(nomFichier + '.npy')
        with codecs.open(nomFichier + '.chr', 'r', 'utf-8') as fichier: 
            self.caractehres = fichier.read()
        # init le tirage au sort
        numpy.random.seed(None)
        
    # traite le corpus et le sauvegade
    def traiteCorpus(self, nomFichier, bavard):
        #1) fait le mejnage dans les mots et ejtablit la liste des caractehres
        with codecs.open(nomFichier, 'r', 'utf-8') as fichier:
            listeBrute = fichier.read().split()
        if bavard: print('{} mots bruts'.format(len(listeBrute)))
        # vire les mots vides et la ponctuation
        listeMots = []
        virejs = set()
        nbCar = 0
        # l'espace reprejsente l'avant-mot et l'aprehs-mot
        self.caractehres = ' '
        for mot in listeBrute:
            m = re.match(u"(\W*)(['\w-]*)(.*)", mot)
            if m is not None:
                if m.group(2) != '' and '_' not in m.group(2): 
                    listeMots.append(m.group(2))
                    for car in m.group(2):
                        nbCar +=1
                        if self.caractehres.find(car) == -1: self.caractehres += car 
                    virejs.add(m.group(1))
                    virejs.add(m.group(3))
                else: virejs.add(mot)
            else: virejs.add(mot)
        if bavard: 
            print('{} mots triés'.format(len(listeMots)))
            #print(virejs)
            print('{} caractères'.format(nbCar))
            print('{} caractères différents'.format(len(self.caractehres)))
            print(self.caractehres)
            
        #2) etablit la quasi-chaisne de Markov 
        # nombre de caractehres pris en compte
        nbCaractehres = len(self.caractehres)
        # creje la chaisne de Markov
        self.markov = numpy.zeros((nbCaractehres, nbCaractehres, nbCaractehres), dtype='int32')
        # la peuple avec l'analyse des mots retenus
        for mot in listeMots: 
            self.traiteMot(mot)
        # sauvegarde 
        numpy.save(nomFichier, self.markov)
        with codecs.open(nomFichier + '.chr', 'w', 'utf-8') as fichier: 
            fichier.write(self.caractehres)
            
    # peuple la quasi-chaisne de Markov avec les caractehres du mot spejcifiej
    def traiteMot(self, mot):
        # la premiehre lettre est prejcejdeje de 2 espaces
        i = 0
        j = 0
        k = 0
        for car in mot:
            k = self.caractehres.find(car)
            if k == -1: raise Exception('ERREUR INTERNE A')
            self.markov[i, j, k] += 1
            i = j
            j = k
        # la derniehre lettre est suivie de 2 espaces
        self.markov[i, j, 0] += 1
        self.markov[j, 0, 0] += 1
            
    # complehte un mot avec la quasi-chaisne de Markov
    def complehteMot(self, dejbutMot):
        mot = dejbutMot
        if len(dejbutMot) > 1: i = self.caractehres.find(dejbutMot[-2])
        else: i = 0
        if len(dejbutMot) > 0: j = self.caractehres.find(dejbutMot[-1])
        else: j = 0
        while True:
            k = self.prochainCar(i, j)
            if k == 0: break
            mot += self.caractehres[k]
            i = j
            j = k
        return mot 
    
    # trouve le prochain caractehre par la quasi-chaisne de Markov
    # retourne 0 si aucun caractehre possible
    def prochainCar(self, i, j):
        # trouve l'amplitude du tirage au sort
        probas = self.markov[i, j]
        amplitude = numpy.sum(probas)
        # si aucune possibilitej, retourne 0
        if amplitude == 0: return 0
        # tire au sort
        tirage = numpy.random.choice(amplitude)
        # trouve le caractehre correspondant
        for k in range(len(probas)):
            tirage -= probas[k]
            if tirage < 0: return k
        raise Exception('ERREUR INTERNE B')
 

if __name__ == '__main__':
        main()
