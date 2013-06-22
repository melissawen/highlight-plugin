# -*- coding: utf-8 -*-
'''
Copyright (C) 2013 Melissa Shihfan Ribeiro Wen

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

from gi.repository import GObject, Gtk, GtkSource, Gedit, Gdk
from os import path
import os
import shutil

class HighlighterPlugin(GObject.Object, Gedit.WindowActivatable):
   __gtype_name__ = "HighlighterPlugin"
   
   window = GObject.property(type=Gedit.Window)
   
   def __init__(self):
      GObject.Object.__init__(self)
      self._colordialog = None
      self._start, self._end = None,None
      self._counter = 0
      self._handler_id = None
      self.view = None
      self._color_dict = dict()
   
   def do_activate(self):
      self._insert_toolbar_icon()
      self._insert_sidebar()
      self._activate_save_tag_to_file()   
 
   def do_deactivate(self):
      self.remove_all_markups(None)
      self.stop_highlighting()
      self._remove_toolbar_icon()
      self._remove_sidebar()

   def _insert_toolbar_icon(self):
      vbox = self.window.get_children()[0]
      toolbar = vbox.get_children()[1]
      self._button = Gtk.ToggleToolButton(Gtk.STOCK_SELECT_COLOR)
      self._button.set_tooltip_text("Use Highlighter")
      toolbar.insert(item=self._button, pos=-1)
      self._button.show()
      self._button.connect('toggled', self.on_highlighter_activate)

   def _remove_toolbar_icon(self):
      vbox = self.window.get_children()[0]
      toolbar = vbox.get_children()[1]
      self._button.hide()
      toolbar.remove(self._button)
 
   #Begin to set side panel options
   def _insert_sidebar(self):
      panel = self.window.get_side_panel()
      icon = Gtk.Image.new_from_stock(Gtk.STOCK_SELECT_COLOR, Gtk.IconSize.MENU)
      self.frame = Gtk.Frame(label="Show/Hide Markups")
      self.frame.set_border_width(5)

      self.bbox = Gtk.VButtonBox()
      self.frame.add(self.bbox)
      self.bbox.set_layout(Gtk.ButtonBoxStyle.START)
      
      button = Gtk.Button('Remove all markups')
      button.connect('clicked', self.remove_all_markups)
      self.bbox.add(button)
      button.show()      
 
      button = Gtk.CheckButton('Show/Hide All')
      button.set_active(True)
      button.connect("toggled", self.show_hide_all)
      self.bbox.add(button)
      button.show()
      self.bbox.show()
      self.frame.show()
      
      panel.add_item(self.frame, 'Show markups', 'Highlighter', icon)
      panel.activate_item(self.frame)
   
   def create_color_check_button(self,color):
      gdkcolor = Gdk.color_parse(color)
      button = Gtk.CheckButton(color)
      button.set_active(True)
      button.connect("toggled", self.show_hide_this_color)
      Gtk.Widget.modify_fg(button, Gtk.StateType.NORMAL, gdkcolor)
      self.bbox.add(button)
      button.show()
   
   def find_button(self, color):
      self.bbox.foreach(self.remove_color_check_button, color)
      
   def remove_color_check_button(self, child, color):
      if child.get_label() == color:
         self.bbox.remove(child)

   def _remove_sidebar(self):
      panel = self.window.get_side_panel()
      panel.remove_item(self.frame)
    
   def show_hide_all(self, togglebutton):
      views = self.window.get_views()
      for v in views:
         text = v.get_buffer()
         tag_table = text.get_tag_table()
         if togglebutton.get_active():
            tag_table.foreach(self.show_all_colors, None)
         else:
            tag_table.foreach(self.hide_all_colors, None)
   
   def show_all_colors(self, tag, data):
      name = tag.get_property('name')
      if name:
         color = name.split('-')[0]
         if color[0] == '#':
            tag.set_property('background',color)

   def hide_all_colors(self, tag, data):
      name = tag.get_property('name')
      if name:
         if name[0] == '#':
            tag.set_property('background','#ffffff')

   def show_hide_this_color(self, togglebutton):
      views = self.window.get_views()
      for v in views:
         text = v.get_buffer()
         tag_table = text.get_tag_table()
         if togglebutton.get_active():
            tag_table.foreach(self.show_this_color, togglebutton.get_label())
         else:
            tag_table.foreach(self.hide_this_color, togglebutton.get_label())
   
   def show_this_color(self, tag, color):
      name = tag.get_property('name')
      if name:
         tag_color = name.split('-')[0]
         if tag_color == color :
            tag.set_property('background',color)

   def hide_this_color(self, tag, color):
      name = tag.get_property('name')
      if name:
         tag_color = name.split('-')[0]
         if tag_color == color :
            tag.set_property('background','#ffffff')

   #End to set side panel options

   #Begin to define highlighter actions 
   def on_highlighter_activate(self, toolbutton):
      if toolbutton.get_active():
         if not self._colordialog:
            self._colordialog = Gtk.ColorChooserDialog("Pick Color", self.window)
            self._colordialog.connect_after('response', self.on_colordialog_response)
         self._colordialog.present()
      else:
         self.stop_highlighting()

   def stop_highlighting(self):
      if self.view:
         text = self.view.get_buffer()
         if self._handler_id:
            text.disconnect(self._handler_id)
            self._handler_id = None
            self.view = None

   def on_colordialog_response(self, dialog, response):
      if response == Gtk.ResponseType.OK:
         rgba = Gdk.RGBA()
         dialog.get_rgba(rgba)
         color = '#'+("%02x%02x%02x" % (self.scale_color_component(rgba.red), \
                                              self.scale_color_component(rgba.green), \
                                              self.scale_color_component(rgba.blue)))
         self.use_highlighter(color)
      self._colordialog.destroy()
      self._colordialog = None
      
   def scale_color_component(self, component):
      return min(max(int(round(component * 255.)), 0), 255)

   def use_highlighter(self, color):
      tab = self.window.get_active_tab()
      self.view = tab.get_view()
      if not self.view or not self.view.get_editable():
         return
         
      text = self.view.get_buffer()
      if not text:
          return
          
      self._handler_id = text.connect('mark-set', self.on_textbuffer_markset_event, color)

   def on_textbuffer_markset_event(self, textbuffer, iter, textmark, color):
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
         tag_name = self.add_tag(color, textbuffer)
         self.add_tag_to_file(tag_name)
         self._counter = self._counter+1
         self._start, self._end = None,None
         
   def add_tag(self, color, textbuffer):
      self.sum_n_to_color_dict(color)
      tag_name = color+'-'+str(self._counter)
      if not textbuffer.get_tag_table().lookup(tag_name):
         tag = textbuffer.create_tag(tag_name, background= color)
         textbuffer.apply_tag_by_name(tag_name, self._start, self._end)
      return tag_name
   
   def sum_n_to_color_dict(self, color):
      if color in self._color_dict:
         self._color_dict[color] = self._color_dict[color] + 1
      else:
         self._color_dict[color] = 1
         self.create_color_check_button(color)

   def sub_n_to_color_dict(self, color):
      if self._color_dict[color]:
         if self._color_dict[color] == 1:
            del self._color_dict[color]
            self.find_button(color)
         else:
            self._color_dict[color] = self._color_dict[color] - 1

   def has_highlighted_tag(self, textbuffer, list_tag):
      i=0
      n_tags = len(list_tag)
      while (n_tags > i and list_tag[i*(-1)].get_property('name') == None):
         i = i+1
      if n_tags > i:
         self.remove_markup(textbuffer, list_tag, i)
         return True
      return False

   def remove_markup(self, textbuffer, list_tag, it_tag):
      tag_table = textbuffer.get_tag_table()
      tag = tag_table.lookup(list_tag[it_tag*(-1)].get_property('name'))
      tag_table.remove(tag)
      self.remove_tag_from_file(tag.get_property('name'))          
      self.sub_n_to_color_dict(tag.get_property('name').split('-')[0])

   def remove_all_markups(self, button):
      views = self.window.get_views()
      for v in views:
         text = v.get_buffer()
         tag_table = text.get_tag_table()
         for color in self._color_dict:
            i = self._counter
            while i > 0:
               tag = tag_table.lookup(color+'-'+str(i-1))
               i=i-1
               if tag:
                  tag_table.remove(tag)
      for color in self._color_dict:
         self.find_button(color)
      self._color_dict = dict()
   #End
   
   def _activate_save_tag_to_file(self):
      self.window.connect('tab-added', self.on_tab_added_event) 
      
   def _get_file_path(self, doc):
      fname="."+doc.get_property('shortname')
      lfile = doc.get_location()
      directory = lfile.get_parent().get_path()
      return str(directory+'/'+fname+'.mkf')   

   def open_tags_file(self, mode):
      tab = self.window.get_active_tab()
      doc = tab.get_document()
      if (doc.is_untitled()):
         fname= doc.get_property('shortname')
         directory = path.dirname(path.realpath(__file__))
         self.file = open(directory+'/.tags-files/'+fname+'.mkf', mode)
      else:
         fpath = self._get_file_path(doc)
         self.file = open(fpath, mode)
     
   def add_tag_to_file(self, tag_name):
      self.open_tags_file('a+')
      tag_info = str(self._start.get_offset()) + ' ' 
      tag_info = tag_info + str(self._end.get_offset())
      self.file.write(tag_name+' '+tag_info+'\n')
      self.file.close()
   
   def remove_tag_from_file(self, tag_name):
      self.open_tags_file('r')
      lines = self.file.readlines()
      self.file.close()
      self.open_tags_file('w')
      for line in lines:
         aux = line.split(' ')
         if (aux[0] != tag_name):
            self.file.write(line)
      self.file.close()
   
   def on_tab_added_event(self, win, tab):
      doc = tab.get_document()
      if doc:
         doc.connect('loaded', self.on_load_file_event, tab)
         doc.connect('save', self.on_save_file_event)
    
   def on_dialog_yes_no(self, tab):
      dialog = Gtk.Dialog("Do you want to load markups?", None, 0, (Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES))
      dialog.connect_after('response', self.on_dialog_response, tab)
      dialog.present()
      
   def on_dialog_response(self, dialog, response, tab):
      if response == Gtk.ResponseType.YES:
         self.load_tags_from_file(tab)
      elif response == Gtk.ResponseType.NO:
         doc = tab.get_document()
         fpath = self._get_file_path(doc)
         os.remove(fpath)         
      dialog.destroy()
      
   def on_load_file_event(self, doc, error, tab):
      if not error:
         fpath = self._get_file_path(doc)
         try:
            with open(fpath) as self.file:
               self.on_dialog_yes_no(tab)
         except IOError:
            pass

   def load_tags_from_file(self, tab):
      doc = tab.get_document()
      fpath = self._get_file_path(doc)
      
      self.file = open(fpath,'r')
      
      textbuffer = tab.get_view().get_buffer()
      for line in self.file:
         tag_info = line.split(' ')
         color = tag_info[0].split('-')[0]
         if textbuffer:
            self._start = textbuffer.get_iter_at_offset(int(tag_info[1]))
            self._end = textbuffer.get_iter_at_offset(int(tag_info[2]))
            self._counter = int(tag_info[0].split('-')[1])
            self.add_tag(color, textbuffer)
            self._start, self._end = None,None
      self._counter = self._counter+1
      self.file.close()
   
   def on_save_file_event(self, doc, loc, enc, flag, arg, arg2):
      fpath = None
      if (doc.is_untitled()):
         fname= doc.get_property('shortname')
         directory = path.dirname(path.realpath(__file__))
         fpath = directory+'/.tags-files/'+fname+'.mkf'
      doc.connect('saved', self.on_saved_file_event, fpath)         
      
   def on_saved_file_event(self, doc, error, src):
     if not error:
        dialog = Gtk.Dialog("Do you want to save markups?", None, 0, (Gtk.STOCK_NO, Gtk.ResponseType.NO, Gtk.STOCK_YES, Gtk.ResponseType.YES))
        dialog.connect_after('response', self.on_save_tags_response, doc, src)
        dialog.present()
        
   def on_save_tags_response(self, dialog, response, doc, src):
      if response == Gtk.ResponseType.YES:
         if src:
            dst= self._get_file_path(doc)
            shutil.move(src, dst)
      elif response == Gtk.ResponseType.NO:
         if src:
            os.remove(src)
         else:
            fpath = self._get_file_path(doc)
            try:
               with open(fpath) as self.file:
                  os.remove(fpath)
            except IOError:
               pass         
      dialog.destroy()
         
