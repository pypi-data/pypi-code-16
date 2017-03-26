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
            from config import twitter_card, twitter_site, twitter_title, twitter_description, twitter_image
        except:
            sys.exit("We could not find the Twitter card variables in  your config.py!")
    
    card_meta = ""
    
    if not twitter_card == "":
        if twitter_card == "summary" or twitter_card == "summary_large_image":
            card_meta = card_meta + "<meta name=\"twitter:card\" content=\""+twitter_card+"\" />\n"
            card_meta = card_meta + "<meta name=\"twitter:site\" content=\""+twitter_site+"\" />\n"
            card_meta = card_meta + "<meta name=\"twitter:title\" content=\""+twitter_title+"\" />\n"
            card_meta = card_meta + "<meta name=\"twitter:description\" content=\""+twitter_description+"\" />\n"
            card_meta = card_meta + "<meta name=\"twitter:image\" content=\""+twitter_image+"\" />\n"
    
    return card_meta
