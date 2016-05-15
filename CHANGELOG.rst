=========
Changelog
=========

Darkslide v2.3.3 (2016-05-15)
=============================

* Fixed height of QR svg elements.

Darkslide v2.3.2 (2016-04-12)
=============================

* Fixed underline occlusion shadows in the footer (for links).
* Fixed missing `presenter_notes` class not being set when notes mode was on.

Darkslide v2.3.1 (2016-02-08)
=============================

* MathJax is loaded on HTTPS.

Darkslide v2.3.0 (2016-02-07)
=============================

* The Darkslide version is shown in the help sidebar.

Darkslide v2.2.1 (2015-10-06)
=============================

* Fixed config file parsing for math_output.

Darkslide v2.2.0 (2015-10-06)
=============================

* Now macro failures abort rendering. Previously they would just log a message that you'd probably woulnd't notice.
* Fixed broken handling where you have css/js in the cfg file.
* Allowed setting the math_output option in the cfg file.
* Fixed encoding issues in the QR macro.
* Added back the old theme with completely black background (as "void").
* Tweak the faux underlines to look better.

Darkslide v2.1.0 (2015-10-05)
=============================

* Added demo links.
* Fixed options handling. Options from command line now will actually work if a cfg file is used.
* Corrected relative paths handling:

  - paths in sources are now relative to the cfg file (previously they were relative to whatever was cwd).
  - relative option now correctly works when destination file is not in cwd.
* Fixed layout of slides with many headering (no more paddings for headings, all root elements are spread out evenly
  anyway).
* Fixed bad styling of ToC (and probably other things in the sidebar).
* Fixed ToC links (contributed by Cyrille Pontvieux).

Darkslide v2.0.4 (2015-09-09)
=============================

* Improved handling for filenames that have non-ascii characters in them.

Darkslide v2.0.3 (2015-09-08)
=============================

* Fixed handling for filenames that have non-ascii characters in them.

Darkslide v2.0.2 (2015-07-20)
=============================

- Added color classes in the abyss theme.
- Fixed link underlines in the presenter notes.

Darkslide v2.0.1 (2015-07-19)
=============================

* Don't use Monaco in the ``base.css`` - it's way bigger than Consolas and the other fonts. And Consolas is nice enough.

Darkslide v2.0.0 (2015-07-17)
=============================

- Fix display of RST image target links.
- Add cmd line option to print version.
- Rewrote the default theme (solarized colors)
- Overhauled the abyss theme, improved the coloring.
- Removed all the other themes (they are ugly and broken anyway) (**backwards incompatible**).
- Fixes for print css.
- Added support for two new css files: ``base.css`` and ``theme.css``. This
  makes reusing styles acros themes and kinds of display (print/screen) more easy.
- Expanded mode is now activated by default.
- Changed macros to use compiled regexes.
- Added a footnote macro.
- Changed QR macro to use ``qrcode`` library. Now it's rendered to SVG. The size is removed (**backwards incompatible**).

Darkslide v1.2.2 (2015-05-22)
=============================

- Fix the blank page issue when generating pdfs (via Chrome's pdf printer).

Darkslide v1.2.1 (2015-05-21)
=============================

- Couple minor improvements to Abyss theme.

Darkslide v1.2.0 (2015-05-19)
=============================

- Modifier keys flag was not cleared propertly (kb shortcuts were not working anymore after
  alt-tab etc); now it's cleared on visibility changes and focus loss.
- Changed expanded mode to automatically hide the context.
- Fixed window resize flickering (for every resize event the expaded flag was toggled).
- Disabled context hiding in presenter view.
- Other small styling improvements.
- Added "abyss" theme.

Landslide v1.1.3
================

-  Identify each slide by a numbered class (#171) (dkg)
-  Fix theme image embedding regex to grab all images (#170)
-  Fix blockquote font size for rst (#161)
-  Fix display of RST image target links (#87)
-  Fix relative path generation (#147)
-  Add command line option for print version (#135)
-  Add use of '---' as a slide separator to textile files (#163)
-  README improvements (#88 and #101)
-  Improve image path regex and replacement (#177)

Landslide v1.1.2
================

-  Add support for Python 3
-  Allow support for copy\_theme argument in CFG files (#139) (syscomet)
-  Improve MathJax rendering for Markdown files
-  Support math output (#144) (davidedelvento)
-  Allow presenter notes in slides with no heading in RST files (#141)
   (regebro)
-  And more...

Landslide v1.1.1
================

Fixes
-----

-  Don't accidentally require watchdog (#134)

Landslide v1.1.0
================

Major Enhancements
------------------

-  Add CHANGELOG
-  Add "ribbon" theme from "shower" presentation tool (#129) (durden)
-  Add ``-w`` flag for watching/auto-regenerating slideshow (#71, #120)
   (jondkoon)

Minor Enhancements
------------------

-  Supress ReST rendering errors
-  CSS pre enhancements (#91) (roktas)
-  Add an example using presenter notes (#106) (netantho)
-  Run macros on headers also, to embed images (#74) (godfat)
-  Allow PHP code snippets to not require <?php (#127) (akrabat)
-  Allow for line numbers and emphasis with reStructuredText (#97)
   (copelco)
-  Add an option to strip presenter notes from output (#107) (aaugustin)

Fixes
-----

-  Firefox offset bug on next slide (#73)
-  Fix base64 encoding issue (#109) (ackdesha)
-  Fix to embed images defined in CSS (#126) (akrabat)
-  Minor documentation fixes (#119, #131) (durden, spin6lock)
-  Use configured encoding when reading all embedded files (#125)
   (iguananaut)
-  Allow pygments lexer names that include special characters (#123)
   (shreyankg)
