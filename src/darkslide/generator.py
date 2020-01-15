# -*- coding: utf-8 -*-
import codecs
import inspect
import os
import re
import shutil
import sys

import jinja2
from six import binary_type, string_types

from . import __version__
from . import macro as macro_module
from . import utils
from .parser import Parser
from .conf import UserConfig

BASE_DIR = os.path.dirname(__file__)
THEMES_DIR = os.path.join(BASE_DIR, 'themes')
RCFILEPATH = os.path.expanduser('~/.darkslide.cfg')


class Generator(object):
    """The Generator class takes and processes presentation source as a file, a
       folder or a configuration file and provides methods to render them as a
       presentation.
    """
    default_macros = (
        macro_module.CodeHighlightingMacro,
        macro_module.EmbedImagesMacro,
        macro_module.FixImagePathsMacro,
        macro_module.FxMacro,
        macro_module.NotesMacro,
        macro_module.QRMacro,
        macro_module.FooterMacro,
    )

    # these are basic CSS classes: a slide must be of one of these classes, in
    # addition to user-defined ones
    basic_slide_classes = (
        'slide-title',
        'slide-content',
    )

    def __init__(self, source, logger=None, debug=False, **kwargs):
        """ Configures this generator. Available ``args`` are:
        TODO
        """
        self.debug = debug
        self.logger = logger
        assert self.logger is None or callable(self.logger)
        self.num_slides = 0
        self.__toc = []

        if not source or not os.path.exists(source):
            raise IOError("Source file/directory %s does not exist" % source)

        # priority for options definition: default values, then user config
        # file, then source file, then command-line options
        self.userconf = UserConfig()

        # look for an RCfile
        if os.path.isfile(RCFILEPATH):
            self.userconf.update(UserConfig.from_configfile(RCFILEPATH))

        # if the source given is a config file, then load it
        if source.endswith('.cfg'):
            cfgfile = UserConfig.from_configfile(source)
            if not cfgfile['source']:
                raise IOError('unable to fetch a valid source from config')

            self.userconf.update(cfgfile)
        else:
            self.userconf['source'] = [source]

        # at last override anything that may have been overriden by CLI
        # arguments
        self.userconf.update(kwargs)

        if self.userconf['direct']:
            # Only output html in direct output mode, not log messages
            self.userconf['verbose'] = False

        source_abspath = os.path.abspath(self.userconf['source'][0])
        self.destination_dir = os.path.dirname(self.userconf['destination_file'])

        if not os.path.isdir(source_abspath):
            source_abspath = os.path.dirname(source_abspath)

        self.watch_dir = source_abspath

        dest_file = self.userconf['destination_file']
        if (os.path.exists(dest_file) and not os.path.isfile(dest_file)):
            raise IOError("Destination %s exists and is not a file" %
                          dest_file)

        self.theme_dir = self.find_theme_dir(self.userconf['theme'],
                                             self.userconf['copy_theme'])
        self.template_file = self.get_template_file()

        # macros registering
        self.macros = []
        self.register_macro(*self.default_macros)


    def add_toc_entry(self, title, level, slide_number):
        """ Adds a new entry to current presentation Table of Contents.
        """
        self.__toc.append({'title': title, 'number': slide_number,
                           'level': level})

    @property
    def toc(self):
        """ Smart getter for Table of Content list.
        """
        toc = []
        stack = [toc]
        for entry in self.__toc:
            entry['sub'] = []
            while entry['level'] < len(stack):
                stack.pop()
            while entry['level'] > len(stack):
                stack.append(stack[-1][-1]['sub'])
            stack[-1].append(entry)
        return toc

    def execute(self):
        """ Execute this generator regarding its current configuration.
        """
        if self.userconf['direct']:
            out = getattr(sys.stdout, 'buffer', sys.stdout)
            out.write(self.render().encode(self.userconf['encoding']))
        else:
            self.write_and_log()

            if self.userconf['watch']:
                from .watcher import watch

                self.log(u"Watching %s\n" % self.watch_dir)

                watch(self.watch_dir, self.write_and_log)

    def write_and_log(self):
        self.watch_files = []
        self.num_slides = 0
        self.__toc = []
        self.write()
        self.log(u"Generated file: %s" % self.userconf['destination_file'])

    def get_template_file(self):
        """ Retrieves Jinja2 template file path.
        """
        if os.path.exists(os.path.join(self.theme_dir, 'base.html')):
            return os.path.join(self.theme_dir, 'base.html')
        default_dir = os.path.join(THEMES_DIR, 'default')
        if not os.path.exists(os.path.join(default_dir, 'base.html')):
            raise IOError("Cannot find base.html in default theme")
        return os.path.join(default_dir, 'base.html')


    def fetch_contents(self, sources):
        """ Recursively fetches Markdown contents from a single file or
            directory containing itself Markdown/RST files.
        """
        slides = []

        for source in sources:
            source = os.path.normpath(source)
            if os.path.isdir(source):
                self.log(u"Entering %r" % source)
                entries = os.listdir(source)
                entries.sort()
                for entry in entries:
                    slides.extend(self.fetch_contents(entry))
            else:
                try:
                    parser = Parser(os.path.splitext(source)[1],
                                    self.userconf['encoding'],
                                    self.userconf['extensions'])
                except NotImplementedError as exc:
                    self.log(u"Failed   %r: %r" % (source, exc))
                    return slides

                self.log(u"Adding   %r (%s)" % (source, parser.format))

                try:
                    with codecs.open(source, encoding=self.userconf['encoding']) as file:
                        file_contents = file.read()
                except UnicodeDecodeError:
                    self.log(u"Unable to decode source %r: skipping" % source,
                             'warning')
                else:
                    inner_slides = re.split(r'<hr.+>', parser.parse(file_contents))
                    for inner_slide in inner_slides:
                        slides.append(self.get_slide_vars(inner_slide, source))

        if not slides:
            self.log(u"Exiting  %r: no contents found" % source, 'notice')

        return slides

    def find_theme_dir(self, theme, copy_theme=False):
        """ Finds them dir path from its name.
        """
        if os.path.exists(theme):
            theme_dir = theme
        elif os.path.exists(os.path.join(THEMES_DIR, theme)):
            theme_dir = os.path.join(THEMES_DIR, theme)
        else:
            raise IOError("Theme %s not found or invalid" % theme)

        target_theme_dir = os.path.join(os.getcwd(), 'theme')
        if copy_theme or os.path.exists(target_theme_dir):
            self.log(u'Copying %s theme directory to %s'
                     % (theme, target_theme_dir))
            if not os.path.exists(target_theme_dir):
                try:
                    shutil.copytree(theme_dir, target_theme_dir)
                except Exception as e:
                    self.log(u"Skipped copy of theme folder: %s" % e)
            theme_dir = target_theme_dir

        return theme_dir

    def get_file_content(self, paths, encoding):
        """TODO"""
        if isinstance(paths, string_types):
            paths = (paths,)

        for filepath in paths:
            if not os.path.isfile(filepath):
                continue
            with codecs.open(filepath, encoding=encoding) as file_fd:
                contents = file_fd.read()
            return {
                'path_url': utils.get_path_url(
                    filepath,
                    self.userconf['relative'] and self.destination_dir
                ),
                'dirname': os.path.dirname(filepath),
                'contents': contents,
                'embeddable': True
            }

        # no readable file found
        return None

    def get_css(self):
        """ Fetches and returns stylesheet file path or contents, for both
            print and screen contexts, depending if we want a standalone
            presentation or not.
        """
        css = {}

        for basename in ('base', 'print', 'screen', 'theme'):
            lookup_files = (
                os.path.join(basedir, 'css', '%s.css' % basename)
                for basedir in (self.theme_dir, THEMES_DIR)
            )
            content = self.get_file_content(lookup_files,
                                            self.userconf['encoding'])
            if content is None:
                raise IOError("Cannot find %s.css in default theme" % basename)
            css[basename] = content

        return css


    def get_js(self):
        """ Fetches and returns javascript file path or contents, depending if
            we want a standalone presentation or not.
        """
        lookup_files = (
            os.path.join(self.theme_dir, 'js', 'slides.js'),
            os.path.join(THEMES_DIR, 'default', 'js', 'slides.js'),
        )
        content = self.get_file_content(lookup_files, self.userconf['encoding'])

        if content is None:
            raise IOError(u"Cannot find slides.js in default theme")

        return content


    def get_user_files_content(self, files_list):
        """TODO"""
        user_files = []
        for filepath in files_list:
            if not os.path.isabs(filepath):
                filepath = os.path.join(self.userconf.base_dir, filepath)
            content = self.get_file_content(filepath, self.userconf['encoding'])
            if content is None:
                raise IOError("Cannot read user file '%s'" % filepath)
            user_files.append(content)
        return user_files


    def get_slide_vars(self, slide_src, source,
                       _presenter_notes_re=re.compile(r'<h\d[^>]*>presenter notes</h\d>',
                                                      re.DOTALL | re.UNICODE | re.IGNORECASE),
                       _slide_title_re=re.compile(r'(<h(\d+?).*?>(.+?)</h\d>)\s?(.+)?', re.DOTALL | re.UNICODE)):
        """ Computes a single slide template vars from its html source code.
            Also extracts slide information for the table of contents.
        """
        presenter_notes = ''

        find = _presenter_notes_re.search(slide_src)

        if find:
            if self.userconf['presenter_notes']:
                presenter_notes = slide_src[find.end():].strip()

            slide_src = slide_src[:find.start()]

        find = _slide_title_re.search(slide_src)

        if not find:
            header = level = title = None
            content = slide_src.strip()
        else:
            header = find.group(1)
            level = int(find.group(2))
            title = find.group(3)
            content = find.group(4).strip() if find.group(4) else find.group(4)

        slide_classes = []
        context = {}

        if header:
            header, _ = self.process_macros(header, source, context)

        if content:
            content, slide_classes = self.process_macros(content, source, context)

        # macros enable to set the basic slide class (content or title): if the
        # slide class is not defined, guess it
        if all(cls not in slide_classes for cls in self.basic_slide_classes):
            slide_classes.append('slide-content' if content else 'slide-title')

        source_dict = {}

        if source:
            source_dict = {
                'rel_path': source.decode(sys.getfilesystemencoding(), 'ignore') if isinstance(source,
                                                                                               binary_type) else source,
                'abs_path': os.path.abspath(source)
            }

        if header or content:
            context.update(
                content=content,
                classes=slide_classes,
                header=header,
                level=level,
                source=source_dict,
                title=title,
            )
            context.setdefault('presenter_notes', '')
            context['presenter_notes'] += presenter_notes
            if not context['presenter_notes']:
                context['presenter_notes'] = None
            return context

    def get_template_vars(self, slides):
        """ Computes template vars from slides html source code.
        """
        try:
            head_title = slides[0]['title']
        except (IndexError, TypeError):
            head_title = "Untitled Presentation"

        for slide_vars in slides:
            if not slide_vars:
                continue
            self.num_slides += 1
            slide_number = slide_vars['number'] = self.num_slides
            if slide_vars['level'] and (slide_vars['level'] <=
                                        self.userconf['maxtoclevel']):
                # only show slides that have a title and lever is not too deep
                self.add_toc_entry(slide_vars['title'], slide_vars['level'], slide_number)

        return {
            'head_title': head_title,
            'num_slides': str(self.num_slides),
            'slides': slides,
            'toc': self.toc,
            'embed': self.userconf['embed'],
            'css': self.get_css(),
            'js': self.get_js(),
            'user_css': self.get_user_files_content(self.userconf['user_css']),
            'user_js': self.get_user_files_content(self.userconf['user_js']),
            'version': __version__
        }

    def log(self, message, type='notice'):
        """ Logs a message (eventually, override to do something more clever).
        """
        if self.userconf['verbose']:
            self.logger(message, type)

    def process_macros(self, content, source, context):
        """ Processed all macros.
        """
        classes = []
        for macro in self.macros:
            content, add_classes = macro.process(content, source, context)
            if add_classes:
                classes += add_classes
        return content, classes

    def register_macro(self, *macros):
        """ Registers macro classes passed a method arguments.
        """
        macro_options = {
            'relative': self.userconf['relative'],
            'linenos': self.userconf['linenos'],
            'destination_dir': self.destination_dir
        }
        for m in macros:
            if inspect.isclass(m) and issubclass(m, macro_module.Macro):
                self.macros.append(m(logger=self.logger,
                                     embed=self.userconf['embed'],
                                     options=macro_options))
            else:
                raise TypeError("Couldn't register macro; a macro must inherit"
                                " from macro.Macro")

    def embed_url_data(self, context, html):
        """Find all image and fonts referenced in CSS with an ``url()`` function
        and embed them in base64. Images from the user (i.e. included in its
        source code, *not* in its CSS) are embedded by the macro
        `EmbedImagesMacro`.
        """
        all_urls = re.findall(r'url\([\"\']?(.*?)[\"\']?\)', html,
                              re.DOTALL | re.UNICODE)
        embed_exts = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff2',
                      '.woff')
        embed_urls = (url for url in all_urls if url.endswith(embed_exts))

        css_dirs = (
            [os.path.join(self.theme_dir, 'css')] +
            [css_entry['dirname'] for css_entry in context['user_css']]
        )

        for embed_url in embed_urls:
            embed_url = embed_url.replace('"', '').replace("'", '')

            directory, encoded_url = None, None
            for directory in css_dirs:
                encoded_url = utils.encode_data_from_url(embed_url, directory)
                if encoded_url:
                    break

            if encoded_url:
                html = html.replace(embed_url, encoded_url, 1)
                self.log("Embedded theme file %s from directory %s"
                         % (embed_url, directory))
            else:
                self.log(u"Failed to embed theme file %s" % embed_url)

        return html

    def render(self):
        """ Returns generated html code.
        """
        with codecs.open(self.template_file, encoding=self.userconf['encoding']) as template_src:
            template = jinja2.Template(template_src.read())
        slides = self.fetch_contents(self.userconf['source'])
        context = self.get_template_vars(slides)

        html = template.render(context)

        if self.userconf['embed']:
            html = self.embed_url_data(context, html)

        return html

    def write(self):
        """ Writes generated presentation code into the destination file.
        """
        html = self.render()
        dirname = os.path.dirname(self.userconf['destination_file'])
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        with codecs.open(self.userconf['destination_file'], 'w',
                         encoding='utf_8') as outfile:
            outfile.write(html)
