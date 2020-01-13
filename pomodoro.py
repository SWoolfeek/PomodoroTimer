import tkinter as tk
from tkinter import messagebox as mb
import time
import sqlite3
import pygame


class Main(tk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self._start = 0.0
        self._elapsedtime = 0.0
        self._running = 0
        self.task = 0

        self.music_file = 'music/bell-ring.mp3'
        self.db = db
        self.work_time, self.short_break, self.long_break = db.select_data()

        self.period_1 = 'Working'
        self.period_2 = 'Break'
        self.period = tk.StringVar()
        self.timestr = tk.StringVar()

        self.main_list_changer()
        self.init_main()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.add_img = tk.PhotoImage(file='img/settings.png')
        btn_open_dialog = tk.Button(toolbar, command=self.open_dialog, bg='#d7d8e0',
                                    bd=0, compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        """ Make the time label. """
        timer = tk.Label(self, textvariable=self.timestr, font='Arial 20 bold')
        self._setTime(self._elapsedtime)
        timer.pack(pady=5, padx=60)

        label = tk.Label(self, textvariable=self.period, font='Arial 17')
        self.period.set(self.period_1)
        label.pack(pady=0, padx=0)

        btn1 = tk.Button(self, text='Start', command=self.start).pack(side=tk.LEFT, pady=5)
        btn2 = tk.Button(self, text='Pause', command=self.pause).pack(side=tk.LEFT, pady=5)
        btn3 = tk.Button(self, text='Reset', command=self.reset).pack(side=tk.LEFT, pady=5)

    def _setTime(self, elap):
        """ Set the time string to Minutes:Seconds """
        minutes = int(elap / 60)
        seconds = int(elap - minutes * 60.0)
        self.timestr.set('%02d:%02d' % (minutes, seconds))

    def _update(self):
        """ Update the label with elapsed time. """
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        if int(self._elapsedtime / 60) == self.task:  # Checking does it reach stop time or not.
            self.period_changer()
            self.clener()
            self._running = 0
            self.music()
        else:
            self._timer = self.after(50, self._update)

    def main_list_changer(self):
        """Changing main list which using to  make main generator."""

        self.main_list = [self.work_time, self.short_break] * 4
        self.main_list[-1] = self.long_break

        self.generator_changer()

    def generator_changer(self):
        self.gen = (i for i in self.main_list)

    def iterator(self):
        return next(self.gen)

    def period_changer(self):
        """Changing period of time, Break or Work time"""

        self.period_1, self.period_2 = self.period_2, self.period_1
        self.period.set(self.period_1)

    def start(self):

        try:
            if not self._running:
                self.task = int(self.iterator())
                self._start = time.time() - self._elapsedtime
                self._update()
                self._running = 1
        except StopIteration:
            if not self._running:
                self.generator_changer()
                self.task = int(self.iterator())
                self._start = time.time() - self._elapsedtime
                self._update()
                self._running = 1

    def pause(self):

        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = time.time() - self._start
            self._setTime(self._elapsedtime)
            self._running = 0

    def reset(self):
        """ Reset to starting point, to first work period. """
        self.clener()

        self.pause()
        self.work_time, self.short_break, self.long_break = db.select_data()
        self.generator_changer()

        self.period_1 = 'Working'
        self.period_2 = 'Break'
        self.period.set(self.period_1)

    def clener(self):
        """ Clean main label, and set timer on 00:00. """
        self._start = time.time()
        self._elapsedtime = 0.0
        self._setTime(self._elapsedtime)

    def music(self):
        """ Play music, when period is ended. """
        pygame.init()

        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(2)
        time.sleep(3)
        pygame.mixer.music.stop()

    def open_dialog(self):
        Child()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.db = db
        self.init_child()

    def init_child(self):
        self.title('Доходы рассходы')
        self.geometry('200x130+400+300')
        self.resizable(False, False)

        child_font = ('Arial', '15')

        tk.Label(self, text='Set time in minutes', font=child_font).grid(row=0, columnspan=2)
        tk.Label(self, text='Work time', font=child_font).grid(row=1, column=0)
        tk.Label(self, text='Short break', font=child_font).grid(row=2, column=0)
        tk.Label(self, text='Long break', font=child_font).grid(row=3, column=0)

        self.entry_1 = tk.Entry(self, width=6, font=child_font, justify=tk.RIGHT)
        self.entry_2 = tk.Entry(self, width=6, font=child_font, justify=tk.RIGHT)
        self.entry_3 = tk.Entry(self, width=6, font=child_font, justify=tk.RIGHT)

        tk.Button(self, text='Submit', padx=9, command=self.answer).grid(row=4, column=1, sticky='e')

        self.entry_1.grid(row=1, column=1, sticky='e')
        self.entry_2.grid(row=2, column=1, sticky='e')
        self.entry_3.grid(row=3, column=1, sticky='e')

        self.grab_set()
        self.focus_set()

    def answer(self):
        """ Checking answer in drop menu, and add it to DB """
        try:
            work_time = int(self.entry_1.get())
            short_break = int(self.entry_2.get())
            long_break = int(self.entry_3.get())
            self.db.inset_data(work_time, short_break, long_break)
        except ValueError:
            pass

        self.message()

    def message(self):
        mb.showinfo(title="Changing settings.", message="Hit 'Reset' button to save new settings.")
        self.destroy()


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('tomato.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS settings(
            id integer primary key, 
            work_time integer, 
            short_break integer, 
            long_break integer
            )'''
        )
        self.conn.commit()

    def inset_data(self, work_time, short_break, long_break):
        self.cursor.execute('''UPDATE settings SET work_time=?, short_break=?, long_break=? WHERE id =1''',
                            (work_time, short_break, long_break))
        self.conn.commit()

    def select_data(self):
        try:
            self.cursor.execute('''SELECT work_time, short_break, long_break FROM settings WHERE id = 1''')
            self.conn.commit()
            for a, b, c in self.cursor:
                pass
            return a, b, c
        except:
            self.cursor.execute('''INSERT INTO settings(work_time, short_break, long_break) VALUES (25,5,15)''')
            self.conn.commit()
            return 25, 15, 5


if __name__ == '__main__':
    root = tk.Tk()
    db = DB()
    app = Main(root)
    app.pack()

    root.title('Pomodoro timer')
    root.geometry('300x130+300+200')
    root.resizable(width=False, height=False)
    root.mainloop()
