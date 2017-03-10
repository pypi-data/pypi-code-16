from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ungettext

from .models import Ticket, TicketType
from .views import perform_close


class UsernameSearch(object):
    """The User object may not be auth.User, so we need to provide
    a mechanism for issuing the equivalent of a .filter(user__username=...)
    """

    def __str__(self):
        return 'user__%s' % get_user_model().USERNAME_FIELD


class TicketTypeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {'fields': ('related_model',)}
        ),
        (
            _('Content'),
            {'fields': ('title',)}
        ),
    )

    list_display = ('id', 'title', 'related_model',)

admin.site.register(TicketType, TicketTypeAdmin)


class TicketsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _('Content'),
            {'fields': ('user', 'comment', 'types', 'frontend_status', 'backend_status')}
        ),
        (
            _('Metadata'),
            {'fields': ('is_closed', 'version')}
        ),
    )

    list_display = ('ticket_no', 'user_info', 'object_pk', 'submit_date', 'is_closed', 'backend_status')
    list_filter = ('submit_date', 'backend_status', 'types')
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    raw_id_fields = ('user', 'types')
    search_fields = (UsernameSearch(), 'user_email', 'types')
    actions = ["close_tickets"]

    def get_actions(self, request):
        actions = super(TicketsAdmin, self).get_actions(request)
        # Only superusers should be able to delete the comments from the DB.
        if not request.user.is_superuser and 'delete_selected' in actions:
            actions.pop('delete_selected')
        if not request.user.has_perm('report_system.can_review'):
            if 'approve_tickets' in actions:
                actions.pop('approve_tickets')
            if 'remove_tickets' in actions:
                actions.pop('remove_tickets')
        return actions

    # def flag_tickets(self, request, queryset):
    #     self._bulk_flag(request, queryset, perform_flag,
    #                     lambda n: ungettext('flagged', 'flagged', n))
    #
    # flag_tickets.short_description = _("Flag selected tickets")
    #
    # def approve_tickets(self, request, queryset):
    #     self._bulk_flag(request, queryset, perform_approve,
    #                     lambda n: ungettext('approved', 'approved', n))
    #
    # approve_tickets.short_description = _("Approve selected tickets")

    def close_tickets(self, request, queryset):
        self._bulk_flag(request, queryset, perform_close,
                        lambda n: ungettext('closed', 'closed', n))

    close_tickets.short_description = _("Closes selected tickets")

    def _bulk_flag(self, request, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action. Actually
        calls the `action` argument to perform the heavy lifting.
        """
        n_reports = 0
        for report in queryset:
            action(request, report)
            n_reports += 1

        msg = ungettext('1 report was successfully %(action)s.',
                        '%(count)s comments were successfully %(action)s.',
                        n_reports)
        self.message_user(request, msg % {'count': n_reports, 'action': done_message(n_reports)})

# Only register the default admin if the model is the built-in comment model
# (this won't be true if there's a custom comment app).
admin.site.register(Ticket, TicketsAdmin)