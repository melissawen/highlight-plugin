Highlighter Plugin for Gedit
============================

This plugin creates visual markups in files edited by Gedit. This seems like when we use a highlighter in our notepad to mark parts of text that you want remind later or need extra attention. It is developed using Python.

INSTALL
=======

To make this plugin available in your Gedit, you can copy the files highlighter.plugin and highlighter.py to .local/share/gedit/plugins in your home directory or directly in Gedit plugin's directory.

HOW TO USE
==========

On Gedit, preferences > plugins, check the button of Highlighter plugin to turn it on.

![activate](https://github.com/melissawen/highlight-plugin/raw/master/img/pluginactivate.png)

A "select color" icon will appear on your toolbar. Click on this icon, select a color to be used and so, select part of text that you wanna highlight. The highlighter works only inside the view that was activated when highlighter icon was clicked.

![color dialog](https://github.com/melissawen/highlight-plugin/raw/master/img/colordialog.png)

You can remove a markup selecting the text (or part of this) that was marked by highlighter or clicking on "Remove all markups" button on side panel.

![highlighter side panel](https://github.com/melissawen/highlight-plugin/raw/master/img/highlightersidepanel.png)

You can setup visualization options of markups - show/hide one or more colors. To do it, activate side panel of gedit, click on highlighter tab (identified by "select color" icon) and mark or unmark the check button related to color.

![hide color option](https://github.com/melissawen/highlight-plugin/raw/master/img/hidecoloroption.png)

When you turn off the plugin , all markups will be removed.

Load/Store markups

When you activate this plugin, you will be asked to load or not markups stored on file.
If you say yes, markups of the last session will be displayed. If you say no, markups file will be deleted.
If you want to store current markups on file, you need to press "save to file" button. If you don't do it before closing your document, markups will be discarted.

TO DO
=====

When "Search" tool (Ctrl+F) is in use, plugin have to stop.
