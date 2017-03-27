class Bucket(object):
    """Holds an amount with a value that can be added to and substracted from."""
    
    def __init__(self, amount, value):
        if amount < 0 or value < 0:
            raise NegativeSubstance
            
        self.amount = amount
        self.value = value
        
        
    def take(self, amount):
        if amount <= 0:
            raise NegativeSubstance
            
        if amount > self.amount:
            raise RunDry
            
        removed = round(self.value * amount / self.amount)
        self.amount -= amount
        self.value -= removed
        
        return removed
        
    def give(self, amount, value):
        if amount <= 0 or value < 0:
            raise NegativeSubstance
            
        self.amount += amount
        self.value += value
        
        
class Well(object):
    """Infinite source of pit that can be part of a transaction."""
    def __init__(self, value):
        self.value = value
        
    def take(self, amount):
        return amount*self.value
        
    def give(self, amount, value):
        pass
        
        
class RunDry(Exception):
    """Attempted to get more out of a bucket than it contains."""
    
    
class NegativeSubstance(Exception):
    """Attempted to initialize or modify a bucket with negative values"""
        
        
def flow(source, destination, amount):
    value = source.take(amount)
    destination.give(amount, value)
    
