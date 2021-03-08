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
Programme de test de la classe MotDansTexte.
Donne le mot d'un texte spécifié par son numéro d'ordre.

usage   : %s <fichier entrée> <n° d'ordre>
exemple : %s MadameBovary.txt 1953
"""%(script, script))

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        nomFichier = sys.argv[1]
        numejroOrdre = int(sys.argv[2])
        motDansTexte = MotDansTexte(nomFichier, True)
        print(motDansTexte.mot(numejroOrdre, True))
        print(motDansTexte.mot(numejroOrdre, False))
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            #raise
        sys.exit()
        
class MotDansTexte():
    def __init__(self, nomFichier, bavard = False):
        with codecs.open(nomFichier, 'r', 'utf-8') as fichier:
            listeBrute = fichier.read().split()
        if bavard: print('{} mots bruts'.format(len(listeBrute)))
        listeMots = []
        # vire les mots vides et la ponctuation
        virejs = set()
        for mot in listeBrute:
            m = re.match(u"(\W*)(['\w-]*)(.*)", mot)
            if m is not None:
                if m.group(2) != '': 
                    listeMots.append(m.group(2))
                    virejs.add(m.group(1))
                    virejs.add(m.group(3))
                else: virejs.add(mot)
            else: virejs.add(mot)
        if bavard: 
            print('{} mots triés'.format(len(listeMots)))
            print(virejs)
        self.mots = numpy.asarray(listeMots)
        self.pointeur = 0
        #print(self.mots[0:1000])
        
    # sort le niehme mot du texte, soit en relatif ah partir du pointeur, soit en absolu ah partir de 0
    def mot(self, numejroOrdre, enAbsolu):
        # si en absolu, raz du pointeur
        if enAbsolu: self.pointeur = 0
        self.pointeur += numejroOrdre 
        self.pointeur %= len(self.mots)
        return self.mots[self.pointeur]

if __name__ == '__main__':
        main()
