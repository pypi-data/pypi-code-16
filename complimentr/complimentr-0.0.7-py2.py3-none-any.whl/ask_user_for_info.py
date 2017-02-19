from sys import version_info

py3 = version_info[0] > 2
#creates boolean value for test that Python major version > 2

def askForSettings(question_text):
    if py3:
      response = input(question_text)
    else:
      response = raw_input(question_text)
    return response
