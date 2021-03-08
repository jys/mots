#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
import sys
from os import path
import socket
import urllib
import re
import subprocess
import base64
import traceback
from copy import deepcopy
from MarkovSurMots import MarkovSurMots


HOST = ''
PORT = 8084
NBMOTS = 100

def usage():
    script = path.basename(sys.argv[0])
    print ("""© l'ATEJCON.
Serveur http de fabrique de mots.
Il démarre en localhost et attend sur le port %d
En mode 'local', le client démarre automatiquement sur Firefox.
En mode 'distant', le client se connecte par un navigateur à l'adresse :
http://127.0.0.1:%d ou http://localhost:%d 
Le client a été testé avec succès sur Firefox 84.0.

usage   : %s <LOCAL | DISTANT> 
exemple : %s local
"""%(PORT, PORT, PORT, script, script))
    
def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        localDistant = sys.argv[1].lower()
        if localDistant.startswith('loc'): local = True
        elif localDistant.startswith('dis'): local = False
        else: raise Exception('INCONNU : %s'%(sys.argv[1]))
        fabriqueMots(local)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            traceback.print_exc()
            print ("******************************")
        sys.exit()

###############################        
def fabriqueMots(local):
    # passe la main ah la classe html
    scriptsDir = path.dirname(sys.argv[0])
    serveurHtml = ServeurHtml(scriptsDir, local)
    print('TERMINÉ 2')
    
###############################        
class ServeurHtml():
    def __init__(self, scriptsDir, local):
        self.scriptsDir = scriptsDir
        self.dejbutMot = ''
        self.tousLesCorpus = {'Madame Bovary' : 'MadameBovary.txt', 'Madame Bovary dejsaccentueje' : 'MadameBovary.txt-dejsaccentuej.txt', 'La Recherche du temps perdu' : 'LaRecherche.txt', 'La Disparition' : 'LaDisparition.txt', 'le dictionnaire des lemmes' : 'lemmes-FRE.txt', 'For whom the bell tolls' : 'ForWhomTheBellTolls.txt'}
        self.corpus = ''
        self.markovSurMots = MarkovSurMots()
        self.motsFabriquejs = []
        self.motsSejlectionnejs = []
        self.modedEmploi = False
        # init la socket
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        c.bind((HOST, PORT))
        print ('attend sur le port %d'%(PORT))
        # 1 seul client a la fois, ca permet d'utiliser la socket de connexion pour la reponse
        c.listen(1)  
        # lance le client firefox
        if local: subprocess.run(['firefox', 'http://localhost:{}'.format(PORT)])
        
        while True:
            try:
                csock, caddr = c.accept() 
                donnejesRecues = urllib.parse.unquote_plus(csock.recv(4096).decode('utf-8'))
                
                #repond au client que tout va bien
                csock.send(b'HTTP/1.0 200 OK\n\n') 
                print(donnejesRecues)
                
                # GET / HTTP/1.1 = 1ehre fois
                if 'GET / HTTP/1.1' in donnejesRecues:
                    print('Première fois')
                    self.afficheTout(csock)
                    continue
                
                # choix du corpus
                #     GET /?CORPUS;Madame Bovary dejsaccentueje HTTP/1.1
                m = re.search('GET /.*\?CORPUS;(.*) HTTP/1.1', donnejesRecues)
                if m is not None:
                    self.choisitCorpus(m.group(1))
                    self.afficheTout(csock)
                    continue
                
                # choix du dejbut de mot + lancement calcul
                #     POST /dejbutMot HTTP/1.1
                #     ...
                #     dejbutMot=cul
                if 'POST /dejbutMot HTTP/1.1' in donnejesRecues:
                    m = re.search('dejbutMot=(.*)', donnejesRecues)
                    if m is not None:
                        self.dejbutMot = m.group(1)
                        self.fabriqueMots()
                        self.afficheTout(csock)
                        continue
                    
                # choix d'un mot ah conserver
                #     GET /dejbutMot?MOT;culainer HTTP/1.1
                m = re.search('GET /.*\?MOT;(.*) HTTP/1.1', donnejesRecues)
                if m is not None:
                    self.choisitMot(m.group(1))
                    self.afficheTout(csock)
                    continue
                
                # affichage / masquage mode d'emploi
                #     POST /modedEmploi HTTP/1.1
                if 'POST /modedEmploi HTTP/1.1' in donnejesRecues:
                    self.modedEmploi = not self.modedEmploi
                    self.afficheTout(csock)
                    continue

                else: print("PUTAIN C'EST QUOI ?")
                csock.close()  
                #print('----------------------')
            except Exception as exc:
                if not exc.args == (32, 'Broken pipe'): raise
                print (exc.args)
        
    ###############################        
    def afficheTout(self, csock):
        # l'en-teste
        imageHtml = self.imageBase64("{}/echiquierLatejcon4-200T.png".format(self.scriptsDir))
        csock.sendall(("""
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
            <title>fabrique ah mots</title>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
            <style type="text/css">
            a:link { text-decoration:none; } 
            sti { color:black;  font-size: 35pt; margin: 0%%; font-weight:normal; font-style: italic;}
            mi1 { color:black; font-size: 16pt; margin: 0%%; font-weight:normal; }
            mi2 { color:darkred; font-size: 16pt; margin: 0%%; font-weight:normal; }
            mi3 { color:darkgreen; font-size: 16pt; margin: 0%%; font-weight:normal; }
            mi4 { color:black; font-size: 16pt; margin: 0%%; font-weight:bold; }
            mi5 { color:darkred }
            mi6 { color:darkgreen }
            #af1 {margin-top: 20px; margin-bottom: 20px; margin-right: 100px; margin-left: 50px; background-color: White; }
            #af2 {margin-top: 20px; margin-bottom: 20px; margin-right: 100px; margin-left: 100px; background-color: White; }
            #af3 {margin-top: 20px; margin-bottom: 20px; margin-right: 0px; margin-left: 50px; background-color: White; }
            </style>
            </head>
            """).encode('utf-8'))
        # le titre
        csock.sendall(("""
            <body>
            <table><tr><td><sti>la fabrique à mots de </sti></td><td>{}</td></tr></table>
            """.format(imageHtml)).encode('utf-8'))
        
        # les corpus
        csock.sendall(("""
            <div id="af1"><mi1>le corpus modehle (au choix) :</br></mi1></div><div id="af2">
            """).encode('utf-8'))
        alt = True
        for nomCorpus in list(self.tousLesCorpus.keys()):
            alt = not alt
            if nomCorpus == self.corpus: mic = 'mi4'
            elif alt: mic = 'mi3'
            else: mic = 'mi2'
            csock.sendall(("""
                <a href="?CORPUS;{}"><{}>{}</{}></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                """.format(nomCorpus, mic, nomCorpus, mic)).encode('utf-8'))
        csock.sendall('</div>'.encode('utf-8'))
        
        # si un corpus est dejjah choisi, affiche le champs pour renseigner le dejbut de mot et l'ordre de fabriquer
        if self.corpus != '':
            csock.sendall(("""
                <div id="af1">
                <form action="dejbutMot" method="post">
                <mi1>le dejbut des mots (optionnel) : </mi1>
                <input type="text" name="dejbutMot" value="{}" style="font-size: 16pt" size="10">
                <br/><mi1>l'ordre de </mi1>
                <input type="submit" value="fabriquer" style="font-size: 16pt">
                </form> 
                </div>
                """.format(self.dejbutMot)).encode('utf-8'))
            
        # si des mots ont dejjah ejtej fabriquejs, les affiche
        if len(self.motsFabriquejs) != 0:
            csock.sendall('<div id="af2">'.encode('utf-8'))
            alt = True
            for mot in self.motsFabriquejs:
                alt = not alt
                if mot in self.motsSejlectionnejs: mic = 'mi4'
                elif alt: mic = 'mi3'
                else: mic = 'mi2'
                csock.sendall(("""
                    <a href="?MOT;{}"><{}>{}</{}></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    """.format(mot, mic, mot, mic)).encode('utf-8'))
            csock.sendall('</div>'.encode('utf-8'))
            
        # le mode d'emploi
        csock.sendall(("""
            <div id="af3">
            <br/><br/><br/>
            <form action="modedEmploi" method="post">
            <input type="submit" value="mode d'emploi" style="font-size: 10pt">
            </form>
            """).encode('utf-8'))
        if self.modedEmploi:
            csock.sendall(("""
            Tout ce qui est en couleur (<mi5>rouge</mi5> et <mi6>vert</mi6>) et <b>en gras</b> est clicable.
            <br/>Le corpus qui sert à modejliser doit estre sejlectionné en premier. On peut changer à tout moment de corpus modehle en cliquant simplement sur le nom du nouveau corpus choisi.
            <br/>La contrainte de dejbut pour les mots fabriquejs est optionnelle. Si le champ est laissé vide, la fabrique à mots travaille sans contrainte.
            <br/>Pour fabriquer de nouveaux mots, il suffit de donner l'ordre de fabriquer.
            <br/>L'ordre de fabriquer efface tous les mots en <mi5>rouge</mi5> et <mi6>vert</mi6> et les remplace par les nouveaux mots fabriquejs. Pour conserver un mot par delà d'une nouvelle fabrication, il suffit de cliquer ce mot. Il apparaist alors <b>en gras</b> et ne sera pas effacé lors de la prochaine fabrication. Inversement, pour remettre un mot sauvegardé (affiché <b>en gras</b>) dans la liste des mots effaçables, il suffit de cliquer ce mot. Il redevient alors affiché en <mi5>rouge</mi5> ou <mi6>vert</mi6>. 
            <br/>La sauvegarde des mots fabriquejs ne peut se faire que par un copier-coller.
            <br/>Pour effacer ce mode d'emploi, il suffit de cliquer sur le bouton "mode d'emploi".
            """).encode('utf-8'))
            

        csock.sendall('</div></body>'.encode('utf-8'))
                
    ###############################        
    def imageBase64(self, nom):
        try:
            with open(nom, 'rb') as img:
                extension = nom.split('.')[-1]
                imgStr = base64.b64encode(img.read()).decode()
                return '<img src="data:image/{};base64,{}">\n'.format(extension, imgStr)
        except Exception:
            traceback.print_exc()
            return '<blink>Image pas trouveje !</blink>'
        
    ###############################        
    def choisitCorpus(self, corpusCliquej):
        # si c'est dejjah ce corpus, raf
        if corpusCliquej == self.corpus: return
        # init nouveau corpus et mejmorise
        nomFichier = self.scriptsDir + '/' + self.tousLesCorpus[corpusCliquej]
        self.markovSurMots.initCorpus(nomFichier)
        self.corpus = corpusCliquej
    
    ###############################        
    def fabriqueMots(self):
        # 1) met les mots sejlectionnejs en teste de la liste des mots fabriquejs
        self.motsFabriquejs = deepcopy(self.motsSejlectionnejs)
        # 2) complehte la liste des mots fabriquejs ah 100 
        # il est possible qu'un dejbut de mot ne puisse gejnejrer suffisamment de mots diffejrents
        compteurdArrest = 0
        while compteurdArrest < NBMOTS*10 and len(self.motsFabriquejs) < NBMOTS:
            compteurdArrest +=1
            nouveauMot = self.markovSurMots.complehteMot(self.dejbutMot)
            if nouveauMot in self.motsFabriquejs: continue
            self.motsFabriquejs.append(nouveauMot)
            
    ###############################        
    def choisitMot(self, motCliquej):
        # si le mot est sejlectionnej, le dejselectionne
        # si le mot n'est pas sejlectionnej, le selectionne
        if motCliquej in self.motsSejlectionnejs: self.motsSejlectionnejs.remove(motCliquej)
        else:self.motsSejlectionnejs.append(motCliquej)

    
if __name__ == '__main__':
    main()
