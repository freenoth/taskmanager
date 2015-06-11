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

# version   : 0.1.0
# py_ver    : 3.4.3
# other_ver : -

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
# 0.1.0 - 11.06.2015 реализация программы через tkinter-интерфейс, создаёт структуру и задачи, отображает сообщения

#imports
import sys
import tkinter as tk
import time

try:
    from pathlib import Path # work only with python 3.4.3!!!
except:
    pass

APP_TITLE = 'Work Manager 0.1.0'


class Application(tk.Frame):
    """ Главное окно программы """

    def __init__(self, master=None):
        super(Application, self).__init__(master)
        self.grid(sticky='nsew')

        self.work_dir = None
        self.task_name = None

        self.create_widgets()

    def create_widgets(self):
        # создание элементов окна
        l = tk.Label(self)
        l['text'] = 'Сегодня:'
        l.grid(column=0, row=0, padx=3, pady=3)

        l = tk.Label(self)
        l['text'] = 'Задача:'
        l.grid(column=0, row=1, padx=3, pady=3)

        e = tk.Entry(self)
        e.insert(0, time.strftime('%d.%m.%Y'))
        e['state'] = 'readonly'
        e['width'] = 15
        e.grid(column=1, row=0, padx=3, pady=3)

        self.task_name = tk.StringVar()
        e = tk.Entry(self, textvariable=self.task_name)
        e['width'] = 15
        e.grid(column=1, row=1, padx=3, pady=3)
        e.bind('<Return>', self.make_task_dir)


        b = tk.Button(self)
        b['text'] = 'Создать папку'
        b['command'] = self.make_today_dir
        b['width'] = 15
        b['height'] = 1
        b.grid(column=2, row=0, padx=3, pady=3)

        b = tk.Button(self)
        b['text'] = 'Создать задачу'
        b['command'] = self.make_task_dir
        b['width'] = 15
        b['height'] = 1
        b.grid(column=2, row=1, padx=3, pady=3)

        self.msg = l = tk.Label(self)
        l['text'] = ''
        l.grid(column=0, row=2, columnspan=3, sticky='nsew')

        self.stat = l = tk.Label(self)
        l['text'] = '>'
        l['relief'] = 'groove'
        l['anchor'] = 'w'
        l['foreground'] = 'gray30'
        l.grid(column=0, row=3, columnspan=3, sticky='nsew')

    def set_message(self, text='', is_err=False):
        self.msg['foreground'] = 'red' if is_err else 'dark green'
        self.msg['text'] = text

    def set_status(self, text=''):
        self.stat['text'] = text

    def make_today_dir(self):
        """ Создаёт папки для текущего дня """
        today_dir = Path('work' + time.strftime('/%Y/%m/%d'))

        if today_dir.exists():
            self.set_message('уже существует', False)
        else:
            today_dir.mkdir(parents = True)
            self.set_message('выполнено', False)

        self.set_status('~/' + today_dir.as_posix() + '/>')
        self.work_dir = today_dir

    def make_task_dir(self, arg=None):
        """ Создаёт папку и начальные файлы для задачи """
        task_name = self.task_name.get()
        
        if not self.work_dir:
            self.set_message('Не создана рабочая папка!', True)
        elif not task_name:
            self.set_message('Не задано имя задачи!', True)
        else:
            task_dir = self.work_dir / task_name

            if task_dir.exists():
                self.set_message('уже существует!', True)
            else:
                task_dir.mkdir()
                task_file = task_dir / (task_name + '.sql')
                task_file.touch()
                self.set_message('файлы для задачи %s созданы' % task_name, False)


def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.resizable(width=False, height=False)

    app = Application(master=root)
    root.mainloop()


if __name__ == '__main__':
    try:
        Path()
    except Exception as e:
        root = tk.Tk()
        root.title('ERROR!!!')
        root.resizable(width=False, height=False)
        l = tk.Label(root)
        l['text'] = 'Необходим Python 3.4.3 или новее!!!'
        l['foreground'] = 'red'
        l.grid(sticky='nsew')
        l = tk.Label(root)
        l['text'] = 'Нет необходимого модуля pathlib'
        l['foreground'] = 'red'
        l.grid(sticky='nsew')
        l = tk.Label(root)
        l['text'] = '"' + str(e) + '"'
        l['foreground'] = 'black'
        l.grid(sticky='nsew')
        root.mainloop()
    else:
        main()