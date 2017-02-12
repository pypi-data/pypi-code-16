import tastyapi
import sys


def main():
    if sys.argv[1] is None:
        print('No Command Given!')
        return

    elif sys.argv[1] == 'get_user':
        if sys.argv[2] is not None:
            print(tastyapi.get_user(sys.argv[2]))
        else:
            print("No User Provided!")
        return

    else:
        print('Invalid Command!')
        return
