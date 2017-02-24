from django.core import mail 
from trigger.default import Plugin
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
import os

class TriggerSMTPPlugin(Plugin):
    name = 'smtpplugin'
    sender = 'noreply@notix.smtp'
    log_file = 'trigger_plugin.log'

    messages = {}

    emails = []
    include = []
    exclude = []
    subject = 'no reply'

    def get_emails(self, event, instance):
         return self.emails
    # end def

    def get_include(self, event, instance):
         return self.include
    # end def

    def get_exclude(self, event, instance):
        return self.exclude
    # end def

    def get_subject(self, event, instance):
         return self.subject
    # end def

    def get_html(self, html, instance):
        return html
    # end def

    def log(self, message_log):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(BASE_DIR, self.log_file), 'a+') as log:
            log.write(message_log)
            log.close()
        # end with
    # end def

    def emit(self, event, instance):
        if event in self.messages:
            if 'template_name' in self.messages[event]:
                html = render_to_string(self.template_name, instance)
            elif 'html' in self.messages[event]:
                html = self.get_html(self.messages[event]['html'], instance)
            # end if
        else:
            raise Exception('Must define a template_name or html key in massages[%s]'% (event,)) 
        # end if

        to = self.get_emails(event, instance)
        include = self.get_include(event, instance)
        exclude = self.get_exclude(event, instance)
        subject = self.get_subject(event, instance)
        
        for email in include:
            to.append(email)
        # end for        
        for email in exclude:
            to.remove(email)
        # end for

        self.log("%s sended to: %s\n" % (datetime.now(), to, ))

        if len(to):
            msg = mail.EmailMultiAlternatives(subject, ".", self.sender, to)
            msg.attach_alternative(html, "text/html")
            msg.send()
        # end def 
    # end def

# end class