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

    except sqlite3.Error:
        print "Cannot connect to %s" % ( dbname )
        sys.exit(1)

    return con



def fetchFilter(name):
    con = dbconnect("Filters.db")
    cur = con.cursor()
    cur.execute("SELECT lambda, transmission FROM filterData WHERE name = '%s'" % (name))
    res = cur.fetchall()
    cur.execute("SELECT centralWavelength FROM filterInfo WHERE name = '%s'" % (name))
    lambdaCenter, = cur.fetchone()
    con.close()
    return lambdaCenter, res


def quad(x,y):
    return np.sum( ( y[1:] + y[:-1] ) * ( x[1:] - x[:-1] ) ) / 2


def synphot(spec, filt, lambdaCenter):

    filtResample = interpolate.interp1d(filt['lambda'], filt['transmission'], bounds_error=False, fill_value=0.)(spec['lambda'])
    flux = quad(spec['lambda'], spec['lambda'] * spec['flux'] * filtResample) / quad( spec['lambda'], spec['lambda'] * filtResample )

    return -2.5 * np.log10(flux * lambdaCenter * ( lambdaCenter * 1e-8 ) / speedOfLight ) - 48.60


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
    lc = np.array(synthesizeLightCurve(filt='PTF R'), dtype=[('day', 'f'), ('mag', 'f')])
    with open("PTF_R_IaTemplate.txt", "w") as fp:
        fp.write("# day, mag\n")
        fp.write("".join(["%(day)5.2f  %(mag)5.2f\n" % row for row in lc]))
    lc = np.array(synthesizeLightCurve(filt='PTF g'), dtype=[('day', 'f'), ('mag', 'f')])
    with open("PTF_g_IaTemplate.txt", "w") as fp:
        fp.write("# day, mag\n")
        fp.write("".join(["%(day)5.2f  %(mag)5.2f\n" % row for row in lc]))
    lc = np.array(synthesizeLightCurve(filt='swift b'), dtype=[('day', 'f'), ('mag', 'f')])
    with open("swift_b_IaTemplate.txt", "w") as fp:
        fp.write("# day, mag\n")
        fp.write("".join(["%(day)5.2f  %(mag)5.2f\n" % row for row in lc]))