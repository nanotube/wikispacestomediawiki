# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
import optparse
import os.path

class VersionInfo:
    '''Just a container for some information.'''
    version = '0.0.1'
    name = 'Wikispaces To MediaWiki Converter'
    url = 'http://wiki.df.dreamhosters.com/wiki/Wikispaces_to_Mediawiki_Converter'
    author='Daniel Folkinshteyn'
    
class Starter:
    '''Grabs cli options, and runs the converter on specified files.'''
    def __init__(self):
        self.parse_options()
    
    def start(self):
        for filepath in self.options.file:
            wp = WikispacesToMediawikiConverter(filepath, self.options)
            wp.run()
        
    def parse_options(self):
        '''Read command line options
        '''
        parser = optparse.OptionParser(
                        version=VersionInfo.name + " version " +VersionInfo.version + "\nProject homepage: " + VersionInfo.url, 
                        description="This script can convert a Mikispaces-style source page into a MediaWiki-style source page. For a more detailed usage manual, see the project homepage: " + VersionInfo.url, 
                        formatter=optparse.TitledHelpFormatter(),
                        usage="%prog [options]\n or \n  python %prog [options]")
        parser.add_option("-d", "--debug", action="store_true", dest="debug", help="debug mode (print some extra debug output). [default: %default]")
        parser.add_option("-f", "--file", action="append", dest="file", help="Specify filepath to convert. For multiple files use this option multiple times. [default: %default]")
        
        parser.set_defaults(debug=False, 
                            file=[])
        
        (self.options, args) = parser.parse_args()
        if self.options.debug:
            print "Your commandline options:\n", self.options

class WikispacesToMediawikiConverter:
    '''The actual converter: reads in file, converts, outputs.
    
    Reference material:
    http://www.mediawiki.org/wiki/Help:Formatting
    http://www.wikispaces.com/wikitext
    '''
    def __init__(self, filepath, options):
        self.filepath = filepath
        self.options = options
        
        self.content = open(filepath).read()
        
    def run(self):
        self.run_regexps()
        self.write_output()
        
    def run_regexps(self):
        '''Run some regexps on the source.'''
        self.parse_toc()
        self.parse_italics()        
        self.parse_external_links()        
        self.parse_bold()
        self.parse_code()
        self.parse_images()
        self.parse_indents()
        
    def parse_toc(self):
        '''remove the [[toc]] since mediawiki does it by default'''
        self.content = re.sub(r'\[\[toc(\|flat)?\]\]', r'', self.content)
    
    def parse_italics(self):
        """change italics from // to ''"""
        self.content = re.sub(r'(?<!http:)(?<!https:)(?<!ftp:)//', r"''", self.content)
    
    def parse_external_links(self):
        '''change external link format, and free 'naked' external links.
        
        external links with labels get single-braces instead of double
        and space instead of pipe as delimiter between url and label
        
        naked external links (those without label) simply get stripped of
        braces, since that produces the equivalent output in mediawiki.
        '''
        # change external link format
        self.content = re.sub(r'\[\[(https?://[^|\]]*)\|([^\]]*)\]\]', r'[\1 \2]', self.content)
        self.content = re.sub(r'\[\[(ftp://[^|\]]*)\|([^\]]*)\]\]', r'[\1 \2]', self.content)
        
        # free naked external links
        self.content = re.sub(r'\[\[(https?://[^|\]]*)\]\]', r'\1', self.content)
        self.content = re.sub(r'\[\[(ftp://[^|\]]*)\]\]', r'\1', self.content)
    
    def parse_bold(self):
        """change bold from ** to '''"""
        self.content = re.sub(r'(?<![\n\*])\*{2}', "'''", self.content)
    
    def parse_code(self):
        '''convert the [[code]] tags to indented text
        
        by default mediawiki doesn't support code highlighting, so that info
        is lost in conversion.
        
        there are mediawiki extensions that do support it, such as GeSHi,
        but they are not included in the default install. 
        
        maybe will add optional support for that with an extra cli option.
        '''
        def code_indent(matchobj):
            code = matchobj.group(2)
            if self.options.debug:
                print code
            code_lines = code.split('\n')
            indented_code = '\n'.join([' '+line for line in code_lines])
            return indented_code
        self.content = re.sub(r'(?s)\[\[code( +format=".*?")?\]\](.*?)\[\[code\]\]', code_indent, self.content)

    def parse_images(self):
        '''convert [[image:...]] tags to [[File:...]] tags.
        
        various image attributes are supported:
        align, width, height, caption, link.
        
        reference material: 
        http://www.mediawiki.org/wiki/Help:Images
        http://www.wikispaces.com/image+tags
        '''
        def image_parse(matchobj):
            imagetag = matchobj.group(0)
            if self.options.debug:
                print imagetag
            image_filename = re.search(r'\[\[image:([^ ]*)', imagetag).group(1)
            
            try:
                image_width = re.search(r'width="(\d+?)"', imagetag).group(1)
            except AttributeError:
                image_width = None
            
            try:
                image_height = re.search(r'height="(\d+?)"', imagetag).group(1)
            except AttributeError:
                image_height = None
                
            if image_width is not None and image_height is not None:
                image_size = '|' + image_width + 'x' + image_height + 'px'
            elif image_width is not None and image_height is None:
                image_size = '|' + image_width + 'px'
            elif image_width is None and image_height is not None:
                image_size = '|' + 'x' + image_height + 'px'
            else:
                image_size = ''
            
            try:
                image_align = re.search(r'align="(.*?)"', imagetag).group(1)
            except AttributeError:
                image_align = None
            if image_align is not None:
                image_align = '|' + image_align
            else:
                image_align = ''
            
            try:
                image_comment = re.search(r'caption="(.*?)"', imagetag).group(1)
            except AttributeError:
                image_comment = None
            if image_comment is not None:
                image_comment = '|' + image_comment
            else:
                image_comment = ''
            
            try:
                image_link = re.search(r'link="(.*?)"', imagetag).group(1)
            except AttributeError:
                image_link = None
            if image_link is not None:
                image_link = '|' + 'link=' + image_link
            else:
                image_link = ''
            
            # in MW, thumbs cannot be links, but otherwise, a thumb is the 
            # best representation of a captioned wikispaces image.
            if image_comment != '' and image_link == '':
                image_thumb = '|thumb'
            else:
                image_thumb = ''
            
            return '[[File:' + image_filename + image_thumb + image_size + \
                        image_align + image_link + image_comment
            
        self.content = re.sub(r'\[\[image:[^\]]+', image_parse, self.content)
    
    def parse_indents(self):
        '''change indent from > to :'''
        def replace_indents(matchobj):
            indents = matchobj.group(0)
            if self.options.debug:
                print indents
            indents = indents.replace('>', ':')
            return indents
        
        self.content = re.sub(r'(?m)^>+', replace_indents, self.content)
    
    def write_output(self):
        output_filepath = os.path.join(os.path.dirname(self.filepath), 
                            os.path.basename(self.filepath) + '_mediawiki')
                            
        open(output_filepath, 'w').write(self.content)


if __name__ == '__main__':
    s = Starter()
    s.start()
