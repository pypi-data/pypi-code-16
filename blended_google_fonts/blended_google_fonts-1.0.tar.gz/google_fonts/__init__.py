import os
import sys

cwd = os.getcwd()

def main():
    # Make sure there is actually a configuration file
    config_file_dir = os.path.join(cwd, "config.py")
    if not os.path.exists(config_file_dir):
        sys.exit("There dosen't seem to be a configuration file. Have you run the init command?")
    else:
        sys.path.insert(0, cwd)
        try:
            from config import google_fonts
        except:
            sys.exit("We could not find the google_fonts variable in  your config.py!")
    
    fonts_import_string = ""
    
    if google_fonts:
        for i in range(0, len(google_fonts)):
            fonts_import_string = fonts_import_string + google_fonts[i][0].replace(" ", "+")
            try:
                fonts_import_string = fonts_import_string + ":" + google_fonts[i][1]
            except:
                fonts_import_string = fonts_import_string
            
            if i != len(google_fonts)-1:
                fonts_import_string = fonts_import_string + "|"
    
    fonts_final_string = "<link href=\"https://fonts.googleapis.com/css?family="+fonts_import_string+"\" rel=\"stylesheet\">"
    
    return fonts_final_string
