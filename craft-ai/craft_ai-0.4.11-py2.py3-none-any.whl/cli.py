import requests

from codecs import open

from argparse import ArgumentParser

try:
    import pypandoc
    pypandoc.get_pandoc_version()
except (ImportError) as e:
    raise e
except (OSError):
    # expects a installed pypandoc: pip install pypandoc
    from pypandoc.pandoc_download import download_pandoc
    download_pandoc()


def update_readme():
    url = "http://www.craft.ai/content/api/python.md"
    r = requests.get(url)

    if r.status_code == 200:
        text = r.text
        with open("README.md", 'w', encoding="utf-8") as f:
            for line in text:
                f.write(line)
            print("Successfully updated README.md")

    # Conversion to rst
    try:
        import pypandoc
        readme = pypandoc.convert("README.md", "rst")
        readme = readme.replace("\r", "")
    except (OSError, ImportError) as e:
        print("Pandoc not found. md->rst conversion failure.")
        raise e

    with open("README.rst", 'w', encoding="utf-8") as outfile:
        outfile.write(readme)
    print("Successfully converted README.md to README.rst")


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--update_readme",
        action="store_true",
        help="Updates the README.md file from craft.ai official documentation")

    args = parser.parse_args()
    if args.update_readme:
        update_readme()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
