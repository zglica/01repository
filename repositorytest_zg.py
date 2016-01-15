# -*- coding: utf-8 -*-

import repository_zg
import sqlite3
import unittest

db_path = 'zg.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Produkty')
        c.execute('DELETE FROM Zamowienie')
        c.execute('''INSERT INTO Zamowienie (id_zamowienie, data_zamowienia, kwota) VALUES(1, '2016-01-13', 3000)''')
        c.execute('''INSERT INTO Produkty (nazwa, kwota, ilosc, id_zamowienie) VALUES('komputer',5000,4,1)''')
        c.execute('''INSERT INTO Produkty (nazwa, kwota, ilosc, id_zamowienie) VALUES('laptop',5300,2,1)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Produkty')
        c.execute('DELETE FROM Zamowienie')
        conn.commit()
        conn.close()

    def testGetByIdInstance(self):
        zamowienie = repository_zg.ZamowienieRepository().getById(1)
        self.assertIsInstance(zamowienie, repository_zg.Zamowienie, "Objekt nie jest klasy Zamowienie")

    def testGetByIdNotFound(self):
        self.assertEqual(repository_zg.ZamowienieRepository().getById(4),
                None, "Powinno wyjść None")

    def testGetByIdInvitemsLen(self):
        self.assertEqual(len(repository_zg.ZamowienieRepository().getById(1).produkty),
                6, "Powinno wyjść 6")

    def testDeleteNotFound(self):
        self.assertRaises(repository_zg.RepositoryException,
                repository_zg.ZamowienieRepository().delete, 4)



if __name__ == "__main__":
    unittest.main()
