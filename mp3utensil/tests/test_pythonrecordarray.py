# pylint: disable=trailing-whitespace, import-error, invalid-name
# pylint: disable=no-member, too-many-public-methods
'''Test Module for pythonrecordarray module'''

import unittest
import pythonrecordarray

class Test_PythonRecordArray(unittest.TestCase):
    """Test class for PythonRecordArray"""
    
    def test_short_01_init_and_access(self):
        """Currently tests everything in this class."""
        typedef = [("recordone",'H'),
                   ("recordtwo",'L'),
                   ("recordthree",'L')]
        parray = pythonrecordarray.PythonRecordArray(10,typedef,0)
        self.assertEqual([0,0,0],parray[0])
        self.assertEqual(0, parray.recordone[0])
        parray[0] = (1,2,3)
        self.assertEqual([1,2,3],parray[0])
        self.assertEqual(2, parray.recordtwo[0])
        self.assertEqual(2, parray[0][1])
        parray.recordthree[0] = 9
        self.assertEqual(9, parray.recordthree[0])
        self.assertEqual(10, len(parray))
        with self.assertRaises(TypeError):
            pythonrecordarray.PythonRecordArray(10, [("recordone",None),])

if __name__ == '__main__':
    import test_all #@UnresolvedImport
    test_all.run_tests([Test_PythonRecordArray])
    