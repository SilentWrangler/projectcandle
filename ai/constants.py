import numpy as np

from world.constants import BALANCE as WORLD_BALANCE, WORLD_GEN


ASSUMED_MAX_ID = 100_000
LEARNING_WORLD_WIDTH = WORLD_GEN.WIDTH//4
LEARNING_WORLD_HEIGHT = WORLD_GEN.HEIGHT//4

class MEGABOX_COORDS:

    SHAPE = (25,13,8)
    class MAP:
        ROW_START = 0
        COLUMN_START = 4
        SIZE = 11
        DEPTH = 4

    class CHAR:
        ID = (0, 0, 0)
        SKILL_LEVELS_START = (0, 1, 0)
        SKILL_EXP_START = (0, 2, 0)
        X = (0, 3, 0)
        Y = (0, 3, 1)
        PRIMARY_RACE = (0, 3, 2)
        SECONDARY_RACE = (0, 3, 3)
        PROJECT_TYPE = (0, 4, 0)
        WORK_REQUIRED = (0, 4, 1)
        WORK_DONE = (0, 4, 2)

    FACTIONS = (0, 5, 0)

    class OTHERS:
        ID = (0, 6, 0)
        SKILL_LEVELS_START = (0, 7, 0)
        X = (0, 8, 0)
        Y = (0, 8, 1)
        PRIMARY_RACE = (0, 8, 2)
        SECONDARY_RACE = (0, 8, 3)
        IS_FRIEND = (0, 9, 0)
        HAS_SHARED_FACTION = (0, 9, 1)

    class POP:
        ID = (0, 10, 0)
        RACE = (0, 10, 1)
        X = (0, 11, 0)
        Y = (0, 11, 1)
        GROWTH = (0, 12, 0)
        SUPPORTS_YOU = (0, 12, 1)




MEGABOX_LOW = np.zeros(MEGABOX_COORDS.SHAPE, dtype=int)
MEGABOX_HIGH = np.zeros(MEGABOX_COORDS.SHAPE, dtype=int)

map_highs = [2,4,8,5]
for i in range(MEGABOX_COORDS.MAP.SIZE):
    for j in range(MEGABOX_COORDS.MAP.SIZE):
        for k in range(MEGABOX_COORDS.MAP.DEPTH):
            MEGABOX_LOW[i][j][k+MEGABOX_COORDS.MAP.COLUMN_START]=-1
            MEGABOX_HIGH[i][j][k+MEGABOX_COORDS.MAP.COLUMN_START]=map_highs[k]

for i in range(MEGABOX_COORDS.SHAPE[0]):
    _, j, k = MEGABOX_COORDS.FACTIONS
    MEGABOX_HIGH[i][j][k] = ASSUMED_MAX_ID

    _, j, k = MEGABOX_COORDS.OTHERS.ID
    MEGABOX_HIGH[i][j][k] = ASSUMED_MAX_ID
    _, j, k = MEGABOX_COORDS.OTHERS.X
    MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_WIDTH
    _, j, k = MEGABOX_COORDS.OTHERS.Y
    MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_HEIGHT
    _, j, k = MEGABOX_COORDS.OTHERS.PRIMARY_RACE
    MEGABOX_HIGH[i][j][k] = 5
    _, j, k = MEGABOX_COORDS.OTHERS.SECONDARY_RACE
    MEGABOX_HIGH[i][j][k] = 5
    _, j, k = MEGABOX_COORDS.OTHERS.IS_FRIEND
    MEGABOX_HIGH[i][j][k] = 1
    _, j, k = MEGABOX_COORDS.OTHERS.HAS_SHARED_FACTION
    MEGABOX_HIGH[i][j][k] = 1

    _, j, _ = MEGABOX_COORDS.OTHERS.SKILL_LEVELS_START
    for k in range(4):
        MEGABOX_HIGH[i][j][k] = 5

    _, j, k = MEGABOX_COORDS.POP.ID
    MEGABOX_HIGH[i][j][k] = ASSUMED_MAX_ID
    _, j, k = MEGABOX_COORDS.POP.RACE
    MEGABOX_HIGH[i][j][k] = 5
    _, j, k = MEGABOX_COORDS.POP.X
    MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_WIDTH
    _, j, k = MEGABOX_COORDS.POP.Y
    MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_HEIGHT
    _, j, k = MEGABOX_COORDS.POP.GROWTH
    MEGABOX_LOW[i][j][k] = WORLD_BALANCE.POP_DEATH_THRESHOLD-50
    MEGABOX_HIGH[i][j][k] = WORLD_BALANCE.GROWTH_THRESHOLD+50
    _, j, k = MEGABOX_COORDS.POP.SUPPORTS_YOU
    MEGABOX_HIGH[i][j][k] = 1

i, j, k = MEGABOX_COORDS.CHAR.ID
MEGABOX_HIGH[i][j][k] = ASSUMED_MAX_ID
i, j, k = MEGABOX_COORDS.CHAR.X
MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_WIDTH
i, j, k = MEGABOX_COORDS.CHAR.Y
MEGABOX_HIGH[i][j][k] = LEARNING_WORLD_HEIGHT

i, j, k = MEGABOX_COORDS.CHAR.WORK_REQUIRED
MEGABOX_LOW[i][j][k] = -2
MEGABOX_HIGH[i][j][k] = 20_000
i, j, k = MEGABOX_COORDS.CHAR.WORK_DONE
MEGABOX_LOW[i][j][k] = -2
MEGABOX_HIGH[i][j][k] = 20_000

for k in range(4):
    i, j, _ = MEGABOX_COORDS.CHAR.SKILL_LEVELS_START
    MEGABOX_HIGH[i][j][k] = 5
    i, j, _ = MEGABOX_COORDS.CHAR.SKILL_EXP_START
    MEGABOX_HIGH[i][j][k] = 20_000

class REWARDS:
    FRIEND_REWARD = 5
    ENEMY_REWARD = 0

    BASE_SKILL_REWARD = 10

    @classmethod
    def reward_for_skill(cls, skill_level):
        reward = 0
        for lvl in range(skill_level):
            reward += lvl * REWARDS.BASE_SKILL_REWARD
        return reward


