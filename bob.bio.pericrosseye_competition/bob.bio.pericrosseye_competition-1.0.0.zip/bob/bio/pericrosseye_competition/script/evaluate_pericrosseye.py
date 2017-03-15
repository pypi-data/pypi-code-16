#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Thu 12 Nov 2015 16:35:08 CET 
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the ipyplotied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

"""This script evaluates the given score files and computes EER, HTER.
It also is able to plot CMC and ROC curves."""

import bob.measure

import argparse
import numpy, math
import os

# matplotlib stuff
import matplotlib; matplotlib.use('pdf') #avoids TkInter threaded start
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages

# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
# increase the default font size
matplotlib.rc('font', size=18)

import bob.core
logger = bob.core.log.setup("bob.bio.pericrossed")


def _plot_roc(scores_input, colors, labels, title, linestyle=None,fontsize=18, position=None):

    #linestyle = ['-','--','-','--','-','--']
    linestyle = None

    if position is None: position = 4
    figure = pyplot.figure()
      
    logger.info("Computing CAR curves on the development " )
    fars = [math.pow(10., i * 0.25) for i in range(-16,0)] + [1.] 
    frrs = [bob.measure.roc_for_far(scores[0], scores[1], fars) for scores in scores_input]
     
    offset = 0
    step   = int(len(scores_input)/len(labels))
   
    #For each group of labels
    for i in range(len(labels)):

      frrs_accumulator = numpy.zeros((step,frrs[0][0].shape[0]))
      fars_accumulator = numpy.zeros((step,frrs[0][1].shape[0]))
      for j in range(offset,offset+step):
        frrs_accumulator[j-i*step,:] = frrs[j][0]
        fars_accumulator[j-i*step,:] = frrs[j][1]

      frr_average = numpy.mean(frrs_accumulator, axis=0)
      far_average = numpy.mean(fars_accumulator, axis=0); far_std = numpy.std(fars_accumulator, axis=0)    

      if(linestyle is not None):
        pyplot.semilogx(frr_average*100, 100. - 100.0*far_average, color=colors[i], lw=2, ms=10, mew=1.5, label=labels[i], ls=linestyle[i].replace("\\",""))
      else:
        pyplot.semilogx(frr_average*100, 100. - 100.0*far_average, color=colors[i], lw=2, ms=10, mew=1.5, label=labels[i])
      
      pyplot.errorbar(frr_average*100, 100. - 100.0*far_average, far_std*100, lw=0.5, ms=10)    
      
      offset += step
      
    # plot FAR and CAR for each algorithm
    #for i in range(len(frrs)):
      #pyplot.semilogx([100.0*f for f in frrs[i][0]], [100. - 100.0*f for f in frrs[i][1]], color=colors[i+1], lw=0.5, ls='--', ms=10, mew=1.5, label=str(i))

    # finalize plot
    pyplot.plot([0.1,0.1],[0,100], "--", color=(0.3,0.3,0.3))
    pyplot.axis([frrs[0][0][0]*100,100,0,100])
    pyplot.xticks((0.01, 0.1, 1, 10, 100), ('0.01', '0.1', '1', '10', '100'))
    pyplot.xlabel('FAR (\%)')
    pyplot.ylabel('CAR (\%)')
    pyplot.grid(True, color=(0.6,0.6,0.6))
    pyplot.legend(loc=position, prop = {'size':fontsize})
    pyplot.title(title)

    return figure


def compute_error_eer(scores_dev, scores_eval, labels):

    n_labels = len(labels)
    step   = int(len(scores_dev)/n_labels)

    eer = []
    hter = []
    
    means_dev = []
    means_eval = []    
    std_dev = []
    std_eval = []

    for i in range(len(labels)):
            
        for j in range(step):
            index = (step)*i + j
        
            # Dev
            t = bob.measure.eer_threshold(scores_dev[index][0], scores_dev[index][1])
            far, frr = bob.measure.farfrr(scores_dev[index][0], scores_dev[index][1], t)
            eer.append(far)

            # Eval
            far, frr = bob.measure.farfrr(scores_eval[index][0], scores_eval[index][1], t)
            hter.append((far+frr)/2)

        eer_mean = numpy.mean(eer) * 100
        eer_std = numpy.std(eer) * 100
        
        hter_mean = numpy.mean(hter) * 100
        hter_std = numpy.std(hter) * 100
        
        #print ("Experiment {0}, Mean EER dev: {1} ({2}), Mean HTER eval: {3}({4}) ".format(labels[i] , eer_mean, eer_std, hter_mean, hter_std))
        means_dev.append(eer_mean)
        means_eval.append(hter_mean)        
        std_dev.append(eer_std)
        std_eval.append(hter_std)

        eer = []
        hter = []
        
    return means_dev, means_eval, std_dev, std_eval


def compute_error_far(scores_dev, scores_eval, labels, far_value=0.01):

    n_labels = len(labels)
    step   = int(len(scores_dev)/n_labels)

    frr_dev = []
    frr_eval = []
    
    means_dev = []
    means_eval = []    
    std_dev = []
    std_eval = []
    
    for i in range(len(labels)):
        for j in range(step):
            index = (step)*i + j
        
            # Dev
            t = bob.measure.far_threshold(scores_dev[index][0], scores_dev[index][1], far_value=far_value)
            far, frr = bob.measure.farfrr(scores_dev[index][0], scores_dev[index][1], t)
            frr_dev.append(frr)

            # Eval
            far, frr = bob.measure.farfrr(scores_eval[index][0], scores_eval[index][1], t)
            frr_eval.append(frr)

        frr_dev_mean = numpy.mean(frr_dev) * 100
        frr_dev_std = numpy.std(frr_dev) * 100
        
        frr_eval_mean = numpy.mean(frr_eval) * 100
        frr_eval_std = numpy.std(frr_eval) * 100
        
        means_dev.append(frr_dev_mean)
        means_eval.append(frr_eval_mean)
        std_dev.append(frr_dev_std)
        std_eval.append(frr_eval_std)

        frr_dev = []
        frr_eval = []
    return means_dev, means_eval, std_dev, std_eval


def main():
    """Reads score files, computes error measures and plots curves."""

    # set up command line parser
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d', '--dev-files', required=True, nargs='+', help = "A list of score files of the development set.")

    parser.add_argument('-e', '--eval-files', required=True, nargs='+', help = "A list of score files of the test set.")

    parser.add_argument('-n', '--names', required=True, nargs='+', help = "Names of the plots")
    
    parser.add_argument('-s', '--system', required=True, help = "Name of the biometric system", choices=('ISV', 'GFK-gabor', 'GFK', 'NON'))

    parser.add_argument('-r', '--report-name', required=True, help = "Name of the report", default="report.pdf")
    

    # parse arguments
    args = parser.parse_args()

    # Loading files
    scores_dev = [ bob.measure.load.split_four_column(f) for f in args.dev_files ]
    scores_eval = [ bob.measure.load.split_four_column(f) for f in args.eval_files ]
    names = args.names
    system = args.system
    report_name = args.report_name
    
    [means_dev_eer, means_eval_eer, std_dev_eer, std_eval_eer] = compute_error_eer(scores_dev, scores_eval, names)
    [means_dev_far100, means_eval_far100, std_dev_far100, std_eval_far100] = compute_error_far(scores_dev, scores_eval, names, far_value=0.01)
    [means_dev_far1000, means_eval_far1000, std_dev_far1000, std_eval_far1000] = compute_error_far(scores_dev, scores_eval, names, far_value=0.001)



    if system=="ISV":
        grid = "+------------+-----------+------+------------+------------+------------+------------+------------+------------+\n" \
               "| Image size | Gaussians |  U   | EER/HTER (%)            | FRR with FAR=1%         | FRR with FAR=0.1%       |\n" \
               "|            |           |      +------------+------------+------------+------------+------------+------------+\n" \
               "|            |           |      | dev        | eval       | dev        | eval       | dev        | eval       |\n" \
               "+============+===========+======+============+============+============+============+============+============+\n"
    elif system=="GFK":
        
        grid = "+------------+-----------+------+------------+------------+------------+------------+------------+------------+\n" \
               "| Image size | Subspaces | Feat.| EER/HTER (%)            | FRR with FAR=1%         | FRR with FAR=0.1%       |\n" \
               "|            |           |      +------------+------------+------------+------------+------------+------------+\n" \
               "|            |           |      | dev        | eval       | dev        | eval       | dev        | eval       |\n" \
               "+============+===========+======+============+============+============+============+============+============+\n"
               
    elif system=="GFK-gabor":

        grid = "+------------+-----------+------+------------+------------+------------+------------+------------+------------+\n" \
               "| Image size | radius    |angle | EER/HTER (%)            | FRR with FAR=1%         | FRR with FAR=0.1%       |\n" \
               "|            |           |      +------------+------------+------------+------------+------------+------------+\n" \
               "|            |           |      | dev        | eval       | dev        | eval       | dev        | eval       |\n" \
               "+============+===========+======+============+============+============+============+============+============+\n"
                   
    else:
        grid = "+------------+-----------+------+------------+------------+------------+------------+------------+------------+\n" \
               "| Image size | Algorithm |  -   | EER/HTER (%)            | FRR with FAR=1%         | FRR with FAR=0.1%       |\n" \
               "|            |           |------+------------+------------+------------+------------+------------+------------+\n" \
               "|            |           |      | dev        | eval       | dev        | eval       | dev        | eval       |\n" \
               "+============+===========+======+============+============+============+============+============+============+\n"



    #import ipdb; ipdb.set_trace()
    for i in range(len(names)):
           grid += "| XxX        | XX        |  X   |{:12s}|{:12s}|{:12s}|{:12s}|{:12s}|{:12s}|\n".format( 
             str(round(means_dev_eer[i],2)) + "(" + str(round(std_dev_eer[i] ,2)) + ")",
             str(round(means_eval_eer[i],2)) + "(" + str(round(std_eval_eer[i] ,2)) + ")",

             str(round(means_dev_far100[i],2)) + "(" + str(round(std_dev_far100[i],2)) + ")",
             str(round(means_eval_far100[i],2)) + "(" + str(round(std_eval_far100[i],2)) + ")",
             
             str(round(means_dev_far1000[i],2)) + "(" + str(round(std_dev_far1000[i],2)) + ")",
             str(round(means_eval_far1000[i],2)) + "(" + str(round(std_eval_far1000[i],2)) + ")"
           )
           if i < len(names)-1:
               grid +=  "+            +-----------+------+------------+------------+------------+------------+------------+------------+\n"

    grid += "+------------+-----------+------+------------+------------+------------+------------+------------+------------+\n"
    print(grid)
    
    
    print("Roc ..")
    
    #Creating a multipage PDF
    pdf = PdfPages(args.report_name)
    cmap = pyplot.cm.get_cmap(name='hsv')
    colors = [cmap(i) for i in numpy.linspace(0, 1.0, len(args.dev_files)+1)]
    scores_dev = [bob.measure.load.split_four_column(f) for f in args.dev_files]
    scores_eval = [bob.measure.load.split_four_column(f) for f in args.eval_files]
    pdf.savefig(_plot_roc(scores_dev, colors, args.names, "ROC Curve between 5 splits - dev"))
    pdf.savefig(_plot_roc(scores_eval, colors, args.names, "ROC Curve between 5 splits - eval"))
    pdf.close()
    

    
    

    

