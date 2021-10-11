# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 22:07:22 2021

@author: pcjean
"""



import PySimpleGUI as sg
import os.path
import sys
import pandas as pd
#import os
import platform



#
# Sous programmes
#

def data_to_str(strdecod): # decodage des valeurs codées UTF
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

#
    
def decode_card(adecod, long):
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
            valeurc = data_to_str(valeur)
        else:
            valeurc = valeur

        if (param != ''): res = [0]
        res.extend([j for j in range(len(param)) if param.startswith(";", j)])
        nbrpar = len(res)
        param = param.replace(';',' ', 5)
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
    initvcard = []
    nbcard = 0
    bdecod =''
    longueur = 0
    resu = []
    listcard = []
    listot = []
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
                    elif (initvcard[i].find('END') != -1): #fin carte
                        prop, para, val, respar, resu = decode_card(bdecod, longueur)
                        listcard = [nbcard,prop,respar,para,val]
                        fichr.write(str(listcard)+ '\n')
                        listot.append(listcard)
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
                            bdecod = initvcard[i]
                            longueur = len(initvcard[i])-1
                            debut = 0
                            
            #    listot.append(listcard)
                print(nbcard)
        
    #            donne = pd.DataFrame(data = listot, columns = ['numéro','property','nb param', 'paramètres', 'valeur'])
    #        return donne, nbcard
    #            donne = pd.DataFrame(data = listot, columns = ['numéro','property','nb param', 'paramètres', 'valeur'])
            return listot, nbcard
    except:
        pass
    return
    
# fichier resultat
usersystem = platform.system() # on teste le systeme pour adapter
print("système :" + usersystem) 
if (usersystem == "Windows"):
    fichres = 'D:/Documents/fichier_appli/python/vcard/result.txt'
else:
    fichres = '/home/jean/Documents/fichier_appli/python/vcard/result.txt'

# ------ Make the Table Data ------
data = []
headings = ['numéro','property','nb param', 'paramètres', 'valeur']


sg.theme('Dark Blue 3')  # please make your windows colorful


# First the window layout
menu_def = [['Fichier',['Ouvrir', 'Save', 'Exit'  ]], ['Editer', ['Modifier','Inserer','Supprimer']]]
layout = [
          [sg.Menu(menu_def, background_color='lightsteelblue',text_color='navy',
            disabled_text_color='yellow', font='Verdana', pad=(10,10),key = 'menu')],
          [sg.Text('Données du fichier .vcf sélectionné')],
          [sg.Table(values=data[1:][:], headings = headings,
    # Set column widths for empty record of table
            auto_size_columns=False,
#            change_submits = True,
#            col_widths=list(map(lambda x:len(x)+1, headings)),
            key = 'Table',enable_click_events = True)],
          ]


window = sg.Window("Vcard editor", layout )
window2_active = False 

#                   , size =(600,600))

# event loop

while True:  # Event Loop
    event, values = window.read()
    print("event: " + str(event) + " values: "+ str(values))
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    if event == 'Ouvrir':
        fichdon = sg.popup_get_file('file to open', no_window=True,file_types=(("Vcf Files", "*.vcf"),))      
        print("fichier: " + fichdon)
        try:
            fichdon
            data, nbc = litVcard(fichdon, fichres)
            window['Table'].update(data)
        except:
            print("pas de fichier choisi")
            
# edition: modification d'une ligne de données
    if event == 'Modifier':
        ligne = values['Table']
        print("modification ligne : " + str(ligne[0]))
#        data.insert(ligne[0],["insertion"])
        window['Table'].update(data)
            
# edition: insertion d'une ligne de données
    if not window2_active and event == 'Inserer' and not values['Table'] == []:
        ligne = values['Table']
        print("insertion ligne : " + str(ligne[0]))
        window2_active = True
        layout2 = [
        [sg.Text('Données')], [sg.Text('Numéro',size = (15,1)),sg.Input()],
        [sg.Text('Age', size =(15, 1)), sg.InputText()],
        [sg.Text('Phone', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Modifier', key = 'modif'), sg.Cancel(button_text = 'Annuler', key = 'annul')]
          ]
        window2 = sg.Window("Données", layout2)
#        affichage fenetre pour insérer des données
        if window2_active:
            ev2, vals2 = window2.read()
            print("event2: " + str(ev2) + " values2: "+ str(vals2))
            if ev2 == sg.WIN_CLOSED or ev2 == 'Exit' or ev2 == 'annul':
                window2_active  = False
                window2.close()
            if ev2 == 'modif':
                newnum = vals2[0]
                data.insert(ligne[0],[newnum])
                window2_active  = False
                window2.close()
                
        window['Table'].update(data)
# edition: suppression d'une ligne
    if event == 'Supprimer':
        ligne = values['Table']
        print("suppression ligne : " + str(ligne[0]))
        print("données : "+ str(data[ligne[0]]))
        data.pop(ligne[0])
        window['Table'].update(data)
# fin du programme
window.close()
