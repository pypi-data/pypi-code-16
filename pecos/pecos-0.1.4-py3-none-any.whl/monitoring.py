"""
The monitoring module contains the PerformanceMonitoring class used to run
quality control tests and store results.
"""
import pandas as pd
import numpy as np
import re
import logging

none_list = ['','none','None','NONE', None, [], {}]

logger = logging.getLogger(__name__)
    
class PerformanceMonitoring(object):

    def __init__(self):
        """
        PerformanceMonitoring class
        """
        self.df = pd.DataFrame()
        self.trans = {}
        self.tfilter = pd.Series()
        self.test_results = pd.DataFrame(columns=['System Name', 'Variable Name', 
                                                'Start Date', 'End Date', 
                                                'Timesteps', 'Error Flag']) 
    
    def add_dataframe(self, df, system_name, add_identity_translation_dictionary = False):
        """
        Add DataFrame to the PerformanceMonitoring object.
        
        Parameters
        -----------
        df : pd.Dataframe
            Dataframe to add to the PerformanceMonitoring object
        
        system_name : string
            System name
            
        add_identity_translation_dictionary : boolean (optional)
            Add a 1:1 translation dictionary to the PerformanceMonitoring object
            using all column names in df, default = False
        """
        temp = df.copy()
        
        # Combine variable name with system name (System: Variable)
        temp.columns = [system_name + ':' + s  for s in temp.columns]
        
        if self.df is not None:
            self.df = self.df.combine_first(temp)
        else:
            self.df = temp.copy()     

        # define identity translation
        if add_identity_translation_dictionary:
            trans = {}
            for col in df.columns:
                trans[col] = [col]
            
            self.add_translation_dictionary(trans, system_name)
            
    def add_translation_dictionary(self, trans, system_name):
        """
        Add translation dictionary to the PerformanceMonitoring object.
        
        Parameters
        -----------
        trans : dictionary
            Translation dictionary
        
        system_name : string
            System name
        """    
        # Combine variable name with system name (System: Variable)
        for key, values in trans.items():
            self.trans[key] = []
            for value in values:
                self.trans[key].append(system_name + ':' + value)
        
    def add_time_filter(self, time_filter):
        """
        Add a time filter to the PerformanceMonitoring object.
        
        Parameters
        ----------
        time_filter : pd.DataFrame with a single column or pd.Series
            Time filter containing boolean values for each time index
        """
        if isinstance(time_filter, pd.DataFrame):
            self.tfilter = pd.Series(data = time_filter.values[:,0], index = self.df.index)
        else:
            self.tfilter = time_filter

    def add_signal(self, col_name, data):
        """
        Add signal to the PerformanceMonitoring DataFrame.
        
        Parameters
        -----------
        col_name : string
            Column name to add to translation dictionary
        
        data : pd.DataFarame or pd.Series
            Data to add to df
        """
        if type(data) is pd.core.series.Series:
            data = data.to_frame(col_name)
        if type(data) is not pd.core.frame.DataFrame:
            logger.warning("Add signal failed")
            return
            
        if col_name in self.trans.keys():
            logger.info(col_name + ' already exists in trans')
            return
        for col in data.columns.values.tolist():
            if col in self.df.columns.values.tolist():
                logger.info(col + ' already exists in df')
                return
        try:
            self.trans[col_name] = data.columns.values.tolist()
            #self.df[df.columns] = df
            for col in data.columns:
                self.df[col] = data[col]
        except:
            logger.warning("Add signal failed: " + col_name)
            return
            
    def append_test_results(self, mask, error_msg, min_failures=1, variable_name=True): #, sub_df=None):
        """
        Append QC results to the PerformanceMonitoring object.
        
        Parameters
        ----------
        mask : pd.Dataframe
            Result from quality control test, boolean values
        
        error_msg : string
            Error message to store with the QC results
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        
        variable_name : boolean  (optional)
            Add variable name to QC results, set to False for timestamp tests, default = True
        """
        if len(mask.columns) == 1 and mask.columns[0] == 0:
            sub_df = self.df
        else:
            sub_df = self.df[mask.columns]
        
        # Find blocks
        order = 'col'
        if order == 'col':
            mask = mask.T
            
        np_mask = mask.values
        
        start_nans_mask = np.hstack((np.resize(np_mask[:,0],(mask.shape[0],1)),
                                     np.logical_and(np.logical_not(np_mask[:,:-1]), np_mask[:,1:])
                                     ))
        stop_nans_mask = np.hstack((np.logical_and(np_mask[:,:-1], np.logical_not(np_mask[:,1:])),
                                    np.resize(np_mask[:,-1], (mask.shape[0],1))
                                    ))
    
        start_row_idx,start_col_idx = np.where(start_nans_mask)
        stop_row_idx,stop_col_idx = np.where(stop_nans_mask)
        
        if order == 'col':
            temp = start_row_idx; start_row_idx = start_col_idx; start_col_idx = temp
            temp = stop_row_idx; stop_row_idx = stop_col_idx; stop_col_idx = temp
            #mask = mask.T
        
        block = {'Start Row': list(start_row_idx), 
                 'Start Col': list(start_col_idx), 
                 'Stop Row': list(stop_row_idx), 
                 'Stop Col': list(stop_col_idx)}
                 
        #if sub_df is None:
        #    sub_df = self.df
        
        for i in range(len(block['Start Col'])):
            length = block['Stop Row'][i] - block['Start Row'][i] + 1
            if length >= min_failures:
                if variable_name:
                    var_name = sub_df.iloc[:,block['Start Col'][i]].name #sub_df.icol(block['Start Col'][i]).name
                    system_name = ''
                    temp = var_name.split(':')
                    if len(temp) == 2:
                        var_name = temp[1]
                        system_name = temp[0]
                else:
                    var_name = ''
                    system_name = ''
                frame = pd.DataFrame([system_name, var_name, 
                                      sub_df.index[block['Start Row'][i]],
                                      sub_df.index[block['Stop Row'][i]], 
                                      length, error_msg], 
                                      index=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])         
                frame_t = frame.transpose()
                self.test_results = self.test_results.append(frame_t, ignore_index=True)
        
    def check_timestamp(self, frequency, expected_start_time=None, expected_end_time=None, min_failures=1):
        """
        Check time series for non-monotonic and duplicate timestamps.
        
        Parameters
        ----------
        frequency : int
            Expected time series frequency, in seconds
        
        expected_start_time : Timestamp (optional)
            Expected start time. If not specified, the minimum timestamp is used
        
        expected_end_time : Timestamp (optional)
            Expected end time. If not specified, the maximum timestamp is used
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check timestamp")
        
        if self.df.empty:
            logger.info("Empty database")
            return
        if expected_start_time is None:
            expected_start_time = min(self.df.index)
        if expected_end_time is None:
            expected_end_time = max(self.df.index)
            
        rng = pd.date_range(start=expected_start_time, end=expected_end_time, freq=str(frequency) + 's')
        
        # Check to see if timestamp is monotonic   
#        mask = pd.TimeSeries(self.df.index).diff() < 0
        mask = pd.Series(self.df.index).diff() < pd.Timedelta('0 days 00:00:00')
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)
        mask.columns = [0]
        
        self.append_test_results(mask, 'Nonmonotonic timestamp', variable_name=False, min_failures=min_failures)    
      
        # If not monotonic, sort df by timestamp
        if not self.df.index.is_monotonic:
            self.df = self.df.sort_index()
            
        # Check for duplicate timestamps
#        mask = pd.TimeSeries(self.df.index).diff() == 0
        mask = pd.Series(self.df.index).diff() == pd.Timedelta('0 days 00:00:00')
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)
        mask.columns = [0]
        mask['TEMP'] = mask.index # remove duplicates in the mask
        mask.drop_duplicates(subset='TEMP', keep='last', inplace=True)
        del mask['TEMP']
        
        # Drop duplicate timestamps (this has to be done before the results are appended)
        self.df['TEMP'] = self.df.index
        #self.df.drop_duplicates(subset='TEMP', take_last=False, inplace=True)
        self.df.drop_duplicates(subset='TEMP', keep='first', inplace=True)
        
        self.append_test_results(mask, 'Duplicate timestamp', variable_name=False, min_failures=min_failures)
    
        # reindex timestamps
        missing = []
        for i in rng:
            if i not in self.df.index:
                missing.append(i)
        self.df = self.df.reindex(index=rng)
        mask = pd.DataFrame(data=self.df.shape[0]*[False], index = self.df.index)
        mask.loc[missing] = True
        self.append_test_results(mask, 'Missing timestamp', variable_name=False, min_failures=min_failures)
        

        del self.df['TEMP']
        
    def check_range(self, bound, key=None, specs={}, rolling_mean=1, min_failures=1):
        """
        Check data range.
        
        Parameters
        ----------
        bound : list of floats
            [lower bound, upper bound], None can be used in place of a lower or upper bound
            
        key : string (optional)
            Translation dictionary key.  If not specified, all columns are used in the test.
        
        specs : dictionary (optional)
            Constants used in bound
        
        rolling_mean : int (optional)
            Rolling mean window in number of time steps, default = 1
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check variable ranges")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Range: " + key)
                return 
        else:
            df = self.df 
        
        # Compute moving average
        if rolling_mean > 1:
            df = pd.rolling_mean(df, rolling_mean)
            
        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        # Lower Bound        
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data < lower bound, '+str(bound[0]), min_failures=min_failures) # sub_df=df)
                    
        # Upper Bound   
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data > upper bound, '+str(bound[1]), min_failures=min_failures) #sub_df=df)
        
    def check_increment(self, bound, key=None, specs={}, increment=1, absolute_value=True, rolling_mean=1, min_failures=1):
        """
        Check range on data increments.
        
        Parameters
        ----------
        bound : list of floats
            [lower bound, upper bound], None can be used in place of a lower or upper bound
        
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.
            
        specs : dictionary (optional)
            Constants used in bound
        
        increment : int (optional)
            Time step shift used to compute difference, default = 1
            
        absolute_value : boolean (optional)
            Take the absolute value of the increment data, default = True
            
        rolling_mean : int (optional)
            Rolling mean window in number of time steps, default = 1
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check increment range")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Increment: " + key)
                return 
        else:
            df = self.df 
            
        # Compute moving average
        if rolling_mean > 1:
            df = pd.rolling_mean(df, rolling_mean)
            
        # Compute interval
        if absolute_value:
            df = np.abs(df.diff(periods=increment))
        else:
            df = df.diff(periods=increment)
            
        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        # Lower Bound        
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Increment < lower bound, '+str(bound[0]), min_failures=min_failures) #sub_df=df)
                    
        # Upper Bound   
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Increment > upper bound, '+str(bound[1]), min_failures=min_failures) #sub_df=df)
        
    def check_missing(self, key=None, min_failures=1):
        """
        Check for missing data
        
        Parameters
        ----------
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check for missing data")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Missing: " + key) 
                return 
        else:
            df = self.df 
        
        mask = pd.isnull(df) # checks for np.nan, np.inf
        
        missing_timestamps = self.test_results[self.test_results['Error Flag'] == 'Missing timestamp']
        for index, row in missing_timestamps.iterrows():
            mask.loc[row['Start Date']:row['End Date']] = False
            
        if not tfilter.empty:
            mask[~tfilter] = False
        
        if mask.sum(axis=1).sum(axis=0) > 0:
            self.append_test_results(mask, 'Missing data', min_failures=min_failures)
        
    def check_corrupt(self, corrupt_values, key=None, min_failures=1):
        """
        Check for corrupt data.
        
        Parameters
        ----------
        corrupt_values : list of floats
            List of corrupt data values
            
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.
        
        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check for corrupt data")
        
        if self.df.empty:
            logger.info("Empty database")
            return
            
        tfilter = self.tfilter
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Corrupt: " + key)
                return 
        else:
            df = self.df 
            
        mask = pd.DataFrame(data = np.zeros(df.shape), index = df.index, columns = df.columns, dtype = bool) # all False
        for i in corrupt_values:
            mask = mask | (df == i)
            
        if not tfilter.empty:
            mask[~tfilter] = False
            
        if mask.sum(axis=1).sum(axis=0) > 0:
            self.df[mask] = np.nan
            self.append_test_results(mask, 'Corrupt data', min_failures=min_failures)
             
    def evaluate_string(self, col_name, string_to_eval, specs={}):
        """
        Returns the evaluated python equation written as a string (BETA).  
        For each {keyword} in string_to_eval, 
        {keyword} is first expanded to self.df[self.trans[keyword]], 
        if that fails, then {keyword} is expanded to specs[keyword].

        Parameters
        ----------
        col_name : string
            Column name for the new signal
        
        string_to_eval : string
            String to evaluate
        
        specs : dictionary (optional)
            Constants used as keywords
            
        Returns
        --------
        signal : pd.DataFrame or pd.Series
            DataFrame or Series with results of the evaluated string
        """

        match = re.findall(r"\{(.*?)\}", string_to_eval)
        for m in set(match):
            m = m.replace('[','') # check for list
            
            if m == 'ELAPSED_TIME':
                ELAPSED_TIME = self.get_elapsed_time()
                string_to_eval = string_to_eval.replace("{"+m+"}",m)
            elif m == 'CLOCK_TIME':
                CLOCK_TIME = self.get_clock_time()
                string_to_eval = string_to_eval.replace("{"+m+"}",m)
            else:
                try:
                    self.df[self.trans[m]]
                    datastr = "self.df[self.trans['" + m + "']]"
                    string_to_eval = string_to_eval.replace("{"+m+"}",datastr)
                except:
                    try:
                        specs[m]
                        datastr = "specs['" + m + "']"
                        string_to_eval = string_to_eval.replace("{"+m+"}",datastr)
                    except:
                        pass
                    
        try:
            signal = eval(string_to_eval)
            if type(signal) is tuple:
                col_name = [col_name + " " + str(i+1)  for i in range(len(signal))]
                signal = pd.concat(signal, axis=1)
                signal.columns = [col_name]
                signal.index = self.df.index
            elif type(signal) is float:
                signal = signal
            else:
                signal = pd.DataFrame(signal)
                if len(signal.columns) == 1:
                    signal.columns = [col_name]
                else:
                    signal.columns = [col_name + " " + str(i+1)  for i in range(signal.shape[1])]
                signal.index = self.df.index
        except:
            signal = None
            logger.warning("Insufficient data for Composite Signals: " + col_name + ' -- ' + string_to_eval)
                             
        return signal

    def get_elapsed_time(self):
        """
        Returns the elapsed time in seconds for each Timestamp in the DataFrame index.
        
        Returns
        --------
        elapsed_time : pd.DataFrame
            Elapsed time of the DataFrame index 
        """
        elapsed_time = ((self.df.index - self.df.index[0]).values)/1000000000 # convert ns to s
        elapsed_time = pd.DataFrame(data=elapsed_time, index=self.df.index, dtype=int)
        
        return elapsed_time
    
    def get_clock_time(self):
        """
        Returns the time of day in seconds past midnight for each Timestamp in the DataFrame index.
        
        Returns
        --------
        clock_time : pd.DataFrame
            Clock time of the DataFrame index
        """
        
        secofday = self.df.index.hour*3600 + \
                   self.df.index.minute*60 + \
                   self.df.index.second + \
                   self.df.index.microsecond/1000000.0
        clock_time = pd.DataFrame(secofday, index=self.df.index)
        
        return clock_time
    
    def get_test_results_mask(self, key=None):
        """
        Return a mask of data-times that failed a quality control test.
        
        Parameters
        -----------
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used
            
        Returns
        --------
        test_results_mask : pd.DataFrame
            DataFrame containing boolean values for each data point, True =  
            data point pass all tests, False = data point did not pass at least one test.
        """
        if self.df.empty:
            logger.info("Empty database")
            return
        
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Key not in DataFrame")
                return
        else:
            df = self.df 
            
        test_results_mask = ~pd.isnull(df)
        for i in self.test_results.index:
            system = self.test_results.loc[i, 'System Name']
            variable = self.test_results.loc[i, 'Variable Name']
            start_date = self.test_results.loc[i, 'Start Date']
            end_date = self.test_results.loc[i, 'End Date']
            error_flag = self.test_results.loc[i, 'Error Flag']
            if error_flag in ['Nonmonotonic timestamp', 'Duplicate timestamp']:
                continue
            if variable == '': # occurs when data is missing
                test_results_mask.loc[start_date:end_date] = False
            else:
                if system == '': # occurs when data is a composite signal
                    column_name = variable
                else:
                    column_name = system + ':'+ variable
                test_results_mask.loc[start_date:end_date,column_name] = False
            
        return test_results_mask
