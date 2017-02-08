"""
Created on Fri Aug 31 2012 14:05

Copyright (c) 2012, Martin S. Lindner and Maximilian Kollock,
Robert Koch-Institut, Germany,
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the author may not be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL MARTIN S. LINDNER OR MAXIMILIAN KOLLOCK BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

usage = """
%prog [options] NAME

Help on python script fitGCP.py

Fits mixtures of probability distributions to genome coverage profiles using an
EM-like iterative algorithm.

The script uses a SAM file as input and parses the mapping information and 
creates a Genome Coverage Profile (GCP). The GCP is written to a file, such that
this step can be skipped the next time.
The user provides a mixture model that is fitted to the GCP. Furthermore, the 
user may specify initial parameters for each model. 

As output, the script generates a text file containing the final set of fit 
parameters and additional information about the fitting process. A log file
contains the the current set of parameters in each step of the iteration. If 
requested, a plot of the GCP and the fitted distributions can be created.

PARAMETER:

NAME: Name of SAM file to analyze.
"""


import pysam
import numpy as np
import scipy.stats as stats
import sys
import os
from collections import namedtuple
import time
import pickle
from optparse import OptionParser
from scipy.special import digamma, betainc
from scipy.optimize import newton


"""----------------------------------------------------------------------------
    Define the distributions
----------------------------------------------------------------------------"""

class Distribution:
	_p1 = None
	_p2 = None
	_name = "General Distribution"
	_dof = 0 # Number of degrees of freedom

	alpha = 1.
	def __str__(self):
		""" return the name of the distribution """
		return self._name
	
	def set_par(self,p1=None, p2=None):
		""" explicitly set a parameter """
		if p1 != None:
			self._p1 = p1
		if p2 != None:
			self._p2 = p2

	def pmf(self, x):
		""" return the value of the probability mass function at x """
		return x*0.

	def estimate_par(self, data=None, weights=None):
		""" estimate the distribution parameters from the data and the weights 
		(if provided) """
		pass

	def init_par(self, mean=None, var=None):
		""" estimate initial distribution parameters given the mean and 
		variance of the data"""
		pass

	def report_stats(self, width=20):
		""" return a string that reports information about the distribution """
		return str(self._name).ljust(width) + str(self.alpha).ljust(width) + \
	           str(self._p1).ljust(width) + str(self._p2).ljust(width)


class Zero(Distribution):
	_name = "Zero"
	_dof = 1

	def pmf(self,x):
		if isinstance(x,np.ndarray):
			return (x==0).astype(np.float)
		else:
			return float(x==0)


class NBinom(Distribution):
	_name = "NBinom"
	_dof = 3
	_use_MOM = False
	
	def pmf(self, x):
		return stats.nbinom.pmf(x,self._p1,self._p2)

	def estimate_par(self, data, weights=None):
		if weights == None:
			weights = data*0. + 1.
		norm = np.sum(weights)
		mean = np.sum(data*weights)/(norm + 10**(-25))
		var = np.sum((data - mean)**2 * weights) / (norm + 10**(-25))

		if self._use_MOM:
			if var < mean:
				print("Warning: var < mean")
				var = 1.01*mean
			self._p1 = mean**2 / (var - mean)
			self._p2 = mean / var
		else:
			def dp1_llnbinom(param,obs,obs_w):
				# param: parameter 1
				# obs:   observed values
				# obs_w: weight of each value
				N = np.sum(obs_w)
				data_mean = np.sum(obs*obs_w)/(N)
				return np.sum(digamma(obs+param)*obs_w) - N*digamma(param) + \
			           N*np.log(data_mean/(param+data_mean))
			try:
				self._p1 = newton(dp1_llnbinom,self._p1, args=(data,weights),
								  maxiter=10000)
				self._p2 = (self._p1)/(self._p1+mean)
			except:
				print("Warning: MLE for negative binomial failed. Using MOM.")
				if var < mean:
					print("Warning: var < mean")
					var = 1.01*mean
				self._p1 = mean**2 / (var - mean)
				self._p2 = mean / var
				


	def report_stats(self, width=20):
		""" return a string that reports information about the distribution """
		return str(self._name).ljust(width) + str(self.alpha).ljust(width) + \
	           str(self._p1).ljust(width) + str(self._p2).ljust(width) + \
			   str(stats.nbinom.mean(self._p1,self._p2)).ljust(width)


		
class Poisson(Distribution):
	_name = "Poisson"
	_dof = 2

	def pmf(self,x):
		return stats.poisson.pmf(x,self._p1)

	def estimate_par(self, data, weights=None):
		mean = np.sum(data*weights) / (np.sum(weights) )
		self._p1 = mean



class TailDistribution(Distribution):
	_name = "Tail"
	_dof = 1
	_norm = False  # normalization; recalculate only if necessary
	_parent = None
	_active = True # switch tail on/off

	def set_par(self,p1=None, p2=None):
		""" explicitly set a parameter """
		if p1 != None:
			self._p1 = p1
		if p2 != None:
			self._p2 = p2
		self._norm = False

	def estimate_par(self, data=None, weights=None):
		""" Do not estimate parameters, but obtain parameters from parent 
		distribution """
		self._p1 = self._parent._p1
		self._p2 = self._parent._p2
		self._norm = False



class NbTail(TailDistribution):
	_name = "Tail"
	_dof = 1
	def __init__(self, nbinom):
		""" NbTail distribution must be connected to a negative binomial"""
		if isinstance(nbinom, NBinom):
			self._parent = nbinom
		else:
			raise(Exception("NbTail must be connected to a NBinom object"))
	
	def pmf(self, x):
		if np.isscalar(x) and x == 0:
			return 0.
		
		if self._active == False:
			return 0*x
		if stats.nbinom.mean(self._p1, self._p2) < 1.:
			self._active = False # switch tail permanently off

		def betaincreg(x,p1,p2):
			return 1-betainc(p1,x+1,p2)

		# calculate normalization up to certain precision
		if not self._norm:
			ks = int(max(2,stats.nbinom.ppf(0.999999,self._p1,self._p2)))
			norm = np.sum(betaincreg(np.arange(1,ks),self._p1,self._p2))
		else:
			norm = self._norm
		# now return the value(s)
		ret = betaincreg(x,self._p1,self._p2) / norm
		if not np.isscalar(x):
			ret[np.where(x==0)] = 0.
		return ret



class PoissonTail(TailDistribution):
	_name = "Tail of Poisson"
	_dof = 1
	def __init__(self, poisson):
		""" PoissonTail distribution must be connected to a poisson 
		distribution """
		if isinstance(poisson, Poisson):
			self._parent = poisson
		else:
			raise(Exception("PoissonTail must be connected to a Poisson object"))
	
	def pmf(self, x):
		if self._p1 < 1.:
			self._active = False # switch tail permanently off
		if self._active == False:
			return 0*x

		if np.isscalar(x) and x == 0:
			return 0.

		xmax = int(max(np.max(x),5,stats.poisson.ppf(0.999999,self._p1)))+1
		xs = np.arange(0,xmax, dtype=np.float)
		#backward cumulative sum
		tx = np.cumsum((stats.poisson.pmf(xs, self._p1)/xs)[::-1])[::-1]
		tx[0] = 0
		tx /= np.sum(tx)
		return tx[x]


def build_mixture_model(dist_str):
	""" Build a mixture model from a string """
	num_dist = len(dist_str)
	mm = np.array([Zero()]*num_dist)
	it = 0	
	for dist in dist_str:
		if dist == "z":
			it += 1
		elif dist=="n":
			mm[it] = NBinom()
			mm[it]._use_MOM = True
			it += 1
		elif dist=="N":
			mm[it] = NBinom()
			mm[it]._use_MOM = False
			it += 1
		elif dist == "t":
			if it > 0 and isinstance(mm[it-1], NBinom):
				mm[it] = NbTail(mm[it-1])
				it += 1
			elif it > 0 and isinstance(mm[it-1], Poisson):
				mm[it] = PoissonTail(mm[it-1])
				it += 1
			else:
				raise Exception("Error: wrong input '%s'. A Tail distribution "
								"(t) must follow a Negative Binomial (n|N) or "
								"Poisson (p)."%dist_str)
		elif dist == "p":
			mm[it] = Poisson()
			it+=1
		else:
			raise Exception("Input Error: distribution %s not recognized!"%dist)

	# initialize all distributions with equal weights
	alpha = 1./len(mm)
	for dist in mm:
		dist.alpha = alpha
		
	return mm


def init_gamma(mixture_model, dataset):
	""" create initial responsibilities gamma. The probability that a coverage 
	belongs to a distribution is equal for all distributions."""
	N_mm = len(mixture_model)
	N_cov = len(dataset.cov)
	
	return np.array([[1./N_mm for d in mixture_model] for i in range(N_cov)])



"""----------------------------------------------------------------------------
    Define DataSet to store all relevant information (incl. GCP)
----------------------------------------------------------------------------"""

class DataSet:
	fname = ""                        # path to original SAM file
	cov = np.array([],dtype=np.int)   # observed coverage values
	count = np.array([],dtype=np.int) # number of observations for each cov
	rlen = 0                          # average read length of mapped reads
	rds = 0                           # total number of reads
	glen = 0                          # length of the genome
	
	def read_from_pickle(self,filename):
		""" read a genome coverage profile from a pickle file. """
		data = pickle.load(open(filename,'r'))

		self.cov = np.array(data[0],dtype=np.int)
		self.count = np.array(data[1],dtype=np.int)
		self.rlen = data[2]
		self.rds = data[3]
		self.glen = data[4]
		if len(data) == 6:
			self.fname = data[5] 


	def read_from_sam(self, filename):
		""" extract a genome coverage profile from a sam file. """
		sf = pysam.Samfile(filename,'r')
	
		cov = np.zeros((sum(sf.lengths),))
		start_pos = np.zeros((len(sf.lengths),))
		start_pos[1:] = np.cumsum(sf.lengths[:-1])

		read_length = 0
		num_reads = 0
		for read in sf:
			if not read.is_unmapped:
				r_start = start_pos[read.tid] + read.pos # start position 
				r_end = start_pos[read.tid] + read.pos + read.qlen # end 
				cov[r_start:r_end] += 1 
				num_reads += 1
				read_length += r_end-r_start
		self.fname = filename
		self.rds = num_reads
		self.rlen = read_length/float(num_reads)  # average length mapped reads
		self.glen = len(cov)
		self.cov = np.unique(cov)
		self.count = np.array( [np.sum(cov==ucov) for ucov in self.cov] )
	
	def write_to_pickle(self, filename):
		""" store dataset in a pickle file. """
		return pickle.dump([self.cov, self.count, self.rlen, self.rds,
							 self.glen, self.fname], open(filename,'w'))
	


"""----------------------------------------------------------------------------
    Iterative Method function definitions
----------------------------------------------------------------------------"""


def update_gamma(data_set, mixture_model, gamma):
	""" Update the probability gamma_i(x), that a position with coverage x 
	belongs to distribution i
	"""
	num_dist = len(mixture_model)
	for it in range(len(data_set.cov)):
		# calculate probability that coverages[it] belongs to a distribution
		print(data_set.cov[it])
		prob = [dist.alpha*dist.pmf(data_set.cov[it]) for dist in mixture_model]
		if sum(prob) <= 0:
			gamma[it,:] = 0.
		else:
			gamma[it,:] = np.array([prob[i]/sum(prob) for i in range(num_dist)])
	
	return 1


def update_alpha(data_set, mixture_model, gamma):		
	""" Update alpha_i, the proportion of data that belongs to 
	distribution i """

	for i in range(len(mixture_model)-1):
		w_probs = np.array([p*w for p,w in zip(gamma[:,i],data_set.count)])
		mixture_model[i].alpha = np.sum(w_probs) / np.sum(data_set.count)

	mixture_model[-1].alpha = 1 - sum([d.alpha for d in mixture_model[:-1]])

	return 1


def iterative_fitting(data_set, mixture_model, gamma, iterations):
	""" Generator fuction to run the iterative method. Operates directly on the
	data structures mixture_model and gamma. """
	
	for i in range(iterations):
		# Expectation-step: update gammas
		update_gamma(data_set, mixture_model, gamma)
		
		# temporarily store old parameters
		old_p1 = np.array([d._p1 or 0 for d in mixture_model])
		old_p2 = np.array([d._p2 or 0 for d in mixture_model])
		old_alpha = np.array([d.alpha for d in mixture_model])

		# Parameter estimation step
		for j,dist in enumerate(mixture_model):
			dist_weights = gamma[:,j]*data_set.count
			dist.estimate_par(data_set.cov, dist_weights)
		update_alpha(data_set, mixture_model, gamma)

		# calculate relative change of the parameters
		new_p1 = np.array([d._p1 or 0 for d in mixture_model])
		new_p2 = np.array([d._p2 or 0 for d in mixture_model])
		new_alpha = np.array([d.alpha for d in mixture_model])
		
		rel_p1 = np.max(np.abs(new_p1-old_p1) / (new_p1 + 1e-20))
		rel_p2 = np.max(np.abs(new_p2-old_p2) / (new_p2 + 1e-20))
		rel_alpha = np.max(np.abs(new_alpha-old_alpha) / (new_alpha + 1e-20))

		max_change = np.max([rel_p1, rel_p2, rel_alpha])

		# maximum CDF difference
		xs = np.arange(np.max(data_set.cov)+1)
		ref_pdf = np.zeros((np.max(data_set.cov)+1,))
		for dist in mixture_model:
			ref_pdf += dist.pmf(xs)*dist.alpha
		
		obs_pdf = np.zeros((np.max(data_set.cov)+1,))
		obs_pdf[data_set.cov.astype(np.int)] = data_set.count/float(np.sum(data_set.count))
		max_cdf_diff = np.max(np.abs(np.cumsum(ref_pdf)-np.cumsum(obs_pdf)))

		yield i, max_change, max_cdf_diff


"""----------------------------------------------------------------------------
    Auxiliary code
----------------------------------------------------------------------------"""

class Logger:
	""" simple logger class """
	log_file = None
	def __init__(self, filename=None):
		if filename:
			self.log_file = open(filename,'w')

	def log(self, s, c=True):
		""" write string s to log file and print to console (if c) """
		if c:
			print(s)
		if self.log_file:
			self.log_file.write(s+'\n')


def create_plot(ds, mm, filename):
	""" create a plot showing the data and the fitted distributions """
	plt.figure()
	xmax = np.max(ds.cov)+1
	plotXs = np.arange(xmax)
	plt.plot(ds.cov[np.where(ds.cov<xmax)],ds.count[np.where(ds.cov<xmax)]/
			 float(ds.glen),'k', lw=2, label="GCP")
	plotY_total = np.zeros((len(plotXs),))
	for dist in mm:
		if isinstance(dist,Poisson):
			format_string = "--"
			color = 'r'
		elif isinstance(dist,NBinom):
			format_string = "-."
			color = 'b'
		elif isinstance(dist,TailDistribution):
			format_string = ":"
			color = 'Purple'
		elif isinstance(dist,Zero):
			format_string = "-"
			color = 'YellowGreen'

		plotYs = dist.pmf(plotXs)*dist.alpha
		plotY_total += plotYs
		plt.plot(plotXs,plotYs, format_string, color=color, lw=2, label=dist._name)
	plt.plot(plotXs,plotY_total,'--',color='gray',lw=2, label="Mixture")
	plt.xlabel('coverage')
	plt.ylabel('')
	plt.xlim(xmin=0, xmax=xmax)
	plt.legend()
	plt.savefig(filename, dpi=300, bbox_inches='tight')



"""----------------------------------------------------------------------------
    Main function
----------------------------------------------------------------------------"""

if __name__ == "__main__":

	# Define command line interface using OptionParser
	parser = OptionParser(usage=usage)
	
	parser.add_option("-d", "--distributions", dest="dist",	
	help="Distributions to fit. z->zero; n: nbinom (MOM); N: nbinom (MLE); "
	"p:binom; t: tail. Default: %default", default="zn")
	
	parser.add_option("-i", "--iterations", dest="steps", type='int', 
	help="Maximum number of iterations. Default: %default", default=50)
	
	parser.add_option("-t", "--threshold", dest="thr", type='float', help="Set"
	" the convergence threshold for the iteration. Stop if the change between "
	"two iterations is less than THR. Default: %default", default=0.01)
	
	parser.add_option("-c", "--cutoff", dest="cutoff", type='float', 
	help="Specifies a coverage cutoff quantile such that only coverage values"
	" below this quantile are considered. Default: %default", default=0.95)
	
	parser.add_option("-p", "--plot", action="store_true", dest="plot", 
	help="Create a plot of the fitted mixture model. Default: %default",
	default=False)
	
	parser.add_option("-m", "--means", dest="mean", type='float', 
	action="append", help="Specifies the initial values for the mean of each "
	"Poisson or Negative Binomial distribution. Usage: -m 12.4 -m 16.1 will "
	"specify the means for the first two non-zero/tail distributions. The "
	"default is calculated from the data.", default=None)
	
	parser.add_option("-a", "--alpha", dest="alpha", action="append", 
	help="Specifies the initial values for the proportion alpha of each "
	"distribution. Usage: For three distributions -a 0.3 -a 0.3 specifies the "
	"proportions 0.3, 0.3 and 0.4. The default is "
	"equal proportions for all distributions.", default=None)
	
	parser.add_option("-l", "--log", action="store_true", dest="log", 
	help="Enable logging. Default: %default", default=False)

	parser.add_option("--view", action="store_true", dest="view", 
	help="Only view the GCP. Do not fit any distribution. Respects cutoff "
		    ". Default: %default", default=False)

	(options, args) = parser.parse_args()
	
	if len(args) != 1:
		parser.print_help()
		sys.exit(1)


	# process command line input

	# check input file name
	name = args[0] # filename is the first (and only) argument
	if not os.path.exists(name):
		raise Exception("Could not find file with name '%s'."%name)
	if name.endswith('.sam'):
		name = name[:-4]


	# enable logging
	if options.log and not options.view:
		logfile = name + '_%s_log.txt'%options.dist
	else:
		logfile = None
	lg = Logger(logfile)

	
	# load data
	DS = DataSet()
	if os.path.exists(name+'.pcl'):
		print('found pickle file')
		DS.read_from_pickle(name+'.pcl')
	else:
		DS.read_from_sam(name+'.sam')
		DS.write_to_pickle(name+'.pcl')


	# weight cutoff. Coverages above this value have no weight in parameter estimation
	try:
		cutoff = max(int(np.max(DS.cov[np.where(np.cumsum(DS.count)<= \
				 options.cutoff*DS.glen)])+1),10)
	except:
		cutoff = np.max(DS.cov)+1
	lg.log("Using coverage cutoff: %i"%cutoff)

	DS.count = DS.count[np.where(DS.cov < cutoff)]
	DS.cov = DS.cov[np.where(DS.cov < cutoff)]
	num_unique = len(DS.cov)
	DS.glen = np.sum(DS.count)
	mean_cov = np.sum(DS.cov*DS.count)/np.sum(DS.count).astype(np.float)


	# only view the GCP
	if options.view:
		try:
			import matplotlib.pyplot as plt
		except:
			raise Exception("Error: could not import matplotlib.")
		
		# create empty mixture model
		MM = np.array([])
		create_plot(DS,MM,name+'.png')
		print("Wrote GCP plot to file %s."%(name+'.png'))
		sys.exit(0)


	# Plotting: check if matplotlib is installed
	plot = options.plot		
	if plot:
		try:
			import matplotlib.pyplot as plt
		except:
			lg.log("Warning: could not import matplotlib. Plotting disabled.")
			plot = False

	# create the mixture model
	if options.dist.count('z') > 1:
		raise Exception("Error: only one Zero disribution is allowed!")

	if options.dist.count("t") > 1:
		lg.log("Warning: more than one tail distribution may yield inaccurate "
		"estimates!")

	MM = build_mixture_model(options.dist)
	num_dist = len(MM)
	the_zero = options.dist.find('z')
	
	if options.alpha != None:
		if len(options.alpha) >= num_dist:
			raise Exception("Error: the number of alpha values (%i) exceeds "
			"the number of distributions (%i)!"%(len(options.alpha,num_dist)))


	# set initial proportions for each distribution
	if options.alpha:
		alpha = options.alpha
		if len(options.alpha) < len(MM):
			rest_alpha = 1. - sum(options.alpha)
			rest_models = len(MM) - len(options.alpha)
			alpha.append([rest_alpha / rest_models] * rest_models)			
		
		for dist,a in zip(MM,alpha):
			dist.alpha = float(a)
		
	# initialize distribution parameters
	n_dist = options.dist.count('n') + options.dist.count('N') + \
		     options.dist.count('p')
	factors = np.linspace(-n_dist,n_dist,n_dist)
	data_mean = np.power(np.abs(factors),np.sign(factors))*np.mean(DS.cov[1:]*\
				DS.count[1:]/np.mean(DS.count))

	if options.mean:
		# use mean values provided by the user, where possible
		for i,m in enumerate(options.mean):
			data_mean[i] = m

	data_var = np.array([np.sum((DS.cov-m)**2*DS.count)/DS.glen \
						 for m in data_mean])

	it = 0
	for dist in MM:
		if isinstance(dist,Zero) or isinstance(dist,NbTail) \
		or isinstance(dist,PoissonTail):
			dist.estimate_par()
			continue
		if isinstance(dist,NBinom):
			m,v = data_mean[it],data_var[it]
			if m > v:
				v = 1.01*m
			dist.set_par(m**2 / (v - m) , m / v )
			it += 1
			continue
		if isinstance(dist,Poisson):
			dist.set_par(data_mean[it])
			it += 1


	# set initial values for the responsibilities gamma
	GAMMA = init_gamma(MM,DS)
	

	# write initial values to log file
	lg.log('Initial values',False)
	lg.log('distribution'.ljust(20)+'alpha'.ljust(20)+'parameter 1'.ljust(20)+
		   'parameter 2',False)
	for i in range(num_dist):
		lg.log(str(MM[i]).ljust(20)+str(MM[i].alpha).ljust(20)+
			   str(MM[i]._p1).ljust(20)+str(MM[i]._p2),False)
	lg.log('\n',False)



	# run the iteration, repeatedly update the variables MM and GAMMA
	t_start = time.time()
	for i,change,diff in iterative_fitting(DS, MM, GAMMA, options.steps):	
		print(i)
		t_step = time.time() - t_start
		lg.log(('step#: '+str(i+1)).ljust(20)+'time: '+str(round(t_step,1))+'s'
			   +'\n',False)
		lg.log('distribution'.ljust(20)+'alpha'.ljust(20)+
			   'parameter 1'.ljust(20)+'parameter 2',False)
		for d in MM:
			lg.log(d.report_stats(20),False)
		lg.log('Max. CDF diff:'.ljust(20)+'%f'%diff,False)
		lg.log('\n',False)

		if change < options.thr:
			break
		t_start = time.time()
	
	

	# Estimate genome fragmentation and correct the zero-coverage estimate,
	# if a tail distribution was used
	zero_frac = MM[the_zero].alpha
	tail = False
	for dist in MM:
		if isinstance(dist,PoissonTail) and dist.alpha > 0:
			p_tail   = dist.alpha
			p_parent = dist._parent.alpha
			part_cov = dist._parent._p1
		elif isinstance(dist,NbTail) and dist.alpha > 0:
			p_tail   = dist.alpha
			p_parent = dist._parent.alpha
			part_cov = stats.nbinom.mean(dist._parent._p1,dist._parent._p2)
		else:
			continue
		
		tail=True
		gfrag = DS.glen/(1.+p_parent/p_tail)/2./DS.rlen*(p_parent+p_tail)
			
		start_prob = 1. - stats.poisson.cdf(0,part_cov/float(DS.rlen))
		zero_corr = (2*gfrag-1)*(min(stats.nbinom.mean(1,start_prob),DS.rlen) 
								 - start_prob/3.*4./9.)
		zero_est = DS.glen*MM[the_zero].alpha
		zero_frac = (zero_est-zero_corr)/float(DS.glen)


	# write results to file
	res = open(name+'_'+str(options.dist)+'_results.txt','w')
	res.write('Genome length:       %i\n'%DS.glen)
	res.write('Number of reads:     %i\n'%DS.rds)
	res.write('Average read length: %i\n'%DS.rlen)
	#res.write('Average Coverage:    %f\n'%mean_cov)
	res.write('Max. CDF difference: %f\n\n'%diff)
	res.write('Distribution'.ljust(20)+'alpha'.ljust(20)+
			  'parameter 1'.ljust(20)+'parameter 2'.ljust(20)+'[Mean]\n')
	for d in MM:
		res.write(d.report_stats(20)+'\n')
	
	if tail:
		res.write('\nNum. Fragments:'.ljust(20)+'%.01f'%gfrag+'\n')
		res.write('Observed Zeros:'.ljust(20)+
				  '%.04f'%(zero_est/float(DS.glen))+'\n')
		res.write('Corrected Zeros:'.ljust(20)+
				  '%.04f'%((zero_est-zero_corr)/float(DS.glen))+'\n')
	res.close()

	lg.log('\nFinal Results:\n')
	#lg.log('Average Coverage:    %f'%mean_cov)
	lg.log('Max. CDF difference: %f\n'%diff)
	lg.log('Distribution'.ljust(20)+'alpha'.ljust(20)+'parameter 1'.ljust(20)+
		   'parameter 2'.ljust(20)+'[Mean]')
	for d in MM:
		lg.log(d.report_stats(20))
		
	if tail:
		lg.log('Num. Fragments:'.ljust(20)+'%.01f'%gfrag)
		lg.log('Observed Zeros:'.ljust(20)+'%.04f'%(zero_est/float(DS.glen)))
		lg.log('Corrected Zeros:'.ljust(20)+'%.04f'%((zero_est-zero_corr)/
													 float(DS.glen)))


	# plot the figure, if requested
	if plot:
		create_plot(DS,MM,name+'_'+options.dist+'.png')

	print("\nFinished.")
