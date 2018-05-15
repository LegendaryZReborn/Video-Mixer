from clipShuffle2 import *
from tkinter import *
from tkinter import filedialog, scrolledtext, ttk

LARGE_FONT = ("Verdana", 12)
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480

class Application(Tk):
	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)
		
		self.title("Video Clip Randomizer")
		#self.minsize(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
		windowSize = str(DEFAULT_WIDTH) + "x" + str(DEFAULT_HEIGHT)
		self.geometry(windowSize)
		
		container = Frame(self)
		container.pack(side="top", fill="both", expand=True)	
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)		

		self.frames = {}	
		
		frame = HomePage(container, self)
		
		self.frames[HomePage] = frame
		
		frame.grid(row=0, column=0, sticky="nsew")
		
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)		
		
		self.showFrame(HomePage)	

	def showFrame(self, frame):
		frame = self.frames[frame]
		frame.tkraise()

class HomePage(Frame):
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		
		self.createWidgets()
	
	
	def generateVideo(self):
		intervals = [3, 4, 5]
		filenames = self.filenames
		
		if(filenames):
			audioClip = AudioFileClip(audio_dir + "Everybody's Circulation.mp3")
			mixClips(filenames, intervals, 10)
		
	def browseFilenames(self):
		filetuple = filedialog.askopenfilenames(parent=self, title="Choose your video files")
		self.filenames = list(filetuple)
		
		self.selectedFileBox.delete(1.0, END) #clears textbox
		
		for f in self.filenames:
			self.selectedFileBox.insert(END, f + "\n")

		
	def createWidgets(self):
		
		self.panedWindow = ttk.Panedwindow(self, orient="vertical")
		self.panedWindow.grid(row=0, column=0, sticky="nsew")
		
	
		self.topPane = ttk.Panedwindow(self.panedWindow, orient="horizontal")
		self.bottomPane = ttk.Panedwindow(self.panedWindow, orient="horizontal")   # second pane
		
		self.tlFrame = ttk.Labelframe(self.topPane, text='Pane1')
		self.trFrame = ttk.Labelframe(self.topPane, text='Pane2')   # second pane
		self.blFrame = ttk.Labelframe(self.bottomPane, text='Pane3')
		self.brFrame = ttk.Labelframe(self.bottomPane, text='Pane4')  
		
		self.panedWindow.add(self.topPane, weight=2)
		self.panedWindow.add(self.bottomPane, weight=1)
		self.topPane.add(self.tlFrame, weight=1)
		self.topPane.add(self.trFrame, weight=5)
		self.bottomPane.add(self.blFrame, weight=1)
		self.bottomPane.add(self.brFrame, weight=5)
		
		'''
		#Stop frames from resizing based on the widgets they contain
		self.controlFrame.grid_propagate(False)
		self.previewFrame.grid_propagate(False)
		self.timelineFrame.grid_propagate(False)
'''
		#Create and configure other need widgets within each frame
		self.selectedFileBox = scrolledtext.ScrolledText(self.trFrame)
		self.selectedFileBox.grid(row=0, column=0, sticky="nsew")
	'''	
		self.Browse = Button(self.controlFrame, text="Browse", fg="black", command=self.browseFilenames)		
		self.Generate = Button(self.controlFrame, text="Generate", fg="black", command=self.generateVideo)		
		self.Quit = Button(self.controlFrame, text="Quit", fg="black", command=self.quit)
		
		
		self.Browse.grid(row=0, column=0)
		self.Generate.grid(row=0, column=1)
		self.Quit.grid(row=0, column=2)
		'''
		
	
		
def main():
	app = Application()
	app.mainloop()
	#root.destroy()		

	
if __name__ == "__main__":
	main()
