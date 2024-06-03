from .constants import PROJECTS as p
from .constants import EXP, BALANCE
from .models import Character, Player
from world.logic import get_active_world
from world.constants import MAIN_BIOME
from world.models import Cell


class ProjectProcessor:
    processors = dict()


    def process(self, project):
        def default(_):
            pass
        ProjectProcessor.processors.get(project.type, default)(project)

    @classmethod
    def detect_processors(cls):
        from importlib import import_module
        from candle.settings import PROJECT_PROCESSORS
        for module in PROJECT_PROCESSORS:
            import_module(module)

def processor(project_type):
    def decorator(func):
        ProjectProcessor.processors[project_type] = func
        return func
    return decorator

def calc_power(char, subject):
    result = p.WORK.BASE_WORK
    lvl = char.level(subject)
    exp = char.get_exp(subject)
    result += p.WORK.EXP_LEVEL_BUFF * lvl
    result += int (exp * 4 / calc_lvlup_req(lvl+1))
    #TODO: add buffs from traits
    return result


def calc_pop_work_power(char, subject):
    result = p.WORK.POP_WORK_BONUS
    lvl = char.level(subject)
    result += p.WORK.POP_EXP_BOOST * lvl
    return result

def calc_exp(char, subject, teacher_id = None , on_purpose = False):
    lvl = char.level(subject) # Дабы не лезть в БД лишние разы
    teacher_buff = 0
    teacher_lvl_diff = 0
    if teacher_id is not None:
        try:
            teacher = Character.objects.get(pk=int(teacher_id))
            if teacher.current_project is not None:
                if teacher.current_project.name == p.TYPES.TEACH: #учитель должен учить
                    kwargs = teacher.current_project.arguments_dict
                    pupils = []
                    if len(kwargs['pupils'])>0:
                        pupils = [int(i) for i in kwargs['pupils'].split(',')]
                    if char.id in pupils and subject == kwargs['subject']:
                        teacher_lvl_diff = max( teacher.level(subject) - lvl, 0)
        except Character.DoesNotExist:
            pass

    teacher_buff = EXP.TEACHER_LVL_BUFF * (teacher_lvl_diff -1)

    bloodline_buff = 0
    bloodline_level = char.bloodline_level(subject)

    if bloodline_level > 0:
        bloodline_buff += EXP.BLOODLINE_PERK_BUFF
    if bloodline_level > lvl and char.controller is not None:
        bloodline_buff += EXP.BLOODLINE_MEMORY_BUFF

    age_buff = 0
    world_age = get_active_world().ticks_age
    age = world_age - char.birth_date
    if age < EXP.UNDERSTANDING_START:
        return 0
    elif age < EXP.EDUCATION_START:
        age_buff = EXP.TOO_YOUNG_EXP_MOD
    elif age < EXP.YOUNG_BUFF_CUTOFF:
        age_buff = EXP.YOUNG_EXP_MOD
    elif age>=EXP.OLD_DEBUFF_START:
        age_buff = EXP.TOO_OLD_EXP_MOD

    total_exp_pre_multi_buffs = EXP.NORMAL_EXP_GAIN + teacher_buff + bloodline_buff + age_buff

    extra_exp_multiplier = (EXP.SCIENCE_BUFF_PER_LEVEL * char.level('science'))

    multi_buffs = int(extra_exp_multiplier * total_exp_pre_multi_buffs)
    total_exp = total_exp_pre_multi_buffs + multi_buffs
    if not on_purpose:
        total_exp = int(total_exp / 2)

    return max(total_exp, EXP.MINIMUM_EXP_GAINED)


def calc_lvlup_req(level):
    result  = EXP.TRAIT_EXP_REQUIREMENT
    for i in range(level-1):
        result = int(result * EXP.TRAIT_EXR_MULT)
    return result

def give_exp(char,subject,exp):
    prev_exp = char.get_exp(subject)
    level = char.level(subject)
    lvlup = calc_lvlup_req(level)
    prev_exp += exp
    if prev_exp>=lvlup and level<EXP.TRAIT_LVL_MAX:
        prev_exp-=lvlup
        char.level_up(subject)
    char.set_exp(subject,prev_exp)

# study
@processor(p.TYPES.STUDY)
def process_study(project):
    kwargs = project.arguments_dict
    subject = kwargs.get('subject', None)
    teacher_id = kwargs.get('teacher', None)
    if teacher_id=='':
        teacher_id=None
    exp = calc_exp(project.character, subject, teacher_id, True)
    give_exp(project.character, subject, exp)

#--------------------------

#teach
@processor(p.TYPES.TEACH)
def process_teach(project):
    kwargs = project.arguments_dict
    subject = kwargs.get('subject', None)
    exp = calc_exp(project.character, subject)
    give_exp(project.character, subject, exp)
#-------------------------------------

#relocate

class RelocateHelpers:
    @classmethod
    def calculate_range(cls,char):
        return BALANCE.BASE_COMMUNICATION_RANGE
    @classmethod
    def can_relocate(cls, char , target):
        result = target.main_biome != MAIN_BIOME.WATER
        loc = char.location
        dist = max(abs(loc['x']-target.x), abs(loc['y']-target.y))
        result = result and dist<=RelocateHelpers.calculate_range(char)
        return result

    @classmethod
    def can_relocate_to_coords(cls, char , x, y):
        try:
            target = get_active_world().cell_set.get(x = x, y= y)
            return cls.can_relocate(char, target)
        except Cell.DoesNotExist:
            return False


@processor(p.TYPES.RELOCATE)
def process_relocate(project):
    kwargs = project.arguments_dict
    target = kwargs.get('target')
    project.character.location = target
    project.character.start_next_project()
    project.end()


#-----------------------------

@processor(p.TYPES.ADVENTURE)
def process_adventure(project):
    kwargs = project.arguments_dict
    exp = kwargs.get("exp")
    friends = kwargs.get('friends',[])
    enemies = kwargs.get('enemies',[])
    for subject in exp:
        give_exp(project.character, subject, exp[subject])
    for friend in friends:
        target = Character.objects.get(pk=friend)
        if target in project.character.enemies:
            project.character.end_enmity(target)
        else:
            project.character.add_friendship(target)
    for enemy in enemies:
        target = Character.objects.get(pk=friend)
        if target in project.character.friends:
            project.character.remove_friendship(target)
        else:
            project.character.add_enmity(target)
    project.character.start_next_project()
    project.end()

#--------------------------------


@processor(p.TYPES.MAKE_FRIEND)
def process_make_friend(project):

    target = project.target
    loc = project.character.location
    loc_t = target.location
    dist = max(abs(loc['x']-loc_t['x']), abs(loc['y']-loc_t['y']))
    if dist>BALANCE.BASE_COMMUNICATION_RANGE:
        project.is_current = False
        project.save()
        return #Если слишком далеко, отключить проект
    exp = calc_exp(project.character, 'politics')
    give_exp(project.character, 'politics', exp)
    done = calc_power(project.character, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        project.character.end_enmity(target)
        project.character.add_friendship(target)
        project.character.start_next_project()
        project.end()




