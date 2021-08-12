from .constants import PROJECTS as p
from .constants import EXP
from .models import Character, Trait
from world.logic import get_active_world
from world.constants import MAIN_BIOME
import json

class ProjectProcessor:
    processors = dict()


    def process(self, project):
        def default(_):
            pass
        ProjectProcessor.processors.get(project.type, default)(project)


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


def calc_exp(char, subject, teacher_id = None , on_purpose = False):
    lvl = char.level(subject) # Дабы не лезть в БД лишние разы
    teacher_buff = 0
    teacher_lvl_diff = 0
    if teacher_id is not None:
        try:
            teacher = Character.objects.get(pk=teacher_id)
            if teacher.current_project is not None:
                if teacher.current_project.name == p.TYPES.TEACH: #учитель должен учить
                    kwargs = json.loads(teacher.current_project.content)
                    if char.id in kwargs['pupils'] and subject == kwargs['subject']:
                        teacher_lvl_diff = max( teacher.level(subject) - lvl, 0)
        except Character.DoesNotExist:
            pass

    teacher_buff = EXP.TEACHER_LVL_BUFF * (teacher_lvl_diff -1)

    bloodline_buff = 0
    bloodline_level = char.bloodline_level(subject)

    if bloodline_level > 0:
        bloodline_buff += EXP.BLOODLINE_PERK_BUFF
    if bloodline_level > lvl:
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

    total_exp = EXP.NORMAL_EXP_GAIN + teacher_buff + bloodline_buff + age_buff

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
        char.level_up()
    char.set_exp(prev_exp)

# study
@processor(p.TYPES.STUDY)
def process_study(project):
    kwargs = json.loads(project.arguments)
    subject = kwargs.get('subject', None)
    teacher_id = kwargs.get('teacher', None)
    exp = calc_exp(project.character, subject, teacher_id, True)
    give_exp(project.char, subject, exp)

#--------------------------

#teach
@processor(p.TYPES.TEACH)
def process_teach(project):
    kwargs = json.loads(project.arguments)
    subject = kwargs.get('subject', None)
    exp = calc_exp(project.char, subject)
    give_exp(project.char, subject, exp)
#-------------------------------------

#relocate

class RelocateHelpers:
    @classmethod
    def calculate_range(cls,char):
        return 999
    @classmethod
    def can_relocate(cls, char , target):
        result = target.main_biome != MAIN_BIOME.WATER
        loc = char.location
        dist = max(abs(loc.x-target.x), abs(loc.y-target.y))
        result = result and dist<RelocateHelpers.calculate_range(char)
        return result



@processor(p.TYPES.RELOCATE)
def process_relocate(project):
    kwargs = json.loads(project.arguments)
    target = kwargs.get('target')
    class Dummy: #Не будем лезть за клеткой в БД, когда координаты имеются
        def __init__(self, d):
            self.x = d['x']
            self.y = d['y']
    project.character.location = Dummy(target)
    project.delete()


#-----------------------------

@processor(p.TYPES.ADVENTURE)
def process_adventure(project):
    kwargs = json.loads(project.arguments)
    exp = kwargs.get("exp")
    friends = kwargs.get('friends',[])
    enemies = kwargs.get('enemies',[])
    for subject in exp:
        give_exp(project.char, subject, exp[subject])
    for friend in friends:
        target = Character.objects.get(pk=friend)
        if target in project.char.enemies:
            project.char.end_enmity(target)
        else:
            project.char.add_friendship(target)
    for enemy in enemies:
        target = Character.objects.get(pk=friend)
        if target in project.char.friends:
            project.char.remove_friendship(target)
        else:
            project.char.add_enmity(target)
    project.delete()

#--------------------------------


@processor(p.TYPES.MAKE_FRIEND)
def process_make_friend(project):
    kwargs = json.loads(project.arguments)
    exp = calc_exp(project.char, 'politics')
    give_exp(project.char, 'politics', exp)
    done = calc_power(project.char, 'politics')
    project.work_done += done
    if project.work_done < project.work_required:
        project.save()
    else:
        target_id = kwargs.get('target')
        target = Character.objects.get(pk=target_id)
        project.char.end_enmity(target)
        project.char.add_friendship(target)
        project.delete()




