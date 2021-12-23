# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 22:07:22 2021

@author: pcjean
"""



import PySimpleGUI as sg
import sys


class Vcard:
    def __init__(self,numer,prop,val, listprop):
        self.numero = numer
        self.ident = prop
        self.valeur = val
        self.listprop = listprop

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
#    print("encodon")
#    print(ligne)
    ligdon = ""
    delim1 = ':'
    delim2 = ';'
    nonascii = False
    ligdon = str(ligne[1])
    nbpara = len(ligne[2])
    valeurs = str(ligne[3])
    if nbpara == 0: 
        delim = delim1
    else: 
        delim = delim2
        for j in range(len(ligne[2])):
            delim = delim + str(ligne[2][j]) + delim2
# si beson d'encoder en UTF 8
            if (str(ligne[2][j]) == 'ENCODING=QUOTED-PRINTABLE'):
                nonascii = True
                valeurs = str_to_utf(str(ligne[3]))
# si valeurs comporte des caractères non ASCII nouveaux
#        la ligne suivante n'est valable qu'après Python 3.7
#        if (ligne[4].isascii() == False) and (nonascii == False):
        if (tascii(ligne[3]) == False) and (nonascii == False):
            delim = delim + 'ENCODING=QUOTED-PRINTABLE'+ delim2
            valeurs = str_to_utf(str(ligne[3]))
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
    return propert, listpar, valeurc , res

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
    carte = []
    list_prop = []
    num = 0
    idepar =[]
    ideval = ''
    
    try:
        with open(fichdonn,'r') as fich:  # ouverture fichier
            with open(fichres,'w') as fichr:  # ouverture fichier résultat
                initvcard = fich.readlines()
                for i in range(len(initvcard)):
                    if (initvcard[i].find('BEGIN') != -1): #debut carte
#                        if nbcard != 0: carte.append(Vcard(num,idepar,ideval,list_prop))
                        list_prop = []
                        nbcard = nbcard + 1
                        bdecod = ''
                        debut = 1
                        listi = []
                        firstcard = 1
                    elif (initvcard[i].find('END') != -1): #fin carte
                        prop, para, val, resu = decode_card(bdecod, longueur)
                        listcard = [nbcard,prop,para,val]
                        list_prop.append(listcard)
                        num = list_prop[0][0]
                        idepar = list_prop[0][1]
                        ideval = list_prop[0][3]
                        """# pour test
                        print("debli")
                        print(num)
                        print(idepar)
                        print(ideval)
                        print(list_prop)
                        """# fin pour test
                        carte.append(Vcard(num,idepar,ideval,list_prop))
                        list_prop = []
                        fichr.write(str(listcard)+ '\n')
                        listot.append(listcard)
                        listi.append(listcard)
                        listvac.append(listi)
                        photo = 0
        
                    elif (initvcard[i].find('VERSION') != -1): #  Version
                        pass
                    elif (initvcard[i].find('PHOTO') != -1): # property photo, écartée pour l'instant
                        photo = 1
                    elif initvcard[i][0] == 'X': # cas des property specifique à un téléphone
                        pass
                    elif ((photo == 1) and (initvcard[i][0] == ' ')): # donnee suite photo
                        pass
                    elif (initvcard[i][0] == '\r') or (initvcard[i][0] == '\n'): # donnée suite
                        pass
                    else:
                        photo = 0
                        if (initvcard[i][0] == '='): # donnee suite d'une property valide
                            bdecod = bdecod + initvcard[i]
                            longueur = longueur + len(initvcard[i])
                            prop, para, val , resu = decode_card(bdecod, longueur)
        
                        elif (i != 0):
                            if (debut != 1): #property apres BEGIN et VERSION
                                prop, para, val, resu = decode_card(bdecod, longueur)
                                if (prop != ' '):
                                    listcard = [nbcard, prop,para,val]
                                    if firstcard == 1: # premiere property 
                                        num = nbcard
                                        idepar = prop
                                        ideval = val
                                        firstcard = 0
                                    list_prop.append(listcard)
                                    fichr.write(str(listcard)+ '\n')
                                    listot.append(listcard)
                                    listi.append(listcard)
                            bdecod = initvcard[i]
                            longueur = len(initvcard[i])-1
                            debut = 0
                            
                print(nbcard)
                """# pour test
                print(" fin lit")
                for i in range(len(carte)):
                    print(carte[i].numero)
                    print(carte[i].ident)
                    print(carte[i].valeur)
                    print(carte[i].listprop)
                """# fin pour test
            return nbcard, carte

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
        # for j in range(len(donnees[i])):
        for j in range(len(donnees[i].listprop)):
            data.append(donnees[i].listprop[j])
#    print(data)
    ficRes(data, fichdat)
    return

def Fenmodv(win_active, cardmod):
    #
    # affichage fenetre modification d une vcard
    # on affiche sous forme de table les property de la vcard
    #
#    win3_active = False
    listm = []
    suppr = False  # indicateur de la suppression de toutes les properties
    head2 = ['numéro','property','paramètre','valeur']
    layout2 = [
    [sg.Text('Données')],
    [sg.Table(values=listm, headings = head2,
        auto_size_columns=False,
        key = 'Tab2',enable_click_events = True,
    )],
    [sg.Submit(button_text='Modifier', key = 'modif'),
     sg.Submit(button_text='Insérer', key = 'inser'),
     sg.Submit(button_text='Supprimer', key = 'suppr'),
     sg.Cancel(button_text = 'Terminer', key = 'termin')]
      ]
    window2 = sg.Window("Properties de la vcard", layout2)
    for i in range(len(cardmod.listprop)):
        listm.append(cardmod.listprop[i] )
    if win_active:
        while True:
            ev2, vals2 = window2.read()
            print("event2: " + str(ev2) + " values2: "+ str(vals2))
            if ev2 == sg.WIN_CLOSED or ev2 == 'Exit' or ev2 == 'termin':
                win_active  = False
                window2.close()
                break
            if ev2 == 'modif':
                win3_active = True
                print("appel modif prop")
# fonction de modification d'une property
                if vals2['Tab2'] != []:
                    win3_active = Fenmodprop(win3_active, cardmod, vals2['Tab2'])
# affichage modifications
                listm = []
                for i in range(len(cardmod.listprop)):
                    listm.append(cardmod.listprop[i] )
                win_active  = False
                window2['Tab2'].update(listm)
                
            if ev2 == 'inser':
                win3_active = True
                print("appel insertion prop")
# fonction d insertion d'une property
                win3_active = Fenmodprop(win3_active, cardmod,[-1])
# affichage apres modifications
                listm = []
                for i in range(len(cardmod.listprop)):
                    listm.append(cardmod.listprop[i] )
                win_active  = False
                window2['Tab2'].update(listm)

            if ev2 == 'suppr':
                win3_active = True
                if vals2['Tab2'] != []:
                    print("appel suppression prop" + str(int(vals2['Tab2'][0])))
# suppression d'une property
                    ligd = int(vals2['Tab2'][0])
                    cardmod.listprop.pop(ligd)
# si on a supprimé toutes les properties c est équivalent à supprimer la vcard
                    if cardmod.listprop == []:
                        print("suppression de toutes les properties")
                        suppr = True
# affichage apres modifications
                    listm = []
                    for i in range(len(cardmod.listprop)):
                        listm.append(cardmod.listprop[i] )
                    win_active  = False
                    window2['Tab2'].update(listm)
    #               au cas où il y a eu modif de la première ligne
            if cardmod.listprop != []:
                cardmod.numero = cardmod.listprop[0][0]
                cardmod.ident = cardmod.listprop[0][1]
                cardmod.valeur = cardmod.listprop[0][3]
            
    return win_active, suppr

def Fenmodprop(win_active, donnee, lign):
    #
    # affichage d'une fenetre de modification/ insertion d'une property
    #
    ligne = int(lign[0])
#    valinit1 = str(donnee.listprop[ligne][0])
    valinit1 = donnee.listprop[ligne][0]
    
    if ligne != -1: # modification
        valinit2 = str(donnee.listprop[ligne][1])
        valinit4 = str(donnee.listprop[ligne][2])
        valinit5 = str(donnee.listprop[ligne][3])
    else:  # insertion
        valinit2 = ""
        valinit4 = ""
        valinit5 = ""
        
    layout3 = [
    [sg.Text('Données')],
    [sg.Text('property', size =(15, 1)), sg.Input(default_text = valinit2,
        enable_events=False, key='INPROP')],
    [sg.Text('paramètre', size =(15, 1)), sg.Input(default_text = valinit4,
        enable_events=False, key='INPAR')],
    [sg.Text('valeur', size =(15, 1)), sg.Input(default_text = valinit5,
        enable_events=False, key='INVAL')],
    [sg.Submit(button_text='Modifier', key = 'modprop'),
     sg.Cancel(button_text = 'Annuler', key = 'annulp')]
      ]
    window3 = sg.Window("Données", layout3)
    if win_active:
        while True:
            ev3, vals3 = window3.read()
            print("event3: " + str(ev3) + " values3: "+ str(vals3))
            if ev3 == sg.WIN_CLOSED or ev3 == 'Exit' or ev3 == 'annulp':
                win_active  = False
                window3.close()
                break
            if ev3 == 'modprop':
                newnum = valinit1  # on ne change pas le numéro de carte
                newprop = vals3['INPROP']
                newparam = []
                if vals3['INPAR'] != '': 
                    newparam = str2list(vals3['INPAR'])
                newvalue = vals3['INVAL']
                newdata = [newnum, newprop,newparam,newvalue]
    # on vient insérer la nouvelle ligne  '                    
                donnee.listprop.insert(ligne,newdata)
                if ligne != -1: # si modif on detruit l ancienne ligne
                    donnee.listprop.pop(ligne+1)
                win_active  = False
                window3.close()

    return win_active

def Fenins(win_active, ligd, listp):
    #
    # fonction d'insertion d'une vcard
    # ligd est le numéro de vcard où faire l'insertion
    # listp est la liste des property de la vcard
    #
    fin = False
#    ligne = int(ligd[0])
    ligne = ligd
    layout4 = [
    [sg.Text('Property à insérer')],
    [sg.Text('property', size =(15, 1)), sg.Input(default_text = "",
        enable_events=False, key='INPROP')],
    [sg.Text('paramètre', size =(15, 1)), sg.Input(default_text = "",
        enable_events=False, key='INPAR')],
    [sg.Text('valeur', size =(15, 1)), sg.Input(default_text = "",
        enable_events=False, key='INVAL')],
    [sg.Submit(button_text='Insérer', key = 'insprop'),
     sg.Submit(button_text='Fin insertion', key = 'fins'),
     sg.Cancel(button_text = 'Annuler', key = 'annuli')]
      ]
    window4 = sg.Window("Property à insérer", layout4)
    if win_active:
        while True:
            ev4, vals4 = window4.read()
            print("event4: " + str(ev4) + " values4: "+ str(vals4))
            if ev4 == sg.WIN_CLOSED or ev4 == 'Exit' or ev4 == 'annuli':
                win_active  = False
                window4.close()
                break
            if ev4 == 'fins':
                newprop = vals4['INPROP']
                newparam = []
                if vals4['INPAR'] != '': 
                    newparam = str2list(vals4['INPAR'])
                newvalue = vals4['INVAL']
                newdata = [ligne, newprop,newparam,newvalue]
                listp.append(newdata)
                win_active = False
                window4.close()
                fin = True
            if ev4 == 'insprop':
                newprop = vals4['INPROP']
                newparam = []
                if vals4['INPAR'] != '': 
                    newparam = str2list(vals4['INPAR'])
                newvalue = vals4['INVAL']
                newdata = [ligne, newprop,newparam,newvalue]
                listp.append(newdata)
                win_active  = False
                window4.close()
                
    return win_active, fin