import tkinter as tk


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", elems=None):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = 'grey'
        self.default_fg_color = self['fg']

        self.func_foc_in = self.bind("<FocusIn>", self.foc_in)
        self.func_foc_out = self.bind("<FocusOut>", self.foc_out)

        if elems is not None:
            elems.append((self, "<FocusIn>", self.func_foc_in))
            elems.append((self, "<FocusOut>", self.func_foc_out))

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
