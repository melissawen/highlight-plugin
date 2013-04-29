Highlighter Plugin for Gedit
============================

This plugin creates visual markups in files that are editing by Gedit. This seems like when we use a highlighter in our notepad to highlight parts of text that need extra attention or to be remind later.
It is being developed using python. 

INSTALL
=======

You can make this plugin available in your Gedit copying files highlighter.plugin and highlighter.py to .local/share/gedit/plugins in your home directory or directly in Gedit plugin's directory.

HOW TO USE
==========

On Gedit, preferences > plugins, check the button of Highlighter plugin to turn it on.

A select color icon will appear on your toolbar. Click on this icon, select a color to use and so select part of text that you wanna highlight. Highlighter turns on only inside the view that was activated when highlighter icon was clicked.

You can remove a markup selecting the text (or part of this) that was marked by highlighter.

You can setup visualization options of markups - show/hide one or more colors. To do it, activate side panel of gedit, click on highlighter tab (identified by Select Color icon) and mark or unmark the check button related to color.

When you turn off the plugin , all markups are removed.

TO DO
=====

Save tags in a file to load them next time.
- Open a dialog to ask if user want to load old tags
- Update file with new tags
- Update Tag Table using the file.

Stop plugin when "Search" tool (Ctrl+F) is in use.
