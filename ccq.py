import re
import os

from tkinter import *
from coresh import HGraph
from tempfile import TemporaryFile, _TemporaryFileWrapper
from tkinter import filedialog
from tkinter import messagebox

class Ccq:

    def __init__(self):

        if len(sys.argv)==1:

            self.top = Tk()

            self.top.title("CCQ Min")

            self.menubar = Menu(self.top)
            self.filemenu = Menu(self.menubar, tearoff=0)
            self.filemenu.add_command(label="Open", command=self.open_file, accelerator="Ctrl-O")
            self.filemenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl-S")
            self.filemenu.add_command(label="Save as", command=self.save_file_as, accelerator="Ctrl-Shift-S")
            self.menubar.add_cascade(label="File", menu=self.filemenu)
            self.top.config(menu=self.menubar)

            self.btn_min = Button(master=self.top, text="Minimise", command=lambda: self.gui_min(self.text.get(1.0, END)))
            self.btn_help = Button(master=self.top, text="?", command=self.info)
            self.text = Text(master=self.top, width=30, height=1)

            self.text.bind("<KeyRelease>", lambda _:self.check_len())

            self.text.insert(END, "().().()")

            self.check_len()

            self.btn_min.grid(row=0, column=0, sticky="we")
            self.btn_help.grid(row=0, column=1, sticky="we")
            self.text.grid(row=1, column=0, sticky="nswe", columnspan=2)

            self.top.grid_columnconfigure(0, weight=1, uniform="row0")
            self.top.grid_columnconfigure(1, weight=1, uniform="row0")

            self.file = ""

            self.title()

            self.top.bind_all("<Control-Key-o>", self.open_file)
            self.top.bind_all("<Control-Key-s>", self.save_file)
            self.top.bind_all("<Control-Key-S>", self.save_file_as)

            self.top.mainloop()

        else:

            print(self.minimise(sys.argv[1]))

    def title(self):

        if not self.file:
            self.top.title("tmp - CCQ Min")
        else:
            self.top.title(self.file+" - CCQ Min")

    def open_file(self, *_):

        self.file = filedialog.askopenfilename(parent=self.top, initialdir=os.path.dirname(os.path.realpath(__file__)), filetypes=[("Plain Text", ".txt"),("All Files", ".*")])

        if self.file:
            f = open(self.file, "r+")
            content = f.read()
            f.close()
            self.text.delete(1.0, END)
            self.text.insert(END, content)

            self.title()
            self.check_len()

    def save_file(self, *_):

        if self.file:
            file = open(self.file, "w+")
            file.write(self.text.get(1.0, END).rstrip("\n"))
            file.flush()
            file.close()
            self.title()
        else:
            self.save_file_as()

    def save_file_as(self, *_):

        self.file = filedialog.asksaveasfilename(parent=self.top, initialdir=os.path.dirname(os.path.realpath(__file__)), filetypes=[("Plain Text", ".txt"),("All Files",".*")], defaultextension=".txt")
        if self.file:
            self.save_file()

    def gui_min(self, q):

        try:
            s = self.minimise(q)
        except:
            return

        self.show_result(s)

    def minimise(self, q):

        regex = re.match(r"\((?P<ubv>[a-zA-Z0-9]+(,[a-zA-Z0-9]+)*)?\)\.\((?P<bv>[a-zA-Z0-9]+(,[a-zA-Z0-9]+)*)?\)\.\((?P<form>[a-zA-Z0-9]+\((?:[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*)?\)(,[a-zA-Z0-9]+\((?:[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*)?\))*)?\)", q)

        if not regex:
            raise messagebox.showerror("Error", "Input does not fit required format")

        if regex.group("ubv"):
            ubv = regex.group("ubv").split(",")
        else:
            ubv = []
        if regex.group("bv"):
            bv = regex.group("bv").split(",")
        else:
            bv = []
        if regex.group("form"):
            form = regex.group("form")
            form = re.findall(r"[a-zA-Z0-9]+\((?:[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*)?\)", form)
            form = [re.match(r"(?P<pred>[a-zA-Z0-9]+)\((?P<args>(?:[a-zA-Z0-9]+(?:,[a-zA-Z0-9]+)*)?)\)", n) for n in form]
            form = [[n.group("pred"), n.group("args").split(",")] for n in form]
            form = [[n[0], n[1] if n[1]!=[''] else []] for n in form]
        else:
            form = []

        edges = list({str(n[0])+" "+str(len(n[1])) for n in form})

        const = list({m for n in form for m in n[1]}-set(ubv+bv))

        if len(set(ubv)) != len(ubv) or len(set(bv)) != len(bv) or set(ubv)&set(bv) != set() or len(edges) != len({n.split(" ")[0] for n in edges}):
            raise messagebox.showerror("Error", "Input does not fit required format")

        tempfile = TemporaryFile(mode="w+")

        tempfile.write("V:\n"+" ".join(ubv+bv+const))

        tempfile.write("\nL:")

        if edges:

            tempfile.write("\n"+"\n".join(edges))

        if ubv+const:

            tempfile.write("\n"+"\n".join([n+"_ 1" for n in ubv+const]))

        tempfile.write("\nE:")

        if form:

            tempfile.write("\n"+"\n".join([" ".join([str(n[0])]+[m for m in n[1]]) for n in form]))

        if ubv+const:

            tempfile.write("\n"+"\n".join([n+"_ "+n for n in ubv+const]))

        tempfile.seek(0)

        hg = HGraph(parse=tempfile)

        hg.solve(am=False)

        result_vars = [n.name for n in hg.hgraph[0]]

        result = "("

        for n in result_vars:
            if n in ubv:
                if result.endswith("("):
                    result += n
                else:
                    result += ","+n

        result += ").("

        for n in result_vars:
            if n in bv:
                if result.endswith("("):
                    result += n
                else:
                    result += ","+n

        result += ").("

        result_preds = [[n.edge.name, [m.name for m in n.args]] for n in hg.hgraph[1] if not n.edge.name.endswith("_")]

        if result_preds:

            result += ",".join([n[0]+"("+",".join([m for m in n[1]])+")" for n in result_preds])

        result += ")"

        return result

    def show_result(self, result):

        self.res = Text(master=self.top, width=30, height=1)
        self.res.insert(END, result)
        self.res.config(state=DISABLED)

        self.res.grid(row=2, column=0, sticky="nswe", columnspan=2)

    def check_len(self):

        self.text.config(width=max(30,len(self.text.get(1.0, END))-1))

    def info(self):

        s ="""Input format as follows: (X).(Y).(A)
Where X, Y and A are comma-seperated lists representing in order:
Unbound variables, bound variables and atomic formulae.
Variables and Predicates are named according to [a-zA-Z0-9]+.
Formulae are written as: A(V), where A is the predicate identifier and
V is a comma-seperated list of variables.
All variables in any formula that are not explicitly listed in X and Y are
implicitly interpreted as constants.

Example Input:
(x).(y,u,v).(R(x,y),R(x,b),R(a,b),R(u,c),R(u,v),S(a,c,d))"""

        info_top = Toplevel()
        info_top.title("Input format info")

        label = Label(master=info_top, text=s)
        label.config(font=("TkDefaultFont", 15))
        label.pack(fill=BOTH, expand=True)

if __name__ == '__main__':

    Ccq()