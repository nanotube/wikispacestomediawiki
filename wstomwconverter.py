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
    '''The actual converter: reads in file, converts, outputs.'''
    def __init__(self, filepath, options):
        self.filepath = filepath
        self.options = options
        
        self.content = open(filepath).read()
        
    def run(self):
        '''Run some regexps on the source.'''
        
        # remove the [[toc]] since mediawiki does it by default
        self.content = re.sub(r'\[\[toc(\|flat)?\]\]', r'', self.content)
        
        #change italics from // to ''
        self.content = re.sub(r'(?<!http:)(?<!https:)(?<!ftp:)//', r"''", self.content)
        
        # change external link format
        self.content = re.sub(r'\[\[(https?://[^|]*)\|([^\]]*)\]\]', r'[\1 \2]', self.content)
        self.content = re.sub(r'\[\[(ftp://[^|]*)\|([^\]]*)\]\]', r'[\1 \2]', self.content)
        
        # change bold from ** to '''
        self.content = re.sub(r'(?<!\n)\*{2}', "'''", self.content)
        
        # convert the [[code]] tags to indented text
        def code_indent(matchobj):
            code = matchobj.group(2)
            if self.options.debug:
                print code
            code_lines = code.split('\n')
            indented_code = '\n'.join([' '+line for line in code_lines])
            return indented_code
        self.content = re.sub(r'(?s)\[\[code( +format=".*?")?\]\](.*?)\[\[code\]\]', code_indent, self.content)
        
        # convert [[image:...]] tags to [[File:...]] tags.
        def image_parse(matchobj):
            imagetag = matchobj.group(0)
            if self.options.debug:
                print imagetag
            image_filename = re.search(r'\[\[image:([^ ]*)', imagetag).group(1)
            try:
                image_width = re.search(r'width="(\d+?)"', imagetag).group(1)
            except AttributeError:
                image_width = None
            if image_width is not None:
                image_width = '|' + image_width + 'px'
            else:
                image_width = ''
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
                
            return '[[File:' + image_filename + image_width + image_align + image_comment
            
        self.content = re.sub(r'\[\[image:[^\]]+', image_parse, self.content)
        
        self.write_output()
        
    def write_output(self):
        output_filepath = os.path.join(os.path.dirname(self.filepath), 
                            os.path.basename(self.filepath) + '_mediawiki')
                            
        open(output_filepath, 'w').write(self.content)


if __name__ == '__main__':
    s = Starter()
    s.start()