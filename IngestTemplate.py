__author__ = 'ycao'


import sqlite3
import cStringIO
import sys


def dbconnect():
    try:
        con = sqlite3.connect("SNIaTemplate.db")

        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')

        data = cur.fetchone()

        print "SQLite version: %s" % data

    except sqlite3.Error:
        print "Cannot connect to SNIaTemplate.db"
        sys.exit(1)

    return con


def ingestTemplate():

    con = dbconnect()

    cur = con.cursor()

    # normal Ia
    cur.execute("CREATE TABLE IF NOT EXISTS normal(day REAL, lambda REAL, flux REAL)")

    with open("sn1a_flux.v1.2.dat", "r") as fp:
        entry = ( tuple(map(float, row.split())) for row in fp if float(row.split()[0]) > 0.1 )
        cur.executemany("INSERT INTO normal VALUES(?,?,?)", entry)

    # 91bg-like
    cur.execute("CREATE TABLE IF NOT EXISTS SN1991bg(day REAL, lambda REAL, flux REAL)")

    with open("sn91bg_flux.v1.1.dat", "r") as fp:
        entry = ( tuple(map(float, row.split())) for row in fp if float(row.split()[0]) > 0.1 )
        cur.executemany("INSERT INTO SN1991bg VALUES(?,?,?)", entry)

        # normal Ia
    cur.execute("CREATE TABLE IF NOT EXISTS SN1991T(day REAL, lambda REAL, flux REAL)")

    with open("sn91t_flux.v1.1.dat", "r") as fp:
        entry = ( tuple(map(float, row.split())) for row in fp if float(row.split()[0]) > 0.1 )
        cur.executemany("INSERT INTO SN1991T VALUES(?,?,?)", entry)

    con.commit()

    return


if __name__ == "__main__":

    ingestTemplate()