from enum import IntEnum


class QueueType(IntEnum):
    CUSTOM = 0
    NORMAL_3x3 = 8
    NORMAL_5x5_BLIND = 2
    NORMAL_5x5_DRAFT = 14
    RANKED_SOLO_5x5 = 4
    RANKED_PREMADE_5x5 = 6
    RANKED_FLEX_TT = 9
    RANKED_TEAM_3x3 = 41
    RANKED_TEAM_5x5 = 42
    ODIN_5x5_BLIND = 16
    ODIN_5x5_DRAFT = 17
    BOT_5x5 = 7
    BOT_ODIN_5x5 = 25
    BOT_5x5_INTRO = 31
    BOT_5x5_BEGINNER = 32
    BOT_5x5_INTERMEDIATE = 33
    BOT_TT_3x3 = 52
    GROUP_FINDER_5x5 = 61
    ARAM_5x5 = 65
    ONEFORALL_5x5 = 70
    FIRSTBLOOD_1x1 = 72
    FIRSTBLOOD_2x2 = 73
    SR_6x6 = 75
    URF_5x5 = 76
    ONEFORALL_MIRRORMODE_5x5 = 78
    BOT_URF_5x5 = 83
    NIGHTMARE_BOT_5x5_RANK1 = 91
    NIGHTMARE_BOT_5x5_RANK2 = 92
    NIGHTMARE_BOT_5x5_RANK5 = 93
    ASCENSION_5x5 = 96
    HEXAKILL = 98
    BILGEWATER_ARAM_5x5 = 100
    KING_PORO_5x5 = 300
    COUNTER_PICK = 310
    BILGEWATER_5x5 = 313
    SIEGE = 315
    DEFINITELY_NOT_DOMINION_5x5 = 317
    ARURF_5X5 = 318
    TEAM_BUILDER_DRAFT_UNRANKED_5x5 = 400
    TEAM_BUILDER_DRAFT_RANKED_5x5 = 410
    TEAM_BUILDER_RANKED_SOLO = 420
    RANKED_FLEX_SR = 440

    @staticmethod
    def is_ranked(value):
        valid_values = [
            QueueType.RANKED_FLEX_SR.name,
            QueueType.RANKED_SOLO_5x5.name,
            QueueType.RANKED_TEAM_3x3.name,
            QueueType.RANKED_TEAM_5x5.name,
            QueueType.TEAM_BUILDER_DRAFT_RANKED_5x5.name,
            QueueType.TEAM_BUILDER_RANKED_SOLO.name
        ]
        return value in valid_values
