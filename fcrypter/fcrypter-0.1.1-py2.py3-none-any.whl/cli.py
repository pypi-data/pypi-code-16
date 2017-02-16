# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click
from fcrypter.fcrypter import get_supported_ciphers, pad_key


supported_ciphers = get_supported_ciphers()
cipher_names = supported_ciphers.keys()


@click.command()
@click.option("--cipher", type=click.Choice(cipher_names),
              help="Cipher mode used for encryption", required=True)
@click.option('--encrypt', 'mode', flag_value='e',
              default=True)
@click.option('--decrypt', 'mode', flag_value='d')
@click.option("--file-in", prompt=True)
@click.option("--file-out", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def main(cipher, mode, file_in, file_out, password):
    """Console script for fcrypter"""
    ciph = supported_ciphers[cipher]()
    modes = dict(e='encrypt_file', d='decrypt_file')

    if len(password) not in ciph.supported_sizes:
        # we cannot support random padding when decrypting
        if mode == "d" or len(password) > max(ciph.supported_sizes):
            raise RuntimeError("Wrong key size given!\nMust be size {}".format(
                " or ".join([str(x) for x in ciph.supported_sizes])))
        # pad the key with extra chars if key size is not supported
        password = pad_key(password, ciph)
        print("Padded key\nYour password is: {p}".format(p=password))

    getattr(ciph, modes[mode])(bytes(password), file_in, file_out)


if __name__ == "__main__":
    main()
