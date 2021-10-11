# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 23:25:46 2021

@author: pcjean
"""

import sys
import pandas as pd
import os
import platform

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import (QObject, QCoreApplication,
                           QLocale, QTranslator, QLibraryInfo)

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import (QInputDialog, QLineEdit,QToolBar,
QPushButton, QProgressBar,QAction,
QSlider, QWidget,QLabel,QVBoxLayout,
QMessageBox,QFileDialog)
from PyQt5.QtWidgets import QTableView,QDataWidgetMapper

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
    
            donne = pd.DataFrame(data = listot, columns = ['numéro','property','nb param', 'paramètres', 'valeur'])
        return donne, nbcard
    
#
class pandasModel(QAbstractTableModel): # pour traitement 

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
# modification pour edition
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            return True
        return False

    def insertRows(self, position, rows, QModelIndex, parent):
        self.beginInsertRows(QModelIndex, position, position+rows-1)
        default_row = ['']*len(self._data[0])  # or _headers if you have that defined.
        self._data.insert(position, default_row)
        self.endInsertRows()
        self.layoutChanged.emit()
        return True

    def removeRows(self, position, rows, QModelIndex):
        print("donnees: "+ str(position) + "row " + str(rows))
        self.beginRemoveRows(QModelIndex, position, position+rows-1)
        del(self._data[position])
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    def flags(self, index):
# pour definir le comportement
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled 

# Fenetre prinicpale pour ouvrir le fichier vcard et editer
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.row = 0
        self.setWindowTitle("Gestion carnet adresses")
# ajout toolbar haut de la fenetre
        self.setFixedSize(QSize(800, 600))
        toolbar = QToolBar("Main toolbar")
        self.addToolBar(toolbar)
# ajout bouton a la toolbar
        button_1 = QAction("Fichier", self)
        button_1.setStatusTip("button 1")
        button_1.triggered.connect(self.ouvrirFichier)
        toolbar.addAction(button_1)
        button_2 = QAction("Modifier", self)
        button_2.setStatusTip("button 2")
        button_2.triggered.connect(self.choix1Vcard)
        toolbar.addAction(button_2)
        button_3 = QAction("Insérer", self)
        button_3.setStatusTip("button 3")
        button_3.triggered.connect(self.insert_row)
        toolbar.addAction(button_3)
        button_4 = QAction("Effacer", self)
        button_4.setStatusTip("button 4")
        button_4.triggered.connect(self.delete_row)
        toolbar.addAction(button_4)


#
    def ouvrirFichier(self):
#
# fenetre de dialogue pour ouvrir le fichier de vcards
# le lire et decoder les vcards
# puis remplir un panda et le modele QT associe à ce panda
        dossier = QFileDialog.getOpenFileName(self)
        QMessageBox.information(self,"Fichier sélectionné",
        "\n"+ dossier[0])
        print(dossier[0])
        fichdonn = dossier[0]
        donne, nbc = litVcard(fichdonn, fichres)
        self.model = pandasModel(donne)
        widgets1 = QLabel()
        widgets1.setText("Nombre de vcard: "+ str(nbc))
        self.widget2 = QTableView(self)
        self.widget2.setModel(self.model)
        vbox = QVBoxLayout()
        vbox.addWidget(widgets1)
        vbox.addWidget(self.widget2)
        widget = QWidget()
        widget.setLayout(vbox)
# si click dans une cellule on appelle la fenetre de modification
#        self.widget2.clicked.connect(self.choixVcard)
        self.setCentralWidget(widget)
        return
    
    def insert_row(self):
        index = self.widget2.currentIndex()
        print("insertion: "+ str(index))
        self.model.insertRows(index.row(), 1, index, None)
    
    def delete_row(self):
        index = self.widget2.selectionModel().currentIndex()
        print("delete: "+ str(index))
        self.model.removeRows(index.row(), 1, index)
    
    
    def choix1Vcard(self):
        # #selected cell value.
        index=(self.widget2.selectionModel().currentIndex())
        self.row =index.row()
        self.editVcard(self.model,self.row)
        return self.row

    def choix2Vcard(self):
        index=(self.widget2.selectionModel().currentIndex())
        self.row =index.row()
        self.insVcard(self.model,self.row)
        return
    
    def choix3Vcard(self):
        index=(self.widget2.selectionModel().currentIndex())
        self.row =index.row()
        self.delVcard(self.model,self.row)
        return
    
    def editVcard(self,model, row):
        self.window2 = fenetrePresentation(self.model, self.row)
        self.window2.show()
        return
    
    def insVcard(self,model, row):
        print("insertion")
#        self.window2 = fenetrePresentation(self.model, self.row)
#        self.window2.show()
        return
    
    def delVcard(self,model, row):
        print("effacer " +str(row))
        self.model.removeRow(self.row)
        self.model.submit()
        self.widget2.update()
#        self.window2 = fenetrePresentation(self.model, self.row)
#        self.window2.show()
        return
#  
#  Pour présentation d une carte
#
class fenetrePresentation(QMainWindow):
    def __init__(self,model, row):
        super().__init__()
# creation d une fenetre
# pour presentation d une carte a la ligne row
# row est recu comme parametre 
        self.setWindowTitle("Modification vcard")
# ajout toolbar haut de la fenetre
#        
        toolbar = QToolBar("Edit toolbar")
        self.addToolBar(toolbar)
        button_1 = QAction("Enregistrer", self)
        button_1.setStatusTip("button 1")
        button_1.triggered.connect(self.enrVcard)
        toolbar.addAction(button_1)

# definition des types de champs de la fenetre de modif
        self.vclabel = QLabel(" carte ")
        self.vcnum = QLineEdit()
        self.vcpropert = QLineEdit()
        self.vcnumpara = QLineEdit()
        self.vcparam = QLineEdit()
        self.vcvaleur = QLineEdit()
# mappage de la fenetre de modif aux items du modele
# references par les colonnes : 0, 1, 2...
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(model)
        self.mapper.addMapping(self.vcnum,0)
        self.mapper.addMapping(self.vcpropert,1)
        self.mapper.addMapping(self.vcnumpara,2)
        self.mapper.addMapping(self.vcparam,3)
        self.mapper.addMapping(self.vcvaleur,4)
#  on se positionne sur la ligne de la cellule selectionnee
# et on mappe avec ses donnees
        self.mapper.setCurrentIndex(row)
#  pour ne pas autoriser la modification automatique du modele
# on bascule en manual submit sinon en auto toute modif est 
# automatiquement rapportee dans le modele
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.vbox1 = QVBoxLayout()
        self.vbox1.addWidget(self.vclabel)
        self.vbox1.addWidget(self.vcnum)
        self.vbox1.addWidget(self.vcpropert)
        self.vbox1.addWidget(self.vcnumpara)
        self.vbox1.addWidget(self.vcparam)
        self.vbox1.addWidget(self.vcvaleur)
        self.widget1 = QWidget()
        self.widget1.setLayout(self.vbox1)
        self.setCentralWidget(self.widget1)
        
    def enrVcard(self):
        print("enregistrement")
# les modifications apportées à la vcard sont reportees dans le modele
        self.mapper.submit()
        self.widget1.close()
        return        
    

#
#
#  Programme principal
#
#
if __name__ == '__main__':
    
    # fichier resultat
    usersystem = platform.system() # on teste le systeme pour adapter
    print("système :" + usersystem) 
    if (usersystem == "Windows"):
        fichres = 'D:/Documents/fichier_appli/python/vcard/result.txt'
    else:
        fichres = '/home/jean/Documents/fichier_appli/python/vcard/result.txt'

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()