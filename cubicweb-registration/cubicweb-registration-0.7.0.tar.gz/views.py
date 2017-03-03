# copyright 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""anonymous registration form and views"""

from yams.schema import role_name

from cubicweb import mail, crypto
from cubicweb.view import StartupView
from cubicweb.predicates import anonymous_user
from cubicweb.web import Redirect, ValidationError, ProcessFormError
from cubicweb.web import controller, form, captcha
from cubicweb.web import formwidgets as fw, formfields as ff
from cubicweb.web.views import forms, basecomponents, urlrewrite

try:
    from cubicweb import _
except ImportError:
    _ = unicode


def qname(attr):
    return role_name(attr, 'subject')


class RegistrationForm(forms.FieldsForm):
    __regid__ = 'registration'
    domid = 'registrationForm'
    form_buttons = [fw.SubmitButton()]

    @property
    def action(self):
        return self._cw.build_url(u'registration_sendmail')

    # properly name fields according to validation errors that may be raised by
    # the register_user service
    login = ff.StringField(widget=fw.TextInput(), role='subject',
                           # we don't want to see 'authenticate'
                           label=_('i18n_register_login'),
                           required=True)
    upassword = ff.StringField(widget=fw.PasswordInput(), role='subject',
                               required=True)
    email_address = ff.StringField(widget=fw.TextInput(), role='subject',
                                   required=True, label=_('i18n_email_address'))
    firstname = ff.StringField(widget=fw.TextInput(), role='subject')
    surname = ff.StringField(widget=fw.TextInput(), role='subject')
    captcha = ff.StringField(widget=captcha.CaptchaWidget(), required=True,
                             label=_('captcha'),
                             help=_('please copy the letters from the image'))


class RegistrationFormView(form.FormViewMixIn, StartupView):
    __regid__ = 'registration'

    def call(self):
        form = self._cw.vreg['forms'].select('registration', self._cw)
        form.render(w=self.w, display_progress_div=False)


class RegistrationSendMailController(controller.Controller):
    __regid__ = 'registration_sendmail'
    content = _(u'''
Hello %(firstname-subject)s %(surname-subject)s,

thanks for registering on %(base_url)s.

Please click on the link below to activate your account :
%(url)s

See you soon on %(base_url)s !
''')
    subject = _(u'Confirm your registration on %(base_url)s')

    def publish(self, rset=None):
        data = self.checked_data()
        recipient = data[qname('email_address')]
        msg = self.build_email(recipient, data)
        self._cw.vreg.config.sendmails([(msg, (recipient,))])
        raise Redirect(self.success_redirect_url())

    def checked_data(self):
        '''only basic data check here (required attributes and password
        confirmation check)
        '''
        form = self._cw.vreg['forms'].select('registration', self._cw)
        form.formvalues = {}  # init fields value cache
        data = {}
        errors = {}
        for field in form.fields:
            try:
                for field, value in field.process_posted(form):
                    if value is not None:
                        data[field.role_name()] = value
            except ProcessFormError as exc:
                errors[field.role_name()] = unicode(exc)
        if errors:
            raise ValidationError(None, errors)
        return data

    def build_email(self, recipient, data):
        activationurl = self.activation_url(data)  # build url before modifying data
        data.setdefault(qname('firstname'), '')
        data.setdefault(qname('surname'), '')
        if not (data.get(qname('firstname')) or data.get(qname('surname'))):
            data[qname('firstname')] = data[qname('login')]
        data.update({'base_url': self._cw.base_url(secure=True),
                     'url': activationurl})
        content = self._cw._(self.content) % data
        subject = self._cw._(self.subject) % data
        return mail.format_mail({}, [recipient], content=content,
                                subject=subject, config=self._cw.vreg.config)

    def activation_url(self, data):
        data.pop(qname('upassword') + '-confirm', None)
        key = crypto.encrypt(data, self._cw.vreg.config['registration-cypher-seed'])
        return self._cw.build_url('registration_confirm', key=key, __secure__=True)

    def success_redirect_url(self):
        msg = self._cw._(u'Your registration email has been sent. Follow '
                         'instructions in there to activate your account.')
        return self._cw.build_url('', __message=msg)


class RegistrationConfirmController(controller.Controller):
    __regid__ = 'registration_confirm'

    def publish(self, rset=None):
        req = self._cw
        try:
            data = crypto.decrypt(req.form['key'],
                                  req.vreg.config['registration-cypher-seed'])
            login = data[qname('login')]
            password = data.pop(qname('upassword'))
        except:
            msg = req._(u'Invalid registration data. Please try registering again.')
            raise Redirect(req.build_url(u'register', __message=msg))
        if self._cw.user.login == login:
            # already logged in (e.g. regstration link replayed twice in the browser)
            raise Redirect(self.success_redirect_url(self._cw.user.name()))
        req.form = data  # hijack for proper validation error handling
        err = None
        try:
            with self.appli.repo.internal_cnx() as cnx:
                cnx.call_service('register_user',
                                 login=login, password=password,
                                 email=data.get(qname('email_address')),
                                 firstname=data.get(qname('firstname')),
                                 surname=data.get(qname('surname')))
                cnx.commit()
        except ValidationError, err:
            if 'login' in err.errors and 'unicity constraint' in err.errors['login']:
                err.errors.pop('', None)
                err.errors.pop('login', None)
                err.errors['login-subject'] = _(
                    'the value "{}" is already used, use another one').format(login)
                err.entity = None
            # XXX TEMPORARY HACK to allow registration links to work more than
            # once. This is required because some email clients (e.g. kmail)
            # start by downloading the url to find the mimetype of the resource
            # and then execute the appropriate action (e.g. open the url in the
            # default browser) based on the mimetype.
            if err.errors.keys() != ['login-subject']:
                raise
        # try to connect using the provided credentials
        try:
            from cubicweb import repoapi
            cnx = repoapi.connect(self.appli.repo, login, password=password)
            with cnx:
                name = cnx.user.name()
            raise Redirect(self.success_redirect_url(name))
        except:
            if err is not None:
                # both registration and login failed, re-raise the previous
                # ValidationError
                raise err
            raise

    def success_redirect_url(self, name):
        login = self._cw.build_url('login')
        msg = self._cw._(u'Congratulations, your registration is complete. '
                         'You can now <a href="{}">login</a>.').format(login)
        return self._cw.build_url('', __message=msg)


class RegisterLink(basecomponents.HeaderComponent):
    __regid__ = 'registration.registerlink'
    __select__ = basecomponents.HeaderComponent.__select__ & anonymous_user()
    context = 'header-right'

    def render(self, w):
        self._cw.add_css('cubicweb.pictograms.css')
        w(u'<a class="logout icon-user-add" title="%s" href="%s"></a>' % (
            self._cw._('i18n_register_user'), self._cw.build_url('register'), ))


# urls #########################################################################

class RegistrationSimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    ignore_baseclass_rules = True
    rules = [
        ('/register', dict(vid='registration')),
    ]
