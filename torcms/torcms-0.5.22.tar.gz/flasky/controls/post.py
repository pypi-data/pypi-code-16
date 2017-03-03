from flask import render_template, session, redirect, render_template_string, url_for
from flask import request
from flask.views import MethodView
from torcms.model.post_model import MPost
from . import main

uu = MPost()


@main.route('/post/add_document', methods=['GET'])
def user():
    return render_template('doc/post/post_add.html', )


from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class EmailPasswordForm(Form):
    # pass
    # email = StringField('Email', validators=[DataRequired(), Email()])
    title = StringField('title', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])


#####################################################################################################
class UserView(MethodView):
    def get(self, **kwargs):
        # print(args)
        # print(kwargs)
        url_str = kwargs['url_str']

        form = EmailPasswordForm()

        if url_str == '_add':
            return render_template('doc/post/post_add.html', form = form)
        elif len(url_str) in [4, 5]:
            # print(url_str)
            postinfo = uu.get_by_uid(url_str)
            return render_template('doc/post/post_view.html', postinfo=postinfo)

    def post(self, **kwargs):

        url_str = kwargs['url_str']

        if url_str == '_add':
            print('=' * 20)
            print('Post: ', url_str)
            print(kwargs)
            print(request.form)

            post_data = {}
            for x in request.form:
                post_data[x] = request.form[x]
            print(post_data)

            form = EmailPasswordForm()

            print(  form.validate_on_submit() )
            if form.validate_on_submit():
                print('YYYYYY')
                return render_template('index/index.html', )
            else:
                print('NNNNNN')
                return render_template('index/index.html', )
            # return render_template('doc/post/post_add.html', )



main.add_url_rule('/post/<url_str>', view_func=UserView.as_view('usesadfr'))
