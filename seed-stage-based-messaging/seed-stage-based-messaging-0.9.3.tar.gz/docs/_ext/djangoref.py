# Enable referencing Django settings with intersphinx
def setup(app):
    app.add_crossref_type(
        directivename='setting',
        rolename='setting',
        indextemplate='pair: %s; setting',
    )
