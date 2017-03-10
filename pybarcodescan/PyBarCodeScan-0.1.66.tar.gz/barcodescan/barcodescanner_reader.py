from barcodescan.BarcodeReader import BarcodeReader
from barcodescan.Push_client import Push_client
import signal
import os
from barcodescan.Config import Config


def main():
  reader = BarcodeReader("/dev/hidraw0")
  signal.signal(signal.SIGTERM, lambda x: reader.close())
  config = Config("/home/pi/.barcodescanner.cfg")
  push_client = Push_client(config.reader_push_url())
  for line in reader.read_generator():
    push_client.push_data({'data': line})


if __name__ == "__main__":
  main()
