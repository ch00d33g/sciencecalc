import math
from scipy import stats
from matplotlib import pyplot as plt

from tkinter import Tk
from tkinter import StringVar
from tkinter import Text, Label, Button, Entry
from tkinter import LEFT, TOP, BOTTOM, END
from tkinter import filedialog
from tkinter.messagebox import showinfo

from io import StringIO
from csv import reader

filename = ""
outfile = "result.png"

class lane:
    name = ""
    L = []
    MW = []
    logW = []
    
    def __init__(self,L,MW=None):
        self.L = L
        if not MW is None:
            self.MW = MW
            self.logW = [math.log(w) for w in self.MW]

def find_rf(distances, buffer):
    return [d/buffer for d in distances]


def fit(log_weights, rfs):
    result = stats.linregress(rfs, log_weights)
    return result.slope, result.intercept

def process_data(ladder, buffer_distance, samples):
    standard_rf = find_rf(ladder.L, buffer_distance)
    k, b = fit(ladder.logW, standard_rf)
    fig = plt.figure()
    ax = fig.add_subplot (121)
    ax.set_title("MW standard")
    ax.scatter(standard_rf, ladder.logW)
    ax.plot(standard_rf,[k * x + b for x in standard_rf] )
    if len (samples) > 0:
        ax1 = fig.add_subplot(122)
        ax1.set_title("Sample lanes")
        for index, sample in enumerate(samples):
            sample_rf = find_rf(sample.L,buffer_distance)
            ax1.scatter(sample_rf, [k*x + b for x in sample_rf],
                label = "Sample {}".format(index + 1))
        ax1.legend()
    plt.grid(axis="y")
    ax.set_ylabel("log(MW)")
    ax.set_xlabel("RF value")
    ax1.set_xlabel("RF value")
    plt.savefig(outfile)

def loadfile():
    global filename
    filename = filedialog.askopenfilename()
    if filename != 0:
        fileinfo.set("Sample file:" + filename)

def read_input():
    masses = []
    distances= []
    for row in textarea.get(1.0,END).rstrip().split("\n"):
        m, d = row.split()
        masses.append(int(m))
        distances.append(int(d))
    ladder = lane(distances,masses)
    buffer_distance = int (buffer_distance_entry.get())
    samples = []
    if filename != "":
        for row in reader(open(filename,"r"),delimiter="\t"):
            row = [int(x) for x in row]
            samples.append(lane(row))
    return ladder, buffer_distance, samples

def run():
    data = read_input()
    process_data(*data)
    showinfo("", f"Output saved to: {outfile}.")
    exit(0)

if __name__ == "__main__" :
    default_ladder = lane(
        [10, 30, 45, 65, 80, 95],
        [1200, 700, 500, 300, 200, 100]
        )

    root = Tk()
    buffer_distance_entry = StringVar()
    ladder_textarea = StringVar()
    fileinfo= StringVar()
    Label(text="Enter distance run by loading buffer in mm. Ex.:125",
        justify=LEFT).pack(side=TOP)
    entry = Entry(textvariable=buffer_distance_entry)
    entry.pack(side=TOP)
    buffer_distance_entry.set("125")
    Label(text="Enter known weight and measured distance of the standard.\n"
        + "Separate the values by a single space. One line per band.\n"
        + "(Default text may be used for a demo or discarded)",
        justify=LEFT).pack()
    textarea = Text(height=15) #,textvariable=ladder_textarea)
    default_text = "\n".join(["{} {}".format (*band) for band in zip
        (default_ladder.MW, default_ladder.L)])
    textarea.insert(1.0, default_text)
    textarea.pack()
    Button(text="Exit", command=root.destroy).pack(
        anchor="e", side=BOTTOM)
    Button(text="Make plots", command=run).pack(
        anchor="e", side=BOTTOM)
    Button(text="Load samples", command=loadfile).pack(anchor="w", side=BOTTOM)
    Label(textvariable=fileinfo,justify=LEFT).pack(anchor="w", side=BOTTOM)
    text = ("Samples in tabular form may be loaded from a TSV"
        + "-formatted file.\n One row per sample. Each row contains"
        + "band distances from a single lane.")
    fileinfo.set(text)
    root.mainloop()

