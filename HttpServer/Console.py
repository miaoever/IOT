import Tkinter as Tk

class Console:
        _win = Tk.Tk()
        _logFrame = Tk.Frame()
        _log      = Tk.Text(_logFrame, wrap=Tk.NONE, setgrid=True)
        _scrollb  = Tk.Scrollbar(_logFrame, orient=Tk.VERTICAL)
        _scrollb.config(command = _log.yview) 
        _log.config(yscrollcommand = _scrollb.set)
        _win.title("Admin Console")
        _log.see(Tk.END)
        _log.grid(column=0, row=0)
        _scrollb.grid(column=1, row=0, sticky=Tk.S+Tk.N)
        _logFrame.pack()

        @staticmethod
        def show():
            Console._win.mainloop()

        @staticmethod 
        def log(ts, src, msg, level=None): # src: source of the message.    msg: content of the message
            # Write on GUI
            Console._log.insert('end', ts + "src: " + str(src) + "  msg: " + msg + '\n')
            #Console._log.update()


        def exitWindow(self):
            # Exit the GUI window and close log file
            print('exit..')
