# pylint: disable=trailing-whitespace, import-error

"""This file aggregates and runs all the test cases found in the test
   directory.  It is used for unittest validation."""

import unittest

try: 
    from test_mp3header import Test_MP3Header  # @UnresolvedImport
    from test_mp3framelist import Test_MP3FrameList  # @UnresolvedImport
    from test_mp3file import Test_MP3File  # @UnresolvedImport
    from test_pythonrecordarray import Test_PythonRecordArray #@UnresolvedImport
    from test_id3 import Test_ID3 #@UnresolvedImport
    from test_id3v2common import Test_ID3v2Common #@UnresolvedImport
    from test_id3v2_frames import Test_ID3v2xFrames #@UnresolvedImport
except:
    from tests.test_mp3header import Test_MP3Header  # @UnresolvedImport
    from tests.test_mp3framelist import Test_MP3FrameList  # @UnresolvedImport
    from tests.test_mp3file import Test_MP3File  # @UnresolvedImport
    from tests.test_pythonrecordarray import Test_PythonRecordArray #@UnresolvedImport
    from tests.test_id3 import Test_ID3 #@UnresolvedImport
    from tests.test_id3v2common import Test_ID3v2Common #@UnresolvedImport
    from tests.test_id3v2_frames import Test_ID3v2xFrames #@UnresolvedImport
    

def build_test_suites(cases=None):
    """Builds three suites of tests, one for all the short tests, medium 
       tests, and long tests."""
    my_test_suites = []
    if None == cases:
        test_cases = [Test_PythonRecordArray, 
                      Test_MP3Header, 
                      Test_MP3FrameList, 
                      Test_MP3File,
                      Test_ID3,
                      Test_ID3v2Common,
                      Test_ID3v2xFrames]
    else:
        test_cases = cases
    test_types = ['short', 'medium', 'long']
    for t_type in test_types:
        suite = unittest.TestSuite()
        for case in test_cases:
            suite.addTest(unittest.makeSuite(case, 'test_{0}'.format(t_type)))
        my_test_suites.append((t_type,suite))
    return my_test_suites

def run_testcase(case):
    """Runs a single test"""
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(case, 'test'))
    runner.run(suite)

def run_suite(suite, name = '', skipif=False):
    """runs a suit of tests, or optionally skips all the tests"""
    if skipif:
        print("Failed previous tests, skipping {0}".format(name))
    else:
        runner = unittest.TextTestRunner()
        #print("Running suite {0}".format(name))
        testresults = runner.run(suite)
        if testresults.failures or testresults.errors:
            return False
        else:
            return True 
        
def run_tests(suites_to_use=None): 
    """Runs all suites of tests built by build_test_suites"""      
    skipif = False
    suites = build_test_suites(suites_to_use)
    print("Running all available tests")
    for name, suite in suites:
        print("Running suite {}".format(name))
        skipif = not run_suite(suite, name, skipif)
        
if __name__ == '__main__':
    run_tests()
