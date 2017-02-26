from barcodescan.BarcodeReader import BarcodeReader
from barcodescan.Push_client import Push_client


def main():
  reader = BarcodeReader("/dev/hidraw0")
  push_client = Push_client("http://localhost:8000")
  for line in reader.read_generator():
    push_client.push_data(line)


if __name__ == "__main__":
  main()
