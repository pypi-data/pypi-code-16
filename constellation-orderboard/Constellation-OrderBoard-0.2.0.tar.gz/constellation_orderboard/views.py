import json

from django.contrib.auth.models import Group
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from guardian.decorators import (
    permission_required,
    permission_required_or_403,
)
from guardian.shortcuts import get_objects_for_user

from constellation_base.models import GlobalTemplateSettings

from .forms import CardForm
from .forms import StageForm
from .forms import BoardForm

from .models import Card
from .models import Stage
from .models import Board


# =============================================================================
# View Functions
# =============================================================================

@login_required
def view_list(request):
    '''Return the base template that will call the API to display
    a list of boards'''
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()

    return render(request, 'constellation_orderboard/view-list.html', {
        'template_settings': template_settings,
    })


@login_required
@permission_required('constellation_orderboard.action_read_board',
                     (Board, 'id', 'board_id'))
def view_board(request, board_id):
    '''Return the base template that will call the API to display the
    entire board with all the cards'''
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    newForm = CardForm()
    editForm = CardForm(prefix="edit")
    board = Board.objects.get(pk=board_id)

    return render(request, 'constellation_orderboard/board.html', {
        'form': newForm,
        'editForm': editForm,
        'id': board_id,
        'template_settings': template_settings,
        'board': board,
    })


@login_required
@permission_required('constellation_orderboard.action_archive_cards',
                     (Board, 'id', 'board_id'))
def view_board_archive(request, board_id):
    '''Return the base template that will call the API to display the
    board's archived cards'''
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()

    return render(request, 'constellation_orderboard/archive.html', {
        'id': board_id,
        'template_settings': template_settings,
    })

# =============================================================================
# Management Functions
# =============================================================================


@login_required
@permission_required('constellation_orderboard.add_board')
def manage_boards(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    boardForm = BoardForm()
    groups = [(g.name, g.pk) for g in Group.objects.all()]

    return render(request, 'constellation_orderboard/manage-boards.html', {
        'form': boardForm,
        'template_settings': template_settings,
        'groups': groups,
    })


@login_required
@permission_required('constellation_orderboard.action_manage_board',
                     (Board, 'id', 'board_id'))
def manage_board_edit(request, board_id):
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    board = Board.objects.get(pk=board_id)
    boardForm = BoardForm(instance=board)
    groups = board.get_board_permissions()

    return render(request, 'constellation_orderboard/edit-board.html', {
        'form': boardForm,
        'board_id': board_id,
        'template_settings': template_settings,
        'groups': groups,
    })


@login_required
@permission_required('constellation_orderboard.change_stage')
def manage_stages(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    stageForm = StageForm()
    return render(request, "constellation_orderboard/manage-stages.html", {
        'form': stageForm,
        'template_settings': template_settings,
    })


# =============================================================================
# API Functions for the v1 API
# =============================================================================

    # The functions in this section handle API calls for creating,
    # activating, and deactivating boards, creating, moving, and archiving
    # cards, and creating, activating, deactivating, and updating states.

# -----------------------------------------------------------------------------
# API Functions related to Board Operations
# -----------------------------------------------------------------------------
@login_required
def api_v1_board_list(request):
    '''List all boards that a user is allowed to view'''
    boardObjects = get_objects_for_user(
        request.user,
        'constellation_orderboard.action_read_board',
        Board)
    if boardObjects:
        boards = serializers.serialize('json', boardObjects)
        return HttpResponse(boards)
    else:
        return HttpResponseNotFound("You have no boards at this time")


@login_required
@permission_required_or_403('constellation_orderboard.add_board')
def api_v1_board_create(request):
    '''Create a board, takes a post with a CSRF token, name, and
    description and returns a json object containing the status which will
    be either 'success' or 'fail' and a friendly message'''
    boardForm = BoardForm(request.POST or None)
    if request.POST and boardForm.is_valid():
        newBoard = Board()
        newBoard.name = boardForm.cleaned_data['name']
        newBoard.desc = boardForm.cleaned_data['desc']
        try:
            newBoard.save()
            newBoard.set_board_permissions(request.POST.items())
            return HttpResponse(serializers.serialize('json', [newBoard, ]))
        except:
            return HttpResponseServerError("Could not save board at this time")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@permission_required_or_403('constellation_orderboard.action_manage_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_update(request, board_id):
    '''Update a board, based upon the form data contained in request'''
    boardForm = BoardForm(request.POST or None)
    if request.POST and boardForm.is_valid():

        try:
            board = Board.objects.get(pk=board_id)
            board.set_board_permissions(request.POST.items())
            newName = boardForm.cleaned_data['name']
            newDesc = boardForm.cleaned_data['desc']

            board.name = newName
            board.desc = newDesc
            board.save()
            return HttpResponse(json.dumps({
                "board": reverse("view_board", args=[board_id, ])
            }))
        except AttributeError:
            return HttpResponseServerError("Invalid board ID")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@permission_required_or_403('constellation_orderboard.action_manage_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_archive(request, board_id):
    '''archives a board, returns status object'''
    board = Board.objects.get(pk=board_id)
    board.archived = True
    try:
        board.save()
        return HttpResponse("Board Archived")
    except:
        return HttpResponseServerError("Board could not be archived")


@login_required
@permission_required_or_403('constellation_orderboard.action_manage_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_unarchive(request, board_id):
    '''unarchives a board, returns status object'''
    board = Board.objects.get(pk=board_id)
    board.archived = False
    try:
        board.save()
        return HttpResponse("Board Un-Archived")
    except:
        return HttpResponseServerError("Board could not be un-archived")


@login_required
@permission_required_or_403('constellation_orderboard.action_read_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_active_cards(request, board_id):
    '''Retrieve all active cards for the stated board'''
    cardObjects = Card.objects.filter(board=Board.objects.get(pk=board_id),
                                      archived=False)
    if cardObjects:
        cards = serializers.serialize('json', cardObjects)
        return HttpResponse(cards)
    else:
        return HttpResponseNotFound("There are no active cards on this board")


@login_required
@permission_required_or_403('constellation_orderboard.action_read_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_archived_cards(request, board_id):
    '''Retrieve all archived cards for the stated board'''
    cardObjects = Card.objects.filter(board=Board.objects.get(pk=board_id),
                                      archived=True)
    if cardObjects:
        cards = serializers.serialize('json', cardObjects)
        return HttpResponse(cards)
    else:
        return HttpResponseNotFound("This board has no archived cards")


@login_required
@permission_required_or_403('constellation_orderboard.action_read_board',
                            (Board, 'id', 'board_id'))
def api_v1_board_info(request, board_id):
    '''Retrieve the title and description for the stated board'''
    try:
        board = Board.objects.get(pk=board_id)
        response = json.dumps({"title": board.name, "desc": board.desc})
        return HttpResponse(response)
    except:
        return HttpResponseNotFound("No board with given ID found")


# -----------------------------------------------------------------------------
# API Functions related to Card Operations
# -----------------------------------------------------------------------------
@login_required
@permission_required_or_403('constellation_orderboard.action_add_cards',
                            (Board, 'id', 'board_id'))
def api_v1_card_create(request, board_id):
    '''Creates a new card from POST data.  Takes in a CSRF token with the
    data as well as card name, quantity, units, description, board reference,
    and active state'''
    cardForm = CardForm(request.POST or None)
    if request.POST and cardForm.is_valid():
        newCard = Card()
        newCard.name = cardForm.cleaned_data['name']
        newCard.quantity = cardForm.cleaned_data['quantity']
        newCard.units = cardForm.cleaned_data['units']
        newCard.notes = cardForm.cleaned_data['notes']
        newCard.stage = cardForm.cleaned_data['stage']
        newCard.board = get_object_or_404(Board, id=board_id)
        newCard.archived = False
        try:
            newCard.save()
            return HttpResponse(serializers.serialize('json', [newCard, ]))
        except:
            return HttpResponseServerError("Could not create card")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@permission_required_or_403('constellation_orderboard.action_add_cards',
                            (Board, 'pk', 'board_id'))
def api_v1_card_edit(request, board_id, card_id):
    '''Edits an existing card from POST data.  Takes in a CSRF token with the
    data as well as card name, quantity, units, and description'''
    cardForm = CardForm(request.POST or None, prefix="edit")
    if request.POST and cardForm.is_valid():
        card = Card.objects.get(pk=card_id)
        card.name = cardForm.cleaned_data['name']
        card.quantity = cardForm.cleaned_data['quantity']
        card.units = cardForm.cleaned_data['units']
        card.notes = cardForm.cleaned_data['notes']
        try:
            card.save()
            return HttpResponse(serializers.serialize('json', [card, ]))
        except:
            return HttpResponseServerError("Could not create card")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@permission_required_or_403('constellation_orderboard.action_archive_cards',
                            (Board, 'pk', 'board_id'))
def api_v1_card_archive(request, board_id, card_id):
    '''Archive a card identified by the given primary key'''
    card = Card.objects.get(pk=card_id)
    card.archived = True
    try:
        card.save()
        return HttpResponse("Card successfully archived")
    except:
        return HttpResponseServerError("Card could not be archived")


@login_required
@permission_required_or_403('constellation_orderboard.action_archive_cards',
                            (Board, 'pk', 'board_id'))
def api_v1_card_unarchive(request, board_id, card_id):
    '''Unarchive a card identified by the given primary key'''
    card = Card.objects.get(pk=card_id)
    card.archived = False
    try:
        card.save()
        return HttpResponse("Card successfully un-archived")
    except:
        return HttpResponseServerError("Card could not be un-archived")


@login_required
@permission_required_or_403('constellation_orderboard.action_move_cards',
                            (Board, 'pk', 'board_id'))
def api_v1_card_move_right(request, board_id, card_id):
    '''Move a card to the next stage to the left'''
    stages = list(Stage.objects.filter(archived=False))
    stages.sort(key=lambda x: x.index)

    card = get_object_or_404(Card, pk=card_id)
    stageID = stages.index(card.stage)

    try:
        card.stage = stages[stageID + 1]
        card.save()
        retVal = {}
        retVal['status'] = "success"
        retVal['msg'] = "Card unarchived successfully"
        retVal['stageName'] = card.stage.name
        retVal['stageID'] = card.stage.pk
        return HttpResponse(json.dumps(retVal))
    except:
        return HttpResponseServerError("Card could not be moved at this time")


@login_required
@permission_required_or_403('constellation_orderboard.action_move_cards',
                            (Board, 'pk', 'board_id'))
def api_v1_card_move_left(request, board_id, card_id):
    '''Move a card to the next stage to the left'''
    stages = list(Stage.objects.filter(archived=False))
    stages.sort(key=lambda x: x.index)

    card = get_object_or_404(Card, pk=card_id)
    stageID = stages.index(card.stage)

    try:
        if stageID - 1 < 0:
            raise IndexError
        card.stage = stages[stageID - 1]
        card.save()
        retVal = {}
        retVal['status'] = "success"
        retVal['msg'] = "Card unarchived successfully"
        retVal['stageName'] = card.stage.name
        retVal['stageID'] = card.stage.pk
        return HttpResponse(json.dumps(retVal))
    except:
        return HttpResponseServerError("Card could not be moved at this time")


# -----------------------------------------------------------------------------
# API Functions related to Stage Operations
# -----------------------------------------------------------------------------
@login_required
def api_v1_stage_list(request):
    '''List all stages, can be filtered by the client, will return a list
    of all stages, including stages that the client is not authorized to
    use.'''
    stageObjects = Stage.objects.all()
    if stageObjects:
        stages = serializers.serialize('json', Stage.objects.all())
        return HttpResponse(stages)
    else:
        return HttpResponseNotFound("There are no stages defined")


@login_required
@permission_required_or_403('constellation_orderboard.modify_stages',
                            raise_exception=True)
def api_v1_stage_create(request):
    '''Creates a new stage from POST data.  Takes in a CSRF token with the
    data as well as stage name, quantity, description, board reference, and
    active state'''
    stageForm = StageForm(request.POST or None)
    if request.POST and stageForm.is_valid():
        newStage = Stage()
        newStage.name = stageForm.cleaned_data['name']
        newStage.index = -1   # The model save function will append the stage
        newStage.archived = False
        try:
            newStage.save()
            return HttpResponse(serializers.serialize('json', [newStage, ]))
        except:
            return HttpResponseServerError("Stage could not be created")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@permission_required_or_403('constellation_orderboard.modify_stages',
                            raise_exception=True)
def api_v1_stage_archive(request, stageID):
    '''Archive a stage identified by the given primary key'''
    stage = Stage.objects.get(pk=stageID)
    stage.archived = True
    try:
        stage.save()
        return HttpResponse("Stage successfully archived")
    except:
        return HttpResponseServerError("Stage could not be archived")


@permission_required_or_403('constellation_orderboard.modify_stages',
                            raise_exception=True)
def api_v1_stage_unarchive(request, stageID):
    '''Unarchive a stage identified by the given primary key'''
    stage = Stage.objects.get(pk=stageID)
    stage.archived = False
    try:
        stage.save()
        return HttpResponse("Stage successfully un-archived")
    except:
        return HttpResponse("Stage could not be un-archived at this time")


@permission_required_or_403('constellation_orderboard.modify_stages',
                            raise_exception=True)
def api_v1_stage_move_left(request, stageID):
    '''Move a stage to the left'''
    stageCurrent = Stage.objects.get(pk=stageID)
    if stageCurrent.index > 0:
        stageLeft = Stage.objects.get(index=stageCurrent.index-1)
        try:
            stageCurrent.swap(stageLeft)
            return HttpResponse("Stage successfully moved")
        except:
            return HttpResponseServerError("Stage could not be moved")
    else:
        return HttpResponseBadRequest("Stage cannot be moved")


@permission_required_or_403('constellation_orderboard.modify_stages',
                            raise_exception=True)
def api_v1_stage_move_right(request, stageID):
    '''Move a stage to the right'''
    stageCurrent = Stage.objects.get(pk=stageID)
    try:
        stageRight = Stage.objects.get(index=stageCurrent.index+1)
        stageCurrent.swap(stageRight)
        return HttpResponse("Stage successfully moved")
    except:
        return HttpResponseServerError("Stage could not be moved at this time")

# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------


@login_required
def view_dashboard(request):
    '''Return a card that will appear on the main dashboard'''

    return render(request, 'constellation_orderboard/dashboard.html')
