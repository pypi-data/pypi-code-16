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

import time

import easycache as ec


def myExpensiveFunction(cost):
    time.sleep(cost)
    print("This was expensive!")
    return cost



def simpleExample():
    cachedExpensiveFunction = ec.cacheFunction(myExpensiveFunction, 'example.pkl', name="myExpensiveFunction",
                                               overwrite=True)
    cost = .5

    startTime = time.time()
    result = cachedExpensiveFunction(cost)
    endTime = time.time()

    print("Run 1: result = {}, Total time:{}".format(result, endTime - startTime))

    startTime = time.time()
    result = cachedExpensiveFunction(cost)
    endTime = time.time()

    print("Run 2: result = {}, Total time:{}".format(result, endTime - startTime))

    startTime = time.time()
    result = cachedExpensiveFunction(cost, mode='force_run')
    endTime = time.time()

    print("Run 3: result = {}, Total time:{}".format(result, endTime - startTime))

    startTime = time.time()
    result = cachedExpensiveFunction(cost)
    endTime = time.time()

    print("Run 4: result = {}, Total time:{}".format(result, endTime - startTime))

    print("Peek: {}".format(cachedExpensiveFunction(cost, mode='cache_peek')))
    cachedExpensiveFunction(cost, mode='clear_cache')
    print("Peek: {}".format(cachedExpensiveFunction(cost, mode='cache_peek')))

    cachedExpensiveFunction(cost)

    fc = ec.EasyCache('example.pkl')
    fc.cacheFunction(myExpensiveFunction, "myExpensiveFunction")

    startTime = time.time()
    result = fc.myExpensiveFunction(cost)
    endTime = time.time()

    print("Run 5: result = {}, Total time:{}".format(result, endTime - startTime))

    fc.cacheProperty('bar')
    print('fc.bar={}'.format(fc.bar))
    fc.bar = 12
    print('fc.bar={}'.format(fc.bar))

    fc2 = ec.EasyCache('example.pkl')
    fc2.cacheProperty('bar')
    print('fc2.bar={}'.format(fc2.bar))

def gridSearchExample(paramA, paramB):
    """ Simulates a grid search over parameter values
    
    :param paramA: list of values
    :param paramB: list of values
    :return: 
    """
    cachedEF = ec.cacheFunction(myExpensiveFunction, 'example.pkl', name="myExpensiveFunction")

    bestValue = None
    bestA = None
    bestB = None
    for a in paramA:
        for b in paramB:
            newValue = cachedEF(a+b)
            if bestValue is None or newValue > bestValue:
                bestValue = newValue
                bestA = a
                bestB = b
    return bestValue, bestA, bestB

def runClass(cache):
    print("Cached Value={}", cache.someValue)
    #Assignment will flush the cache.
    #If this is a complex object you will need to manually flush if internal state changes
    cache.someValue = 12
    print("Cached Value={}", cache.someValue)
    print("peek={}".format(cache.myExpensiveFunction(.5, mode="cache_peek")))
    cache.myExpensiveFunction(.5)

def classExample():
    cache = ec.EasyCache("exampleClass.pkl")
    cache.clearCache()
    cache.cacheFunction(myExpensiveFunction, name="myExpensiveFunction")
    cache.cacheProperty("someValue", initialValue=42)
    runClass(cache)
    runClass(cache)
    cache.myExpensiveFunction(.5,mode="force_run")
    cache.myExpensiveFunction(.5,mode="cache_clear")
    cache.myExpensiveFunction(.5)
    del cache.someValue
    del cache.myExpensiveFunction
    try:
        cache.myExpensiveFunction(.5)
    except:
        print("No function!")

def main():
    simpleExample()
    print("Best Value={} using A={} and B={}".format(*gridSearchExample([.1, .2], [.01, .02])))
    #Oh, we REALLY should have searched more! This should only run the 2 new tests
    print("Best Value={} using A={} and B={}".format(*gridSearchExample([.1, .2], [.01, .02, .003])))
    classExample()

if __name__ == "__main__":
    main()
