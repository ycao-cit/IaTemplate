__author__ = 'ycao'


import sqlite3
import numpy as np
import pyfits

def dbconnect():
    try:
        con = sqlite3.connect("Filters.db")

        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')

        data = cur.fetchone()

        print "SQLite version: %s" % data

    except sqlite3.Error:
        print "Cannot connect to SNIaTemplate.db"
        sys.exit(1)

    return con



def createTables():

    con = dbconnect()
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS filterInfo ( name Text, centralWavelength REAL ) ")

    cur.execute("CREATE TABLE IF NOT EXISTS filterData ( name Text, lambda REAL, transmission REAL ) ")

    cur.execute("CREATE INDEX IF NOT EXISTS name_filter_idx ON filterData(name)")

    con.commit()

    con.close()

    return


def insertFilter(name, centralWavelength, data):

    con = dbconnect()
    cur = con.cursor()

    cur.execute("INSERT INTO filterInfo VALUES ( ?, ? )", ( name, centralWavelength ))

    cur.executemany("INSERT INTO filterData VALUES ( ?, ?, ? )",
                    ( tuple([name, float(row['lambda']), float(row['transmission'])]) for row in data ) )

    con.commit()

    con.close()

    return



def main():

    createTables()

    # PTF filters
    data = np.genfromtxt("PTF_R.txt", dtype = [ ( 'lambda', 'f' ), ( 'transmission', 'f' ) ])
    data['lambda'] = data['lambda'] * 10
    insertFilter("PTF R", 6581., data)

    data = np.genfromtxt("PTF_g.txt", dtype = [ ( 'lambda', 'f' ), ( 'transmission', 'f' ) ])
    data['lambda'] = data['lambda'] * 10
    insertFilter("PTF g", 4770., data)


    # Swift filters
    filenameDict = { 'b': 'swubb_20041120v104.arf', 'u': 'swuuu_20041120v104.arf', 'v': 'swuvv_20041120v104.arf',
                     'uvw1': 'swuw1_20041120v106.arf', 'uvm2': 'swum2_20041120v105.arf', 'uvw2': 'swuw2_20041120v105.arf' }
    lambda_eff = { 'v': 5468., 'b': 4392., 'u': 3465., 'uvw1': 2600., 'uvm2': 2246, 'uvw2': 1928. }
    for filt, filename in filenameDict.iteritems():
        tbl = pyfits.getdata(filename, ext=1)
        data = np.ndarray(len(tbl), dtype = [ ( 'lambda', 'f' ), ( 'transmission', 'f' ) ] )
        data['lambda'] = ( tbl['WAVE_MIN'] + tbl['WAVE_MAX'] ) / 2.
        data['transmission'] = tbl['SPECRESP']
        insertFilter("swift %s" % filt, lambda_eff[filt], data)

    return


if __name__ == "__main__":
    main()