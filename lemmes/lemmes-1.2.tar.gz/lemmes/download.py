from os import path, popen, makedirs
import shutil
import zipfile
import urllib
import config as cf


class ResourceData:
    @staticmethod
    def unzip(source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

    @classmethod
    def unzip_from_source(self, zip_name, dest_dir):
        zip, headers = urllib.urlretrieve(
                                        '{0}/{1}.zip'.format(
                                            cf.RESOURCES_URL,
                                            zip_name)
                                        )
        self.unzip(zip, dest_dir)
        return True

    @classmethod
    def download(self):
        home = path.expanduser("~")
        ntltk_path = path.join(home, 'nltk_data')
        if not path.isdir(ntltk_path):
            makedirs(ntltk_path)
        if not path.isdir(cf.PATH_BIN_LEMMES):
            makedirs(cf.PATH_BIN_LEMMES)
        print('set content in: ' + cf.PATH_BIN_LEMMES)
        self.unzip_from_source('corpora', ntltk_path)
        self.unzip_from_source('tokenizers', ntltk_path)
        print('done!')
        return True

if __name__ == '__main__':
    ResourceData.download()
