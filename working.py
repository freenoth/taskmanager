#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ЗАО "ЭР-Телеком Холдинг" / Алексей Яковлев

    Программа для создания рабочих папок и файлов.

    Смысл: автоматизация организации рабочего пространства 
        - создание структуры папок по датам и задачам
        - создание стандартных файлов для работы с задачей

        - (!на будущее!) реструктуризация каталога и ведение архива: в проекте должны быть только 7-10 дней, всё остальное переносится в архив + отдельно архивируются sql-скрипты

    структура каталогов
    ~/year(yyyy)/month(mm)/day(dd)/task(XX-NNNNNN)/<files>

    ~/
      2015/
           05/..
           06/
              01/..
              ..
              10/
                 SD-1234/..
                 ..
                 SD-5678/
                         SD-5678.txt
                         script.sql
                         screen.png
                         ...

    (!на будущее!) разделение рабочей папки на две:
    ~ -> 
        archive/.. (архивные данные с сохранением структуры /yyyy/mm/dd/..)
                + scripts/
                          YYYY-MM-DD-XX-NNNNN-script_name.sql
        work/..(рабочее пространство, данные по 7-10 дням)

    функции:
        - отображает дату
        - кнопка создания структуры папок для текущего дня
        - кнопка создания структуры для задачи по её имени
        - текстовое поле для задания имени задачи
"""

# version   : 0.0.1
# py_ver    : 3.4.3
# other_ver : [other modules versions in {module - 0.0.0}]

# date      : 10.06.2015
# author    : Aleksey Yakovlev
# email     : nothscr@yandex.ru / aleksei.n.iakovlev@domru.ru
# contacts  : github: freenoth

# license   : WTFPL v2

# [ LICENSE_COMMENT ]
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it
# under the terms of the Do What The Fuck You Want To Public License Version 2
# See http://www.wtfpl.net/ for more details.

# history
# 0.0.0 - 10.06.2015 создан файл и описана основная логика программы
# 0.0.1 - 10.06.2015 описана основная логика, уже можно создавать папки через консольку

#imports
import sys
import time
from pathlib import Path


def make_path_from_cur_date():
    """ Возвращает строку вида '/yyyy/mm/dd' для сегодняшнего дня """
    ct = time.localtime()

    res = '/' + str(ct.tm_year)
    res += '/' + (str(ct.tm_mon) if ct.tm_mon > 9 else '0'+str(ct.tm_mon))
    res += '/' + (str(ct.tm_mday) if ct.tm_mday > 9 else '0'+str(ct.tm_mday))

    return res


def make_today_dir():
    """ Создаёт папки для текущего дня и возвращает объект Path """
    curdir = Path.cwd()
    today_dir = Path('work' + make_path_from_cur_date())

    if not today_dir.exists():
        today_dir.mkdir(parents = True)

    return today_dir



def make_task_dir(work_dir, task_name):
    """ Создаёт папку и начальные файлы для задачи """
    task_dir = work_dir / task_name
    if not task_dir.exists():
        task_dir.mkdir()

    task_file = task_dir / (task_name + '.txt')
    if not task_file.exists():
        task_file.touch()

    return 'created..'


def main():
    """ Работа с функционалом """
    print('Создание директорий... ')
    work_dir = make_today_dir()
    print(work_dir)

    print('\nCOMMANDS:\nmk task_name - создание папки задачи\nq - выход\n')
    cmd = ''
    while cmd != 'q':
        cmd = input('> ')
        if cmd.split()[0] == 'mk':
            print(make_task_dir(work_dir, cmd.split()[1]))

    print('bye bye')


if __name__ == '__main__':
    print('#! using python {0}.{1}.{2}\n'.format(sys.version_info[0], 
                                            sys.version_info[1], 
                                            sys.version_info[2]))
    if sys.version_info[0] == 3 and sys.version_info[1] >= 4 and sys.version_info[2] >= 3:
        main()
    else:
        print('Python 3.4.3 or older required!!')