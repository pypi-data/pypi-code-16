
class ConsoleAlert(object):

    def call(self, exceptions):
        print " \nexceptions RAISED!! : \n"
        for ex in exceptions:
            print 'case: ', ex['case']
            print 'message: ', ex['message']
            print 'traceback: ', ex['traceback']

    def report(self, title, is_pass, stat):
        print title
        print 'Pass: ', is_pass
        print 'Stat: ', stat
