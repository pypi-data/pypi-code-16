# valid_email.py

class check:

    def __init__(self):
        self.check_pts = ["@", ".", "_"]
        self.allowed = [".", "_"]

    def occurence(self, string, char):
        count = 0
        for i in string:
            if i == char:
                count += 1
        if count == 1:
            return count, string.index(char)
        return count, None

    def run_check(self, email):
        if not email.isdigit():
            if "@" not in email:
                
                return 0
            else:
                # since there is "@"s in the email, next step is to ensure it is only one in email.

                count_of_at, index = self.occurence(email, "@")
                
                if count_of_at <> 1:
                    
                    return 0
                else:
                    # Now check if there is no special characters at the beginning or end of email id.

                    if not email[0].isalpha() or not email[-1].isalpha():
                        
                        return 0
                    else:
                        # Now the part of email after @ must have a '.'

                        if '.' not in email[index:]:
                            
                            return 0
                        else:
                            for i in email[0:index]:
                                if not i.isalnum():
                                    if i not in self.allowed:
                                        
                                        return 0
            return 1
                            

