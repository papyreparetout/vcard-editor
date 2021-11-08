# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 22:07:22 2021

@author: pcjean
"""



import PySimpleGUI as sg
import os.path
import sys
# import platform
import vcard_module as vm

#
# Programme principal

# ------ Make the Table Data ------
# data: liste des données élémentaires des vcard
# datav: liste de liste, chaque datav correspond à une carte 
# contenant les data élémentaires associées
#
data = []
datav = []
headings = ['numéro',
#'property','nb param',
    'valeur']

sg.theme('Dark Blue 3') 

# layout de la fenêtre principale
menu_def = [['Fichier',['Ouvrir', 'Save', 'Exit'  ]], ['Editer', ['Modifier','Inserer','Supprimer']]]
layout = [
          [sg.Menu(menu_def, background_color='lightsteelblue',text_color='navy',
            disabled_text_color='yellow', font='Verdana', pad=(10,10),key = 'menu')],
          [sg.Text('Données du fichier .vcf sélectionné')],
          [sg.Table(values=datav, headings = headings,
            auto_size_columns=False,
            key = 'Table',enable_click_events = True,
            )],
          ]

window = sg.Window("Vcard editor", layout, resizable=True, finalize=True )
window2_active = False
window3_active = False 

# event loop

while True:  # Event Loop
    event, values = window.read()
    print("event: " + str(event) + " values: "+ str(values))
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    if event == 'Ouvrir':   # on ouvre le fichier des vcard
        fichdon = sg.popup_get_file('file to open', no_window=True,file_types=(("Vcf Files", "*.vcf"),))      
        print("fichier: " + fichdon)
        folder = os.path.dirname(fichdon)
        listaffich = []
        try:
#            ouverture fichiers données et résultat
            fichres = folder + '/result.txt'
            fichd = folder +'/data.vcf'
            data, nbc, datav = vm.litVcard(fichdon, fichres)
            for j in range(len(datav)):
#      on n'affiche que le numéro et la valeur de la première ligne de la vcard
                listaffich.append([datav[j][0][0],datav[j][0][4]] )

# remplissage de la fenêtre par la table issue de la liste
            window['Table'].update(listaffich)
# pour que la fenêtre soit redimensionnable
            window['Table'].expand(True,True)
            window['Table'].table_frame.pack(expand=True, fill='both')
        except Exception as e:
            print("pas de fichier choisi")
            print(e, file = sys.stderr)
            sg.popup('pas de fichier choisi!')
            
# edition: modification d'une ligne de données
    try:
        if not window3_active and event == 'Modifier' and not values['Table'] == []:
            ligne = values['Table']
            print("modification ligne : " + str(ligne[0]))
            window3_active = True
            valinit1 = str(data[ligne[0]][0])
            valinit2 = str(data[ligne[0]][1])
            valinit3 = str(data[ligne[0]][2])
            valinit4 = str(data[ligne[0]][3])
            valinit5 = str(data[ligne[0]][4])
            layout3 = [
            [sg.Text('Données')],
            [sg.Text('Numéro',size = (15,1)),sg.Input( default_text = valinit1,#)],
                enable_events=False, key='INNUM')],
            [sg.Text('property', size =(15, 1)), sg.Input(default_text = valinit2,
                enable_events=False, key='INPROP')],
            [sg.Text('nb param', size =(15, 1)), sg.Input(default_text = valinit3,
                enable_events=False, key='INNBPAR')],
            [sg.Text('paramètre', size =(15, 1)), sg.Input(default_text = valinit4,
                enable_events=False, key='INPAR')],
            [sg.Text('valeur', size =(15, 1)), sg.Input(default_text = valinit5,
                enable_events=False, key='INVAL')],
            [sg.Submit(button_text='Modifier', key = 'modif'), sg.Cancel(button_text = 'Annuler', key = 'annul')]
              ]
            window3 = sg.Window("Données", layout3)
            if window3_active:
                ev3, vals3 = window3.read()
                print("event3: " + str(ev3) + " values3: "+ str(vals3))
                if ev3 == sg.WIN_CLOSED or ev3 == 'Exit' or ev3 == 'annul':
                    window3_active  = False
                    window3.close()
                if ev3 == 'modif':
                    newnum = int(vals3['INNUM'])
                    newprop = vals3['INPROP']
                    newnbpar = int(vals3['INNBPAR'])
                    newparam = []
                    if vals3['INPAR'] != '': newparam = [vals3['INPAR']]
                    newvalue = vals3['INVAL']
                    newdata = [newnum, newprop,newnbpar,newparam,newvalue]
    # on vient insérer la nouvelle ligne et detruire l'ancienne '                    
                    data.insert(ligne[0],newdata)
                    data.pop(ligne[0]+1)
                    window3_active  = False
                    window3.close()
            window['Table'].update(data)
                
    # edition: insertion d'une ligne de données
        if not window2_active and event == 'Inserer' and not values['Table'] == []:
            ligne = values['Table']
            print("insertion ligne : " + str(ligne[0]))
            window2_active = True
            layout2 = [
            [sg.Text('Données')], [sg.Text('Numéro',size = (15,1)),sg.Input( #)],
                enable_events=False, key='INNUM')],
            [sg.Text('property', size =(15, 1)), sg.Input(
                enable_events=False, key='INPROP')],
            [sg.Text('nb param', size =(15, 1)), sg.Input(
                enable_events=False, key='INNBPAR')],
            [sg.Text('paramètre', size =(15, 1)), sg.Input(
                enable_events=False, key='INPAR')],
            [sg.Text('valeur', size =(15, 1)), sg.Input(
                enable_events=False, key='INVAL')],
            [sg.Submit(button_text='Inserer', key = 'inser'), sg.Cancel(button_text = 'Annuler', key = 'annul')]
              ]
            window2 = sg.Window("Données", layout2)
    #        affichage fenetre pour insérer des données
            if window2_active:
                ev2, vals2 = window2.read()
                print("event2: " + str(ev2) + " values2: "+ str(vals2))
                if ev2 == sg.WIN_CLOSED or ev2 == 'Exit' or ev2 == 'annul':
                    window2_active  = False
                    window2.close()
                if ev2 == 'inser':
                    newnum = int(vals2['INNUM'])
                    newprop = vals2['INPROP']
                    newnbpar = int(vals2['INNBPAR'])
                    newparam = []
                    if vals2['INPAR'] != '': newparam = [vals2['INPAR']]
                    newvalue = vals2['INVAL']
                    newdata = [newnum, newprop,newnbpar,newparam,newvalue]
                    data.insert(ligne[0],newdata)
                    window2_active  = False
                    window2.close()
                    
            window['Table'].update(data)
    # edition: suppression d'une vcard donc de toutes les données associées
        if event == 'Supprimer':
            ligne = values['Table']
            print("suppression ligne : " + str(ligne[0]))
            print("données : "+ str(datav[ligne[0]]))
            listaffich.pop(ligne[0])
            datav.pop(ligne[0])
            window['Table'].update(listaffich)

    except Exception as e:
        print("erreur édition")
        print(e, file = sys.stderr)
        sg.popup('erreur edition')

# si option save on sauve le résultat dans un nouveau fichier
    if event == 'Save':
        fichd = sg.popup_get_file('file to open', save_as = True, no_window=True,file_types=(("Vcf Files", "*.vcf"),))      
        print("fichier sortie: " + fichd)
        vm.ficRes2(datav,fichd)
# fin du programme
window.close()
