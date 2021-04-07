import os
import subprocess
import shutil
import json
import sublime
import sublime_plugin


def plugin_loaded():
  checkingFoldersWithTemplates()
  createSideBar()


def getOnlyTemplateNames(item_list):
  clear_list_folders = prettyFolderList(item_list)
  return list(filter(lambda f: os.path.isdir(getTemplatesFolderPath() + '/' + f), clear_list_folders))


# Remove folders you don't need from the list. Example: ".DS_Store"
def prettyFolderList(folder_list):
  return list(filter(lambda f: f != '.DS_Store', folder_list))



def Window(window=None):
    return window if window else sublime.active_window()


def getTemplatesFolderPath():
  return sublime.packages_path() + '/User/EasyTemplates'


def getTemplateNameList():
  allFolderList = os.listdir(getTemplatesFolderPath())
  templateNameList = list(filter(
    lambda name: name[0] != '.',
    allFolderList
  ))
  return templateNameList


def checkingFoldersWithTemplates():
  isTemplatesFolderExist = os.path.exists(getTemplatesFolderPath())

  if not isTemplatesFolderExist:
    shutil.copytree(
      sublime.packages_path() + '/EasyTemplates/Examples',
      sublime.packages_path() + '/User/EasyTemplates'
    )


def createSideBar():
  template_names = os.listdir(getTemplatesFolderPath())
  template_names = getOnlyTemplateNames(template_names)
  side_bar_items = list(map(createSideBarItem, template_names))

  side_bar_full = [
    {
      "id": "easyTemplates",
      "caption": "Create From Template",
      "children": side_bar_items
    }
  ]

  with open(getTemplatesFolderPath() + '/Side Bar.sublime-menu', 'w') as fp:
      json.dump(side_bar_full, fp,  indent=4)


def createSideBarItem(item):
  return {
    'id': item,
    'caption': item,
    'command': 'es_tmpl_new_file_menu',
    'args': {
      'template_name': item,
      'paths': []
    }
  }


def createTemplate(name):
  isTemplateExist = os.path.exists(getTemplatesFolderPath() + '/' + name)
  if isTemplateExist:
    sublime.error_message('A template named ' + name + ' already exists')
  else:
    os.mkdir(getTemplatesFolderPath() + '/' + name)
    createSideBar()
    openTemplateInNewWindow(name)


def removeTemplate(nameTemplate):
  response = sublime.ok_cancel_dialog('remove: ' + nameTemplate)
  if response:
    shutil.rmtree(getTemplatesFolderPath() + '/' + nameTemplate)
    createSideBar()


def openTemplateInNewWindow(name):
  executable_path = sublime.executable_path()

  if sublime.platform() == "osx":
    app_path = executable_path[: executable_path.rfind(".app/") + 5]
    executable_path = app_path + "Contents/SharedSupport/bin/subl"

  folder_path = getTemplatesFolderPath() + '/' + name
  subprocess.Popen([executable_path, folder_path])


def callQuickPanel(self, func):
  templateNameList = getTemplateNameList()
  templateNameList = getOnlyTemplateNames(templateNameList)
  self.view.window().show_quick_panel(
    templateNameList,
    lambda id: func(templateNameList[id]) if id != -1 else ''
  )


def enterFileName(template_name, name, path):
  Window().show_input_panel(
      "{name}:",
      name,
      lambda name: createFilesByTemplate(template_name, name, path),
      None,
      None,
  )


def createFilesByTemplate(template_name, user_entered_name, path):
  template_folder = getTemplatesFolderPath() + '/' + template_name
  template_files = os.listdir(template_folder)
  template_files = prettyFolderList(template_files)

  if len(template_files) == 0:
    sublime.error_message('Template is empty')
    return

  for item in template_files:
    item_path = template_folder + '/' + item

    if os.path.isfile(item_path):
      createNewFile(item_path, path, user_entered_name)

    if os.path.isdir(item_path):
      folder_name = item
      index_folder_name_tag = item.lower().find('{name}')
      if index_folder_name_tag >= 0:
        folder_name = folder_name[:index_folder_name_tag] + user_entered_name + folder_name[index_folder_name_tag+6:]

      os.mkdir(path + '/' + folder_name)
      createFilesByTemplate(template_name + '/' + item, user_entered_name, path + '/' + folder_name)


def createNewFile(template_file_path, new_file_location, user_entered_name):
  file_name = os.path.basename(template_file_path)
  is_open_file = False
  
  index_open_tag = file_name.lower().find('{open}')
  if index_open_tag >= 0:
      is_open_file = True
      file_name = file_name[:index_open_tag] + '' + file_name[index_open_tag+6:]

  index_name_tag = file_name.lower().find('{name}')
  if index_name_tag >= 0:
    file_name = file_name[:index_name_tag] + user_entered_name + file_name[index_name_tag+6:]

  tmpl = open(template_file_path)
  new_file_content = tmpl.read()
  tmpl.close()

  while True:
    index_content_tag = new_file_content.lower().find('{name}')
    if index_content_tag == -1:
      break
    else:
      new_file_content = new_file_content[:index_content_tag] + user_entered_name + new_file_content[index_content_tag+6:]

  new_file_path = new_file_location + '/' + file_name
  new_file = open(new_file_path, 'w')
  new_file.write(new_file_content)
  new_file.close()

  if is_open_file:
    Window().open_file(new_file_path)


class EsTmplCreateTemplate(sublime_plugin.TextCommand):
  def run(self, edit, name = ''):
    Window().show_input_panel(
        "Template name:",
        name,
        createTemplate,
        None,
        None,
    )


class EsTmplEditTemplate(sublime_plugin.TextCommand):
  def run(self, edit):
    callQuickPanel(self, openTemplateInNewWindow)


class EsTmplRemoveTemplate(sublime_plugin.TextCommand):
  def run(self, edit):
    callQuickPanel(self, removeTemplate)


class EsTmplNewFile(sublime_plugin.TextCommand):
  def run(self, edit, type_folder):
    name = ''
    path_for_new_files = getPathForNewFiles(self, type_folder)
    
    if not path_for_new_files:
      sublime.error_message('Open project')
      return

    templateNameList = getTemplateNameList()
    templateNameList = getOnlyTemplateNames(templateNameList)
    self.view.window().show_quick_panel(
      templateNameList,
      lambda id: enterFileName(templateNameList[id], name, path_for_new_files) if id != -1 else ''
    )


class EsTmplNewFileMenu(sublime_plugin.WindowCommand):
  def run(self, template_name, paths=[]):
    path = paths[0]

    if os.path.isfile(path):
      path = os.path.dirname(path)
    
    name = ''
    enterFileName(template_name, name, path)
    

def getPathForNewFiles(self, type_folder):
  file_path = self.view.file_name()
  folders = Window().folders()

  if len(folders) == 0:
    return False

  if type_folder == 'current' and file_path:
    return os.path.dirname(file_path)

  if len(folders) > 1 and file_path:
    for pf in folders:
        if pf.startswith(file_path):
          return pf
  else:
    return folders[0]

