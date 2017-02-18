import json

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import (
    login_required,
    permission_required
)

from constellation_base.models import GlobalTemplateSettings

from .forms import CardForm
from .forms import StageForm
from .forms import BoardForm

from .models import Card
from .models import Stage
from .models import Board

from .util import board_permission, board_perms


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
@board_permission('read')
def view_board(request, board_id):
    '''Return the base template that will call the API to display the
    entire board with all the cards'''
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    newForm = CardForm()
    editForm = CardForm(prefix="edit")

    can_move = board_perms(request.user, 'move', board_id)
    can_add = board_perms(request.user, 'add', board_id)
    can_delete = board_perms(request.user, 'delete', board_id)

    return render(request, 'constellation_orderboard/board.html', {
        'form': newForm,
        'editForm': editForm,
        'id': board_id,
        'template_settings': template_settings,
        'can_move': can_move,
        'can_add': can_add,
        'can_delete': can_delete,
    })


@login_required
@board_permission('read')
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
@permission_required('constellation_orderboard.create_board')
def manage_boards(request):
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    boardForm = BoardForm()

    return render(request, 'constellation_orderboard/manage-boards.html', {
        'form': boardForm,
        'template_settings': template_settings,
    })


@login_required
@board_permission('manage')
def manage_board_edit(request, board_id):
    template_settings_object = GlobalTemplateSettings(allowBackground=False)
    template_settings = template_settings_object.settings_dict()
    board = Board.objects.get(pk=board_id)
    boardForm = BoardForm(instance=board)
    return render(request, 'constellation_orderboard/edit-board.html', {
        'form': boardForm,
        'board_id': board_id,
        'template_settings': template_settings,
    })


@login_required
@permission_required('constellation_orderboard.modify_stages')
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
    if not request.user.is_superuser:
        boardObjects = Board.objects.filter(pk__in=request.user.groups.all())
    else:
        boardObjects = Board.objects.all()
    if boardObjects:
        boards = serializers.serialize('json', boardObjects)
        return HttpResponse(boards)
    else:
        return HttpResponseNotFound("You have no boards at this time")


@login_required
@permission_required('constellation_orderboard.create_board')
def api_v1_board_create(request):
    '''Create a board, takes a post with a CSRF token, name, and
    description and returns a json object containing the status which will
    be either 'success' or 'fail' and a friendly message'''
    boardForm = BoardForm(request.POST or None)
    if request.POST and boardForm.is_valid():
        newBoard = Board()
        newBoard.name = boardForm.cleaned_data['name']
        newBoard.desc = boardForm.cleaned_data['desc']
        newBoard.readGroup = boardForm.cleaned_data['readGroup']
        newBoard.addGroup = boardForm.cleaned_data['addGroup']
        newBoard.moveGroup = boardForm.cleaned_data['moveGroup']
        newBoard.deleteGroup = boardForm.cleaned_data['deleteGroup']
        newBoard.manageGroup = boardForm.cleaned_data['manageGroup']
        try:
            newBoard.save()
            return HttpResponse(serializers.serialize('json', [newBoard,]))
        except:
            return HttpResponseServerError("Could not save board at this time")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@board_permission('manage')
def api_v1_board_update(request, boardID):
    '''Update a board, based upon the form data contained in request'''
    boardForm = BoardForm(request.POST or None)
    if request.POST and boardForm.is_valid():
        try:
            board = Board.objects.get(pk=boardID)
            newName = boardForm.cleaned_data['name']
            newDesc = boardForm.cleaned_data['desc']
            board.name = newName
            board.desc = newDesc
            board.readGroup = boardForm.cleaned_data['readGroup']
            board.addGroup = boardForm.cleaned_data['addGroup']
            board.moveGroup = boardForm.cleaned_data['moveGroup']
            board.deleteGroup = boardForm.cleaned_data['deleteGroup']
            board.manageGroup = boardForm.cleaned_data['manageGroup']
            board.save()
            return HttpResponse(json.dumps({"board" : reverse("view_board", args=[boardID,])}))
        except:
            return HttpResponseServerError("Invalid board ID")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
@board_permission('manage')
def api_v1_board_archive(request, boardID):
    '''archives a board, returns status object'''
    board = Board.objects.get(pk=boardID)
    board.archived = True
    try:
        board.save()
        return HttpResponse("Board Archived")
    except:
        return HttpResponseServerError("Board could not be archived at this time")


@login_required
@board_permission('manage')
def api_v1_board_unarchive(request, boardID):
    '''unarchives a board, returns status object'''
    board = Board.objects.get(pk=boardID)
    board.archived = False
    try:
        board.save()
        return HttpResponse("Board Un-Archived")
    except:
        return HttpResponseServerError("Board could not be un-archived at this time")


@login_required
@board_permission('read')
def api_v1_board_active_cards(request, boardID):
    '''Retrieve all active cards for the stated board'''
    cardObjects = Card.objects.filter(board=Board.objects.get(pk=boardID),
                                      archived=False)
    if cardObjects:
        cards = serializers.serialize('json', cardObjects)
        return HttpResponse(cards)
    else:
        return HttpResponseNotFound("There are no active cards on this board")


@login_required
@board_permission('read')
def api_v1_board_archived_cards(request, boardID):
    '''Retrieve all archived cards for the stated board'''
    cardObjects = Card.objects.filter(board=Board.objects.get(pk=boardID),
                                      archived=True)
    if cardObjects:
        cards = serializers.serialize('json', cardObjects)
        return HttpResponse(cards)
    else:
        return HttpResponseNotFound("This board has no archived cards")


@login_required
@board_permission('read')
def api_v1_board_info(request, boardID):
    '''Retrieve the title and description for the stated board'''
    try:
        board = Board.objects.get(pk=boardID)
        response = json.dumps({"title" : board.name, "desc" : board.desc})
        return HttpResponse(response)
    except:
        return HttpResponseNotFound("No board with given ID found")


# -----------------------------------------------------------------------------
# API Functions related to Card Operations
# -----------------------------------------------------------------------------
@login_required
def api_v1_card_create(request):
    '''Creates a new card from POST data.  Takes in a CSRF token with the
    data as well as card name, quantity, units, description, board reference,
    and active state'''
    cardForm = CardForm(request.POST or None)
    if request.POST and cardForm.is_valid():
        if not board_perms(request.user, 'add',
                           cardForm.cleaned_data['board'].id):
            return HttpResponseServerError("Permission Denied")
        newCard = Card()
        newCard.name = cardForm.cleaned_data['name']
        newCard.quantity = cardForm.cleaned_data['quantity']
        newCard.units = cardForm.cleaned_data['units']
        newCard.notes = cardForm.cleaned_data['notes']
        newCard.stage = cardForm.cleaned_data['stage']
        newCard.board = cardForm.cleaned_data['board']
        newCard.archived = False
        try:
            newCard.save()
            return HttpResponse(serializers.serialize('json', [newCard,]))
        except:
            return HttpResponseServerError("Could not create card at this time")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@login_required
def api_v1_card_edit(request, cardID):
    '''Edits an existing card from POST data.  Takes in a CSRF token with the
    data as well as card name, quantity, units, and description'''
    cardForm = CardForm(request.POST or None, prefix="edit")
    if request.POST and cardForm.is_valid():
        if not board_perms(request.user, 'add',
                           cardForm.cleaned_data['board'].id):
            return HttpResponseServerError("Permission Denied")
        card = Card.objects.get(pk=cardID)
        card.name = cardForm.cleaned_data['name']
        card.quantity = cardForm.cleaned_data['quantity']
        card.units = cardForm.cleaned_data['units']
        card.notes = cardForm.cleaned_data['notes']
        try:
            card.save()
            return HttpResponse(serializers.serialize('json', [card,]))
        except:
            return HttpResponseServerError("Could not create card at this time")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")

@login_required
def api_v1_card_archive(request, cardID):
    '''Archive a card identified by the given primary key'''
    card = Card.objects.get(pk=cardID)

    if not board_perms(request.user, 'move',
                       card.board.id):
        return HttpResponseServerError("Permission Denied")
    card.archived = True
    try:
        card.save()
        return HttpResponse("Card successfully archived")
    except:
        return HttpResponseServerError("Card could not be archived at this time")


@login_required
def api_v1_card_unarchive(request, cardID):
    '''Unarchive a card identified by the given primary key'''
    card = Card.objects.get(pk=cardID)
    if not board_perms(request.user, 'move',
                       card.board.id):
        return HttpResponseServerError("Permission Denied")
    card.archived = False
    try:
        card.save()
        return HttpResponse("Card successfully un-archived")
    except:
        return HttpResponseServerError("Card could not be un-archived at this time")


@login_required
def api_v1_card_move_right(request, cardID):
    '''Move a card to the next stage to the left'''
    stages = list(Stage.objects.filter(archived=False))
    stages.sort(key=lambda x: x.index)

    card = get_object_or_404(Card, pk=cardID)
    if not board_perms(request.user, 'move',
                       card.board.id):
        return HttpResponseServerError("Permission Denied")
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
def api_v1_card_move_left(request, cardID):
    '''Move a card to the next stage to the left'''
    stages = list(Stage.objects.filter(archived=False))
    stages.sort(key=lambda x: x.index)

    card = get_object_or_404(Card, pk=cardID)
    if not board_perms(request.user, 'move',
                       card.board.id):
        return HttpResponseServerError("Permission Denied")
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
@permission_required('constellation_orderboard.modify_stages', raise_exception=True)
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
            return HttpResponse(serializers.serialize('json', [newStage,]))
        except:
            return HttpResponseServerError("Stage could not be created at this time")
    else:
        return HttpResponseBadRequest("Invalid Form Data!")


@permission_required('constellation_orderboard.modify_stages', raise_exception=True)
def api_v1_stage_archive(request, stageID):
    '''Archive a stage identified by the given primary key'''
    stage = Stage.objects.get(pk=stageID)
    stage.archived = True
    try:
        stage.save()
        return HttpResponse("Stage successfully archived")
    except:
        return HttpResponseServerError("Stage could not be archived at this time")


@permission_required('constellation_orderboard.modify_stages', raise_exception=True)
def api_v1_stage_unarchive(request, stageID):
    '''Unarchive a stage identified by the given primary key'''
    stage = Stage.objects.get(pk=stageID)
    stage.archived = False
    try:
        stage.save()
        return HttpResponse("Stage successfully un-archived")
    except:
        return HttpResponse("Stage could not be un-archived at this time")


@permission_required('constellation_orderboard.modify_stages', raise_exception=True)
def api_v1_stage_move_left(request, stageID):
    '''Move a stage to the left'''
    stageCurrent = Stage.objects.get(pk=stageID)
    if stageCurrent.index > 0:
        stageLeft = Stage.objects.get(index=stageCurrent.index-1)
        try:
            stageCurrent.swap(stageLeft)
            return HttpResponse("Stage successfully moved")
        except:
            return HttpResponseServerError("Stage could not be moved at this time")
    else:
        return HttpResponseBadRequest("Stage cannot be moved")


@permission_required('constellation_orderboard.modify_stages', raise_exception=True)
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
