import unittest

from test_mp3header import Test_MP3Header

def build_test_suites():
    myTestSuites = {}
    test_cases = [Test_MP3Header]
    test_types = ['short', 'medium', 'long']
    for type in test_types:
        suite = unittest.TestSuite()
        for case in test_cases:
            suite.addTest(unittest.makeSuite(case, 'test_{0}'.format(type)))
        myTestSuites[type] = suite
    return myTestSuites

def run_testcase(case):
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(case, 'test'))
    runner.run(suite)

def run_suite(suite, name = '', skipif=False):
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

if __name__ == '__main__':
    
    skipif = False
    global myTestSuites
    suites = build_test_suites()
    print("Running all available tests")
    for name, suite in suites.items():
        skipif = not run_suite(suite, name, skipif) 

