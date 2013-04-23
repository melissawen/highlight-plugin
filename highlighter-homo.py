from gi.repository import GObject, Gtk, GtkSource, Gedit, Gdk
import gettext
from gpdefs import *

try:
    gettext.bindtextdomain(GETTEXT_PACKAGE, GP_LOCALEDIR)
    _ = lambda s: gettext.dgettext(GETTEXT_PACKAGE, s);
except:
    _ = lambda s: s


class HighlighterPlugin(GObject.Object, Gedit.WindowActivatable):
   __gtype_name__ = "HighlighterPlugin"
   
   window = GObject.property(type=Gedit.Window)
   
   def __init__(self):
      GObject.Object.__init__(self)
      self._colordialog = None
      self.view = None
      self._start, self._end = 0,0
      self._counter = 0
      self._color = None
      self._handler_id = None
   
   def do_activate(self):
      self._insert_toolbar_icon()
      self._insert_sidebar() 

   def do_deactivate(self):
      self._remove_toolbar_icon()

   def _insert_toolbar_icon(self):
      vbox = self.window.get_children()[0]
      toolbar = vbox.get_children()[1]
      self._button = Gtk.ToggleToolButton(Gtk.STOCK_SELECT_COLOR)
      self._button.set_tooltip_text(_("Use highlighter"))
      toolbar.insert(item=self._button, pos=-1)
      self._button.show()
      self._button.connect('toggled', self.on_highlighter_activate)

   def _remove_toolbar_icon(self):
      vbox = self.window.get_children()[0]
      toolbar = vbox.get_children()[1]
      self._button.hide()
      toolbar.remove(self._button)
      self._remove_sidebar()      
   
   def _insert_sidebar(self):
      panel = self.window.get_side_panel()
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_SELECT_COLOR, Gtk.IconSize.MENU)
      self._show_highlight = Gtk.CheckButton('Show Highlights')
      self._show_highlight.set_active(True)
      self._show_highlight.connect("toggled", self.highlight_state)
      panel.add_item(self._show_highlight, 'Show Highlight', _('Highlighter'), icon)
      panel.activate_item(self._show_highlight)

   def _remove_sidebar(self):
      panel = self.window.get_side_panel()
      panel.remove_item(self._show_highlight)
   
   def highlight_state(self, togglebutton):
      text = self.view.get_buffer()
      tag_table = text.get_tag_table()
      if togglebutton.get_active():
         tag_table.foreach(self.show_colors, None)
      else:
         tag_table.foreach(self.hide_colors, None)
   
   def hide_colors(self, tag, data):
      name = tag.get_property('name')
      if name:
         if name[0] == '#':
            tag.set_property('background','#ffffff')

   def show_colors(self, tag, data):
      name = tag.get_property('name')
      if name:
         color = name.split('-')[0]
         if color[0] == '#':
            tag.set_property('background',color)
      
   def on_highlighter_activate(self, toolbutton):
      if not self._handler_id:
         if not self._colordialog:
            self._colordialog = Gtk.ColorChooserDialog(_("Pick Color"), self.window)
            self._colordialog.connect_after('response', self.on_colordialog_response)
         self._colordialog.present()
      else:
         self.stop_highlight()

   def stop_highlight(self):
      self.view = self.window.get_active_view()
      text = self.view.get_buffer()
      text.disconnect(self._handler_id)
      self._handler_id = None

   def on_colordialog_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
           rgba = Gdk.RGBA()
           dialog.get_rgba(rgba)
           self._color = '#'+("%02x%02x%02x" % (self.scale_color_component(rgba.red), \
                                                self.scale_color_component(rgba.green), \
                                                self.scale_color_component(rgba.blue)))
           self.use_highlighter()
        self._colordialog.destroy()
        self._colordialog = None

   def scale_color_component(self, component):
        return min(max(int(round(component * 255.)), 0), 255)

   def use_highlighter(self):
      self.view = self.window.get_active_view()
      if not self.view or not self.view.get_editable():
         return

      text = self.view.get_buffer()

      if not text:
          return
      self._handler_id = text.connect('mark-set', self.on_textbuffer_markset_event)

   def on_textbuffer_markset_event(self, textbuffer, iter, textmark):
      if textmark.get_name() != 'selection_bound' and textmark.get_name() != 'insert':
         return

      #Keep lastest position of start and end
      if textbuffer.get_selection_bounds():
         self._start, self._end = textbuffer.get_selection_bounds()
         return
      
      #Only act after selection was finished
      if textbuffer.get_has_selection() and not textbuffer.get_selection_bounds():
         list_tag = self._start.get_tags()
         if list_tag:
            if self.has_highlighted_tag(textbuffer, list_tag):
               return               
         
         tag_name = self._color+'-'+str(self._counter)
         if textbuffer.get_tag_table().lookup(tag_name) == None:
            tag = textbuffer.create_tag(tag_name, background= self._color)
            textbuffer.apply_tag_by_name(tag_name, self._start, self._end)
            self._counter = self._counter+1
            self._start, self._end = 0,0

   def has_highlighted_tag(self, textbuffer, list_tag):
      i=0
      n_tags = len(list_tag)
      while (n_tags > i and list_tag[i*(-1)].get_property('name') == None):
         i = i+1
      if n_tags > i:
         self.remove_highlight(textbuffer, list_tag, i)
         return True
      return False

   def remove_highlight(self, textbuffer, list_tag, it_tag):
      tag_table = textbuffer.get_tag_table()
      tag = tag_table.lookup(list_tag[it_tag*(-1)].get_property('name'))
      tag_table.remove(tag)
