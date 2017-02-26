import argparse
import os
import fnmatch


def txt_replace(new_str, old_str, directory=cwd, file_type="*"):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, file_type):
            file_path = os.path.join(path, filename)
            with open(file_path) as f:
                n = f.read()
            n = n.replace(new_str, old_str)
            with open(file_path, "w") as f:
                f.write(n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("new_str",
                        help="New replacement string")
    parser.add_argument("old_str",
                        help="String to be replaced")
    parser.add_argument("directory",
                        help="Directory to do the replacement")
    parser.add_argument("file_type",
                        help="The types of file to look in")
    args = parser.parse_args()
    cwd = os.getcwd()

    if args.directory and args.file_type:
        txt_replace(args.newstr, args.oldstr, args.directory,
                   args.file_type)

    elif args.directory:
        txt_replace(args.newstr, args.oldstr, args.directory)

    elif args.file_type:
        txt_replace(args.newstr, args.oldstr, file_type=args.directory)

    else:
        txt_replace(args.newstr, args.oldstr)


if __name__ == '__main__':
    main()



