# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 15:51:17 2021

@author: pcjean
"""
import PySimpleGUI as sg
import os.path
import sys
# import platform
import vcard_class_module as vm

class Vcard:
    def __init__(self,numer,prop,val, listprop):
        self.numero = numer
        self.ident = prop
        self.valeur = val
        self.listprop = listprop

#
# Programme principal

# ------ Make the Table Data ------
# data: liste des données élémentaires des vcard
# datav: liste de liste, chaque datav correspond à une carte 
# contenant les data élémentaires associées
#

listaffich = []
cartes = []
#nbinit = 0
#propriete = []
headings = ['numéro','valeur']

sg.theme('Dark Blue 3') 

# layout de la fenêtre principale
menu_def = [['Fichier',['Ouvrir', 'Save', 'Exit'  ]], ['Editer', ['Modifier','Inserer','Supprimer']]]
layout = [
          [sg.Menu(menu_def, background_color='lightsteelblue',text_color='navy',
            disabled_text_color='yellow', font='Verdana', pad=(10,10),key = 'menu')],
          [sg.Text('Données du fichier .vcf sélectionné')],
          [sg.Table(values=listaffich, headings = headings,
            auto_size_columns=False,
            expand_x = True, # pour etendre automatiquement et éviter erreur sur click hors table
            key = 'Table',enable_click_events = True,
            )],
          ]

window = sg.Window("Vcard editor", layout, resizable=True, finalize=True )
window2_active = False
window3_active = False 

while True:  # Event Loop
    event, values = window.read()
    print("event: " + str(event) + " values: "+ str(values))
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    if event == 'Ouvrir':   # on ouvre le fichier des vcard
        fichdon = sg.popup_get_file('file to open', no_window=True,file_types=(("Vcf Files", "*.vcf"),))      
        print("fichier: " + fichdon)
        folder = os.path.dirname(fichdon)
#        listaffich = []
        try:
#            ouverture fichiers résultat lecture
            fichres = folder + '/result.txt'
            nbc, cartes = vm.litVcard(fichdon, fichres)
# affichage des vcard    
            for j in range(len(cartes)):
#      on n'affiche que le numéro et la valeur de la première ligne de la vcard
                listaffich.append([cartes[j].numero, cartes[j].valeur] )
# remplissage de la fenêtre par la table issue de la liste
            window['Table'].update(listaffich)
# pour que la fenêtre soit redimensionnable
            window['Table'].expand(True,True)
            window['Table'].table_frame.pack(expand=True, fill='both')
            
        except Exception as e:
            print("pas de fichier choisi")
            print(e, file = sys.stderr)
            sg.popup('pas de fichier choisi!' + '\n'+ str(e))

# gestion des vcard: modification, insertion, suppression
    try:
        # edition: modification d'une vcard
        if not window2_active and event == 'Modifier' and not values['Table'] == []:
            ligne = values['Table']
            listm = []
            print("modification vcard numéro : " + str(ligne[0]))
            cardm = cartes[ligne[0]]
            window2_active = True
            window2_active, suppr = vm.Fenmodv(window2_active, cardm)
            window2_active  = False
            if suppr: # suppression de toutes les properties donc de la vcard
                cartes.pop(ligne[0])
#      mise à jour de la fenetre des vcard
            listaffich = []
            for j in range(len(cartes)):
#      on n'affiche que le numéro et la valeur de la première ligne de la vcard
                listaffich.append([cartes[j].numero, cartes[j].valeur] )
            window['Table'].update(listaffich)
                
    # edition: insertion d'une vcard
        if not window3_active and event == 'Inserer' and not values['Table'] == []:
            ligne = values['Table']
            print("insertion vcard : " + str(ligne[0]))
            fini = False
            listp = []
            ligd = int(ligne[0])
            while fini != True:
                window3_active = True
                window3_active, fini = vm.Fenins(window3_active, ligd, listp)
                window3_active = False
#            carttemp = Vcard((int(ligne[0])), listp[0][1],listp[0][3],listp)
            carttemp = Vcard((nbc+1), listp[0][1],listp[0][3],listp)
            nbc = nbc + 1
            cartes.insert(int(ligne[0]),carttemp)
            #      mise à jour de la fenetre des vcard
            listaffich = []
            for j in range(len(cartes)):
#      on n'affiche que le numéro et la valeur de la première ligne de la vcard
                listaffich.append([cartes[j].numero, cartes[j].valeur] )
            window['Table'].update(listaffich)

    # edition: suppression d'une vcard donc de toutes les données associées
        if event == 'Supprimer':
            ligne = values['Table']
            print("suppression ligne : " + str(ligne[0]))
            print("données : "+ str(cartes[ligne[0]]))
            listaffich.pop(ligne[0])
            cartes.pop(ligne[0])
            window['Table'].update(listaffich)

    except Exception as e:
        print("erreur édition")
        print(e, file = sys.stderr)
        sg.popup('erreur edition' + '\n' + str(e))

# si option save on sauve le résultat dans un nouveau fichier
    if event == 'Save':
        fichd = sg.popup_get_file('file to open', save_as = True, no_window=True,file_types=(("Vcf Files", "*.vcf"),))      
        print("fichier sortie: " + fichd)
        vm.ficRes2(cartes,fichd)
# fin du programme
window.close()
            







        
