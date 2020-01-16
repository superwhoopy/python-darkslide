# -*- coding: utf-8 -*-
import re

SUPPORTED_FORMATS = {
    'markdown': {'.mdown', '.markdown', '.markdn', '.md', '.mdn', '.mdwn'},
    'restructuredtext': {'.rst', '.rest'},
    'textile': {'.textile'},
}


class Parser(object):
    """This class generates the HTML code depending on which syntax is used in
       the souce document.

       The Parser currently supports both Markdown and restructuredText
       syntaxes.
    """
    RST_REPLACEMENTS = [
        (r'<div.*?>', r'', re.UNICODE),
        (r'</div>', r'', re.UNICODE),
        (r'<p class="system-message-\w+">.*?</p>', r'', re.UNICODE),
        (r'Document or section may not begin with a transition\.',
            r'', re.UNICODE),
        (r'<h(\d+?).*?>', r'<h\1>', re.DOTALL | re.UNICODE),
        (r'<hr.*?>\n', r'<hr />\n', re.DOTALL | re.UNICODE),
        (r'<a class=\"toc-backref\" href=\"#id[0-9]+\">(.+)<\/a>', r'\1', re.UNICODE),
    ]

    # default_md_extensions = [
    #     'extra', # fenced_code, tables, ...
    #     'smarty', # dashes, quotes and ellipsis
    #     'markdown_checklist.extension',
    # ]

    def __init__(self, extension, encoding='utf8', md_extensions=''):
        """Configures this parser.
        """
        self.encoding = encoding
        self.format = None

        for supp_format, supp_extensions in SUPPORTED_FORMATS.items():
            if extension in supp_extensions:
                self.format = supp_format

        if not self.format:
            raise NotImplementedError(u"Unsupported format %s" % extension)

        self.md_extensions = [
            value.strip() for value in md_extensions.split(',') if value.strip()
        ]

    def parse(self, text):
        """Parses and renders a text as HTML regarding current format.
        """
        if self.format == 'markdown':
            try:
                import markdown
            except ImportError:
                raise RuntimeError(u"Looks like markdown is not installed")

            if text.startswith(u'\ufeff'):  # check for unicode BOM
                text = text[1:]

            return markdown.markdown(text, extensions=self.md_extensions)
        elif self.format == 'restructuredtext':
            try:
                from .rst import html_body
            except ImportError:
                raise RuntimeError(u"Looks like docutils are not installed")

            html = html_body(text, input_encoding=self.encoding)

            # RST generates pretty much markup to be removed in our case
            for (pattern, replacement, mode) in self.RST_REPLACEMENTS:
                html = re.sub(re.compile(pattern, mode), replacement, html, 0)

            return html.strip()
        elif self.format == 'textile':
            try:
                import textile
            except ImportError:
                raise RuntimeError(u"Looks like textile is not installed")

            text = text.replace('\n---\n', '\n<hr />\n')

            return textile.textile(text)
        else:
            raise NotImplementedError(u"Unsupported format %s, cannot parse"
                                      % self.format)
