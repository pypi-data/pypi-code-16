from django import template
from django.template.loader import render_to_string

from ..models import Like


register = template.Library()


@register.simple_tag(takes_context=True)
def like_button(context, target):
    user = context['request'].user

    # do nothing when user isn't authenticated
    if not user.is_authenticated():
        return ''

    target_model = '.'.join((target._meta.app_label, target._meta.object_name))

    undo = False
    # prepare button to unlike if the user
    # already liked this object
    if Like.objects.get_like(user, target):
        undo = True

    return render_to_string(
        'like/button.html', {
            'target_model': target_model,
            'target_object_id': target.id,
            'undo': undo,
            'like_count': Like.objects.for_object(target).count()
        }
    )



@register.filter
def get_like_for(obj, user):
    """
    Get Like instance for an object (obj) and a user (user)

    Usage:
    {% with obj|get_like_for:user as like_object %}
        ...
    {% endwith %}
    """

    return Like.objects.get_like(user, obj)


@register.filter
def likes_count(obj):
    """
    Usage:

    Given an object `obj` you may show it Like count like this:

    <p>Like Count {{ obj|likes_count }}</p>
    """

    return Like.objects.for_object(obj).count()


@register.assignment_tag
def user_likes(user, app_model=None):
    """
    Usage:

    Get all user liked objects:

        {% with user_likes <user> as like_list %}
            {% for like_obj in like_list %}
                {# do something with like_obj #}
            {% endfor %}
        {% endwith %}

    or, just likes from one model:

        {% with user_likes <user> "app_label.model" as like_list %}
            {% for like_obj in like_list %}
                {# do something with like_obj #}
            {%
        {% endwith %}
    """

    return Like.objects.for_user(user, app_model)


@register.assignment_tag
def model_likes(app_model):
    """
    Gets all liked objects that are instances of a model
    given in module notation.

    Usage:

        {% with model_likes "app_label.model" as like_list %}
            {% for like_obj in like_list %}
                {# do something with like_obj #}
            {% endfor %}
        {% endwith %}
    """

    return Like.objects.for_model(app_model)
