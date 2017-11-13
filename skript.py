#!/usr/bin/env python3

###################################################################################################################################
# Skript zur Abfrage einer Windows Exchange 2016 Rest-API und anschließender Erstellung einer SQLite3 Datenbank.                  #
# Die Kontaktdaten werden zur Namensauflösung mittels AGI-Skript für Asterisk bereitgestellt.                                     #
###################################################################################################################################

import requests
from requests.auth import HTTPBasicAuth
import sqlite3

# Name oder IP-Adresse des Exchange Servers
exchange='172.30.0.20'

# ID des Abzufragenden Kontaktverzeichnisses. Dieses wird mit einem Benutzer in Microsoft Outlook erstellt
contactfolder_id='AAMkADkwODlkYzViLWI0MzMtNDIzNi1hMzg3LTU1ZDViYzM2MjU3YgAuAAAAAADfHxF3n46JSK5A30DV3XEPAQCg6_qwVh_mSaPouIh_YqpxAAAH8tarAAA='

# Benutzername und Passwort des Exchange Users, der das Kontaktverzeichniss erstellt hat
credential_user='administrator@daninc.lokal'
credential_password='Decoit2017'

# Pfad für die SQLite3 Datenbank
path_sqlite3db='/var/lib/asterisk/telefonbuch.db'

# Abfrage der REST-Api mit Credentials. 
# Im ISS-Webserver muss bei der Site "API" die Authorizierungsmethode Standard aktiviert werden
resp = requests.get('https://%s/api/v2.0/me/contactfolders/%s/contacts?$select=DisplayName,HomePhones,MobilePhone1,BusinessPhones,CompanyName' % (exchange,contactfolder_id), auth=HTTPBasicAuth('%s' % credential_user,'%s' % credential_password), verify=False)

# Der Verbindungsaufbau wird Kontrolliert
if resp.status_code != 200:
    print (resp.status_code)
    exit (resp.status_code) 

contacts = resp.json()

liste=[]

for contact in (contacts['value']):

    for number in contact['HomePhones']:
        liste.append((contact['DisplayName'],number,contact['CompanyName']))

    if contact['MobilePhone1']:
        liste.append((contact['DisplayName'],contact['MobilePhone1'],contact['CompanyName']))

    for number in contact['BusinessPhones']:
        liste.append((contact['DisplayName'],number,contact['CompanyName']))

connection = sqlite3.connect('%s' % path_sqlite3db)
connection.execute('DROP TABLE IF EXISTS TELEFONBUCH')
connection.execute('CREATE TABLE TELEFONBUCH (DisplayName VARCHAR(20) NOT NULL , Number VARCHAR(20) NOT NULL , Company VARCHAR(20));')

for row in liste:
    connection.execute("INSERT INTO TELEFONBUCH ('DisplayName','Number','Company') VALUES (?,?,?);",(row[0],row[1],row[2]))

connection.commit()

connection.close()
