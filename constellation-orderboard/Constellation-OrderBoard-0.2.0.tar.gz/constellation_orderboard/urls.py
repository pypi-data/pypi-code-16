from django.conf.urls import url

from . import views

urlpatterns = [
# =============================================================================
# View Routes
# =============================================================================

    url(r'^view/list$', views.view_list,
        name="view_list"),
    url(r'^view/board/(?P<board_id>\d+)$', views.view_board,
        name="view_board"),
    url(r'^view/board/(?P<board_id>\d+)/archive$', views.view_board_archive,
        name="view_board_archive"),

# =============================================================================
# Management Routes
# =============================================================================

    url(r'^manage/boards$', views.manage_boards,
        name="manage_boards"),
    url(r'^manage/board/(?P<board_id>\d+)/edit$', views.manage_board_edit,
        name="manage_board_edit"),
    url(r'^manage/stages$', views.manage_stages,
        name="manage_stages"),

# =============================================================================
# API Routes for the v1 API
# =============================================================================

    # The API routes are divided into functional groups based on what
    # they control.  In general each group will contain the standard
    # CRUD calls, but may also contain additional calls for specific
    # objects.

# -----------------------------------------------------------------------------
# API Routes related to Board Operations
# -----------------------------------------------------------------------------

    url(r'^api/v1/board/list$',
        views.api_v1_board_list,
        name="api_v1_board_list"),

    url(r'^api/v1/board/create$',
        views.api_v1_board_create,
        name="api_v1_board_create"),

    url(r'^api/v1/board/(?P<board_id>\d+)/update$',
        views.api_v1_board_update,
        name="api_v1_board_update"),

    url(r'^api/v1/board/(?P<board_id>\d+)/archive$',
        views.api_v1_board_archive,
        name="api_v1_board_archive"),

    url(r'^api/v1/board/(?P<board_id>\d+)/unarchive$',
        views.api_v1_board_unarchive,
        name="api_v1_board_unarchive"),

    url(r'^api/v1/board/(?P<board_id>\d+)/active-cards$',
        views.api_v1_board_active_cards,
        name="api_v1_board_active_cards"),

    url(r'^api/v1/board/(?P<board_id>\d+)/archived-cards$',
        views.api_v1_board_archived_cards,
        name="api_v1_board_archived_cards"),

    url(r'^api/v1/board/(?P<board_id>\d+)/info$',
        views.api_v1_board_info,
        name="api_v1_board_info"),

# -----------------------------------------------------------------------------
# API Routes related to Card Operations
# -----------------------------------------------------------------------------

    url(r'^api/v1/card/create-on/(?P<board_id>\d+)$',
        views.api_v1_card_create,
        name="api_v1_card_create"),

    url(r'^api/v1/card/(?P<board_id>\d+)-(?P<card_id>\d+)/edit$',
        views.api_v1_card_edit,
        name="api_v1_card_edit"),

    url(r'^api/v1/card/(?P<board_id>\d+)-(?P<card_id>\d+)/archive$',
        views.api_v1_card_archive,
        name="api_v1_card_archive"),

    url(r'^api/v1/card/(?P<board_id>\d+)-(?P<card_id>\d+)/unarchive$',
        views.api_v1_card_unarchive,
        name="api_v1_card_unarchive"),

    url(r'^api/v1/card/(?P<board_id>\d+)-(?P<card_id>\d+)/move-right$',
        views.api_v1_card_move_right,
        name="api_v1_card_move_right"),

    url(r'^api/v1/card/(?P<board_id>\d+)-(?P<card_id>\d+)/move-left$',
        views.api_v1_card_move_left,
        name="api_v1_card_move_left"),

# -----------------------------------------------------------------------------
# API Routes related to Stage Operations
# -----------------------------------------------------------------------------

    url(r'^api/v1/stage/list$', views.api_v1_stage_list,
        name="api_v1_stage_list"),
    url(r'^api/v1/stage/create$', views.api_v1_stage_create,
        name="api_v1_stage_create"),
    url(r'^api/v1/stage/([\d]*)/archive$', views.api_v1_stage_archive,
        name="api_v1_stage_archive"),
    url(r'^api/v1/stage/([\d]*)/unarchive$', views.api_v1_stage_unarchive,
        name="api_v1_stage_unarchive"),
    url(r'^api/v1/stage/([\d]*)/move-left$', views.api_v1_stage_move_left,
        name="api_v1_stage_move_left"),
    url(r'^api/v1/stage/([\d]*)/move-right$', views.api_v1_stage_move_right,
        name="api_v1_stage_move_right"),

# -----------------------------------------------------------------------------
# Dashboard routes
# -----------------------------------------------------------------------------

    url(r'^view/dashboard$', views.view_dashboard,
        name="view_dashboard"),

]
