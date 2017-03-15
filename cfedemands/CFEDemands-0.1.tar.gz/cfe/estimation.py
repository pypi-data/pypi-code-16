
# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Expenditure%20Shares][agg_shares_and_mean_shares]]

# Tangled on Tue Mar 14 21:25:42 2017
import pylab as pl 
import pandas as pd
import numpy as np

def expenditure_shares(df):

    aggshares=df.groupby(level='t').sum()
    aggshares=aggshares.div(aggshares.sum(axis=1),axis=0).T
    meanshares=df.div(df.sum(axis=1),level='j',axis=0).groupby(level='t').mean().T

    mratio=(np.log(meanshares)-np.log(aggshares))
    sharesdf=pd.Panel({'Mean shares':meanshares,'Agg. shares':aggshares})

    return sharesdf,mratio

def agg_shares_and_mean_shares(df,figname=None,ConfidenceIntervals=False,ax=None):
    """Figure of log mean shares - log agg shares.

    Input df is a pd.DataFrame of expenditures, indexed by (t,j).

    ConfidenceIntervalues is an optional argument.  
    If True, the returned figure will have 95% confidence intervals.  
    If a float in (0,1) that will be used for the size of the confidence 
    interval instead.
    """

    shares,mratio=expenditure_shares(df)
    meanshares=shares['Mean shares']

    tab=shares.to_frame().unstack()
    tab.sort_values(by=('Agg. shares',meanshares.columns[0]),ascending=False,inplace=True)

    if ax is None:
        fig, ax = pl.subplots()

    mratio.sort_values(by=mratio.columns[0],inplace=True)
    ax.plot(range(mratio.shape[0]),mratio.as_matrix(), 'o')
    ax.legend(mratio.columns,loc=2)
    ax.set_ylabel('Log Mean shares divided by Aggregate shares')

    v=ax.axis()
    i=0
    for i in range(len(mratio)):
        name=mratio.ix[i].name # label of expenditure item

        if mratio.iloc[i,0]>0.2:
            #pl.text(i,mratio.T.iloc[0][name],name,fontsize='xx-small',ha='right')

            # The key option here is `bbox`. 
            ax.annotate(name, xy=(i,mratio.T.iloc[0][name]), xytext=(-20,10), 
                        textcoords='offset points', ha='right', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.25', 
                        color='red'),fontsize='xx-small')

        if mratio.iloc[i,0]<-0.2:
            #pl.text(i,mratio.T.iloc[0][name],name,fontsize='xx-small')
            ax.annotate(name, xy=(i,mratio.T.iloc[0][name]), xytext=(20,-10), 
                        textcoords='offset points', ha='left', va='top',
                        bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.25', 
                        color='red'),fontsize='xx-small')

    if ConfidenceIntervals>0: # Bootstrap some confidence intervals
        if ConfidenceIntervals==1: ConfidenceIntervals=0.95
        current=0
        last=1
        M=np.array([],ndmin=3).reshape((mratio.shape[0],mratio.shape[1],0))
        i=0
        mydf=df.loc[:,mratio.index]
        while np.max(np.abs(current-last))>0.001 or i < 1000:
            last=current
            # Sample households in each  round with replacement
            bootdf=mydf.iloc[np.random.random_integers(0,df.shape[0]-1,df.shape[0]),:]
            bootdf.reset_index(inplace=True)
            bootdf['j']=range(bootdf.shape[0])
            bootdf.set_index(['t','j'],inplace=True)
            shares,mr=expenditure_shares(bootdf)
            M=np.dstack((M,mr.as_matrix()))
            M.sort(axis=2)
            a=(1-ConfidenceIntervals)/2.
            lb= mratio.as_matrix() - M[:,:,np.floor(M.shape[-1]*a)]
            ub=M[:,:,np.floor(M.shape[-1]*(ConfidenceIntervals+a))] - mratio.as_matrix()
            current=np.c_[lb,ub]
            i+=1
        T=mratio.shape[1]
        for t in range(T):
            ax.errorbar(np.arange(mratio.shape[0]),mratio.as_matrix()[:,t],yerr=current[:,[t,t-T]].T.tolist())
            tab[(df.index.levels[0][t],'Upper Int')]=current[:,t-T]
            tab[(df.index.levels[0][t],'Lower Int')]=current[:,t]

    ax.axhline()

    if figname:
        pl.savefig(figname)

    return tab,ax

# agg_shares_and_mean_shares ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Expenditure%20Shares][group_expenditures]]

# Tangled on Tue Mar 14 21:25:42 2017
def group_expenditures(df,groups):
    myX=pd.DataFrame(index=df.index)
    for k,v in groups.iteritems():
        myX[k]=df[['$x_{%d}$' % i for i in v]].sum(axis=1)
            
    return myX

# group_expenditures ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Rank%201%20Approximation][svd_rank1_approximation_with_missing_data]]

# Tangled on Tue Mar 14 21:25:42 2017
import pandas as pd
import numpy as np

def missing_inner_product(X,min_obs=None):
  n,m=X.shape

  if n<m: 
      axis=1
      N=m
  else: 
      axis=0
      N=n

  xbar=X.mean(axis=axis)

  if axis:
      C=(N-1)*X.T.cov(min_periods=min_obs)
  else:
      C=(N-1)*X.cov(min_periods=min_obs)

  return C + N*np.outer(xbar,xbar)

def drop_columns_wo_covariance(X,min_obs=None,VERBOSE=False):
    """Drop columns from pd.DataFrame that lead to missing elements of covariance matrix."""

    m,n=X.shape
    assert(m>n)

    HasMiss=True
    while HasMiss:
        foo = X.cov(min_periods=min_obs).count()
        if np.sum(foo<X.shape[1]):
            badcol=foo.argmin()
            del X[badcol] # Drop  good with  most missing covariances
            if VERBOSE: print("Dropping %s." % badcol)
        else:
            HasMiss=False

    return X

def svd_missing(A,max_rank=None,min_obs=None):

    P=missing_inner_product(A,min_obs=min_obs)

    sigmas,u=np.linalg.eig(P)

    order=np.argsort(-sigmas)
    sigmas=sigmas[order]

    # Truncate rank of representation using Kaiser criterion (positive eigenvalues)
    u=u[:,order]
    u=u[:,sigmas>0]
    s=np.sqrt(sigmas[sigmas>0])

    if max_rank is not None and len(s) > max_rank:
        u=u[:,:max_rank]
        s=s[:max_rank]

    r=len(s)
    us=np.matrix(u)*np.diag(s)

    v=np.zeros((len(s),A.shape[1]))
    for j in range(A.shape[1]):
        a=A.iloc[:,j].as_matrix().reshape((-1,1))
        x=np.nonzero(~np.isnan(a))[0] # non-missing elements of vector a
        if len(x)>=r:
            v[:,j]=(np.linalg.pinv(us[x,:])*a[x]).reshape(-1)
        else:
            v[:,j]=np.nan

    return np.matrix(u),s,np.matrix(v).T

def svd_rank1_approximation_with_missing_data(x,return_usv=False,max_rank=None,min_obs=None,VERBOSE=True):
    """
    Return rank 1 approximation to a pd.DataFrame x, where x may have
    elements which are missing.
    """
    x=x.copy()
    m,n=x.shape

    if n<m:  # If matrix 'thin', make it 'short'
        x=x.T
        TRANSPOSE=True
    else:
        TRANSPOSE=False

    x=x.dropna(how='all',axis=1) # Drop any column which is /all/ missing.
    x=x.dropna(how='all',axis=0) # Drop any row which is /all/ missing.

    x=drop_columns_wo_covariance(x.T,min_obs=min_obs).T
    u,s,v = svd_missing(x,max_rank=max_rank,min_obs=min_obs)
    if VERBOSE:
        print("Estimated singular values: ",)
        print(s)

    xhat=pd.DataFrame(v[:,0]*s[0]*u[:,0].T,columns=x.index,index=x.columns).T

    if TRANSPOSE: xhat=xhat.T

    if return_usv:
        return xhat,u,s,v
    else: return xhat

# svd_rank1_approximation_with_missing_data ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Estimation%20of%20reduced%20form][estimate_reduced_form]]

# Tangled on Tue Mar 14 21:25:45 2017
import pandas as pd
import warnings
import sys
from collections import OrderedDict
import numpy as np
from scipy import sparse

def df_norm(a,b=None,ignore_nan=True):
    a=a.copy()
    if not b is None:
      b=b.copy()
    else:
      b=pd.DataFrame(np.zeros(a.shape),columns=a.columns,index=a.index)

    if ignore_nan:
        missing=(a.isnull()+0.).replace([1],[np.NaN]) +  (b.isnull()+0.).replace([1],[np.NaN]) 
        a=a+missing
        b=b+missing
    return np.linalg.norm(a.fillna(0).as_matrix() - b.fillna(0).as_matrix())

def df_to_orgtbl(df,tdf=None,sedf=None,conf_ints=None,float_fmt='%5.3f'):
    """
    Returns a pd.DataFrame in format which forms an org-table in an emacs buffer.
    Note that headers for code block should include ":results table raw".

    Optional inputs include conf_ints, a pair (lowerdf,upperdf).  If supplied, 
    confidence intervals will be printed in brackets below the point estimate.

    If conf_ints is /not/ supplied but sedf is, then standard errors will be 
    in parentheses below the point estimate.

    If tdf is False and sedf is supplied then stars will decorate significant point estimates.
    If tdf is a df of t-statistics stars will decorate significant point estimates.
    """
    if len(df.shape)==1: # We have a series?
       df=pd.DataFrame(df)

    if (tdf is None) and (sedf is None) and (conf_ints is None):
        return '|'+df.to_csv(sep='|',float_format=float_fmt,line_terminator='|\n|')
    elif not (tdf is None) and (sedf is None) and (conf_ints is None):
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'\t|\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns:
                try:
                    stars=(np.abs(tdf.loc[i,j])>1.65) + 0.
                    stars+=(np.abs(tdf.loc[i,j])>1.96) + 0.
                    stars+=(np.abs(tdf.loc[i,j])>2.577) + 0.
                    if stars>0:
                        stars='^{'+'*'*stars + '}'
                    else: stars=''
                except KeyError: stars=''
                entry='| $'+float_fmt+stars+'$  '
                s+=entry % df.loc[i,j]
            s+='|\n'

        return s
    elif not (sedf is None) and (conf_ints is None): # Print standard errors on alternate rows
        if tdf is not False:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns: # Point estimates
                if tdf is not False:
                    try:
                        stars=(np.abs(tdf.loc[i,j])>1.65) + 0.
                        stars+=(np.abs(tdf.loc[i,j])>1.96) + 0.
                        stars+=(np.abs(tdf.loc[i,j])>2.577) + 0.
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| $'+float_fmt+stars+'$  '
                s+=entry % df.loc[i,j]
            s+='|\n|'
            for j in df.columns: # Now standard errors
                s+='  '
                try:
                    se='$(' + float_fmt % sedf.loc[i,j] + ')$' 
                except KeyError: se=''
                entry='| '+se+'  '
                s+=entry 
            s+='|\n'
        return s
    elif not (conf_ints is None): # Print confidence intervals on alternate rows
        if tdf is not False and sedf is not None:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns: # Point estimates
                if tdf is not False and tdf is not None:
                    try:
                        stars=(np.abs(tdf.loc[i,j])>1.65) + 0.
                        stars+=(np.abs(tdf.loc[i,j])>1.96) + 0.
                        stars+=(np.abs(tdf.loc[i,j])>2.577) + 0.
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| $'+float_fmt+stars+'$  '
                s+=entry % df.loc[i,j]
            s+='|\n|'
            for j in df.columns: # Now confidence intervals
                s+='  '
                try:
                    ci='$[' + float_fmt +','+ float_fmt + ']$'
                    ci= ci % (conf_ints[0].loc[i,j],conf_ints[1].loc[i,j])
                except KeyError: ci=''
                entry='| '+ci+'  '
                s+=entry 
            s+='|\n'
        return s

def orgtbl_to_df(table, col_name_size=1, format_string=None, index=None):
  """
  Returns a pandas dataframe.
  Requires the use of the header `:colnames no` for preservation of original column names.
  `table` is an org table which is just a list of lists in python.
  `col_name_size` is the number of rows that make up the column names.
  `format_string` is a format string to make the desired column names.
  `index` is a column label or a list of column labels to be set as the index of the dataframe.
  """
  import pandas as pd

  if col_name_size==0:
    return pd.DataFrame(table)
 
  colnames = table[:col_name_size]

  if col_name_size==1:
    if format_string:
      new_colnames = [format_string % x for x in colnames[0]]
    else:
      new_colnames = colnames[0]
  else:
    new_colnames = []
    for colnum in range(len(colnames[0])):
      curr_tuple = tuple([x[colnum] for x in colnames])
      if format_string:
        new_colnames.append(format_string % curr_tuple)
      else:
        new_colnames.append(str(curr_tuple))

  df = pd.DataFrame(table[col_name_size:], columns=new_colnames)
 
  if index:
    df.set_index(index, inplace=True)

  return df

def balance_panel(df):
    """Drop households that aren't observed in all rounds."""
    pnl=df.to_panel()
    keep=pnl.loc[list(pnl.items)[0],:,:].dropna(how='any',axis=1).iloc[0,:]
    df=pnl.loc[:,:,keep.index].to_frame(filter_observations=False)
    df.index.names=pd.core.base.FrozenList(['Year','HH'])

    return df

def drop_missing(X):
    """
    Return tuple of pd.DataFrames in X with any 
    missing observations dropped.  Assumes common index.
    """

    foo=pd.concat(X,axis=1).dropna(how='any')
    assert len(set(foo.columns))==len(foo.columns) # Column names must be unique!

    Y=[]
    for x in X:
        Y.append(foo.loc[:,x.columns])

    return tuple(Y)

def use_indices(df,idxnames):
    return df.reset_index()[idxnames].set_index(df.index)

def broadcast_binary_op(x, op, y):
    """Perform x op y, allowing for broadcasting over a multiindex.

    Example usage: broadcast_binary_op(x,lambda x,y: x*y ,y)
    """
    x = pd.DataFrame(x.copy())
    y = pd.DataFrame(y.copy())
    if y.shape[1]==1:
        y=pd.DataFrame([y.iloc[:,0]]*x.shape[1],index=x.columns).T

    cols = list(x.columns)
    xindex = list(x.index.names)
    yindex = list(y.index.names)

    dif = list(set(xindex)-set(yindex))
    x.reset_index(dif, inplace=True)

    x=x.sortlevel()

    newdf = x.copy()

    for col in cols:
        newdf[col] = op(x[col],y[col])

    newdf = newdf.reset_index().set_index(xindex).sortlevel()
    return newdf

def arellano_robust_cov(X,u,clusterby=['t','mkt']):
    X,u = drop_missing([X,u])
    clusters = set(zip(*tuple(use_indices(u,clusterby)[i] for i in clusterby)))
    if  len(clusters)>1:
        # Take out time averages
        u=broadcast_binary_op(u,lambda x,y:x-y, u.groupby(level=clusterby).mean()).squeeze()
        X=broadcast_binary_op(X,lambda x,y:x-y, X.groupby(level=clusterby).mean()) 
        Xu=X.mul(u,axis=0)
        if len(X.shape)==1:
            XXinv=np.array([1./(X.T.dot(X))])
        else:
            XXinv=np.linalg.inv(X.T.dot(X))
        Vhat = XXinv.dot(Xu.T.dot(Xu)).dot(XXinv)
    else:
        u=u-u.mean()
        X=X-X.mean()

        Xu=X.mul(u,axis=0)
        if len(X.shape)==1:
            XXinv=np.array([1./(X.T.dot(X))])
        else:
            XXinv=np.linalg.inv(X.T.dot(X))
        Vhat = XXinv.dot(Xu.T.dot(Xu)).dot(XXinv)

    try:
        return pd.DataFrame(Vhat,index=X.columns,columns=X.columns)
    except AttributeError:
        return Vhat


def ols(x,y,return_se=True,return_v=False,return_e=False):

    x=pd.DataFrame(x) # Deal with possibility that x & y are series.
    y=pd.DataFrame(y)
    N,n=y.shape
    k=x.shape[1]

    # Drop any observations that have missing data in *either* x or y.
    x,y = drop_missing([x,y]) 

    b=np.linalg.lstsq(x,y)[0]

    b=pd.DataFrame(b,index=x.columns,columns=y.columns)

    out=[b.T]
    if return_se or return_v or return_e:

        u=y-x.dot(b)

        # Use SUR structure if multiple equations; otherwise OLS.
        # Only using diagonal of this, for reasons related to memory.  
        S=sparse.dia_matrix((sparse.kron(u.T.dot(u),sparse.eye(N)).diagonal(),[0]),shape=(N*n,)*2) 

        if return_se or return_v:

            # This will be a very large matrix!  Use sparse types
            V=sparse.kron(sparse.eye(n),(x.T.dot(x).dot(x.T)).as_matrix().view(type=np.matrix).I).T
            V=V.dot(S).dot(V.T)

        if return_se:
            se=np.sqrt(V.diagonal()).reshape((x.shape[1],y.shape[1]))
            se=pd.DataFrame(se,index=x.columns,columns=y.columns)

            out.append(se)
        if return_v:
            # Extract blocks along diagonal; return an Nxkxn array
            V={y.columns[i]:pd.DataFrame(V[i*k:(i+1)*k,i*k:(i+1)*k],index=x.columns,columns=x.columns) for i in range(n)} 
            out.append(V)
        if return_e:
            out.append(u)
    return tuple(out)

def estimate_reduced_form(y,z,return_v=False,return_se=False,VERBOSE=False):
    """Estimate reduced-form Frisch expenditure/demand system.

    Inputs:
       - y : pd.DataFrame of log expenditures or log quantities, indexed by (j,t,mkt), 
             where j indexes the household, t the period, and mkt the market.  
             Columns are different expenditure items.

       - z : pd.DataFrame of household characteristics; index should match that of y.

    Ethan Ligon                                            February 2017
    """
    assert(y.index.names==['j','t','mkt'])
    assert(z.index.names==['j','t','mkt'])

    periods = list(set(y.index.get_level_values('t')))
    mkts = list(set(y.index.get_level_values('mkt')))

    # Time-market dummies
    DateLocD = use_indices(y,['t','mkt'])
    DateLocD = pd.get_dummies(zip(DateLocD['t'],DateLocD['mkt']))
    DateLocD.index = y.index

    sed = pd.DataFrame(columns=y.columns)
    a = pd.Series(index=y.columns)
    b = OrderedDict() #pd.DataFrame(index=y.columns)
    d = OrderedDict() #pd.DataFrame(index=y.columns,columns=z.columns).T
    ce = pd.DataFrame(index=y.index,columns=y.columns)
    V = pd.Panel(items=y.columns,major_axis=z.columns,minor_axis=z.columns)

    for i,Item in enumerate(y.columns):
        if VERBOSE: print(Item)

        lhs,rhs=drop_missing([y.iloc[:,[i]],pd.concat([z,DateLocD],axis=1)])

        # Calculate deviations
        lhsbar=lhs.mean(axis=0)
        assert ~np.any(np.isnan(lhsbar)), "Missing data in lhs?"
        lhs=lhs-lhsbar
        lhs=lhs-lhs.mean(axis=0)

        rhsbar=rhs.mean(axis=0)
        assert ~np.any(np.isnan(rhsbar)), "Missing data in rhs?"
        rhs=rhs-rhsbar
        rhs=rhs-rhs.mean(axis=0)

        # Need to make sure time-market effects sum to zero; add
        # constraints to estimate restricted least squares
        ynil=pd.DataFrame([0],index=[(-1,0,0)],columns=lhs.columns)
        znil=pd.DataFrame([[0]*z.shape[1]],index=[(-1,0,0)],columns=z.columns)
        timednil=pd.DataFrame([[1]*DateLocD.shape[1]],index=[(-1,0,0)],columns=DateLocD.columns)

        X=rhs.append(znil.join(timednil))

        # Estimate d & b
        myb,mye=ols(X,lhs.append(ynil),return_se=False,return_v=False,return_e=True) # Need version of pandas >0.14.0 (?) for this use of join
        ce[Item]=mye.iloc[:-1,:] # Drop constraint that sums time-effects to zero

        if return_v or return_se:
            V[Item]=arellano_robust_cov(z,mye)
            sed[Item]=pd.Series(np.sqrt(np.diag(V[Item])), index=z.columns) # reduced form se on characteristics

        #d[Item]=myb.iloc[:,:z.shape[1]].as_matrix()[0] # reduced form coefficients on characteristics
        d[Item]=myb[z.columns] # reduced form coefficients on characteristics

        b[Item] = myb[DateLocD.columns].squeeze()  # Terms involving prices
        a[Item] = y[Item].mean() - d[Item].dot(z.mean(axis=0)) - b[Item].dot(DateLocD.mean().values)

    b = pd.DataFrame(b)
    b.index=pd.MultiIndex.from_tuples(b.index,names=['t','mkt'])
    b = b.T

    d = pd.concat(d.values())

    out = [b.add(a,axis=0),ce,d]
    if return_se:
        out += [sed]
    if return_v:
        out += [V]
    return out

# estimate_reduced_form ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Extraction%20of%20Frisch%20Elasticities%20and%20Neediness][get_loglambdas]]

# Tangled on Tue Mar 14 21:25:45 2017
import pandas as pd

def get_loglambdas(e,TEST=False,time_index='t',max_rank=1,min_obs=None):
    """
    Use singular-value decomposition to compute loglambdas and price elasticities,
    up to an unknown factor of proportionality phi.

    Input e is the residual from a regression of log expenditures purged
    of the effects of prices and household characteristics.   The residuals
    should be arranged as a matrix, with columns corresponding to goods. 
    """ 
    assert(e.shape[0]>e.shape[1]) # Fewer goods than observations

    chat = svd_rank1_approximation_with_missing_data(e,VERBOSE=False,max_rank=max_rank,min_obs=min_obs)

    R2 = chat.var()/e.var()

    # Possible that initial elasticity b_i is negative, if inferior goods permitted.
    # But they must be positive on average.
    if chat.iloc[0,:].mean()>0:
        b=chat.iloc[0,:]
    else:
        b=-chat.iloc[0,:]

    loglambdas=(-chat.iloc[:,0]/b.iloc[0])

    # Find phi that normalizes first round loglambdas
    phi=loglambdas.groupby(level=time_index).std().iloc[0]
    loglambdas=loglambdas/phi

    loglambdas=pd.Series(loglambdas,name='loglambda')
    bphi=pd.Series(b*phi,index=e.columns,name=r'\phi\beta')

    if TEST:
        foo=pd.DataFrame(-np.outer(bphi,loglambdas).T,index=loglambdas.index,columns=bphi.index)
        assert df_norm(foo-chat)<1e-4
        #print "blogL norm: %f" % np.linalg.norm(foo-chat)

    return bphi,loglambdas

def iqr(x):
    """The interquartile range of a pd.Series of observations x."""
    import numpy as np
    return x.quantile([0.25,0.75]).diff().iloc[1]

def bootstrap_elasticity_stderrs(e,tol=1e-3,minits=30,return_samples=False,VERBOSE=False,outfn=None,TRIM=True):
    """Bootstrap estimates of standard errors for \phi\beta.

    Takes pd.DataFrame of residuals as input.

    If optional parameter TRIM is True, then calculations are
    performed using the interquartile range (IQR) instead of the
    standard deviation, with the standard deviation computed as
    IQR*0.7416 (which is a good approximation provided the
    distribution is normal).

    Ethan Ligon                              January 2017
    """
    bhat,Lhat=get_loglambdas(e)

    if outfn: outf=open(outfn,'a')

    delta=1.
    old=np.array(1)
    new=np.array(0)
    i=1
    L=[]
    while delta>tol or i < minits:
        delta=np.nanmax(np.abs(old.reshape(-1)-new.reshape(-1)))
        if VERBOSE and (i % 2)==0 and i>2: 
            print "Iteration %d, delta=%5.4f.  Measure of non-normality %6.5f." % (i, delta,np.nanmax(np.abs(std0.reshape(-1)-std1.reshape(-1))))
        old=new
        S=e.iloc[np.random.random_integers(0,e.shape[0]-1,size=e.shape[0]),:]
        S=S-S.mean() 

        bs,ls=get_loglambdas(S)
        assert(~np.any(np.isnan(bs)))
        try:
            B=B.append(bs,ignore_index=True)
        except NameError:
            B=pd.DataFrame(bs).T # Create B

        L.append(ls)

        std0=B.std()
        std1=B.apply(iqr)*0.7416 # Estimate of standard deviation, with trimming
        if TRIM:
            new=std1
        else:
            new=std0

        if outfn: outf.write(','.join(['%6.5f' % b for b in bs])+'\n')
        i+=1

    if outfn: outf.close()
    if return_samples:
        return new,B
    else:
        return new

# get_loglambdas ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Estimation%20of%20Price%20Elasticities][direct_price_elasticities]]

# Tangled on Tue Mar 14 21:25:49 2017

def direct_price_elasticities(y,p,z,VERBOSE=True,return_se=False,return_v=False):
    """Estimate reduced-form Frisch expenditure/demand system.

       Inputs:
         - y : pd.DataFrame of log expenditures or log quantities, indexed by (j,t,mkt), 
               where j indexes the household, t the period, and mkt the market.  
               Columns are different expenditure items.

         - p : pd.DataFrame of log prices, indexed by (t,mkt), with
               prices for different goods across columns.

         - z : pd.DataFrame of household characteristics; index should match that of y.

      Ethan Ligon                                            March 2017
    """
    assert(y.index.names==['j','t','mkt'])
    assert(z.index.names==['j','t','mkt'])

    periods = list(set(y.index.get_level_values('t')))
    mkts = list(set(y.index.get_level_values('mkt')))
    sed = pd.DataFrame(columns=y.columns)
    a = pd.Series(index=y.columns)
    b = OrderedDict() #pd.DataFrame(index=y.columns)
    d = OrderedDict() #pd.DataFrame(index=y.columns,columns=z.columns).T
    ce = pd.DataFrame(index=y.index,columns=y.columns)
    V = pd.Panel(items=y.columns,major_axis=z.columns,minor_axis=z.columns)

    for i,Item in enumerate(y.columns):
        if VERBOSE: print(Item)
        if np.any(np.isnan(p[Item])): continue # Don't estimate with missing prices

        rhs = z.reset_index('j').join(p[Item]).reset_index().set_index(['j','t','mkt'])
        rhs.rename(columns={Item:'log p'},inplace=True)

        lhs,rhs=drop_missing([y.iloc[:,[i]],rhs])

        rhs['Constant']=1

        myb,mye=ols(rhs,lhs,return_se=False,return_v=False,return_e=True) # Need version of pandas >0.14.0 (?) for this use of join
        ce[Item]=mye

        if return_v or return_se:
            V[Item]=arellano_robust_cov(rhs,mye)
            sed[Item]=pd.Series(np.sqrt(np.diag(V[Item])), index=z.columns) # reduced form se on characteristics

        d[Item]=myb[z.columns] # reduced form coefficients on characteristics

        a[Item] = myb['Constant']
        b[Item] = myb['log p'].values[0]

    b = pd.Series(b)

    d = pd.concat(d.values())

    out = [a,b,ce,d]
    if return_se:
        out += [sed]
    if return_v:
        out += [V]
    return out

# direct_price_elasticities ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Estimation%20of%20Price%20Elasticities][Estimation\ of\ Price\ Elasticities:1]]

# Tangled on Tue Mar 14 21:25:49 2017
def indirect_price_elasticities(a,p,zbar):
    """Estimate reduced-form Frisch expenditure/demand system.

       Inputs:
         - a : pd.DataFrame of good-time-market effects estimated by =estimate_reduced_form=,
               indexed by (t,mkt), where t indexes the period, and mkt the market.  
               Columns are different expenditure items.

         - p : pd.DataFrame of log prices, indexed by (t,mkt), with
               prices for different goods across columns.

         - zbar : pd.DataFrame of average household characteristics; index should match that of a.

      Ethan Ligon                                            March 2017
    """
    assert(a.index.names==['t','mkt'])
    assert(zbar.index.names==['t','mkt'])

    # Filter p
    X=zbar.copy()
    X['Constant'] = 1
    y = p.dropna(how='any',axis=1)

    # pe are filtered log prices
    bp,pe = ols(X,y,return_se=False,return_e=True)

    X = pe.copy()

    Xm=np.matrix((X-X.mean()).as_matrix())

    ym=np.matrix((a-a.mean()).as_matrix())
  
    B=OrderedDict()
    SE=OrderedDict()
    for i,Item in enumerate(y.columns):
        B[Item] = np.linalg.lstsq(Xm[:,i],ym[:,i])[0][0,0]
        e = ym[:,i] - Xm[:,i]*B[Item]
        SE[Item] = np.sqrt(np.var(e)/np.var(Xm[:,i]))

    B = pd.Series(B)
    SE = pd.Series(SE)
    return B,SE

# Estimation\ of\ Price\ Elasticities:1 ends here
