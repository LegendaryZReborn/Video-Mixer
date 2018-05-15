from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.decorators import requires_duration
from functools import partial
from math import sqrt
import time
import threading
import numpy as np
import pygame as pg
import math
from clipShuffle2 import *

pg.init()

images_dir = "Images/"
clip_dir = "Clips/"

class VideoPlayer(Frame):
	def __init__(self, *args, **kwargs):
		self.clip = kwargs.pop('clip', None) #pop keyward clip and its value from kwargs
		Frame.__init__(self, *args, **kwargs)
		self.pack(side="top", fill="both", expand=True)
		
		self.canvas = Canvas(self, bg="#212121")
		self.canvas.pack(side="top", fill="both", expand=True)
		self.canvas.update()	#so the width returned from self.canvas.winfo_width() can actually be right
		canvas_width = self.canvas.winfo_width()
		
		root = args[0]
		action = partial(self.onClose, root)
		root.protocol("WM_DELETE_WINDOW", action)
		
		action_scrub = partial(self.scrub)
		self.videoSlider = ttk.Scale(master=self, orient=HORIZONTAL, command=action_scrub)
		self.videoSlider.pack(side="top", anchor="center", fill=X, expand=False)	
		
		#Control and widgets initialization 
		controlFrame = Frame(self, bd=5, relief=SUNKEN)
		controlFrame.pack(side="top", anchor="center", fill=X, expand=False, pady=10)
		controlFrame.grid_columnconfigure(0, weight=1, uniform='third')
		controlFrame.grid_columnconfigure(1, weight=1, uniform='third')
		controlFrame.grid_columnconfigure(2, weight=1, uniform='third')

		emptyFrame = Frame(master=controlFrame)
		emptyFrame.grid(row=0, column=0, sticky="nsew")
		
		buttonsFrame = Frame(master=controlFrame)
		buttonsFrame.grid(row=0, column=1)
		
		othersFrame = Frame(master=controlFrame)
		othersFrame.grid(row=0, column=2, sticky="nsew")
		
		image = Image.open(images_dir + "play.png")
		image = image.resize((40, 40), Image.ANTIALIAS)
		self.playImg  = ImageTk.PhotoImage(image)
		
		image = Image.open(images_dir + "stop.png")
		image = image.resize((40, 40), Image.ANTIALIAS)
		self.stopImg  = ImageTk.PhotoImage(image)
		
		image = Image.open(images_dir + "pause.png")
		image = image.resize((40, 40), Image.ANTIALIAS)
		self.pauseImg  = ImageTk.PhotoImage(image)
		
		image = Image.open(images_dir + "skipbackward.png")
		image = image.resize((40, 40), Image.ANTIALIAS)
		self.skipBackwardImg  = ImageTk.PhotoImage(image)
		
		image = Image.open(images_dir + "skipforward.png")
		image = image.resize((40, 40), Image.ANTIALIAS)
		self.skipForwardImg  = ImageTk.PhotoImage(image)
		
		action_play = partial(self.play)		
		action_skipb = partial(self.skipBack)	
		action_skipf = partial(self.skipForward)	
		action_stop = partial(self.stop)
		
		skipBackwardButton = Button(master=buttonsFrame, width=40, height=40, image=self.skipBackwardImg, text="skip back", relief = FLAT, command=action_skipb)
		skipBackwardButton.pack(side="left")
		pauseButton = Button(master=buttonsFrame, width=40, height=40, image=self.pauseImg, text="pause", relief = FLAT, command=self.pause)
		pauseButton.pack(side="left")
		playButton = Button(master=buttonsFrame, width=40, height=40, image=self.playImg, text="play", relief = FLAT, command=action_play)
		playButton.pack(side="left")
		stopButton = Button(master=buttonsFrame, width=40, height=40, image=self.stopImg, text="stop", relief = FLAT, command=action_stop)
		stopButton.pack(side="left")
		pauseButton = Button(master=buttonsFrame, width=40, height=40, image=self.skipForwardImg, text="skip forward", relief = FLAT, command=action_skipf)
		pauseButton.pack(side="left")
		
		volumeScale = Scale(master=othersFrame, orient=HORIZONTAL, to=100, resolution=1, command=self.volumeScrub)
		volumeScale.pack(side="right", anchor=NE)
		volumeScale.set(50)
		
		self.timeLabel = Label(master=emptyFrame, text="0:00:00 | 0:00:00", font=("Courier", 10))
		self.timeLabel.pack(side="left", anchor="center")
		
		
		#configure defaults for the clip
		if self.clip is not None:
			self.elapsedTime = 0
			self.duration = self.clip.duration
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
		
		self.videothread = None
		self.audiothread = None
		
		#Flag signal to signal video pausing and stoping
		self.pauseFlag = threading.Event()
		self.stopFlag = threading.Event()
		
		self.volume =50
		
	def setClip(self, clip):
		self.clip = clip
		
		#configure defaults for the clip
		self.elapsedTime = 0
		self.duration = self.clip.duration
		elapsedTimeStr = self.getTimeStr()
		durationTimestr = self.getTimeStr(self.clip.duration)		
		self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
		return
	def getImageAtTime(self,fps=24):
		step = 1.0/fps
		frame_num = self.elapsedTime / step	#calculate the frame number at the current time
		t = step * frame_num	#time t for that frame
		npImage = self.clip.get_frame(t)
		return npImage

	def getTimeStr(self, t=None):
		if t is None:
			t = self.elapsedTime
	
		hours = int(t / 3600)
		t -= (hours * 3600)
		minutes = int(t/ 60)
		t -= (minutes * 60)
		seconds = int(t)
		
		if len(str(seconds)) < 2:
			second_str = "0" + str(seconds)
		else:
			second_str = str(seconds)
			
		if len(str(minutes)) < 2:
			minute_str = "0" + str(minutes)
		else:
			minute_str = str(minutes)
			
		time_string = str(hours) + ":" + minute_str + ":" + second_str
		
		return time_string
		
	def display (self, image=None):
		canvasWidth = self.canvas.winfo_width()
		canvasHeight = self.canvas.winfo_height()
		
		#convert numpy array data to Image
		image = Image.fromarray(image, 'RGB')
		
		originalWidth = image.width
		originalHeight = image.height
		
		#calculate the aspect ratio that must be kept
		#referenced: https://stackoverflow.com/questions/33701929/how-to-resize-an-image-in-python-while-retaining-aspect-ratio-given-a-target-s
		aspect = originalWidth / originalHeight
		
		area =	canvasWidth * canvasHeight
		height = int(sqrt(area / aspect))
		width = int(height * aspect)
		
		image = image.resize((width, height), Image.ANTIALIAS)
		photoImage = ImageTk.PhotoImage(image)
		self.canvas.create_image(canvasWidth/2, canvasHeight/2, image=photoImage, anchor='center')
		self.photoImage = photoImage #reference to image must be stored or it will be deleted
	
	def previewVideo(self, fps=24, audio=True, videoFlag=None, audioFlag=None):
		
		if (audio and videoFlag and audioFlag): #synchronize with audio
			videoFlag.set() #tell the audiothread video is ready
			audioFlag.wait() #wait for the audio to be ready
			
		self.pauseFlag.set()
		
		step = 1.0/fps
		prev_frame = max(0, (self.elapsedTime / step) - 1.0)
		isPlaying = True
		
		startTime = time.time() - self.elapsedTime	
		npImage =  self.clip.get_frame(prev_frame)
		self.display(npImage)
			
		while isPlaying:
			if self.pauseFlag is not None:
				self.pauseFlag.wait()
				
			if self.stopFlag.isSet():
				isPlaying = False
				return

			self.elapsedTime = time.time() - startTime

			#stuff that need to change along with the elapsedTime
			self.videoSlider.configure(value=self.elapsedTime)
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)
		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)
			
			frame_num = self.elapsedTime / step	#calculate the frame number at the current time
			
			if frame_num - prev_frame >= 1.0:
				t = step * frame_num	#time t for that frame
				npImage = self.clip.get_frame(t)	
				self.display(npImage)			
				prev_frame_num = frame_num
			
			if self.elapsedTime >= self.duration:
				isPlaying = False
			
		videoFlag.clear()
		return
			
	#heavily references moviepy's preview.py preview()			
	#@requires_duration
	def previewAudio(self, clip, fps=22050,  buffersize=4000, nbytes=2, audioFlag=None,
				videoFlag=None):
		"""
		Plays the sound clip with pygame.
		
		Parameters
		-----------
		
		fps
		   Frame rate of the sound. 44100 gives top quality, but may cause
		   problems if your computer is not fast enough and your clip is
		   complicated. If the sound jumps during the preview, lower it
		   (11025 is still fine, 5000 is tolerable).
			
		buffersize
		  The sound is not generated all at once, but rather made by bunches
		  of frames (chunks). ``buffersize`` is the size of such a chunk.
		  Try varying it if you meet audio problems (but you shouldn't
		  have to).
		
		nbytes:
		  Number of bytes to encode the sound: 1 for 8bit sound, 2 for
		  16bit, 4 for 32bit sound. 2 bytes is fine.
		
		audioFlag, videoFlag:
		  Instances of class threading events that are used to synchronize
		  video and audio during ``VideoClip.preview()``.
		
		"""
		self.duration = clip.duration
		
		pg.mixer.quit()
		
		pg.mixer.init(fps, -8 * nbytes, clip.nchannels, 1024)
		totalsize = int(fps*clip.duration)
		chunk_start = int(((self.elapsedTime * fps) / 4000) + 0.5) * 4000
		pospos = np.array(list(range(chunk_start, totalsize,	buffersize))+[totalsize])
		tt = (1.0/fps)*np.arange(pospos[0], pospos[1])
		sndarray = clip.to_soundarray(tt, nbytes=nbytes, quantize=True)
		chunk = pg.sndarray.make_sound(sndarray)
		
		if (audioFlag is not None) and (videoFlag is not None):
			audioFlag.set()
			videoFlag.wait()
		
		self.pauseFlag.set()
		channel = chunk.play()
		
		for i in range(1, len(pospos)-1):	
			channel.set_volume(self.volume/100)

			if self.pauseFlag is not None:
				self.pauseFlag.wait()
			
			self.sharedTime = (1/fps) * pospos[i]
			
			tt = (1.0/fps)*np.arange(pospos[i], pospos[i+1])
			sndarray = clip.to_soundarray(tt, nbytes=nbytes, quantize=True)
			
			chunk = pg.sndarray.make_sound(sndarray)
			
			while channel.get_queue():
				time.sleep(0.003)
				if videoFlag is not None:
					if self.stopFlag.isSet() or not videoFlag.isSet():
						channel.stop()
						del channel
						return
			channel.queue(chunk)
		
		return
		
	def initializeThreads(self, fps=24, audio=True, audio_fps=22050, audio_buffersize=3000, audio_nbytes=2):
		audio = (self.clip.audio is not None) and audio

		if audio:	
			#two flags to synch audio and video
			videoFlag = threading.Event()
			audioFlag =	 threading.Event()
			
			self.audiothread = threading.Thread(target=self.previewAudio, 
				args = (self.clip.audio, audio_fps, audio_buffersize, audio_nbytes, audioFlag, videoFlag))
			self.audiothread.setDaemon(True)

		self.videothread =	threading.Thread(target=self.previewVideo,
			args=(fps, audio, videoFlag, audioFlag))
		self.videothread.setDaemon(True)
		
		return
		
		
	#heavily references moviepy's preview.py preview()	
	def play(self ):		
		if self.clip is not None:
			self.stopFlag.clear()

			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)
			self.videoSlider.configure(to=self.clip.duration)

			if self.elapsedTime >= self.clip.duration:
				self.elapsedTime = 0

			if self.videothread is None or not self.videothread.isAlive():
				self.initializeThreads()

				self.audiothread.start()
				self.videothread.start()
		
			else:
				self.pauseFlag.set()
		return

	def pause(self):
		self.pauseFlag.clear() 
		
		return
	
	def stop(self):
		if self.clip is not None:
			self.stopFlag.set()	
			
			self.elapsedTime = 0
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
			self.videoSlider.configure(value=self.elapsedTime)
			
			npImage = self.clip.get_frame(0)	
			self.display(npImage)
		return
		
	def skipBack(self):
		if self.clip is not None:
			newElapsedTime = max(0, self.elapsedTime - 10.0)
			
			self.stopFlag.set()	
			
			self.elapsedTime = newElapsedTime
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
			
			self.videoSlider.configure(value=self.elapsedTime)

			npImage = self.getImageAtTime()
			self.display(npImage)
			
		return
		
	def skipForward(self):
		if self.clip is not None:
			newElapsedTime = min(self.duration, self.elapsedTime + 10.0)

			self.stopFlag.set()	
			
			self.elapsedTime = newElapsedTime
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
			
			self.videoSlider.configure(value=self.elapsedTime)

			npImage = self.getImageAtTime()
			self.display(npImage)
			
		return
	
	def scrub(self, value):
		if self.clip is not None:
			self.stopFlag.set()	
			
			self.elapsedTime = float(value)	#value was passed by ttk.Scale as a str for some odd reason
			elapsedTimeStr = self.getTimeStr()
			durationTimestr = self.getTimeStr(self.clip.duration)		
			self.timeLabel.configure(text=elapsedTimeStr + " | " + durationTimestr)	
			
			npImage = self.getImageAtTime()
			self.display(npImage)
			
		return
	
	def volumeScrub(self, value):
		value = float(value)
		self.volume = value
		
		return
		
	def onClose(self, root):
		self.stopFlag.set()
		time.sleep(0.2) 	#sleeps a bit to ensure no segmentation fault caused by straggling daemon threads
		root.destroy()
		
		return

intervals = [2, 2, 3, 4]

filenames = getFilesInDir(clip_dir)
audioClip = AudioFileClip(audio_dir + "Everybody's Circulation.mp3")
finalClip = mixClips(filenames, intervals, audioClip.duration, audioClip)		

root = Tk()
root.geometry("800x480")
#c = VideoFileClip(clip_dir + "NarutovsSasuke.mp4")
all = VideoPlayer(root, clip=finalClip)
root.title('Tkinter Player')
root.mainloop()

