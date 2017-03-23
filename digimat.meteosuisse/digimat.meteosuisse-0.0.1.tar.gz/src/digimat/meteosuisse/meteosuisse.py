import csv
from datetime import datetime


class MeteoSuisseDataFile(object):
    def __init__(self):
        self.raz()

    def raz(self):
        self._columns=[]
        self._units=[]
        self._site=None

    def guessColumnUnitFromName(self, name):
        try:
            if name[:3]=='tre':
                return 1
            if name[:3]=='ure' or name[:3]=='sre':
                return 4
            if name[:2]=='su':
                return 18
        except:
            pass

    def setColumnsUnits(self):
        for col in range(2, len(self._columns)):
            name=self._columns[col]
            unit=self.guessColumnUnitFromName(name)
            if unit is not None:
                self._units[col]=unit

    def declareSite(self, site):
        if not self._site and site:
            self._site=site.lower()

    def declareColumns(self, columns):
        if not self._columns and columns:
            columns=[c.lower() for c in columns]
            if 'stn' in columns:
                self._columns=columns
                self._units=[255 for c in columns]
                self.setColumnsUnits()

    def getColumn(self, name):
        try:
            return self._columns.index(name.lower())
        except:
            pass

    def getRowColumn(self, row, name):
        try:
            return row[self.getColumn(name)]
        except:
            pass

    def getKeyFromColumnIndex(self, index):
        try:
            if index>1:
                key='r_9100_2_mto%s%s_0_0' % (self._site, self._columns[index])
                return key.lower()
        except:
            pass

    def parseStamp(self, rdate):
        try:
            return datetime.strptime(rdate, '%d/%m/%Y')
        except:
            pass

        try:
            return datetime.strptime(rdate, '%d.%m.%Y')
        except:
            pass

    def readDataRow(self, row):
        try:
            if self._columns and row and len(row)==len(self._columns):
                self.declareSite(self.getRowColumn(row, 'stn'))

                data=[]

                # 'date', 'zeit', ... better use index for this column!
                dt=self.parseStamp(row[1])
                if dt:
                    for i in range(len(row)):
                        try:
                            key=self.getKeyFromColumnIndex(i)
                            value=float(row[i])
                            unit=self._units[i]
                            data.append({'stamp': dt, 'key': key, 'value': value, 'unit': unit})
                        except:
                            pass
                    return data
        except:
            self.logger.exception('readDataRow')
            pass

    def read(self, f):
        self.raz()
        try:
            data=[]
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
            for row in reader:
                if row:
                    if not self._columns:
                        self.declareColumns(row)
                    else:
                        rdata=self.readDataRow(row)
                        if rdata:
                            data.extend(rdata)
            return data
        except:
            pass

    def readFile(self, fpath):
        try:
            with open(fpath, 'rb') as f:
                return self.read(f)
        except:
            pass


class MeteoSuisseDailyDataFile(MeteoSuisseDataFile):
    pass


if __name__ == "__main__":
    pass
