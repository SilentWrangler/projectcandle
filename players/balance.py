from .constants import EXP

def trait_level_exp_required(level):
    assert level in range(0,EXP.TRAIT_LVL_MAX+1), "Level must be an integer in [1,5] (both inclusive) interval"

    if level==0:
        return 0

    exp = EXP.TRAIT_EXP_REQUIREMENT

    for i in range(1,level):
        exp*=EXP.TRAIT_EXR_MULT
    return int(exp)

levels_total_exp = [0]
for l in range(1,EXP.TRAIT_LVL_MAX+1):
    levels_total_exp.append(levels_total_exp[l-1]+trait_level_exp_required(l))

def level_from_total_exp(exp):
    assert exp>=0, "Exp cannot be negative"
    lvl = 0
    for i in range(EXP.TRAIT_LVL_MAX+1):
        if exp>=levels_total_exp[i]:
            lvl+=1
        else:
            return lvl
    return lvl


def normal_npc_trait_gain(age):
    assert age>=0, "Age must be greater than zero"
    exp = 0
    age -= EXP.EDUCATION_START
    exp += (EXP.NORMAL_EXP_GAIN + EXP.YOUNG_EXP_MOD) * min(age, EXP.YOUNG_BUFF_CUTOFF)
    age -= EXP.YOUNG_BUFF_CUTOFF
    if age <= 0:
        return level_from_total_exp(exp)
    exp += (EXP.NORMAL_EXP_GAIN) * min(age,EXP.OLD_DEBUFF_START)
    age -= EXP.OLD_DEBUFF_START
    if age <= 0:
        return level_from_total_exp(exp)
    exp+=(EXP.NORMAL_EXP_GAIN +EXP.TOO_OLD_MOD)
    return level_from_total_exp(exp)
