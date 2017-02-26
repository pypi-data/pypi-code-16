import os
import shutil
from collections import defaultdict

from ._settings import ANDROID as ANDROID_SETTINGS

#----------------------------------------------------------------------
def __updatedict__(dm, ds):

    for key in ds.keys():
        if isinstance(ds[key], dict):
            if key in dm:
                ds[key].update(dm[key])

        elif isinstance(ds[key], list):
            if key in dm:
                ds[key] = set(ds[key] + dm[key])

        elif isinstance(ds[key], (int, float, str, bytes)):
            if key in dm:
                ds[key] = dm[key]

    dm.update(ds)
    return dm


#----------------------------------------------------------------------
def get_p4a_args(settings):
    """"""
    ANDROID = __updatedict__(settings.ANDROID, ANDROID_SETTINGS)

    PORT = ANDROID['PORT']
    APK_NAME = ANDROID['APK']['name']
    #NAME = settings.__str__()[settings.__str__().find('"')+1:settings.__str__().find('.')]
    NAME = os.path.split(settings.BASE_DIR)[-1]
    VERSION = ANDROID['APK']['version']
    NUMERICVERSION = ANDROID['APK']['numericversion']
    PACKAGE = ANDROID['APK']['package']
    ICON = ANDROID['APK']['icon']
    ORIENTATION = ANDROID['APK']['orientation']

    PERMISSIONS = ""
    for permission in set(ANDROID['PERMISSIONS']):
        PERMISSIONS += "--permission={}\n".format(permission)

    BUILD_DIR = os.path.join(ANDROID['BUILD']['build'], NAME, 'build')
    RECIPES_DIR = os.path.join(ANDROID['BUILD']['build'], NAME, 'recipes')
    WHITELIST = os.path.join(RECIPES_DIR, 'whitelist')

    REQUIREMENTS = ",".join(ANDROID['BUILD']['__requirements'] + ANDROID['BUILD']['requirements'])

    ANDROID_SDK = ANDROID['ANDROID']['SDK']
    ANDROID_SDK_API = ANDROID['ANDROID']['API']

    CRYSTAX_NDK = ANDROID['ANDROID']['CRYSTAX_NDK']
    CRYSTAX_NDK_VERSION = ANDROID['ANDROID']['CRYSTAX_NDK_VERSION']

    ARCH = ANDROID['ANDROID']['ARCH']

    BUILD = ANDROID['BUILD']


    EXTRA_OPTIONS = ""
    APP_MULTITHREAD = ANDROID['APP']['multithread']

    if APP_MULTITHREAD:
        print("Use multithread for Django server is NOT compatible with Jnius!!!")


    if ANDROID['APK']['intent_filters']:
        EXTRA_OPTIONS = '--intent-filters="{}"\n'.format(ANDROID['APK']['intent_filters'])


    locals_ = locals()

    for key in ANDROID.get('CUSTOM', {}):
        #eval('CUSTOM_{} = {}'.format(key, ANDROID['CUSTOM'][key]))
        locals_['CUSTOM_{}'.format(key)] = ANDROID['CUSTOM'][key]



    return locals()



#----------------------------------------------------------------------
def update_apk(settings):
    """"""
    ARGS = get_p4a_args(settings)

    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    app_dir = os.path.join(build_dir, 'app')
    resources_dir = os.path.join(app_dir, 'resources')
    #os.makedirs(app_dir, exist_ok=True)
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    #if os.path.exists(resources_dir):
        #shutil.rmtree(resources_dir)
    os.makedirs(resources_dir, exist_ok=True)
    os.makedirs(ARGS['BUILD_DIR'], exist_ok=True)

    #generate icon apk
    icon = settings.ANDROID['APK']['icon']
    shutil.copyfile(icon, os.path.join(resources_dir, 'icon.png'))

    #generate static html for splash
    splash_html = settings.ANDROID['SPLASH']['static_html']
    if splash_html:
        splash_resources = settings.ANDROID['SPLASH']['resources']
        splash_build = os.path.join(app_dir, 'resources', 'splash.html')
        shutil.copyfile(splash_html, splash_build)
        for rsc in splash_resources:
            shutil.copy(rsc, resources_dir)
        parcefiles([splash_build], ARGS)
    else:
        from djangoforandroid import src
        load = os.path.join(os.path.dirname(src.__file__), 'splash.html')
        shutil.copyfile(load, os.path.join(app_dir, 'resources', 'splash.html'))
        parcefiles([os.path.join(app_dir, 'resources', 'splash.html')], ARGS)


    #generate main.py
    from djangoforandroid import src
    raw_main = os.path.join(os.path.dirname(src.__file__), 'main.py')
    build_main = os.path.join(app_dir, 'main.py')
    shutil.copyfile(raw_main, build_main)
    parcefiles([build_main], ARGS)

    #move project
    project_dir = settings.BASE_DIR
    project_build = os.path.join(app_dir, ARGS['NAME'])
    #if os.path.exists(project_build):
        #shutil.rmtree(project_build)
    shutil.copytree(project_dir, project_build)


    #if ARGS['BUILD']['include_exts']:
        #for root, dirs, files in os.walk(project_build):
            #for file in files:
                #path = os.path.join(root, file)
                #if path.endswith(tuple(ARGS['BUILD']['include_exts'])):
                    #continue
                #else:
                    #print("removing {} from build".format(path))
                    #os.remove(path)

    #if ARGS['BUILD']['exclude_dirs']:
        #for dir_ in ARGS['BUILD']['exclude_dirs']:
            #path = os.path.join(project_build, dir_)
            #if os.path.exists(path):
                #print("removing {} from build".format(path))
                #shutil.rmtree(path, ignore_errors=True)

    #for root, dirs, files in os.walk(project_build):
        #if '__pycache__' in dirs:
            #dirs.remove('__pycache__')
            #path = os.path.join(root, '__pycache__')
            #print("removing {} from build".format(path))
            #shutil.rmtree(path, ignore_errors=True)


    #generate d4a.config
    from djangoforandroid import src
    raw_p4a = os.path.join(os.path.dirname(src.__file__), 'd4a.config')
    build_p4a = os.path.join(build_dir, 'd4a.config')
    shutil.copyfile(raw_p4a, build_p4a)
    parcefiles([build_p4a], ARGS)

    #copy defauts recipes
    from djangoforandroid import recipes
    recipes_dir = os.path.dirname(recipes.__file__)
    recipes_build = os.path.join(build_dir, 'recipes')
    if os.path.exists(recipes_build):
        shutil.rmtree(recipes_build)
    shutil.copytree(recipes_dir, recipes_build)

    #merge recipes
    if 'recipes' in settings.ANDROID['BUILD'] and settings.ANDROID['BUILD']['recipes']:
        recipes = settings.ANDROID['BUILD']['recipes']
        for dir_ in os.listdir(recipes):
            dir_ = os.path.join(recipes, dir_)
            shutil.copytree(dir_, os.path.join(recipes_build, os.path.split(dir_)[-1]))

    #merge whitelist
    if 'whitelist' in settings.ANDROID['BUILD'] and settings.ANDROID['BUILD']['whitelist']:
        lines = open(settings.ANDROID['BUILD']['whitelist'], 'r').readlines()
        file = open(ARGS['WHITELIST'], 'a')
        file.writelines(lines)
        file.close()


#----------------------------------------------------------------------
def overwrite_p4a(settings):
    """"""
    ARGS = get_p4a_args(settings)
    from djangoforandroid import src

    #replace PythonActivity
    #activity_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'src', 'org', 'kivy', 'android', 'PythonActivity.java')
    activity_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'src', 'org', 'kivy', 'android', 'PythonActivity.java')
    activity_dir = os.path.join(os.path.dirname(src.__file__), 'PythonActivity.java')
    if os.path.exists(activity_build):
        #os.remove(activity_build)
        shutil.copy(activity_dir, activity_build)
    statusbarcolor = settings.ANDROID['APK']['statusbarcolor']
    navigationbarcolor = settings.ANDROID['APK']['navigationbarcolor']
    #download = settings.ANDROID['APK']['download_name']
    parcefiles([activity_build], {'STATUS_BAR_COLOR': statusbarcolor, 'NAVIGATION_BAR_COLOR': navigationbarcolor,})

    #replace build.py
    #buildpy_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'build.py')
    buildpy_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'build.py')
    buildpy_dir = os.path.join(os.path.dirname(src.__file__), 'build.py')
    if os.path.exists(buildpy_build):
        shutil.copy(buildpy_dir, buildpy_build)

    #replace AndroidManifest.tmpl.xml
    #manifest_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'templates', 'AndroidManifest.tmpl.xml')
    manifest_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'templates', 'AndroidManifest.tmpl.xml')
    manifest_dir = os.path.join(os.path.dirname(src.__file__), 'AndroidManifest.tmpl.xml')
    if os.path.exists(manifest_build):
        shutil.copy(manifest_dir, manifest_build)

    #clear webview_includes
    #webview_includes = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'webview_includes')
    webview_includes = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'webview_includes')
    if os.path.exists(webview_includes):
        for file in os.listdir(webview_includes):
            os.remove(os.path.join(webview_includes, file))
    else:
        os.makedirs(webview_includes)



#----------------------------------------------------------------------
def parcefiles(editfiles, kwargs):
    """"""
    for filename in editfiles:
        if not os.path.exists(filename):
            return
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        new_lines = "".join(lines)
        new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
        new_lines = new_lines.replace("{", "{{").replace("}", "}}")
        new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")

        #new_lines = new_lines.format(**kwargs)
        d = defaultdict(lambda: 'UNKNOWN')
        d.update(kwargs)

        new_lines = new_lines.format_map(d)

        file = open(filename, "w")
        file.write(new_lines)
        file.close()



#----------------------------------------------------------------------
def clean_build(settings):
    """"""
    ARGS = get_p4a_args(settings)
    shutil.rmtree(ARGS['BUILD_DIR'])


#----------------------------------------------------------------------
def post_update_apk(settings):
    """"""
    ARGS = get_p4a_args(settings)
    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    app_dir = os.path.join(build_dir, 'app')
    project_build = os.path.join(app_dir, ARGS['NAME'])

    if ARGS['BUILD']['exclude_dirs']:
        for dir_ in ARGS['BUILD']['exclude_dirs']:
            path = os.path.join(project_build, dir_)
            if os.path.exists(path):
                print("removing {} from build".format(path))
                shutil.rmtree(path, ignore_errors=True)

    if ARGS['BUILD']['exclude_files']:
        for file in ARGS['BUILD']['exclude_files']:
            path = os.path.join(project_build, file)
            if os.path.exists(path):
                print("removing {} from build".format(path))
                os.remove(path)

    if ARGS['BUILD']['include_exts']:
        for root, dirs, files in os.walk(project_build):
            for file in files:
                path = os.path.join(root, file)
                if path.endswith(tuple(ARGS['BUILD']['include_exts'])):
                    continue
                else:
                    print("removing {} from build".format(path))
                    os.remove(path)

    for root, dirs, files in os.walk(project_build):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            path = os.path.join(root, '__pycache__')
            print("removing {} from build".format(path))
            shutil.rmtree(path, ignore_errors=True)


def read_configuration(settings):

    ARGS = get_p4a_args(settings)
    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    build_p4a = os.path.join(build_dir, 'd4a.config')
    argv = []

    with open("d4a.config") as fd:
        lines = fd.readlines()
    lines = filter(lambda l:l.startswith("--"), lines)
    lines = list(map(lambda l:l.replace("\n", ""), lines))

    return " ".join(lines)