__author__ = 'ycao'
__version__ = "0.1.0"

import sqlite3
import numpy as np
import sys
from scipy import interpolate

speedOfLight = 3.e10

def dbconnect(dbname):
    try:
        con = sqlite3.connect(dbname)

        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')

        data = cur.fetchone()

        print "SQLite version: %s" % data

    except sqlite3.Error:
        print "Cannot connect to SNIaTemplate.db"
        sys.exit(1)

    return con



def fetchFilter(name):
    con = dbconnect("Filters.db")
    cur = con.cursor()
    cur.execute("SELECT lambda, transmission FROM filterData WHERE name = ?", (name))
    res = cur.fetchall()
    cur.execute("SELECT centralWavelength FROM filterInfo WHERE name = ?", (name))
    lambdaCenter, = cur.fetchone()
    con.close()
    return lambdaCenter, res


def quad(x,y):
    return ( y[1:] + y[:-1] ) * ( x[1:] - x[:-1] ) / 2


def synphot(spec, filt, lambdaCenter):

    filtResample = interpolate.interp1d(filt['lambda'], filt['transmission'], bounds_error=False, fill_value=0.)(spec['lambda'])
    flux = quad(spec['lambda'], spec['lambda'] * spec['flux'] * filtResample) / ( spec['lambda'], spec['lambda'] * filtResample )

    return -2.5 * np.log10(flux * lambdaCenter * ( lambdaCenter * 1e-8 ) / speedOfLight )


def fetchSpecSeries(tableName):
    con = dbconnect("SNIaTemplate.db")
    cur = con.cursor()
    cur.execute("SELECT day, lambda, flux FROM %s" % tableName)
    res = cur.fetchall()
    con.close()
    return res


def synthesizeLightCurve(SN = 'normal', filt = "PTF R", z = 0):

    lambdaCenter, tbl = fetchFilter(filt)
    filterCurve = np.array(tbl, dtype=[('lambda', 'f'), ('transmission', 'f')])

    specSeries = fetchSpecSeries(SN)

    def calSynMag(day):
        spec = [ ( row[1], row[2] ) for row in specSeries if row[0] == day ]
        spec.sort()
        spec = np.array(spec, dtype = [ ( 'lambda', 'f' ), ( 'flux', 'f' ) ])
        spec['lambda'] = spec['lambda'] * ( 1 + z )
        spec['flux'] = spec['flux'] * ( 1 + z )
        return day, synphot(spec, filterCurve, lambdaCenter)

    synLC = map(calSynMag, { row[0] for row in specSeries })
    synLC.sort()

    return synLC

if __name__ == "__main__":
    print synthesizeLightCurve()