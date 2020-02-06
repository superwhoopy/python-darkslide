#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser, SUPPRESS

from . import __version__
from . import generator, conf


def _parse_options():
    """Parses landslide's command line options"""

    parser = ArgumentParser(
        description="Generates a HTML5 slideshow from Markdown or "
                    "other formats.")

    parser.add_argument(
        "source",
        help="Source file to process"
    )

    parser.add_argument(
        "--version",
        action='version',
        version="%(prog) " + __version__)

    parser.add_argument(
        "-c", "--copy-theme",
        action="store_true",
        dest="copy_theme",
        help="Copy theme directory into current presentation source directory.",
        default=SUPPRESS)

    parser.add_argument(
        "-b", "--debug",
        action="store_true",
        dest="debug",
        help="Will display any exception trace to stdout.",
        default=False)

    parser.add_argument(
        "-d", "--destination",
        dest="destination_file",
        help="The path to the to the destination html file. Default: presentation.html.",
        metavar="FILE",
        default=SUPPRESS)

    parser.add_argument(
        "-e", "--encoding",
        dest="encoding",
        help="The encoding of your files. Default: utf8.",
        metavar="ENCODING",
        default=SUPPRESS)

    parser.add_argument(
        "-i", "--embed",
        action="store_true",
        dest="embed",
        help="Embed stylesheet and javascript contents, base64-encoded "
             "images and objects in presentation to make a "
             "standalone document.",
        default=SUPPRESS)

    parser.add_argument(
        "-l", "--linenos",
        choices=conf.UserConfig.VALID_LINENOS,
        dest="linenos",
        help="How to output linenos in source code. Three options available: "
             "no (no line numbers); "
             "inline (inside <pre> tag); "
             "table (lines numbers in another cell, copy-paste friendly).",
        default=SUPPRESS,
    )

    parser.add_argument(
        "-m", "--max-toc-level",
        type=int,
        dest="maxtoclevel",
        help="Limits the TOC level generation to a specific level.",
        default=SUPPRESS)

    parser.add_argument(
        "-o", "--direct-output",
        action="store_true",
        dest="direct",
        help="Prints the generated HTML code to stdout.",
        default=SUPPRESS)

    parser.add_argument(
        "-P", "--no-presenter-notes",
        action="store_false",
        dest="presenter_notes",
        help="Don't include presenter notes in the output.",
        default=SUPPRESS)

    parser.add_argument(
        "-q", "--quiet",
        action="store_false",
        dest="verbose",
        help="Won't write anything to stdout (silent mode).",
        default=SUPPRESS)

    parser.add_argument(
        "-r", "--relative",
        action="store_true",
        dest="relative",
        help="Make your presentation asset links relative to current working dir; "
             "This may be useful if you intend to publish your html "
             "presentation online.",
        default=False,
    )

    parser.add_argument(
        "--no-rcfile",
        help="TODO",
        default=False,
    )

    parser.add_argument(
        "-t", "--theme",
        dest="theme",
        help="A theme name, or path to a landlside theme directory",
        default=SUPPRESS)

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        help="Write informational messages to stdout (enabled by default).",
        default=True)

    parser.add_argument(
        "-x", "--extensions",
        dest="extensions",
        help="Comma-separated list of extensions for Markdown.",
        default=SUPPRESS,
    )

    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        dest="watch",
        help="Watch source directory for changes and regenerate slides.",
        default=SUPPRESS
    )

    return parser.parse_args()


def log(message, type):
    """Log notices to stdout and errors to stderr"""

    (sys.stdout if type == 'notice' else sys.stderr).write(message + "\n")


def run(options):
    """Runs the Generator using parsed options."""

    options.logger = log

    opts = options.__dict__
    generator.Generator(**opts).execute()


def main():
    """Main program entry point"""

    options = _parse_options()

    if (options.debug):
        run(options)
    else:
        try:
            run(options)
        except Exception as e:
            sys.stderr.write("Error: %s\n" % e)
            sys.exit(1)
