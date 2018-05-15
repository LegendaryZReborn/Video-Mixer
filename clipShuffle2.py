import imageio
imageio.plugins.ffmpeg.download()
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
import random
from datetime import datetime
import time
import os

clip_dir = "Clips/"
audio_dir = "Audio/"

def getFilesInDir(dir):
	filenames = []
	for file in os.listdir(dir):
		filenames.append(file)
	return filenames
	
def collectClipFragments(originalClip, clips, targetSubDuration, intervals):
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

		clips.append(originalClip.subclip(startTime, endTime))
			
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

	final_clips = []
	numClips = 0
	targetSubDuration = targetDuration/len(filenames)
	fileDir = ""
	
	for filename in filenames:
	
		if (os.path.isabs(filename)):
			fileDir = filename
		else:
			fileDir = clip_dir + filename
			
		originalClip = VideoFileClip(fileDir)
		originalClip = originalClip.resize((1280, 720))
		final_clips = collectClipFragments(originalClip, final_clips, targetSubDuration, intervals)
	
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
	
	return finalClip
	#newFileName = "Vid" + time.strftime("%Y%m%d-%H%M%S") + ".mp4"
	#finalClip.write_videofile(newFileName, fps=24, threads=4)		

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