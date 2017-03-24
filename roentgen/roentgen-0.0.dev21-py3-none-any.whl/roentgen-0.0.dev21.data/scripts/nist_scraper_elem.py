# the following scripts scraps the data from NIST
# and writes the data files
#
import numpy as np
import urllib2
import re

url_base = "http://physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/"
savefile = False

for z in np.arange(1, 93, 1):
    f = 'z' + str(z).zfill(2)
    url = url_base + f + '.html'
    print(url)
    r = urllib2.urlopen(url).read()
    lines = r.split('\n')
    title = re.sub('<[^<]+?>', '', lines[1])
    element_name = title.rsplit(None, 1)[-1]
    short_lines = [line[0:5] for line in lines]
    try:
        line_numbers = [short_lines.index('<PRE>')+6, short_lines.index('</PRE')]
    except:
        print('failed')
        continue
    data_str = lines[line_numbers[0]:line_numbers[1]]
    data_str = [datum.lstrip().rstrip().split() for datum in data_str]
    # remove edge strings
    #for datum in data_str:
        #if len(datum) > 3:
        #    print(datum)
    data = [datum[1:] if len(datum) > 3 else datum for datum in data_str]
    # remove empty lines
    data = [datum for datum in data if len(datum) > 1]
    data = np.array(data, dtype=np.float)
    header = 'Data Source: NIST\n'
    header += 'For more information see \nhttp://physics.nist.gov/PhysRefData/XrayMassCoef/tab3.html\n'
    header += 'For definitions see http://physics.nist.gov/PhysRefData/XrayMassCoef/chap2.html\n'
    header += 'url: ' + url + '\n'
    header += '\n'
    header += element_name + '\n'
    header += '\n'
    header += 'energy, mu/rho, mu_en/rho\n'
    header += 'meV, cm2/g, cm2/g'

    if savefile:
        np.savetxt(f + '.csv', data,                # array to save
            fmt='%.3e',
            delimiter=',',          # column delimiter
            newline='\n',           # new line character
            footer='end of file',   # file footer
            comments='# ',          # character to use for comments
            header=header)
