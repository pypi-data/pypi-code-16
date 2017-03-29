import web
import application

urls = (
    '/', 'application.controllers.products.index.Index',
    '/products/view/(.+)', 'application.controllers.products.view.View',
    '/products/insert', 'application.controllers.products.insert.Insert',
    '/products/edit/(.+)', 'application.controllers.products.edit.Edit',
    '/products/delete/(.+)', 'application.controllers.products.delete.Delete',
)

app = web.application(urls, globals())


web.config.debug = False

if __name__ == "__main__":
    app.run()
