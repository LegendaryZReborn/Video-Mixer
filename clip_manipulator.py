import imageio
imageio.plugins.ffmpeg.download()

import random
import time
import os

from multiprocessing import Process, Manager, Pool
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy import Clip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from datetime import datetime
from functools import partial

clip_dir = "Clips/"
audio_dir = "Audio/"

def getFilesInDir(dir):
	filenames = []
	for file in os.listdir(dir):
		filenames.append(file)
	return filenames

def flattenList(list):
	newList = []
	for l in list:
		newList += l
		
	return newList
		
def collectClipFragments(targetSubDuration, intervals, filename):
	clips = []
	originalClip = VideoFileClip(clip_dir + filename)
	originalClip = originalClip.resize((1280, 720))
	intervals_len = len(intervals)
	stride = intervals[random.randint(0, intervals_len - 1)]
	startTime = random.uniform(0, originalClip.duration - targetSubDuration)
	endTime = startTime + stride
	duration = 0

	#Fill the list with sub-clips of varied lengths from originalClips until targetSubDuration is reached
	while duration < targetSubDuration:
		duration += (endTime - startTime)
		
		if(duration > targetSubDuration):
			overflowTime = duration - targetSubDuration
			endTime  = endTime - overflowTime
			duration = duration - overflowTime

		c = Clip(originalClip.subclip(startTime, endTime))
		clips.append(c)
			
		#crop out the sub-clip between startTIme and endTime from the originalClip
		subClip1 = originalClip.subclip(0, startTime)
		subClip2 = originalClip.subclip(endTime, originalClip.duration)
		originalClip = concatenate_videoclips([subClip1, subClip2], padding = -0.2)
		
		leftOverDuration = targetSubDuration - duration
		stride = intervals[random.randint(0, intervals_len - 1)]
		startTime = random.uniform(0, originalClip.duration - leftOverDuration)
		endTime = startTime + stride
	return clips
		
def applyEffect(clip, crossfadein=False, crossfadeout=False):	
	if(crossfadein):
		clip = clip.crossfadein(1)

	return clip

def mixClips(filenames, intervals, targetDuration, audioClip=None):
	random.seed(datetime.now())
		
	numClips = 0
	targetSubDuration = targetDuration/len(filenames)
	final_clips = []
	
	pool = Pool ()
	func = partial(collectClipFragments, targetSubDuration, intervals)
	result = pool.map(func, filenames)
	#result = flattenList(result)
	print (result)
'''		
	numClips = len(final_clips)
	random.shuffle(final_clips)
	
	#Apply effects to each clip
	final_clips[0] = applyEffect(final_clips[0], crossfadein=True)
	for i in range(1, numClips):
		final_clips[i] = final_clips[i].set_start(final_clips[i - 1].end - 0.2)
		final_clips[i] = final_clips[i].crossfadein(0.2)

	final_clips[numClips - 1] = final_clips[numClips - 1].crossfadeout(0.2)
	
	finalClip = CompositeVideoClip(final_clips)
	
	if(audioClip is None):
		finalClip = finalClip.without_audio()
	else:
		finalClip = finalClip.set_audio(audioClip)
		
	newFileName = "Vid" + time.strftime("%Y%m%d-%H%M%S") + ".mp4"
	finalClip.write_videofile(newFileName, fps=24, threads=4)		
'''
def main():
	intervals = [2, 2, 3, 4]
	#intervals = [4, 7, 10]
	#intervals = [3, 4, 5]
	#intervals = [10, 8, 6]
	filenames = getFilesInDir(clip_dir)
	audioClip = AudioFileClip(audio_dir + "ULTIMATE BATTLE FULL SONG HQ VERSION ( FINALLY) _ AKIRA KUSHIDA _ INSERT SONG _  1.m4a")
	finalClip = mixClips(filenames, intervals, audioClip.duration, audioClip)
	
	
if __name__ == "__main__":
	main()