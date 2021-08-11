from .constants import PROJECTS as p
from .constants import EXP
from .models import Character, Trait
from world.logic import get_active_world
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




def calc_exp(char, subject, teacher_id = None , on_purpose = False):
    lvl = char.level(subject) # Дабы не лезть в БД лишние разы
    teacher_buff = 0
    teacher_lvl_diff = 0
    if teacher_id is not None:
        try:
            teacher = Character.objects.get(pk=teacher_id)
            if teacher.current_project.name == p.TYPES.TEACH: #учитель должен учить
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


# study
@processor(p.TYPES.STUDY)
def process_study(project):
    kwargs = json.loads(project.arguments)
    subject = kwargs.get('subject', None)
    teacher_id = kwargs.get('teacher', None)
    exp = calc_exp(project.character, subject, teacher_id, True)

#--------------------------

#
