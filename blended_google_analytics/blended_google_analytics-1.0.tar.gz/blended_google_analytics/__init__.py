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
            from config import analytics_id
        except:
            sys.exit("We could not find the analytics_id variable in  your config.py!")
    
    analytics_code = """
    <script>
      (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
      (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
      m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
      })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

      ga('create', '"""+analytics_id+"""', 'auto');
      ga('require', 'linkid');
      ga('send', 'pageview');

    </script>
    """
    return analytics_code
