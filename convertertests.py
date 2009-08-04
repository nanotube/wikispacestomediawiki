import unittest
import wstomwconverter

class OptionsContainer:
    pass

class TestConverter(unittest.TestCase):
    def setUp(self):    
        filepath = "./test.tmp"
        open(filepath, 'w').write('junk')
    
        options = OptionsContainer()
        options.debug=False
        
        self.converter = wstomwconverter.WikispacesToMediawikiConverter(filepath, 
                        options)
    
    def test_bold_simple(self):
        self.source_wikitext = \
"""
A paragraph with **some bold text** in it.

Some **multiline 
bold text**
"""
        self.target_wikitext = \
"""
A paragraph with '''some bold text''' in it.

Some '''multiline 
bold text'''
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_bold_lists(self):
        self.source_wikitext = \
"""
* level 1 list item **some bold text**
** level 2 list item **some bold text**
*** level 3 list item **some bold text**
**** level 4 list item **some bold text** **more bold text**
"""
        self.target_wikitext = \
"""
* level 1 list item '''some bold text'''
** level 2 list item '''some bold text'''
*** level 3 list item '''some bold text'''
**** level 4 list item '''some bold text''' '''more bold text'''
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_bold_tricky(self):
        self.source_wikitext = \
"""
Some tricky stuff: ***** this should parse as a bolded star.
"""
        self.target_wikitext = \
"""
Some tricky stuff: '''*''' this should parse as a bolded star.
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_italics_simple(self):
        self.source_wikitext = \
"""
A paragraph with //some italicized text// in it.

Some //multiline
italicized// text.
"""
        self.target_wikitext = \
"""
A paragraph with ''some italicized text'' in it.

Some ''multiline
italicized'' text.
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

if __name__ == '__main__':
    unittest.main()
