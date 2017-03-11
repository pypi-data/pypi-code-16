import requests


class ZenDeskCoreSearch:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_search = self.client.api_root + '/search.json'


class ZenDeskCoreTickets:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_tickets = client.api_root + '/tickets.json'
        self.api_ticket = client.api_root + '/tickets/{id}.json'
        self.api_ticket_related_info = client.api_root + '/tickets/{id}/related.json'
        self.api_ticket_collaborators = client.api_root + '/tickets/{id}/collaborators.json'
        self.api_ticket_incidents = client.api_root + '/tickets/{id}/incidents.json'
        self.api_ticket_problems = client.api_root + '/tickets/problems.json'
        self.api_ticket_mark_as_spam = client.api_root + '/tickets/{id}/mark_as_spam.json'
        self.api_ticket_mark_many_as_spam = client.api_root + '/tickets/mark_many_as_spam.json'
        self.api_tickets_show_many = client.api_root + '/tickets/show_many.json'
        self.api_tickets_create_many = client.api_root + '/tickets/create_many.json'
        self.api_tickets_update_many = client.api_root + '/tickets/update_many.json'
        self.api_tickets_destroy_many = client.api_root + '/tickets/destroy_many.json'
        self.api_tickets_recently_viewed = client.api_root + '/tickets/recent.json'
        self.api_merge_tickets = client.api_root + '/tickets/{id}/merge.json'
        self.api_ticket_comments = client.api_root + '/tickets/{ticket_id}/comments.json'
        self.api_ticket_comment_private = client.api_root + '/tickets/{ticket_id}/comments/{id}/make_private.json'
        self.api_ticket_ticket_metrics = client.api_root + '/tickets/{ticket_id}/metrics.json'
        self.ticket_tags = client.api_root + '/tickets/{id}/tags.json'


class ZenDeskCoreOrganizations:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_org_tickets = client.api_root + '/organizations/{organization_id}/tickets.json'
        self.api_org_users = client.api_root + '/organizations/{id}/users.json'
        self.api_organizations = client.api_root + '/organizations.json'
        self.api_organization = client.api_root + '/organizations/{id}.json'
        self.api_organization_related = client.api_root + '/organizations/{id}/related.json'
        self.api_organizations_autocomplete = client.api_root + '/organizations/autocomplete.json'
        self.api_organizations_show_many = client.api_root + '/organizations/show_many.json'
        self.api_organizations_create_many = client.api_root + '/organizations/create_many.json'
        self.api_organizations_create_or_update = client.api_root + '/organizations/create_or_update.json'
        self.api_organizations_update_many = client.api_root + '/organizations/update_many.json'
        self.api_organizations_destroy_many = client.api_root + '/organizations/destroy_many.json'
        self.api_organizations_search_by_external_id = client.api_root + '/organizations/search.json'
        self.api_organization_organization_subscriptions = \
            client.api_root + '/organizations/{organization_id}/subscriptions.json'
        self.api_organization_organization_memberships = \
            client.api_root + '/organizations/{organization_id}/organization_memberships.json'
        self.org_tags = client.api_root + '/organizations/{id}/tags.json'


class ZenDeskCoreUsers:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_user_tickets_requested = client.api_root + '/users/{user_id}/tickets/requested.json'
        self.api_user_tickets_ccd = client.api_root + '/users/{user_id}/tickets/ccd.json'
        self.api_user_tickets_assigned = client.api_root + '/users/{user_id}/tickets/assigned.json'
        self.api_users = client.api_root + '/users.json'
        self.api_users_search = client.api_root + '/users/search.json'
        self.api_users_autocomplete = client.api_root + '/users/autocomplete.json'
        self.api_users_request_create = client.api_root + '/users/request_create.json'
        self.api_users_me = client.api_root + '/users/me.json'
        self.api_user = client.api_root + '/users/{id}.json'
        self.api_user_related = client.api_root + '/users/{id}/related.json'
        self.api_user_set_password = client.api_root + '/users/{user_id}/password.json'
        self.api_user_get_password_requirements = client.api_root + '/users/{user_id}/password/requirements.json'
        self.api_users_create_many = client.api_root + '/users/create_many.json'
        self.api_users_create_or_update = client.api_root + '/users/create_or_update.json'
        self.api_users_create_or_update_many = client.api_root + '/users/create_or_update_many.json'
        self.api_users_update_many = client.api_root + '/users/update_many.json'
        self.api_users_show_many = client.api_root + '/users/show_many.json'
        self.api_users_destroy_many = client.api_root + '/users/destroy_many.json'
        self.api_user_identities = client.api_root + '/users/{user_id}/identities.json'
        self.api_user_identity = client.api_root + '/users/{user_id}/identities/{id}.json'
        self.api_user_identity_make_primary = client.api_root + '/users/{user_id}/identities/{id}/make_primary'
        self.api_user_identity_verify = client.api_root + '/users/{user_id}/identities/{id}/verify'
        self.api_user_identity_request_verification = \
            client.api_root + '/users/{user_id}/identities/{id}/request_verification.json'
        self.api_user_groups = client.api_root + '/users/{user_id}/groups.json'
        self.api_user_group_memberships = client.api_root + '/users/{user_id}/group_memberships.json'
        self.api_user_group_membership = client.api_root + '/users/{user_id}/group_memberships/{id}.json'
        self.api_user_group_membership_make_default = \
            client.api_root + '/users/{user_id}/group_memberships/{membership_id}/make_default.json'
        self.api_user_organizations = client.api_root + '/users/{user_id}/organizations.json'
        self.api_user_organization_subscriptions = client.api_root + '/users/{user_id}/organization_subscriptions.json'
        self.api_user_organization_memberships = client.api_root + '/users/{user_id}/organization_memberships.json'
        self.api_user_organization_membership = client.api_root + '/users/{user_id}/organization_memberships/{id}.json'
        self.api_user_organization_membership_make_default = \
            client.api_root + '/users/{user_id}/organization_memberships/{id}/make_default.json'
        self.user_tags = client.api_root + '/users/{id}/tags.json'


class ZenDeskCoreSuspendedTickets:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_suspended_tickets = client.api_root + '/suspended_tickets.json'
        self.api_suspended_ticket = client.api_root + '/suspended_tickets/{id}.json'
        self.api_suspended_ticket_recover = client.api_root + '/suspended_tickets/{id}/recover.json'
        self.api_suspended_ticket_recover_many = client.api_root + '/suspended_tickets/recover_many.json'
        self.api_suspended_ticket_destroy_many = client.api_root + '/suspended_tickets/destroy_many.json'


class ZenDeskCoreTicketMetrics:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_ticket_metrics = client.api_root + '/ticket_metrics.json'
        self.api_ticket_metric = client.api_root + '/ticket_metrics/{ticket_metric_id}.json'


class ZenDeskCoreIncremental:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_ticket_metric_events = '/incremental/ticket_metric_events.json'


class ZenDeskCoreGroups:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_group_users = client.api_root + '/groups/{id}/users.json'
        self.api_groups = client.api_root + '/groups.json'
        self.api_group = client.api_root + '/groups/{id}.json'
        self.api_groups_assignable = client.api_root + '/groups/assignable.json'
        self.api_group_group_memberships = client.api_root + '/groups/{group_id}/memberships.json'
        self.api_group_group_memberships_assignable = client.api_root + '/groups/{group_id}/memberships/assignable.json'


class ZenDeskCoreGroupMemberships:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_group_memberships = client.api_root + '/group_memberships.json'
        self.api_group_membership = client.api_root + '/group_memberships/{id}.json'
        self.api_group_memberships_assignable = client.api_root + '/group_memberships/assignable.json'
        self.api_group_memberships_create_many = client.api_root + '/group_memberships/create_many.json'
        self.api_group_memberships_destroy_many = client.api_root + '/group_memberships/destroy_many.json'


class ZenDeskCoreOrganizationSubscriptions:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_organization_subscriptions = client.api_root + '/organization_subscriptions.json'
        self.api_organization_subscription = client.api_root + '/organization_subscriptions/{id}.json'


class ZenDeskCoreOrganizationMemberships:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_organization_memberships = client.api_root + '/organization_memberships.json'
        self.api_organization_membership = client.api_root + '/organization_memberships/{id}.json'
        self.api_organization_memberships_create_many = client.api_root + '/organization_memberships/create_many.json'
        self.api_organization_memberships_destroy_many = client.api_root = '/organization_memberships/destroy_many.json'


class ZenDeskCoreViews:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_views = client.api_root + '/views.json'
        self.api_views_search = client.api_root + '/views/search.json'
        self.api_views_preview = client.api_root + '/views/preview.json'
        self.api_views_preview_count = client.api_root + '/views/preview/count.json'
        self.api_view = client.api_root + '/views/{id}.json'
        self.api_view_execute = client.api_root + '/views/{id}/execute.json'
        self.api_view_tickets = client.api_root + '/views/{id}/tickets.json'
        self.api_view_count = client.api_root + '/views/{id}/count.json'
        self.api_view_export = client.api_root + '/views/{id}/export.json'
        self.api_views_active = client.api_root + '/views/active.json'
        self.api_views_compact = client.api_root + '/views/compact.json'
        self.api_view_count_many = client.api_root + '/views/count_many.json'


class ZenDeskCoreOrganizationFields:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_organization_fields = client.api_root + '/organization_fields.json'
        self.api_organization_fields_reorder = client.api_root + '/organization_fields/reorder.json'
        self.api_organization_field = client.api_root + '/organization_fields/{id}.json'


class ZenDeskCoreActivities:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_activities = client.api_root + '/activities.json'
        self.api_activity = client.api_root + '/activities/{id}.json'


class ZenDeskCoreTags:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_tags = client.api_root + '/tags.json'
        self.autocomplete_tags = client.api_root + '/autocomplete/tags.json'


class ZenDeskCoreTopics:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.topic_tags = client.api_root + '/topics/{id}/tags.json'


class ZenDeskCore:
    def __init__(self, client):
        self.client = client

        # Children
        self.search = ZenDeskCoreSearch(client, self)
        self.tickets = ZenDeskCoreTickets(client, self)
        self.organizations = ZenDeskCoreOrganizations(client, self)
        self.users = ZenDeskCoreUsers(client, self)
        self.groups = ZenDeskCoreGroups(client, self)
        self.group_memberships = ZenDeskCoreGroupMemberships(client, self)
        self.suspended_tickets = ZenDeskCoreSuspendedTickets(client, self)
        self.ticket_metrics = ZenDeskCoreTicketMetrics(client, self)
        self.incremental = ZenDeskCoreIncremental(client, self)
        self.organization_subscriptions = ZenDeskCoreOrganizationSubscriptions(client, self)
        self.organization_memberships = ZenDeskCoreOrganizationMemberships(client, self)
        self.views = ZenDeskCoreViews(client, self)
        self.organization_fields = ZenDeskCoreOrganizationFields(client, self)
        self.activities = ZenDeskCoreActivities(client, self)
        self.tags = ZenDeskCoreTags(client, self)
        self.topics = ZenDeskCoreTopics(client, self)

        # The following API endpoints aren't supported at this time.
        self.incremental_exports = NotImplemented
        self.job_statuses = NotImplemented
        self.ticket_import = NotImplemented
        self.requests = NotImplemented
        self.attachments = NotImplemented
        self.satisfaction_ratings = NotImplemented
        self.satisfaction_reasons = NotImplemented
        self.ticket_audits = NotImplemented
        self.ticket_skips = NotImplemented
        self.custom_agent_roles = NotImplemented
        self.end_users = NotImplemented
        self.sessions = NotImplemented
        self.automations = NotImplemented
        self.macros = NotImplemented
        self.sla_policies = NotImplemented
        self.targets = NotImplemented
        self.triggers = NotImplemented
        self.account_settings = NotImplemented
        self.audit_logs = NotImplemented
        self.brands = NotImplemented
        self.dynamic_content = NotImplemented
        self.locales = NotImplemented
        self.schedules = NotImplemented
        self.sharing_agreements = NotImplemented
        self.support_addresses = NotImplemented
        self.ticket_forms = NotImplemented
        self.ticket_fields = NotImplemented
        self.user_fields = NotImplemented
        self.apps = NotImplemented
        self.app_installation_locations = NotImplemented
        self.app_locations = NotImplemented
        self.oauth_clients = NotImplemented
        self.oauth_tokens = NotImplemented
        self.authorized_global_clients = NotImplemented
        self.bookmarks = NotImplemented
        self.push_notification_devices = NotImplemented
        self.resource_collections = NotImplemented
        self.channel_framework = NotImplemented
        self.twitter_channel = NotImplemented


class ZenDeskHelpCenterCategories:
    def __init__(self, client, parent):
        """ Categories in the ZenDesk Help Center

        Args:
            client (ZenDeskClient): the ZenDesk Python client instance
            parent (ZenDeskHelpCenter): the ZenDesk Help Center instance
        """
        self.client = client
        self.parent = parent
        self._api_hc_categories = parent.api_hc + '/categories.json'
        self._api_hc_category = parent.api_hc + '/categories/{category_id}.json'

    def get(self, category_id=None):
        if id:
            return self.client._get(self._api_hc_category.format(category_id=category_id))
        return self.client._get(self._api_hc_categories)


class ZenDeskHelpCenterSections:
    def __init__(self, client, parent):
        """ Sections in the ZenDesk Help Center

        Args:
            client (ZenDeskClient): the ZenDesk Python client instance
            parent (ZenDeskHelpCenter): the ZenDesk Help Center instance
        """
        self.client = client
        self.parent = parent
        self._api_hc_sections = parent.api_hc + '/sections.json'
        self._api_hc_section = parent.api_hc + '/sections/{section_id}.json'
        self._api_hc_section_articles = parent.api_hc + '/sections/{section_id}/articles.json'
        self._api_hc_section_subscriptions = parent.api_hc + '/sections/{section_id}/subscriptions.json'
        self._api_hc_section_subscription = parent.api_hc + '/sections/{section_id}/subscriptions/{id}.json'

    def get(self, section_id=None):
        if id:
            return self.client._get(self._api_hc_section.format(section_id=section_id))
        return self.client._get(self._api_hc_sections)

    def get_articles(self, section_id):
        return self.client._get(self._api_hc_section_articles.format(section_id=section_id))

    def get_subscriptions(self, section_id):
        return self.client._get(self._api_hc_section_subscriptions.format(section_id=section_id))

    def get_subscription(self, section_id, subscription_id):
        return self.client._get(self._api_hc_section_subscription.format(section_id=section_id, id=subscription_id))


class ZenDeskHelpCenterArticles:
    def __init__(self, client, parent):
        """ Articles in the ZenDesk Help Center

        Args:
            client (ZenDeskClient): the ZenDesk Python client instance
            parent (ZenDeskHelpCenter): the ZenDesk Help Center instance
        """
        self.client = client
        self.parent = parent
        self._api_hc_articles = parent.api_hc + '/articles.json'
        self._api_hc_article = parent.api_hc + '/articles/{id}.json'
        self._api_hc_article_labels = parent.api_hc + '/articles/{id}/labels.json'
        self._api_hc_article_comments = parent.api_hc + '/articles/{id}/comments.json'
        self._api_hc_article_comment = parent.api_hc + '/articles/{article_id}/comments/{id}.json'
        self._api_hc_article_attachments = parent.api_hc + '/articles/{article_id}/attachments.json'
        self._api_hc_article_attachment = parent.api_hc + '/articles/attachments/{id}.json'
        self._api_hc_article_attachments_inline = parent.api_hc + '/articles/{article_id}/attachments/inline.json'
        self._api_hc_article_attachments_block = parent.api_hc + '/articles/{article_id}/attachments/block.json'
        self._api_hc_labels = parent.api_hc + '/articles/labels.json'
        self._api_hc_label = parent.api_hc + '/articles/labels/{id}.json'
        self._api_hc_article_subscriptions = parent.api_hc + '/articles/{article_id}/subscriptions.json'
        self._api_hc_article_subscription = parent.api_hc + '/articles/{article_id}/subscriptions/{id}.json'
        self._api_hc_search_articles = parent.api_hc + '/articles/search.json'
        self._api_hc_article_translations = parent.api_hc + '/articles/{article_id}/translations.json'
        self._api_hc_article_translation = parent.api_hc + '/articles/{article_id}/translations/{locale}.json'

    def get(self, article_id=None, filter_labels=None):
        if article_id:
            return self.client._get(self._api_hc_article.format(article_id=article_id))
        if filter_labels:
            if not isinstance(filter_labels, list):
                filter_labels = [filter_labels]
            return self.client._get(self._api_hc_articles, querystring={'label_names': ','.join(filter_labels)})
        return self.client._get(self._api_hc_articles)

    def update(self, article_id, updates):
        return self.client._put(self._api_hc_article.format(id=article_id), data=updates)

    def get_translations(self, article_id, locale=None):
        if locale:
            return self.client._get(self._api_hc_article_translation.format(article_id=article_id, locale=locale))
        return self.client._get(self._api_hc_article_translations.format(article_id=article_id))

    def update_translation(self, article_id, updates, locale="en-us"):
        return self.client._put(
            self._api_hc_article_translation.format(article_id=article_id, locale=locale),
            {"translation": updates}
        )

    def search(self, query):
        return self.client._get(self._api_hc_search_articles, querystring={'query': query})

    def get_article_labels(self, article_id):
        return self.client._get(self._api_hc_article_labels.format(id=article_id))

    def get_comments(self, article_id):
        return self.client._get(self._api_hc_article_comments.format(id=article_id))

    def get_labels(self, label_id=None):
        if label_id:
            return self.client._get(self._api_hc_labels.format(id=label_id))
        return self.client._get(self._api_hc_labels)

    def get_comment(self, article_id, comment_id):
        return self.client._get(self._api_hc_article_comment.format(article_id=article_id, id=comment_id))

    def get_subscriptions(self, article_id, subscription_id=None):
        if subscription_id:
            return self.client._get(self._api_hc_article_subscription.format(article_id=article_id, id=subscription_id))
        return self.client._get(self._api_hc_article_subscriptions.format(article_id=article_id))

    def get_attachments(self, article_id, fmt=None):
        if fmt and fmt == 'inline':
            return self.client._get(self._api_hc_article_attachments_inline.format(article_id=article_id))
        if fmt and fmt == 'block':
            return self.client._get(self._api_hc_article_attachments_block.format(article_id=article_id))
        return self.client._get(self._api_hc_article_attachments.format(article_id=article_id))

    def get_attachment(self, attachment_id):
        return self.client._get(self._api_hc_article_attachment.format(id=attachment_id))



class ZenDeskHelpCenterUsers:
    def __init__(self, client, parent):
        """ The ZenDesk Help Center

        Args:
            client (ZenDeskClient): the ZenDesk Python client instance
            parent (ZenDeskHelpCenter): the ZenDesk Help Center instance
        """
        self.client = client
        self.parent = parent
        self.api_hc_user_subscriptions = parent.api_hc + '/users/{user_id}/subscriptions.json'
        self.api_hc_user_comments = parent.api_hc + '/users/{id}/comments.json'


class ZenDeskHelpCenter:
    def __init__(self, client):
        """

        Args:
            client (ZenDeskClient): the ZenDesk Python client instance
        """
        self.client = client
        self.api_hc = self.client.api_root + '/help_center'
        self.categories = ZenDeskHelpCenterCategories(client, self)
        self.sections = ZenDeskHelpCenterSections(client, self)
        self.articles = ZenDeskHelpCenterArticles(client, self)


class ZenDeskCommunityTopics:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_c_topics = parent.api_c + '/topics.json'
        self.api_c_topic = parent.api_c + '/topics/{id}.json'
        self.api_c_topic_posts = parent.api_c + '/topics/{id}/posts.json'
        self.api_c_topic_subscriptions = parent.api_c + '/topics/{topic_id}/subscriptions.json'
        self.api_c_topic_subscription = parent.api_c + '/topics/{topic_id}/subscriptions/{id}.json'
        

class ZenDeskCommunityPosts:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_c_posts = parent.api_c + '/posts.json'
        self.api_c_post = parent.api_c + '/posts/{id}.json'
        self.api_c_post_comments = parent.api_c + '/posts/{post_id}/comments.json'
        self.api_c_comment = parent.api_c + '/posts/{post_id}/comments/{id}.json'
        self.api_c_post_subscriptions = parent.api_c + '/posts/{post_id}/subscriptions.json'
        self.api_c_post_subscription = parent.api_c + '/posts/{post_id}/subscriptions/{id}.json'


class ZenDeskCommunityUsers:
    def __init__(self, client, parent):
        self.client = client
        self.parent = parent
        self.api_c_user_posts = parent.api_c + '/users/{id}/posts.json'
        self.api_c_user_comments = parent.api_c + '/users/{id}/comments.json'

        
class ZenDeskCommunity:
    def __init__(self, client):
        self.client = client
        self.api_c = self.client.api_root + '/community'
        self.topics = ZenDeskCommunityTopics(client, self)
        self.posts = ZenDeskCommunityPosts(client, self)
        self.users = ZenDeskCommunityUsers(client, self)


class ZenDeskClient:
    def __init__(self, api_uid, api_token, api_endpoint):
        self.api_uid = api_uid
        self.api_token = api_token
        self.api_endpoint = api_endpoint
        self.locale = 'en'
        self.auth = ('{}/token'.format(self.api_uid), self.api_token)
        self.api_root = 'https://{}/api/v2'.format(self.api_endpoint)

        self.help_center = ZenDeskHelpCenter(self)
        self.community = ZenDeskCommunity(self)
        self.core = ZenDeskCore(self)

    def _get(self, uri, querystring=None):
        _querystring = querystring.copy() if querystring else {}
        response = requests.get(uri, params=_querystring, auth=self.auth)
        return response.json()

    def _put(self, uri, json):
        response = requests.put(uri, json=json, auth=self.auth)
        return response
