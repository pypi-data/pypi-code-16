# -*- coding: utf-8 -*-

import jinja2
import smtplib
import logging


def send_email(config, mail_from, rcpt_to, subject, template, vars={}):
    # settup email template
    template_loader = jinja2.FileSystemLoader(
        searchpath=template[0])
    template_env = jinja2.Environment(loader=template_loader)
    t = template_env.get_template(template[1])
    body = t.render(vars)

    # setup logging
    log = logging.getLogger("")

    # format msg
    message = "From: Access And Security <%s>\n" % mail_from
    message += "To: %s\n" % rcpt_to
    message += "Subject: %s\n\n" % subject
    message += body

    # send email
    log.debug("Sending email to %s with instructions" % rcpt_to)
    try:
        smtpObj = smtplib.SMTP(
            host=config['smtp_host'],
            port=config['smtp_port'],
            timeout=10
        )

        if (config['smtp_tls']):
            smtpObj.starttls()

        smtpObj.ehlo()

        if (config['smtp_auth']):
            smtpObj.login(
                config['smtp_user'],
                config['smtp_pass'])

        smtpObj.sendmail(mail_from, rcpt_to, message)
    except Exception as e:
        log.error("Error while sending email to %s: %s" % (rcpt_to, e))
        return False

    return True
