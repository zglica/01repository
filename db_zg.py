# -*- coding: utf-8 -*-

import sqlite3

db_path = 'zg.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#

c.execute('''
          CREATE TABLE Zamowienie
          ( id_zamowienie INTEGER PRIMARY KEY,
            data_zamowienia DATE NOT NULL,
            kwota NUMERIC NOT NULL
          )
          ''')

c.execute('''
          CREATE TABLE Produkty
          ( nazwa VARCHAR(30),
            kwota MONEY NOT NULL,
            ilosc INTEGER NOT NULL,
            id_zamowienie INTEGER,
           FOREIGN KEY(id_zamowienie) REFERENCES Zamowienie(id),
           PRIMARY KEY (nazwa, id_zamowienie))
          ''')
