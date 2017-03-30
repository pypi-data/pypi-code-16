"""
Copyright 2017 Jeff Ward

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, 
software distributed under the License is distributed on an 
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, 
either express or implied. See the License for the specific 
language governing permissions and limitations under the License.
"""

import pickle
import threading

class EasyCache:
    """This class makes it easy to cache the results of a function. Only functions that are invariant to time should
    be cached. In other words, only functions that return the same result given the same inputs should be cached.
    This currently only supports functions without named parameters.

    """

    def __init__(self, cacheFile, autoFlush=True, overwrite=False):
        self.fileLock = threading.Lock()
        self.cacheLock = threading.Lock()
        self.cacheFile = cacheFile
        self.autoFlush = autoFlush
        self._functionInfo = {}
        try:
            if not overwrite:
                with open(cacheFile, mode="rb") as dataFile:
                    self.cache = pickle.load(dataFile)
            else:
                self._initCache()
                self.cacheUpdated()
        except:
            self._initCache()
            self.cacheUpdated()

    def _initCache(self):
        self.cache = {"properties": {}}

    def flush(self):
        """This will immediately write whatever results are in the cache even if nothing has changed.

        :return:
        """
        with self.fileLock, self.cacheLock:
            with open(self.cacheFile, mode="wb") as dataFile:
                pickle.dump(self.cache, dataFile, protocol=pickle.HIGHEST_PROTOCOL)

    def cacheUpdated(self):
        if self.autoFlush:
            self.flush()

    def clearCache(self):
        """This will IMMEDIATELY delete all contents in the cache. Use with care!

        :return:
        """
        with self.cacheLock:
            self._initCache()
        self.cacheUpdated()

    def __delattr__(self, item):
        try:
            del self.cache["properties"][item]
            self.cacheUpdated()
            return
        except:
            pass
        try:
            del self.cache[item]
            del self._functionInfo[item]
            self.cacheUpdated()
            return
        except:
            pass
        super.__delattr__(self, item)

    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            properties = self.__dict__["cache"]["properties"]
            return properties[item]

    def __setattr__(self, key, value):
        try:
            if key in self.cache["properties"]:
                self.cache["properties"][key] = value
                self.cacheUpdated()
        except:
            pass
        self.__dict__[key] = value

    def cacheProperty(self, name, initialValue=None):
        if name not in self.cache["properties"]:
            self.cache["properties"][name] = initialValue
            self.cacheUpdated()

    def cacheFunction(self, function, name="cachedFunction", threadSafe=True, ignoreParams=0):
        """This will create a cache wrapper for the given function with the given name and bind it to this object with
        that name. The function signature will be whatever args are passed, however a single named parameter, mode,
        is added. Mode can take the following values:
        'use_cache' (default) - use the cached value if available, run the function if not available.
        'force_run' - force the function to run again and overwrite the cached value if there is one.
        'clear_cache' - clears the cache for just this function's inputs and doesn't run the function.
        'cache_peek' - returns immediately with what is in the cache or None if nothing

        :param function:
        :param name:
        :param threadSafe:
        :param ignoreParams: number of initial parameters to ignore (default 0). Use this to allow passing parameters that should not be considered in the cache (for examplke system parameaters)
        :return:
        """
        if threadSafe:
            functionLock = None
        else:
            functionLock = threading.Lock()
        with self.cacheLock:
            self._functionInfo[name] = (functionLock, function, ignoreParams)
            cacheWrapper = lambda *args, **kwargs: self.cachedFunctionCall(name, kwargs.get('mode','use_cache'), *args)
            setattr(self, name, cacheWrapper)
        return self.__dict__[name]

    def _convertArg(self, arg):
        if type(arg) is dict:
            return "".join(("{}{}".format(key, self._convertArg(arg[key])) for key in sorted(arg)))
        elif type(arg) is list:
            return "".join((self._convertArg(val) for val in arg))
        return str(arg)

    def buildCacheArgs(self, args):
        return "".join((self._convertArg(arg) for arg in args))

    def cachedFunctionCall(self, functionName, mode, *args):
        """This will call the named function. See cacheFunction for details on mode.

        :param functionName:
        :param function:
        :param mode: 'use_cache', 'force_run', 'clear_cache', 'cache_peek'
        :param args:
        :return:
        """

        if functionName not in self._functionInfo:
            raise ValueError("{} not a known cached function".format(functionName))
        functionLock, function, ignoreParams = self._functionInfo[functionName]

        cacheArgs = self.buildCacheArgs(args[ignoreParams:])

        with self.cacheLock:
            if functionName not in self.cache:
                functionsCache = {}
                self.cache[functionName] = functionsCache
            else:
                functionsCache = self.cache[functionName]

            if mode == 'clear_cache' or mode == 'force_run':
                del functionsCache[cacheArgs]

        if mode == 'clear_cache':
            self.cacheUpdated()
            return

        if cacheArgs in functionsCache:
            return functionsCache[cacheArgs]
        if mode == 'cache_peek':
            return None
        try:
            if functionLock is not None:
                functionLock.acquire()
            value = function(*args)
            with self.cacheLock:
                functionsCache[cacheArgs] = value
            self.cacheUpdated()
            return value
        finally:
            if functionLock is not None:
                functionLock.release()


def cacheFunction(function, cacheFile, autoFlush=True, overwrite=False, name="cachedFunction", threadSafe=True,
                  ignoreParams=0):
    return EasyCache(cacheFile, autoFlush=autoFlush, overwrite=overwrite).cacheFunction(function, name=name,
                                                                                        threadSafe=threadSafe,
                                                                                        ignoreParams=ignoreParams)
