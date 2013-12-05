# pylint: disable=trailing-whitespace, old-style-class
# pylint: disable=no-member

"""This provides "record array" like functionality (like in numpy)
   with python arrays."""
   
from array import array

class PythonRecordArray():
    """This provides "record array" like functionality (like in numpy)
       with python arrays.  Using integers as field names is unsupported."""  
    #TODO: set these based on the machine architecture. 
    def __init__(self, count, dtype, init=0):
        self.names = {}
        self.arraylist = []
        for name,ntype in dtype:
            self.names[name] = len(self.arraylist)
            self.arraylist.append(array(ntype, (init,)*count))
    
    def __getitem__(self, index):
        """Retrieves a entire record at a given index as a list"""
        record = []
        for _array in self.arraylist:
            record.append(_array[index])
        return record
    
    def __setitem__(self, index, values):
        """Sets a record at a given index to the values passed in"""
        for array_index, value in enumerate(values):
            self.arraylist[array_index][index] = value
    
    def __getattr__(self, index):
        """This should enable myarray.myfield notation"""
        if self.names and index in self.names:
            return self.arraylist[self.names[index]]
        else:
            return self.__dict__[index]
    
    def __setattr__(self, index, value):
        if index != 'names' and self.names and index in self.names:
            self.arraylist[self.names[index]] = value
        else:
            object.__setattr__(self, index, value)
            
    def __len__(self):
        return len(self.arraylist[0])
    
    def __delitem__(self):
        #TODO: Delete things from the array
        raise Exception("Delete Item not yet implemented")
