#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path
import LateconResLingBase
from MotDansTexte import MotDansTexte

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.
A partir de trois nombres fournis séparés par des "/"
(par exemple une date de naissance), donne une phrase de 5 mots : 
un déterminant + un substantif + un adjectif + un verbe + un adverbe
tirés dans le texte spécifié.

usage   : %s <fichier entrée> <nb1/nb2/nb3>
exemple : %s MadameBovary.txt 03/03/1982
"""%(script, script))

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        nomFichier = sys.argv[1]
        nombres = sys.argv[2]
        troisNombres = []
        listeNombres = nombres.split('/')
        for nombre in listeNombres:
            if not nombre.isdecimal(): raise Exception('MAUVAIS FORMAT de NOMBRES')
            troisNombres.append(int(nombre))
        if len(troisNombres) != 3: raise Exception('MAUVAIS FORMAT de NOMBRES')
        trouveDetNcV(nomFichier, troisNombres)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()
        
    
def trouveDetNcV(nomFichier, troisNombres):
    base = LateconResLingBase.LateconResLingBase()
    motDansTexte = MotDansTexte(nomFichier)
    
    # 1) cherche le substantif
    (mot, lemmeId, micro) = trouveBonMot(motDansTexte, base, troisNombres, 'L_NC')
    #print(mot + " (" + str(lemmeId) + ") " + micro)
    substantif = mot
    # dejtermine le genre et le nombre du substantif
    # Nc.ms.  Nc.fs.  Nc.mp.  Nc.fp.
    genreNombre = micro[3:5]
    
    # 2) cherche le dejterminant
    while True:
        (mot, lemmeId, micro) = trouveBonMot(motDansTexte, base, troisNombres, 'L_DET')
        #print(mot + " (" + str(lemmeId) + ") " + micro)
        # cherche la forme qui convient au substantif
        # D...ms.  D...fs.  D...mp.  D...fp.  
        microIdoine = micro[0:4] + genreNombre + micro[6:7]
        rejsultat = formeIdoine(base, lemmeId, microIdoine)
        if len(rejsultat) > 0 : break
    dejterminant = rejsultat[0][0]
    #print(dejterminant)
    if len(rejsultat) > 1:
        if substantif.lower()[0:1] in ('a', 'e', 'i', 'o', 'u', 'y', 'h'):
            if dejterminant[-1:] != "'": dejterminant = rejsultat[1][0]
        elif dejterminant[-1:] == "'": dejterminant = rejsultat[1][0]
        
    # 3) cherche l'adjectif
    (mot, lemmeId, micro) = trouveBonMot(motDansTexte, base, troisNombres, 'L_ADJ')
    #print(mot + " (" + str(lemmeId) + ") " + micro)
    # cherche la forme qui convient au substantif
    # A....ms  A....fs  A....mp  A....fp    
    microIdoine = micro[0:5] + genreNombre
    rejsultat = formeIdoine(base, lemmeId, microIdoine)
    adjectif = rejsultat[0][0]        
    
    # 4) cherche le verbe
    while True:
        (mot, lemmeId, micro) = trouveBonMot(motDansTexte, base, troisNombres, 'L_V')
        #print(mot + " (" + str(lemmeId) + ") " + micro)
        # il faut que le verbe soit conjuguej ah l'indicatif ou au subjonctif
        if micro[2:3] in ('i', 's'): break
    # cherche la forme qui convient au substantif
    # V....3.s  V....3.p
    microIdoine = micro[0:5] + '3-' + genreNombre[1:2]
    verbe = formeIdoine(base, lemmeId, microIdoine)[0][0]
    
    # 5) cherche l'adverbe
    while True:
        (mot, lemmeId, micro) = trouveBonMot(motDansTexte, base, troisNombres, 'L_ADV')
        #print(mot + " (" + str(lemmeId) + ") " + micro)
        # il faut que l'adverbe finisse par "ment"
        if mot[-4:] == 'ment': break
    adverbe = mot

    
    print('\n' + dejterminant + ' ' + substantif + ' ' + adjectif + ' ' + verbe+ ' ' + adverbe)

# trouve le premier mot avec la bonne macrocat
def trouveBonMot(motDansTexte, base, troisNombres, macrocat):
    while True:
        mots = troisMots(motDansTexte, troisNombres)
        #print(mots)
        for mot in mots:
            lemmesMacros = lemmesEtMacrocats(base, mot)
            for (lemmeId, macro, micro) in lemmesMacros:
                if macro == macrocat: return (mot, lemmeId, micro)
    
# rejcupehre 3 mots ah partir des 3 nombres
def troisMots(motDansTexte, troisNombres):
    mots = []
    for nombre in troisNombres:
        mots.append(motDansTexte.mot(nombre, False))
    return mots

# rejcupehre l'identifiant des lemmes, macrocats et microcats d'une forme
def lemmesEtMacrocats(base, forme):
    rejsultat = base.executeSqlSelect('''
        SELECT lemmes.id, graph_macro.graphie, graph_micro.graphie FROM formes 
            JOIN graphies AS graph_forme ON formes.graphie=graph_forme.id 
            JOIN lemmes ON formes.lemme=lemmes.id 
            JOIN macrocats ON lemmes.macrocat=macrocats.id 
            JOIN graphies AS graph_macro ON macrocats.graphie=graph_macro.id 
            JOIN microcats ON formes.microcat=microcats.id 
            JOIN graphies AS graph_micro ON microcats.graphie=graph_micro.id
            WHERE lemmes.langue=145 
            AND graph_forme.graphie="{}";
            '''.format(forme))
    return rejsultat

# rejcupehre la graphie d'une forme ah partir de son lemme et de sa microcat
def formeIdoine(base, lemmeId, microcat):
    rejsultat = base.executeSqlSelect('''
        SELECT graph_forme.graphie FROM formes 
            JOIN graphies AS graph_forme ON formes.graphie=graph_forme.id 
            JOIN lemmes ON formes.lemme=lemmes.id 
            JOIN microcats ON formes.microcat=microcats.id 
            JOIN graphies AS graph_micro ON microcats.graphie=graph_micro.id 
            WHERE lemmes.id={} 
            AND graph_micro.graphie="{}";
            '''.format(lemmeId, microcat))
    #print(rejsultat)
    return rejsultat

    

if __name__ == '__main__':
        main()
