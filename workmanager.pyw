#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ЗАО "ЭР-Телеком Холдинг" / Алексей Яковлев

    Программа для создания рабочих папок и файлов.

    Смысл: автоматизация организации рабочего пространства 
        - создание структуры папок по датам и задачам
        - создание стандартных файлов для работы с задачей

        - (!на будущее!) реструктуризация каталога и ведение архива: 
            в проекте должны быть только 7-10 дней, 
            всё остальное переносится в архив 
            + отдельно архивируются sql-скрипты

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

# version   : 0.3.0
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
# 0.0.1 - 10.06.2015 описана основная логика, уже можно создавать папки через
#                    консольку
# 0.1.0 - 11.06.2015 реализация программы через tkinter-интерфейс, создаёт
#                    структуру и задачи, отображает сообщения
# 0.1.1 - 11.06.2015 немного изменён стиль, добавлены события на поле ввода
#                    (очистка сообщения по фокусу и реакция на "Enter"),
#                    после создания файлов поле ввода очищается
# 0.1.2a- 11.06.2015 добавил меню
# 0.2.0 - 16.06.2015 реализованы настройки через файл .conf в формате JSON
# 0.2.1 - 16.06.2015 изменены импорты, добален файл setup для cx_Freezy
# 0.2.1a- 16.06.2015 мелкие исправления
# 0.3.0 - 29.07.2015 автоматическое создание новых рабочих каталогов в 00:00:01 нового дня по ПН,ВТ,СР,ЧТ,ПТ


#imports
from tkinter import Tk, Toplevel, Menu, Frame, Label, Entry, Button, StringVar
from time import strftime, localtime
from json import dump as json_dump, load as json_load

try:
    from pathlib import Path # work only with python 3.4.3!!!
except:
    pass


VERSION = '0.3.0'
APP_TITLE = 'Work Manager' + ' ' + VERSION

SETTINGS_FILE = 'workmanager.conf'
SETTINGS = {}


class AppMenu(Menu):
    """ Меню для приложения """

    def __init__(self, master=None):
        super(AppMenu, self).__init__(master)

        self['tearoff'] = False
        self['relief'] = 'flat'
        self.build_menu()

    def build_menu(self):
        menu_settings = Menu(self, tearoff=False)
        menu_settings['background'] = SETTINGS['color_main']
        menu_settings.add_command(label='Настройки', command=self._settings)
        self.add_cascade(label='Параметры', menu=menu_settings)

        # menu_about = Menu(self, tearoff=False)
        # menu_about['background'] = SETTINGS['color_main']
        # menu_about.add_command(label='Автор', command=self._about_author)
        # menu_about.add_command(label='Версия', command=self._about_version)
        # self.add_cascade(label='О программе', menu=menu_about)

    def _settings(self):
        settings_win = Toplevel(self.winfo_toplevel())
        settings_win.grab_set()
        settings_win.focus_set()
        settings_win.resizable(width=False, height=False)

        aps = AppSettings(settings_win)

        settings_win.wait_window()

        if aps.is_save:
            load_settings()
            for ch in self.master.children:
                cls = self.master.children[ch].__class__
                if cls == Application:
                    self.master.children[ch].destroy()
                    cls(self.master)

    # def _about_author(self):
    #     pass

    # def _about_version(self):
    #     ver_info = Toplevel(self.winfo_toplevel())
    #     ver_info.grab_set()
    #     ver_info.focus_set()


class AppSettings(Frame):
    """ Окно настроек программы """

    def __init__(self, master=None):
        super(AppSettings, self).__init__(master)

        self.grid(sticky='nsew')
        self['bg'] = SETTINGS['color_main']

        self.settings = {}

        self.is_save = False
        self.create_widgets()

    def create_widgets(self):
        show_sett = [('work_dir',       'Рабочая папка'),
                     ('path_format',    'Формат пути'),
                     ('color_main',     'Цвет основного окна'),
                     ('color_button',   'Цвет кнопок'),
                     ('color_msg_bad',  'Цвет сообщений ошибок'),
                     ('color_msg_good', 'Цвет оповещений')]

        elem_count = 0
        for sett in show_sett:
            l = Label(self)
            l['text'] = sett[1]
            l['bg'] = SETTINGS['color_main']
            l['anchor'] = 'e'
            l.grid(column=0, row=elem_count, padx=3, pady=3, sticky='nsew')

            e = Entry(self)
            e.insert(0, SETTINGS[sett[0]])
            e['relief'] = 'groove'
            e['bd'] = 1
            e['width'] = 15
            e['bg'] = SETTINGS['color_main']
            e.grid(column=1, row=elem_count, padx=3, pady=3, sticky='nsew')

            self.settings[sett[0]] = e

            elem_count += 1

        self.msg = l = Label(self)
        l['text'] = ''
        l['bg'] = SETTINGS['color_main']
        l['height'] = 2
        l.grid(column=0, row=elem_count, columnspan=2, sticky='nsew')

        elem_count += 1

        b = Button(self)
        b['text'] = 'Сохранить'
        b['command'] = self.save
        b['relief'] = 'groove'
        b['bd'] = 2
        b['width'] = 15
        b['height'] = 1
        b['bg'] = SETTINGS['color_button']
        b.grid(column=0, row=elem_count, padx=5, pady=5, sticky='w')

        b = Button(self)
        b['text'] = 'Отмена'
        b['command'] = self.exit
        b['relief'] = 'groove'
        b['bd'] = 2
        b['width'] = 15
        b['height'] = 1
        b['bg'] = SETTINGS['color_button']
        b.grid(column=1, row=elem_count, padx=5, pady=5, sticky='e')

    def set_message(self, text='', is_err=False):
        self.msg['foreground'] = ( SETTINGS['color_msg_bad'] if is_err 
                                      else SETTINGS['color_msg_good'] )
        self.msg['text'] = text

    def save(self):
        self.set_message('', False)
        old_sett = open(SETTINGS_FILE, mode='r').read()

        new_sett = dict(SETTINGS)

        try:
            for s in self.settings:
                if self.settings[s].get() == '':
                    raise Exception()
                else:
                    new_sett[s] = self.settings[s].get()
        except:
            new_sett = None
            self.set_message('Имеются пустые значения!', True)

        if new_sett:
            sett_file = open(SETTINGS_FILE, mode='w')
            try:
                json_dump(new_sett, sett_file, indent=4, sort_keys=True)
            except Exception as e:
                sett_file.write(old_sett)
                self.set_message('Ошибка записи конфигурации!', True)
                raise e
            else:
                self.is_save = True
                self.exit()
            finally:
                sett_file.close()

    def exit(self):
        self.master.destroy()


class Application(Frame):
    """ Главное окно программы """

    def __init__(self, master=None):
        super(Application, self).__init__(master)
        self.grid(sticky='nsew')

        self['bg'] = SETTINGS['color_main']

        self.work_dir = None
        self.task_name = None

        self.create_widgets()
        self._check_work_dir()

    def create_widgets(self):
        # создание элементов окна
        l = Label(self)
        l['text'] = 'Сегодня:'
        l['bg'] = SETTINGS['color_main']
        l.grid(column=0, row=0, padx=3, pady=3)

        l = Label(self)
        l['text'] = 'Задача:'
        l['bg'] = SETTINGS['color_main']
        l.grid(column=0, row=1, padx=3, pady=3)

        self.work_dir_info = StringVar()
        e = Entry(self, textvariable=self.work_dir_info)
        e['relief'] = 'groove'
        e['bd'] = 1
        e['state'] = 'readonly'
        e['width'] = 15
        e.grid(column=1, row=0, padx=3, pady=3, sticky='nsew')

        self.task_name = StringVar()
        e = Entry(self, textvariable=self.task_name)
        e['relief'] = 'groove'
        e['bd'] = 1
        e['width'] = 15
        e['bg'] = SETTINGS['color_main']
        e.grid(column=1, row=1, padx=3, pady=3, sticky='nsew')
        e.bind('<Return>', self._make_task)
        e.bind('<FocusIn>', self._clear_message)
        e.bind('<FocusOut>', self._clear_message)

        b = Button(self)
        b['text'] = 'Создать папку'
        b['command'] = self.make_today_dir
        b['relief'] = 'groove'
        b['bd'] = 2
        b['width'] = 15
        b['height'] = 1
        b['bg'] = SETTINGS['color_button']
        b.grid(column=2, row=0, padx=3, pady=3)

        b = Button(self)
        b['text'] = 'Создать задачу'
        b['command'] = self.make_task_dir
        b['relief'] = 'groove'
        b['bd'] = 2
        b['width'] = 15
        b['height'] = 1
        b['bg'] = SETTINGS['color_button']
        b.grid(column=2, row=1, padx=3, pady=3)

        self.msg = l = Label(self)
        l['text'] = ''
        l['bg'] = SETTINGS['color_main']
        l.grid(column=0, row=2, columnspan=3, sticky='nsew')

        self.stat = l = Label(self)
        l['text'] = '>'
        l['relief'] = 'groove'
        l['bd'] = 1
        l['anchor'] = 'w'
        l['foreground'] = 'gray30'
        l['bg'] = SETTINGS['color_main']
        l.grid(column=0, row=3, columnspan=3, sticky='nsew')

    #__информирование пользователя
    def set_message(self, text='', is_err=False):
        self.msg['foreground'] = ( SETTINGS['color_msg_bad'] if is_err 
                                      else SETTINGS['color_msg_good'] )
        self.msg['text'] = text

    def set_status(self, text=''):
        self.stat['text'] = text

    #__events
    def _clear_message(self, arg=None):
        self.set_message()

    def _make_task(self, arg=None):
        self.make_task_dir()

    # автоматическое создание рабочих папок 
    def _check_work_dir(self):
        now = localtime()

        if not self.work_dir or self.work_dir and self.work_dir_info.get() != strftime('%d.%m.%Y'):
            if now.tm_wday in range(0, 5):
                self.make_today_dir()
                self.set_message()
        
        self.work_dir_info.set(strftime('%d.%m.%Y'))

        slp = ((24-now.tm_hour)*60 - now.tm_min)*60 - now.tm_sec + 1
        self.after(slp*1000, self._check_work_dir)

    #__логика программы
    def make_today_dir(self):
        """ Создаёт папки для текущего дня """
        today_dir = Path(SETTINGS['work_dir'] +
                         strftime(SETTINGS['path_format']))

        if today_dir.exists():
            self.set_message('уже существует', False)
        else:
            today_dir.mkdir(parents = True)
            self.set_message('выполнено', False)

        self.set_status('~' + today_dir.as_posix() + '/>')
        self.work_dir = today_dir

    def make_task_dir(self):
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
                self.set_message('файлы для задачи %s созданы' % task_name,
                                                                        False)
                self.task_name.set('')


def load_settings():
    sett_file = None

    try:
        sett_file = open(SETTINGS_FILE, mode='r')
        global SETTINGS
        SETTINGS = json_load(sett_file)
        sett_file.close()
    except Exception as e:
        root = Tk()
        root.title('ERROR!!!')
        root.resizable(width=False, height=False)
        l = Label(root)
        l['text'] = 'Ошибка чтения файла конфигурации'
        l['foreground'] = 'red'
        l.grid(sticky='nsew')
        l = Label(root)
        l['text'] = '"' + str(e) + '"'
        l['foreground'] = 'black'
        l.grid(sticky='nsew')
        root.mainloop()
        return False
    finally:
        sett_file.close()

    return True


def main():
    if load_settings():
        root = Tk()
        root.title(APP_TITLE)
        root.resizable(width=False, height=False)

        root['menu'] = AppMenu(master=root)
        Application(master=root)
        root.mainloop()


if __name__ == '__main__':
    try:
        Path()
    except Exception as e:
        root = Tk()
        root.title('ERROR!!!')
        root.resizable(width=False, height=False)
        l = Label(root)
        l['text'] = 'Необходим Python 3.4.3 или новее!!!'
        l['foreground'] = 'red'
        l.grid(sticky='nsew')
        l = Label(root)
        l['text'] = 'Нет необходимого модуля pathlib'
        l['foreground'] = 'red'
        l.grid(sticky='nsew')
        l = Label(root)
        l['text'] = '"' + str(e) + '"'
        l['foreground'] = 'black'
        l.grid(sticky='nsew')
        root.mainloop()
    else:
        main()