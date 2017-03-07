from barcodescan.BarcodeReader import BarcodeReader
from barcodescan.Push_client import Push_client
import signal



def main():
  reader = BarcodeReader("/dev/hidraw0")
  signal.signal(signal.SIGTERM, lambda x: reader.close())
  push_client = Push_client("http://localhost:8000")
  for line in reader.read_generator():
    push_client.push_data({'data': line})


if __name__ == "__main__":
  main()
