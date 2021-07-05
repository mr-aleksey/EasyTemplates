import re


def preparationEnteredName (name):
  name_params = {
    'separator': ''
  }

  if name.find(' ') != -1:
    name_params['separator'] = ' '
    name_params['words'] = name.split(' ')

  elif name.find('-') != -1:
    name_params['separator'] = '-'
    name_params['words'] = name.split('-')

  elif name.find('_') != -1:
    name_params['separator'] = '_'
    name_params['words'] = name.split('_')

  elif re.search(r'[A-Z]', name):
    is_first_symbol_lower = name[0].islower()
    format_name = name[0].upper() + name[1::]
    name_params['words'] = re.findall(r'[A-Z][a-z0-9]+', format_name)

    if is_first_symbol_lower:
      name_params['words'][0] = name_params['words'][0].lower()

  else:
    name_params['words'] = [name]

  return name_params


def transformNameStyle (name_params, template):
  word_list = []
  separator = name_params['separator']
  type_template = re.findall(r':(.{0,3})}', template)

  if len(type_template) == 0:
    return separator.join(name_params['words'])

  if len(type_template[0]) == 2:
    separator = ''

  if len(type_template[0]) == 3:
    separator = type_template[0][1] 

  for (index, word) in enumerate(name_params['words']):
    if index == 0 and type_template[0][0].islower():
      word_list.append(word.lower())
    elif index == 0 and (not type_template[0][0].islower()):
      word_list.append(word.capitalize())
    elif index != 0 and type_template[0][-1].islower():
      word_list.append(word.lower())
    elif index != 0 and (not type_template[0][-1].islower()):
      word_list.append(word.capitalize())
  
  return separator.join(word_list)



def replaceNameParameter (text, name_params):
  all_templates = re.findall(r'{name.{0,4}}', text)

  if len(all_templates) == 0:
    return text

  for temp in all_templates:
    text = text.replace(temp, transformNameStyle(name_params, temp))

  return text
