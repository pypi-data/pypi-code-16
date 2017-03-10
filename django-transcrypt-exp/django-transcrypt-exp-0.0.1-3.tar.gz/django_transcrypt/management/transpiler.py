import os
import glob
import shutil

DEBUG_OPTIONS = ['--map']
PRODUCTION_OPTIONS = ['-b']


def transpile_js(path, file, sink, debug=True):
    os.chdir(path)
    js_path = os.path.join(path, "__javascript__")

    def inner_transpile():
        if debug:
            transpiler_str = " ".join(["transcrypt"] +
                                      DEBUG_OPTIONS +
                                      [file])
        else:
            transpiler_str = " ".join(["transcrypt"] +
                                      PRODUCTION_OPTIONS +
                                      [file])
        os.system(transpiler_str)
        files = glob.glob(os.path.join(js_path, '*.js'),
                          recursive=False) +\
            glob.glob(os.path.join(js_path, '**/*.map'),
                      recursive=True)

        for filepath in files:
            if (os.path.isfile(filepath)):

                filepath_postfix = filepath.replace(js_path, "")
                if os.path.isabs(filepath_postfix):
                    filepath_postfix = filepath_postfix[1:]
                dst = os.path.join(
                    sink,
                    filepath_postfix)
                if not os.path.exists(os.path.dirname(dst)):
                    os.makedirs(os.path.dirname(dst))
                print("Copying file: " + filepath + " -> " + dst)
                shutil.copy(
                    src=filepath,
                    dst=dst)

        print("\033[92m[Success] \033[0m")

    return inner_transpile
