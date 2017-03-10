import valid_email as valid
print "Enter an integer to exit."
def run():

    email = valid.check()

    ID = raw_input()

    if email.run_check(ID) <> None:
        print email.run_check(ID)
        run()


if __name__ == '__main__':

    run()
    
