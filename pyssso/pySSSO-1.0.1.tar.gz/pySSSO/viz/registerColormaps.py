#!/usr/bin/env python

"""
  Registring own colormaps.

  Includes:
    - Examples for registering own color maps
    - Utility for listing and showing all or selected named colormaps 
      including self-defined ones
"""

#-------------
# Load modules
#-------------
import matplotlib
import matplotlib.colors as col
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

#-------------------------
def make_colormap(colors):
#-------------------------
    """
    Define a new color map based on values specified in the dictionary
    colors, where colors[z] is the color that value z should be mapped to,
    with linear interpolation between the given values of z.

    The z values (dictionary keys) are real numbers and the values
    colors[z] can be either an RGB list, e.g. [1,0,0] for red, or an
    html hex string, e.g. "#ff0000" for red.
    """

    from matplotlib.colors import LinearSegmentedColormap, ColorConverter
    from numpy import sort

    z = sort(colors.keys())
    n = len(z)
    z1 = min(z)
    zn = max(z)
    x0 = (z - z1) / (zn - z1)

    CC = ColorConverter()
    R = []
    G = []
    B = []
    for i in range(n):
        #i'th color at level z[i]:
        Ci = colors[z[i]]
        if type(Ci) == str:
            # a hex string of form '#ff0000' for example (for red)
            RGB = CC.to_rgb(Ci)
        else:
            # assume it's an RGB triple already:
            RGB = Ci
        R.append(RGB[0])
        G.append(RGB[1])
        B.append(RGB[2])

    cmap_dict = {}
    cmap_dict['red'] = [(x0[i],R[i],R[i]) for i in range(len(R))]
    cmap_dict['green'] = [(x0[i],G[i],G[i]) for i in range(len(G))]
    cmap_dict['blue'] = [(x0[i],B[i],B[i]) for i in range(len(B))]
    mymap = LinearSegmentedColormap('mymap',cmap_dict)
    return mymap


"""
  RBG dictionaries

  - Each dictionary contains a tuple structure for 'red', 'green', and 'blue'.
  - Each color has a list of (x,y0,y1) tuples, where
       * x defines the "index" in the colormap (range 0..1), 
       * y0 is the color value (0..1) left of x, and 
       * y1 the color value right of x.
  - The LinearSegmentedColormap method will linearly interpolate between
    (x[i],y1) and (x[i+1],y0)
    For any input value z falling between x[i] and x[i+1], 
    the output value of a given color will be linearly interpolated between 
    y1[i] and y0[i+1]:
                       row i:   x  y0  y1
                                      /
                                     /
                       row i+1: x  y0  y1

     Black is R=0,G=0,B=0.  White is R=1,G=1,B=1.  Pure Blue is R=0,G=0,B=1.
     Whenever the R,G,B values all equal the same value, you have a shade of gray
"""

# From purple, blue, green, orange to red
cdict_puBGOR = {
    'red'  : ((0.0, 0.0, 0.0), (0.3, 0.5, 0.5), (0.6, 0.7, 0.7), (0.9, 0.8, 0.8), (1.0, 0.8, 0.8)),
    'green': ((0.0, 0.0, 0.0), (0.3, 0.8, 0.8), (0.6, 0.7, 0.7), (0.9, 0.0, 0.0), (1.0, 0.7, 0.7)),
    'blue' : ((0.0, 1.0, 1.0), (0.3, 1.0, 1.0), (0.6, 0.0, 0.0), (0.9, 0.0, 0.0), (1.0, 1.0, 1.0))
    }

cdict = { 
    'red'   : ((0.0, 0.0, 0.0), (0.3, 1.0, 1.0), (0.5, 1.0, 1.0), (0.7, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'green' : ((0.0, 0.0, 0.0), (0.3, 0.0, 0.0), (0.5, 1.0, 1.0), (0.7, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'blue'  : ((0.0, 0.0, 0.0), (0.3, 0.0, 0.0), (0.5, 1.0, 1.0), (0.7, 1.0, 1.0), (1.0, 0.0, 0.0)),
    }

cdict_blue = {
    'blue'  : ((0,0,0),  (1,1,1)),
    'green' : ((0,0,0),  (1,0,0)),
    'red'   : ((0,0,0),  (1,0,0))
    }

cdict_gray = {
    'blue'  : ((0,0,0),  (1,1,1)),
    'green' : ((0,0,0),  (1,1,1)),
    'red'   : ((0,0,0),  (1,1,1))
    }

cdict_redtoblue = {
    'blue'  : ((0,0,0), (0.8,0,1), (1,1,1)),
    'green' : ((0,0,0), (0.8,0,0), (1,1,1)),
    'red'   : ((0,0,0), (0.8,1,0), (1,1,1))
    }

cdict_wbr = {
    'red'  : ((0., 1, 1), (0.05, 1, 1), (0.11, 0, 0), (0.66, 1, 1), (0.89, 1, 1), (1, 0.5, 0.5)),
    'green': ((0., 1, 1), (0.05, 1, 1), (0.11, 0, 0), (0.375, 1, 1), (0.64, 1, 1), (0.91, 0, 0), (1, 0, 0)),
    'blue' : ((0., 1, 1), (0.05, 1, 1), (0.11, 1, 1), (0.34, 1, 1), (0.65, 0, 0), (1, 0, 0))
    }

def register_own_cmaps():
    """
      Define two example colormaps as segmented lists and register them
    """
    # Method 1
    all_white = make_colormap({0.:'w', 1.:'w'})
    cm.register_cmap(name='all_white', cmap=all_white)

    all_light_red = make_colormap({0.:'#ffdddd', 1.:'#ffdddd'})
    cm.register_cmap(name='all_light_red', cmap=all_light_red)

    all_light_blue = make_colormap({0.:'#ddddff', 1.:'#ddddff'})
    cm.register_cmap(name='all_light_blue', cmap=all_light_blue)

    all_light_green = make_colormap({0.:'#ddffdd', 1.:'#ddffdd'})
    cm.register_cmap(name='all_light_green', cmap=all_light_green)

    all_light_yellow = make_colormap({0.:'#ffffdd', 1.:'#ffffdd'})
    cm.register_cmap(name='all_light_yellow', cmap=all_light_yellow)
    
    red_white_blue = make_colormap({0.:'r', 0.5:'w', 1.:'b'})
    cm.register_cmap(name='red_white_blue', cmap=red_white_blue)

    blue_white_red = make_colormap({0.:'b', 0.5:'w', 1.:'r'})
    cm.register_cmap(name='blue_white_red', cmap=blue_white_red)

    white_blue_red = make_colormap({0.:'w', 0.5:'b', 1.:'r'})
    cm.register_cmap(name='white_blue_red', cmap=white_blue_red)

    white_green_blue_red = make_colormap({0.:'w', 0.25:'#ddffdd', 0.75:'b', 1.:'r'})
    cm.register_cmap(name='white_green_blue_red', cmap=white_green_blue_red)

    red_yellow_blue = make_colormap({0.:'r', 0.5:'#ffff00', 1.:'b'})
    cm.register_cmap(name='red_yellow_blue', cmap=red_yellow_blue)

    blue_yellow_red = make_colormap({0.:'b', 0.5:'#ffff00', 1.:'r'})
    cm.register_cmap(name='blue_yellow_red', cmap=blue_yellow_red)

    yellow_red_blue = make_colormap({0.:'#ffff00', 0.5:'r', 1.:'b'})
    cm.register_cmap(name='yellow_red_blue', cmap=yellow_red_blue)

    white_red = make_colormap({0.:'w', 1.:'r'})
    cm.register_cmap(name='white_red', cmap=white_red)

    white_blue = make_colormap({0.:'w', 1.:'b'})
    cm.register_cmap(name='white_blue', cmap=white_blue)

    red_blue = make_colormap({0.:'r', 1.:'b'})
    cm.register_cmap(name='red_blue', cmap=red_blue)

    # Method 2
    # a good guide for choosing colors is provided at
    # http://geography.uoregon.edu/datagraphics/color_scales.htm
    #
    # colormap values are modified as c^gamma, where gamma is (1-beta) for
    # beta>0 and 1/(1+beta) for beta<=0

    cmap = col.LinearSegmentedColormap('my_colormap',cdict_puBGOR,N=256,gamma=0.75)
    cm.register_cmap(name='puBGOR', cmap=cmap)

    cmap = col.LinearSegmentedColormap('my_colormap',cdict_wbr,N=512,gamma=0.75)
    cm.register_cmap(name='wbr', cmap=cmap)

    # Method 3
    startcolor = '#586323'  # a dark olive 
    midcolor = '#fcffc9'    # a bright yellow
    endcolor = '#bd2309'    # medium dark red
    cmap2 = col.LinearSegmentedColormap.from_list('doYR',[startcolor,midcolor,endcolor])
    # extra arguments are N=256, gamma=1.0
    cm.register_cmap(cmap=cmap2)
    # we can skip name here as it was already defined 


def discrete_cmap(N=8):
    """create a colormap with N (N<15) discrete colors and register it"""
    # define individual colors as hex values
    cpool = [ '#bd2309', '#bbb12d', '#1480fa', '#14fa2f', '#000000',
              '#faf214', '#2edfea', '#ea2ec4', '#ea2e40', '#cdcdcd',
              '#577a4d', '#2e46c0', '#f59422', '#219774', '#8086d9' ]
    cmap3 = col.ListedColormap(cpool[0:N], 'indexed')
    cm.register_cmap(cmap=cmap3)

#-------------------------------------------------
# Functions for read files and creating color maps
#-------------------------------------------------

def create_cmap_from_pallete_0_255(filename, cmapName):
    """
      Read ASCII palette file containing RBG values 
      (numbers between 0 and 255) and create a color map.
 
      Arguments
         filename: palette file name to be read
         cmapName: name of the colormap you want to create

      Return value
         colormap
    """
    maxval = 255.0
    palette = open(filename)
    lines = palette.readlines()
    carray = np.zeros([len(lines), 3])
    for line in lines:
        line = line.strip()
        num, a, b, c = line.split()
        num = int(num.strip())
        carray[num, 0] = float(a)/maxval  # R
        carray[num, 1] = float(b)/maxval  # B
        carray[num, 2] = float(c)/maxval  # G
    
    palette.close()
    # Create the color map
    cmap1 = col.ListedColormap(carray, name=cmapName)
    return cmap1

def create_cmap_from_csvFile_0_1(filename, cmapName):
    """
      Read CSV file containing RBG values and create a color map.
      Values are expected in the 0-1 range, not 0-255 range. 
 
      Arguments
         filename: CSV file name to be read
         cmapName: name of the colormap you want to create

      Return value
         colormap
    """

    # Read the file
    LinL = np.loadtxt(filename, delimiter=",")
    
    b3=LinL[:,2] # value of blue at sample n
    b2=LinL[:,2] # value of blue at sample n

    # position of sample n - ranges from 0 to 1
    b1=np.linspace(0,1,len(b2))

    # setting up columns for list
    g3=LinL[:,1]
    g2=LinL[:,1]
    g1=np.linspace(0,1,len(g2))

    r3=LinL[:,0]
    r2=LinL[:,0]
    r1=np.linspace(0,1,len(r2))

    # creating list
    R=zip(r1,r2,r3)
    G=zip(g1,g2,g3)
    B=zip(b1,b2,b3)

    # transposing list
    RGB=zip(R,G,B)
    rgb=zip(*RGB)
    # print rgb

    # creating dictionary
    #--------------------
    k=['red', 'green', 'blue']
    LinearL=dict(zip(k,rgb)) # makes a dictionary from 2 lists

    my_cmap = matplotlib.colors.LinearSegmentedColormap(cmapName,LinearL)

    return my_cmap

#-------------------------------------
# Functions for displaying a color map
#-------------------------------------

def show_cmaps(names=None):
    """
       Display all colormaps included in the names list. 
       If names is None, all defined colormaps will be shown.
    """
    # base code from http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps
    matplotlib.rc('text', usetex=False)
    a=np.outer(np.arange(0,1,0.01),np.ones(10))   # pseudo image data
    f=plt.figure(figsize=(10,5))
    f.subplots_adjust(top=0.8,bottom=0.05,left=0.01,right=0.99)
    # get list of all colormap names
    # this only obtains names of built-in colormaps:
    maps=[m for m in cm.datad if not m.endswith("_r")]
    # use undocumented cmap_d dictionary instead
    maps = [m for m in cm.cmap_d if not m.endswith("_r")]
    maps.sort()
    # determine number of subplots to make
    l=len(maps)+1
    if names is not None: l=len(names)  # assume all names are correct!
    # loop over maps and plot the selected ones
    i=0
    for m in maps:
        if names is None or m in names:
            i+=1
            ax = plt.subplot(1,l,i)
            ax.axis("off")
            plt.imshow(a,aspect='auto',cmap=cm.get_cmap(m),origin="lower")
            plt.title(m,rotation=90,fontsize=10,verticalalignment='bottom')
    plt.savefig("colormaps.png",dpi=100,facecolor='gray')
    plt.show()

def print_sys_cmap():
    maps = [m for m in cm.cmap_d if not m.endswith("_r")]
    maps.sort()
    print maps


if __name__ == "__main__":
    register_own_cmaps()
    discrete_cmap(8)
    print_sys_cmap()
    show_cmaps(['indexed','Blues','OrRd','PiYG','PuOr',
                'RdYlBu','RdYlGn','afmhot','binary','copper',
                'gist_ncar','gist_rainbow','puBGOR','doYR', 'wbr',
                'white_blue', 'blue_white_red', 'all_light_green'])

    # file in http://oceancolor.gsfc.nasa.gov/DOCS/palette_chl_etc.txt
    # Removed the first line: #idx   R   G   B

    filename ="palette_chl_etc.txt"
    cmapName = 'myPalette'
    palMAP = create_cmap_from_pallete_0_255(filename, cmapName)
    cm.register_cmap(cmap=palMAP)
    print_sys_cmap()
    show_cmaps([cmapName])

    filename ="Linear_L_0-1.csv"
    cmapName = 'myCSV'
    csvMap = create_cmap_from_csvFile_0_1(filename, cmapName)
    cm.register_cmap(cmap=csvMap)
    print_sys_cmap()
    show_cmaps([cmapName])
