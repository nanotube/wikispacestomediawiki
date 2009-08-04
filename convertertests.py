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
Some tricky stuff: *****
Wikispaces parses this as a bolded nothing with a star following it.
"""
        self.target_wikitext = \
"""
Some tricky stuff: ''''''*
Wikispaces parses this as a bolded nothing with a star following it.
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
        
    def test_italics_withurls(self):
        self.source_wikitext = \
"""
A paragraph with //some italicized text// in it.

A paragraph with a url: http://www.google.com/
"""
        self.target_wikitext = \
"""
A paragraph with ''some italicized text'' in it.

A paragraph with a url: http://www.google.com/
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_toc(self):
        self.source_wikitext = \
"""
A paragraph...

[[toc]]

[[toc|flat]]
"""
        self.target_wikitext = \
"""
A paragraph...




"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_external_links(self):
        self.source_wikitext = \
"""
A paragraph with [[http://example.com|an external link]].

Another paragraph with [[https://example.com|an external link]].

Yet another paragraph with [[ftp://example.com|an external link]].
"""
        self.target_wikitext = \
"""
A paragraph with [http://example.com an external link].

Another paragraph with [https://example.com an external link].

Yet another paragraph with [ftp://example.com an external link].
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_naked_external_links(self):
        self.source_wikitext = \
"""
A paragraph with a [[http://example.com]] naked external link. Link should 
simply be stripped of brackets.

Another [[ftp://example.com]] naked external link.

And another one [[https://example.com]].

A really naked one here: http://example.com. Nothing should happen to it.
"""
        self.target_wikitext = \
"""
A paragraph with a http://example.com naked external link. Link should 
simply be stripped of brackets.

Another ftp://example.com naked external link.

And another one https://example.com.

A really naked one here: http://example.com. Nothing should happen to it.
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

    def test_code_tags(self):
        self.source_wikitext = \
"""
A paragraph with [[code]]some code in it[[code]].

[[code]]
Some
multiline
code
[[code]]

Yet another paragraph with [[code]]some
multiline
code
[[code]]
"""
        self.target_wikitext = \
"""
A paragraph with 
 some code in it
.


 Some
 multiline
 code


Yet another paragraph with 
 some
 multiline
 code

"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)
        
    def test_image_tags(self):
        self.source_wikitext = \
"""
A paragraph with an image:
[[image:somefile.gif width="20" height="80" align="left" link="http://example.com" caption="some caption"]].

A paragraph with a simpler image: [[image:somefile.gif]]

A paragraph with a medium-complexity image: [[image:somefile.gif height="80" align="right"]]
"""
        self.target_wikitext = \
"""
A paragraph with an image:
[[File:somefile.gif|20px|left|some caption]].

A paragraph with a simpler image: [[File:somefile.gif]]

A paragraph with a medium-complexity image: [[File:somefile.gif|right]]
"""
        self.converter.content = self.source_wikitext
        self.converter.run_regexps()
        self.assertEqual(self.converter.content, self.target_wikitext)

if __name__ == '__main__':
    unittest.main()
