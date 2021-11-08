# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 22:07:22 2021

@author: pcjean
"""



import PySimpleGUI as sg
import os.path
import sys
import platform

#
# Sous programmes associés au codage/décodage de vcard
#

def str2list(chaine): # renvoie une liste de string à partir d'une string entre []
    l = []
    ch1 = chaine.strip("[]")
    ch2 = ch1.replace("'","")
    ch = ch2.replace(" ","")
    l = ch.split(",")
    return l

def tascii(chaine): # test si une chaine de caratère est ASCII ou pas
    return all(ord(c) < 128 for c in chaine)

def str_to_utf(strencod): # encodage en UTF8 d'une chaine de caractère
    strdecod1 = ";"
#    print("donnees à encoder: " + strencod)
    lisenc = strencod.split(";")
    for j in range(len(lisenc)):
        strdecod = ""
        str1 = lisenc[j].encode()
        bstr1 = bytearray(str1)
        strdec = bstr1.hex()
        if len(strdec) != 0:

            for k in range(int(len(strdec)/2)):
                strint = strdec[2*k]+ strdec[2*k+1]
#                if strint == "20" : strint= "0A"
                strdecod = strdecod+ "=" + strint
        else: strdecod =""
        if len(strdec) !=0: strdecod1 = strdecod1 + ";" + strdecod 
#    print(strdecod1)
    return strdecod1

def utf_to_str(strdecod): # decodage des valeurs codées UTF8
    strutf1 = ''
    strutf2 = ''
    strhex = ''
    for i in range(len(strdecod)):

        if strdecod[i] == "=": # début de byte
            strhex = strhex + ' '

        elif strdecod[i] == ";":  # fin de séquence
            strhex = strhex.replace('0A','20')
            byte_array = bytearray.fromhex(strhex)
            strutf1 = byte_array.decode('utf-8','replace')
            strutf2 = strutf2 + strutf1 + ','
            strutf1 = ''
            strhex = ''
        elif strdecod[i] == '\r':
            strdecod.replace('\r',' ')
        elif strdecod[i] == '\n':
            strdecod.replace('\n',' ')
        else:
            strhex = strhex + strdecod[i]
            strhex = strhex.replace('0A','20')

    byte_array = bytearray.fromhex(strhex)
    strutf1 = byte_array.decode('utf-8','replace')

    strutf2 = strutf2 + strutf1
    return strutf2

def encodDon(ligne): # construction de la ligne du fichier vcf
#    print(ligne)
    ligdon = ""
    delim1 = ':'
    delim2 = ';'
    nonascii = False
    ligdon = str(ligne[1])
    nbpara = ligne[2]
    valeurs = str(ligne[4])
    if nbpara == 0: 
        delim = delim1
    else: 
        delim = delim2
        for j in range(len(ligne[3])):
            delim = delim + str(ligne[3][j]) + delim2
# si beson d'encoder en UTF 8
            if (str(ligne[3][j]) == 'ENCODING=QUOTED-PRINTABLE'):
                nonascii = True
                valeurs = str_to_utf(str(ligne[4]))
# si valeurs comporte des caractères non ASCII nouveaux
#        la ligne suivante n'est valable qu'après Python 3.7
#        if (ligne[4].isascii() == False) and (nonascii == False):
        if (tascii(ligne[4]) == False) and (nonascii == False):
            delim = delim + 'ENCODING=QUOTED-PRINTABLE'+ delim2
            valeurs = str_to_utf(str(ligne[4]))
#            print(delim)
        delim = delim[:len(delim)-1]+delim1
    ligdon = ligdon + delim + valeurs
    return ligdon
    
def decode_card(adecod, long):
#   extraction des données property, paramètres et valeurs pour chaque ligne
#   décodage des données 
    propert = ''
    param = ''
    valeurc = ''
    res = []
    listpar= []
    deb1 = adecod.find(':')
    deb2 = adecod.find(';')
    if ((deb1 == -1)): deb1 = 999
    if ((deb2 == -1)): deb2 = 999
    debmotc = min(deb1,deb2)
    if (debmotc != 999):
        propert = adecod[:debmotc]
        param = adecod[(debmotc+1):(deb1)]
        valeur = adecod[(deb1+1):long]
        if (param.find('ENCODING=QUOTED-PRINTABLE') != -1):
#            print('à décoder '+ valeur)
            lisdec = valeur.split(";")
            for j in range(len(lisdec)):
                valeurc = valeurc + ";" + utf_to_str(lisdec[j])
        else:
            valeurc = valeur

        if (param != ''): res = [0]
        res.extend([j for j in range(len(param)) if param.startswith(";", j)])
        nbrpar = len(res)
        param = param.replace(';',' ', 5) # au max 5 paramètres!!!
        for i in range(nbrpar):
            if (i != nbrpar-1): 
                if (i == 0): listpar.append(param[res[i]:res[i+1]])
                else: listpar.append(param[res[i]+1:res[i+1]])
            else: 
                if (nbrpar != 1): listpar.append(param[res[i]+1:])
                else: listpar.append(param[res[i]:])
#        print(listpar)
    return propert, listpar, valeurc , nbrpar, res

#
def litVcard(fichdonn, fichres):
#
# lecture du fichier des vcard, décodage et remplissage de la liste de travail
#
    initvcard = []
    nbcard = 0
    bdecod =''
    longueur = 0
    resu = []
    listcard = []
    listot = []
    listi = []
    listvac = []
    photo = 0
    
    try:
        with open(fichdonn,'r') as fich:  # ouverture fichier
            with open(fichres,'w') as fichr:  # ouverture fichier résultat
                initvcard = fich.readlines()
                for i in range(len(initvcard)):
                    if (initvcard[i].find('BEGIN') != -1): #debut carte
                        nbcard = nbcard + 1
                        bdecod = ''
                        debut = 1
                        listi = []
                    elif (initvcard[i].find('END') != -1): #fin carte
                        prop, para, val, respar, resu = decode_card(bdecod, longueur)
                        listcard = [nbcard,prop,respar,para,val]
                        fichr.write(str(listcard)+ '\n')
                        listot.append(listcard)
                        listi.append(listcard)
                        listvac.append(listi)
                        photo = 0
        
                    elif (initvcard[i].find('VERSION') != -1):
                        pass
                    elif (initvcard[i].find('PHOTO') != -1):
                        photo = 1
                    elif initvcard[i][0] == 'X': # cas des property specifique à un téléphone
                        pass
                    elif ((photo == 1) and (initvcard[i][0] == ' ')): # donnee suite photo
                        pass
                    elif (initvcard[i][0] == '\r') or (initvcard[i][0] == '\n'):
                        pass
                    else:
                        photo = 0
                        if (initvcard[i][0] == '='): # donnee suite
                            bdecod = bdecod + initvcard[i]
                            longueur = longueur + len(initvcard[i])
                            prop, para, val , respar, resu = decode_card(bdecod, longueur)
        
                        elif (i != 0):
                            if (debut != 1): 
                                prop, para, val, respar, resu = decode_card(bdecod, longueur)
                                if (prop != ' '):
                                    listcard = [nbcard, prop,respar,para,val]
                                    fichr.write(str(listcard)+ '\n')
                                    listot.append(listcard)
                                    listi.append(listcard)
                            bdecod = initvcard[i]
                            longueur = len(initvcard[i])-1
                            debut = 0
                            
                print(nbcard)
            return listot, nbcard, listvac
    except Exception as e:
        print(e, file=sys.stderr)
        pass
    return
#
# 

def ficRes(data, fichdat):
#
#  on reconstitue un fichier vcf à partir de la liste modifiée
#
    delim1 = ':'
    delim2 = ';'

    try:
        with open(fichdat,'w') as fid:
            inid = 0
            nbcard = 0

            for i in range(len(data)-1): # toutes les donnees sauf la derniere
                if data[i][0] != inid: #1ere donnee differente = nouvelle vcard
                    inid = data[i][0]
                    nbcard = nbcard + 1
                    if i != 0: fid.write("END:VCARD\n") # on met d'abord le delimiteur de fin
                    fid.write("BEGIN:VCARD\n") # on commence une nouvelle vcard
                    fid.write("VERSION:2.1\n")
                    sortie = encodDon(data[i])
                    fid.write(sortie + "\n")
                else:
                    sortie = encodDon(data[i])
                    fid.write(sortie + "\n")
                    

            ncard = len(data)  # derniere donnee
            sortie = encodDon(data[ncard-1])
            fid.write(sortie + "\n")
            fid.write("END:VCARD")
            
        print(nbcard)

    except Exception as e:
        print("erreur transcription "+ str(data[i]))
        print(e, file = sys.stderr)
        pass
    return

def ficRes2(donnees, fichdat):
    data = []
    for i in range(len(donnees)):
        for j in range(len(donnees[i])):
            data.append(donnees[i][j])
    ficRes(data, fichdat)
    return

