import tkinter as tk
import time
import pygame


class PomodoroTimer(tk.Frame):

    def __init__(self, parent=None, **kw):
        tk.Frame.__init__(self, parent, kw)

        self.short_break = 5
        self.long_break = 15
        self.work_time = 25

        self.main_list = [self.work_time, self.short_break] * 2
        self.main_list[-1] = self.long_break
        self.gen = (i for i in self.main_list)

        self.music_file = 'music/bell-ring.mp3'

        self.task = 0
        self._start = 0.0
        self._elapsedtime = 0.0
        self._running = 0

        self.period_1 = 'Work'
        self.period_2 = 'Break'
        self.period = tk.StringVar()
        self.timestr = tk.StringVar()
        self.main_widgets()

    def main_list_changer(self):
        """Changing main list which using to  make main generator."""

        self.main_list = [self.work_time, self.short_break] * 4
        self.main_list[-1] = self.long_break

        self.gen_changer()

    def gen_changer(self):
        self.gen = (i for i in self.main_list)

    def period_changer(self):
        """Changing period of time, Break or Work time"""

        self.period_1, self.period_2 = self.period_2, self.period_1
        self.period.set(self.period_1)

    def gener(self):
        return next(self.gen)

    def main_widgets(self):
        """ Make the time label. """
        timer = tk.Label(self, textvariable=self.timestr)
        self._setTime(self._elapsedtime)
        timer.pack(fill=tk.X, expand=tk.NO, pady=2, padx=2)

        label = tk.Label(self, textvariable=self.period)
        self.period.set(self.period_1)
        label.pack(fill=tk.X, expand=tk.NO, pady=2, padx=2)

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

    def _setTime(self, elap):
        """ Set the time string to Minutes:Seconds """
        minutes = int(elap / 60)
        seconds = int(elap - minutes * 60.0)
        self.timestr.set('%02d:%02d' % (minutes, seconds))

    def Start(self):
        """ Start the stopwatch, ignore if running. """

        try:
            if not self._running:
                self.task = int(self.gener())
                self._start = time.time() - self._elapsedtime
                self._update()
                self._running = 1
        except StopIteration:
            if not self._running:
                self.gen_changer()
                self.task = int(self.gener())
                self._start = time.time() - self._elapsedtime
                self._update()
                self._running = 1

    def Pause(self):
        """ Stop the stopwatch, ignore if stopped. """

        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = time.time() - self._start
            self._setTime(self._elapsedtime)
            self._running = 0
            print(self.work_time)

    def clener(self):
        """ Clean main label, and set timer on 00:00. """
        self._start = time.time()
        self._elapsedtime = 0.0
        self._setTime(self._elapsedtime)

    def Reset(self):
        """ Reset to starting point, to first work period. """
        self.clener()

        self.Pause()
        self.gen_changer()

        self.period_1 = 'Work'
        self.period_2 = 'Break'
        self.period.set(self.period_1)

    def menu_widgets(self):
        """ Make the drop menu. """
        self.win = tk.Toplevel(self)

        tk.Label(self.win, text='Set time in minutes', font=20).grid(row=0, columnspan=2)
        tk.Label(self.win, text='Work time', font=20).grid(row=1, column=0)
        tk.Label(self.win, text='Short break', font=20).grid(row=2, column=0)
        tk.Label(self.win, text='Long break', font=20).grid(row=3, column=0)

        self.entry_2 = tk.Entry(self.win, width=3, font=15)
        self.entry_3 = tk.Entry(self.win, width=3, font=15)
        self.entry_4 = tk.Entry(self.win, width=3, font=15)

        tk.Button(self.win, text='Submit', command=self.answer).grid(row=4, column=2, sticky='w')

        self.entry_2.grid(row=1, column=1, sticky='e')
        self.entry_3.grid(row=2, column=1, sticky='e')
        self.entry_4.grid(row=3, column=1, sticky='e')

    def answer(self):
        """ Checking answer in drop menu. """
        try:
            self.work_time = int(self.entry_2.get())
        except ValueError:
            pass

        try:
            self.short_break = int(self.entry_3.get())
        except ValueError:
            pass

        try:
            self.long_break = int(self.entry_4.get())
        except ValueError:
            pass

        self.main_list_changer()
        self.win.destroy()

    def music(self):

        """ Play music, when period is ended. """
        pygame.init()

        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(2)
        time.sleep(3)
        pygame.mixer.music.stop()


root = tk.Tk()

root.title('Pomodoro Timer')

sw = PomodoroTimer(root)
sw.pack(side=tk.TOP)

tk.Button(root, text='Start', command=sw.Start).pack(side=tk.LEFT)
tk.Button(root, text='Pause', command=sw.Pause).pack(side=tk.LEFT)
tk.Button(root, text='Reset', command=sw.Reset).pack(side=tk.LEFT)
tk.Button(root, text='Quit', command=root.quit).pack(side=tk.LEFT)

main_menu = tk.Menu(root)
root.configure(menu=main_menu)
first_item = tk.Menu(main_menu, tearoff=0)
main_menu.add_cascade(label='Setings', menu=first_item)
first_item.add_command(label='Open', command=sw.menu_widgets)

root.mainloop()
