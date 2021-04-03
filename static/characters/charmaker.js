

race_name = {
    'HUM':gettext("Люди"),
    'ELF':gettext("Эльфы"),
    'ORC':gettext("Орки"),
    'DWA':gettext("Дварфы"),
    'GOB':gettext("Гоблины"),
    'FEY':gettext("Феи")
}

race_description = {
    'HUM':gettext("Люди лучше всех остальных владеют магией общения,\
а некоторые даже способны к телепатии без всякой тренировки.\
Это значительно помогает им в организации и убеждении.<br>\
Рекомендованные специализации: Политик, Военный"),
    'ELF':gettext("Эльфы обладают натуральной способностью к магии жизни,\
 получая преимущество в управлении регенерацией. Это делет их хорошими медиками\
 и крепкими бойцами.<br>\
 Рекомендованные специализации: Учёный, Военный"),
    'ORC':gettext("Орки способны магическим образом увеличивать физическую силу и выносливость.\
 Это даёт им возможность сражаться и заниматься тяжёлым трудом лучше остальных рас.<br>\
 Рекомендованные специализации: Хозяйственник, Военный"),
    'DWA':gettext("Дварфы смогли приручить крайне капризную силу: вдохновение. Их способность\
 при необходимости получать подсказки от интуиции\"по щелчку пальцев\" даёт им совершать\
 открытия и создавать воодушевляющие произведения искусства.<br>\
 Рекомендованные специализации: Политик, Учёный"),
    'GOB':gettext("Гоблины умеют использовать магию для усиления своей мысли.\
 Они могут проводить долгое время за умственной работой, не испытывая усталости\
 и держа в голове каждую маленькую деталь.<br>\
 Рекомендованные специализации: Учёный, Хозяйственник"),
    'FEY':gettext("Феи")
}


spec_name = {
    'military':gettext("Военный"),
    'politics':gettext("Политик"),
    'economics':gettext("Хозяйственник"),
    'science':gettext("Учёный")
}

spec_dsc = {
    'military':gettext("Военные специализируются на использовании насилия для достижения целей.\
 Эта специлизация включает в себя как личные боевые качества, так и способность к организации дисциплины\
 и тактику."),
    'politics':gettext("Политики специализируются на тонких манипуляциях.\
 Эта специализация включает в себя способности договариваться, плести интриги и\
 привлекать толпу на свою сторону."),
    'economics':gettext("Хозяйственники специализируются на материальном благополучии.\
 Эта специализация включает в себя как возможность лично взяться за ремесло, так и\
 умение продуктивно организовывать чужой труд."),
    'science':gettext("Учёные специализируются на движении прогресса вперёд.\
 Эта специализация включает в себя эрудицию и умение делать выводы из\
 экспериментов и естественных явлений.")
}

prev_r = null;
prev_s = null;

function race_pick(el,race, gender){
    if (prev_r){
        prev_r.children[0].classList.toggle('fancyback');
    }
    el.children[0].classList.toggle('fancyback');
    prev_r = el;
    document.getElementById('char_race').value = race;
    document.getElementById('char_gender').value = gender;
    document.getElementById('race_name').innerHTML = race_name[race];
    document.getElementById('race_desc').innerHTML = race_description[race];
    if (prev_s){
        document.getElementById("confirm").type = "submit"
    }
}
function spec_pick(el,spec){
    if (prev_s){
        prev_s.children[0].classList.toggle('fancyback');
    }
    el.children[0].classList.toggle('fancyback');
    prev_s = el;
    document.getElementById('char_exp').value = spec;
    document.getElementById('spec_name').innerHTML = spec_name[spec];
    document.getElementById('spec_desc').innerHTML = spec_dsc[spec];
    if (prev_r){
        document.getElementById("confirm").type = "submit"
    }
}

function yesno(){
    msg = gettext("Если вы уже имеете одного персонажа, вы потеряете над ним контроль! Действительно создать персонажа? ")
    return confirm(msg);
}