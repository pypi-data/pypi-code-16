import scipy.stats as stats
import pandas as pd
import tableprint as tp
import statsmodels.api as sm
from statsmodels.formula.api import ols


def chi2(dataFrame,x1,x2):
    """ Function to calculate chi2"""
    if x1 not in dataFrame:
        print("Can't find column: %s" % x1)
        return 0
    if x2 not in dataFrame:
        print("Can't find column: %s" %  x2)
        return 0
    crosstab = pd.crosstab(dataFrame[x1],dataFrame[x2])
    result = stats.chi2_contingency(crosstab)
    p = "%.4f" % result[0]
    chi = "%.4f" % result[1]
    columns = ["Pearson Chi2", "P-Value"]
    data = [[p,chi]]
    print(crosstab)
    tp.table(data,columns,width=12)
    return 0

def anova(dataFrame, column, groupBy):
    """ Function to calculate anova"""
    if column not in dataFrame:
        print("Can't find column: %s" % column)
        return 0
    if groupBy not in dataFrame:
        print("Can't find column: %s" % groupBy)
        return 0
    search_string = column + " ~ " + groupBy
    mod = ols(search_string, data=dataFrame).fit()
    aov_table = sm.stats.anova_lm(mod,typ=2)
    row0_sum = "%.4f" % aov_table.iloc[0]['sum_sq']
    row1_sum = "%.4f" % aov_table.iloc[1]['sum_sq']
    row0_df = round(aov_table.iloc[0]["df"])
    row1_df = round(aov_table.iloc[1]["df"])
    data = [[]]
    headers = ["Source","SS","df"]
    data.append(["Between Groups",row0_sum,row0_df])
    data.append(["Within Groups",row1_sum,row1_df])
    data.pop(0)
    print("ANOVA Test for %s" % column)
    tp.table(data,headers,width=15)

    columns = ["F statistic","P-value"]
    pvalue = "%.4f" % aov_table.iloc[0]["PR(>F)"]
    f = "%.4f" % aov_table.iloc[0]["F"]
    data = [[f,pvalue]]
    tp.table(data,columns)
    #print(aov_table)
    return 0



def ttest_by(dataFrame, column, sortBy):
    """ Function to calculate ttest"""
    if column not in dataFrame:
        print("Can't find column: %s" % column)
        return 0
    if sortBy not in dataFrame:
        print("Can't find column: %s" % sortBy)
        return 0
    by = dataFrame[sortBy].unique()
    if len(by) > 2:
        print("Wrong test, use an ANOVA")
        return 0
    if len(by) < 2:
        print("Need at least two groups to come")
        return 0
    firstT = dataFrame[dataFrame[sortBy]==by[0]][column]        
    mean = "%.4f" % firstT.mean()
    std = "%.4f" % firstT.std()
    data = [[by[0],len(firstT), mean,std]]
    secondT = dataFrame[dataFrame[sortBy]==by[1]][column]  
    mean = "%.4f" % secondT.mean()
    std = "%.4f" % secondT.std()
    data.append([by[1],len(secondT), mean,std])
    
    
    combined = dataFrame[column]
    mean = "%.4f" % combined.mean()
    std = "%.4f" % combined.std()
    data.append(['','','',''])
    data.append(['Combined', len(combined), mean, std])
    
    
    result = stats.ttest_ind(firstT,secondT)
    columns = ['Group','Obs','Mean','Std. Dev']
    print('Two sample T-test')
    print('Means of %s' % column)
    tp.table(data,columns,width=15)
    print()
    columns = ["T statistic","P-value"]
    pvalue = "%.4f" % result.pvalue
    t = "%.4f" % result[0]
    data = [[t,pvalue]]
    tp.table(data,columns)
    return ''



