

def my_function(x, y):
  for i in range(10):
    yield x + y
    x += 1

def main():
  for n in my_function(3, 2):
    print(n)


if __name__ == "__main__":
  main()