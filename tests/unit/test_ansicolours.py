import unittest

from pyraxshell.ansicolours import ANSIColours


class TestANSIColours(unittest.TestCase):


    def test_endc(self):
        c = ANSIColours()
        self.assertEqual(c.endc, '\033[0m')

    def test_get(self):
        c = ANSIColours()
        # normal colours
        self.assertEqual(c.get('black'), '\033[90m')
        self.assertEqual(c.get('red'), '\033[91m')
        self.assertEqual(c.get('green'), '\033[92m')
        self.assertEqual(c.get('yellow'), '\033[93m')
        self.assertEqual(c.get('blue'), '\033[94m')
        self.assertEqual(c.get('magenta'), '\033[95m')
        self.assertEqual(c.get('cyan'), '\033[96m')
        self.assertEqual(c.get('white'), '\033[97m')
        # bright colours
        self.assertEqual(c.get('black', True), '\033[100m')
        self.assertEqual(c.get('red', True), '\033[101m')
        self.assertEqual(c.get('green', True), '\033[102m')
        self.assertEqual(c.get('yellow', True), '\033[103m')
        self.assertEqual(c.get('blue', True), '\033[104m')
        self.assertEqual(c.get('magenta', True), '\033[105m')
        self.assertEqual(c.get('cyan', True), '\033[106m')
        self.assertEqual(c.get('white', True), '\033[107m')

    def test_list_colours(self):
        c = ANSIColours()
        colours_list = ['black', 'red', 'green', 'yellow', 'blue', 'magenta',
                        'cyan', 'white']
        self.assertEqual(c.colours, colours_list)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()