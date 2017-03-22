

class NotDeletableAdminMixin(object):

    def get_actions(self, request):
        actions = super(NotDeletableAdminMixin, self).get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


class NotAddableAdminMixin(object):

    def has_add_permission(self, request):
        return False
