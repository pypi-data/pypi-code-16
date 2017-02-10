from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Board


def board_permission(level):
    def deny(request):
        raise PermissionDenied

    def decorator(view_function):
        @wraps(view_function)
        def _inner(request, board_id, *args, **kwargs):
            board = get_object_or_404(Board, pk=board_id)

            if level == 'read':
                group = list(set([board.readGroup,
                                 board.addGroup,
                                 board.deleteGroup,
                                 board.moveGroup,
                                 board.manageGroup]))
            elif level == 'add':
                group = list(set([board.addGroup, board.deleteGroup,
                                 board.moveGroup, board.manageGroup]))
            elif level == 'move':
                group = list(set([board.deleteGroup, board.moveGroup,
                                  board.manageGroup]))
            elif level == 'delete':
                group = list(set([board.deleteGroup,
                                  board.manageGroup]))
            elif level == 'manage':
                group = [board.manageGroup]
            else:
                return view_function(request, board_id, *args, **kwargs)

            user = request.user
            if not user.is_authenticated():
                return deny(request)
            group = [f.name for f in group if f is not None]
            if len(group) == 0:
                return view_function(request, board_id, *args, **kwargs)

            if (user.groups.filter(name__in=group).exists() or
                    user.is_superuser):
                return view_function(request, board_id, *args, **kwargs)

            return deny(request)

        return _inner
    return decorator


def board_perms(user, level, board_id):
    board = Board.objects.get(pk=board_id)
    if level == 'read':
        group = list(set([board.readGroup,
                         board.addGroup,
                         board.deleteGroup,
                         board.moveGroup,
                         board.manageGroup]))
    elif level == 'add':
        group = list(set([board.addGroup, board.deleteGroup,
                         board.moveGroup, board.manageGroup]))
    elif level == 'move':
        group = list(set([board.deleteGroup, board.moveGroup,
                          board.manageGroup]))
    elif level == 'delete':
        group = list(set([board.deleteGroup,
                          board.manageGroup]))
    elif level == 'manage':
        group = [board.manageGroup]
    else:
        return True

    if not user.is_authenticated():
        return False
    group = [f.name for f in group if f is not None]
    if len(group) == 0:
        return True

    if (user.groups.filter(name__in=group).exists() or
            user.is_superuser):
        return True
