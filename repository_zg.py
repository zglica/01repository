import sqlite3
from datetime import datetime

db_path = 'zg.db'

import scipy
import numpy
import numpy as np
import matplotlib.pylab as plt
from scipy import stats


class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

#
# Model danych
#

class Zamowienie():

    def __init__(self, id_zamowienie, data_zamowienia=[], produkty=[] ):
        self.id_zamowienie = id_zamowienie
        self.data_zamowienia = data_zamowienia
        self.produkty = produkty
        self.kwota = sum([item.kwota*item.ilosc for item in self.produkty])

    def __repr__(self):
        return "<Zamowienie(id_zamowienie='%s', data_zamowienia='%s', kwota='%s', items='%s')>" % (
                    self.id_zamowienie, str(self.data_zamowienia), str(self.kwota), str(self.produkty)
                )

class Produkt():

    def __init__(self, nazwa=[], kwota=[], ilosc=[]):
        self.nazwa = nazwa
        self.kwota = kwota
        self.ilosc = ilosc

    def __repr__(self):
        return "<Produkt(nazwa='%s', kwota='%s', ilosc='%s')>" % (
                    str(self.nazwa), str(self.kwota), str(self.ilosc)
                )

#
# Klasa bazowa repozytorium
#
class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)


class ZamowienieRepository(Repository):

    def add(self, zamowienie):
        """Metoda dodaje pojedyncze zamowienie do bazy danych,
        wraz ze wszystkimi jego pozycjami.
        """
        try:
            c = self.conn.cursor()
            # zapisz nagłowek zamowienia
            kwota = sum([item.kwota*item.ilosc for item in zamowienie.produkty])
            c.execute('INSERT INTO Zamowienie (id_zamowienie, data_zamowienia, kwota) VALUES(?, ?, ?)',
                        (zamowienie.id_zamowienie, str(zamowienie.data_zamowienia), zamowienie.kwota)
                    )
            # zapisz pozycje zamowienia
            if zamowienie.produkty:
                for produkt in zamowienie.produkty:
                    try:
                        c.execute('INSERT INTO Produkty (nazwa, kwota, ilosc, id_zamowienie) VALUES(?,?,?,?)',
                                        (produkt.nazwa, produkt.kwota, produkt.ilosc, zamowienie.id_zamowienie)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding zamowienie item: %s, to zamowienie: %s' %
                                                    (str(produkt), str(zamowienie.id_zamowienie))
                                                )
        except Exception as e:
            #print "zamowienie add error:", e
            raise RepositoryException('error adding zamowienie %s' % str(zamowienie))

    def delete(self, zamowienie):
        """Metoda usuwa pojedyncze zamowienie z bazy danych,
        wraz ze wszystkimi jego pozycjami.
        """
        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Produkty WHERE id_zamowienie=?', (zamowienie.id_zamowienie,))
            # usuń nagłowek
            c.execute('DELETE FROM Zamowienie WHERE id_zamowienie=?', (zamowienie.id_zamowienie,))

        except Exception as e:
            #print "zamowienie delete error:", e
            raise RepositoryException('error deleting zamowienie %s' % str(zamowienie))

    def getById(self, id_zamowienie):
        """Get zamowienie by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Zamowienie WHERE id_zamowienie=?", (id_zamowienie,))
            zam_row = c.fetchone()
            zamowienie = Zamowienie(id_zamowienie=id_zamowienie)
            if zam_row == None:
                zamowienie=None
            else:
                zamowienie.data_zamowienia = zam_row[1]
                zamowienie.kwota = zam_row[2]
                c.execute("SELECT * FROM Produkty WHERE id_zamowienie=? order by nazwa", (id_zamowienie,))
                zam_items_rows = c.fetchall()
                items_list = []
                for item_row in zam_items_rows:
                    item = Produkt(nazwa=item_row[0], kwota=item_row[1], ilosc=item_row[2])
                    items_list.append(item)
                zamowienie.produkty=items_list
        except Exception as e:
            #print "zamowienie getById error:", e
            raise RepositoryException('error getting by id_zamowienie id_zamowienie: %s' % str(id_zamowienie))
        return zamowienie

    def update(self, zamowienie):
        """Metoda uaktualnia pojedyncze zamowienie w bazie danych,
        wraz ze wszystkimi jego pozycjami.
        """
        try:
            # pobierz z bazy zamowienie
            inv_oryg = self.getById(zamowienie.id_zamowienie)
            if inv_oryg != None:
                # zamowienie jest w bazie: usuń je
                self.delete(zamowienie)
            self.add(zamowienie)

        except Exception as e:
            #print "zamowienie update error:", e
            raise RepositoryException('error updating zamowienie %s' % str(zamowienie))

#tworzymy pierwsze zamowienie
if __name__ == '__main__':
    try:
        with ZamowienieRepository() as zamowienie_repository:
            zamowienie_repository.add(
                Zamowienie(id_zamowienie = 1, data_zamowienia = datetime.now(),
                        produkty = [
                            Produkt(nazwa = "komputer",   kwota = 3500, ilosc = 5),
                            Produkt(nazwa = "myszka",    kwota = 35, ilosc = 6),
                            Produkt(nazwa = "klawiatura",  kwota = 32, ilosc = 5),
                        ]
                    )
                )
            zamowienie_repository.complete()
    except RepositoryException as e:
        print(e)

    print(ZamowienieRepository().getById(1))

#dodajemy zamowienie nr 2
    try:
        with ZamowienieRepository() as zamowienie_repository:
            zamowienie_repository.add(
                Zamowienie(id_zamowienie = 2, data_zamowienia = datetime.now(),
                        produkty = [
                            Produkt(nazwa = "laptop", kwota = 4200, ilosc = 2),
                            Produkt(nazwa = "mikrofon", kwota = 69, ilosc = 3),
                            Produkt(nazwa = "kamera",   kwota = 49, ilosc = 4),
                            Produkt(nazwa = "pendrive", kwota=35, ilosc = 10),
                            Produkt(nazwa = "głośniki", kwota = 550, ilosc = 5)
                        ]
                    )
                )
            zamowienie_repository.complete()
    except RepositoryException as e:
        print(e)

    print(ZamowienieRepository().getById(2))

# dodajemy zamowienie nr 3
    try:
        with ZamowienieRepository() as zamowienie_repository:
            zamowienie_repository.add(
                Zamowienie(id_zamowienie = 3, data_zamowienia = datetime.now(),
                        produkty = [
                            Produkt(nazwa = "powerbank", kwota = 90, ilosc = 10),
                            Produkt(nazwa = "drukarka laserowa", kwota = 650, ilosc = 3),
                            Produkt(nazwa = "notebook",   kwota = 3200, ilosc = 5),
                            Produkt(nazwa = "tablet", kwota=350, ilosc = 10),
                            Produkt(nazwa = "laptop", kwota = 2500, ilosc =3)
                        ]
                    )
                )
            zamowienie_repository.complete()
    except RepositoryException as e:
        print(e)

    print(ZamowienieRepository().getById(3))

# aktualizujemy zamowienie nr 1
    try:
        with ZamowienieRepository() as zamowienie_repository:
            zamowienie_repository.update(
                Zamowienie(id_zamowienie = 1, data_zamowienia = datetime.now(),
                        produkty = [
                            Produkt(nazwa = "komputer", kwota = 4500, ilosc = 2),
                            Produkt(nazwa = "myszka", kwota = 46, ilosc = 3),
                            Produkt(nazwa = "drukarka",  kwota = 540, ilosc = 4),
                            Produkt(nazwa = "klawiatura", kwota = 43, ilosc = 2),
                            Produkt(nazwa = "notebook", kwota = 530, ilosc = 5),
                            Produkt(nazwa = "aparat", kwota = 1800, ilosc = 2)
                        ]
                    )
                )
            zamowienie_repository.complete()
    except ZamowienieException as e:
        print(e)

    print(ZamowienieRepository().getById(1))

# usuwamy zamówienie nr 1
   # try:
   #     with ZamowienieRepository() as zamowienie_repository:
   #         zamowienie_repository.delete( Zamowienie(id_zamowienie = 1) )
   #         zamowienie_repository.complete()
   # except RepositoryException as e:
   #     print(e)

#przeprowadzimy testy statystyczne dotyczące 1 zamowienia
#k=kwota*ilosc danego produktu
k1=[4500*2,46*3,540*4,43*2,530*5,1800*2]
print(k1)
n, (k1min, k1max), k1m, k1v, k1s, k1k = stats.describe(k1)
k1str = 'mean = %6.4f, variance = %6.4f, skew = %6.4f, kurtosis = %6.4f'
print ('statystyka kwot z zamowienia 1:')
print (k1str %(k1m, k1v, k1s, k1k))

#teraz przeprowadzimy testy statystyczne dla kwot z 3 zamowien
k2=[4200*2,69*3,49*4,35*10,550*5]
k3=[90*10,650*3,3200*5,350*10,2500*3]
print('kwota zamowienia 1:')
print(sum(k1))
print('kwota zamowienia 2:')
print(sum(k2))
print('kwota zamowienia3:')
print(sum(k3))
x=[sum(k1),sum(k2),sum(k3)]
n, (xmin, xmax), xm, xv, xs, xk = stats.describe(x)
xstr = 'mean = %6.4f, variance = %6.4f, skew = %6.4f, kurtosis = %6.4f'
print ('statystyka kwot z 3 zamowien:')
print (xstr %(xm, xv, xs, xk))




