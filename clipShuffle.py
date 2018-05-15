import imageio
imageio.plugins.ffmpeg.download()
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
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
	
def mixClips(filenames, intervals, target_duration, audioClip=None):
	clips = []
	numClips = 0
	final_duration = 0
	intervals_len = len(intervals)
	random.seed(datetime.now())

	for filename in filenames:
		originalClip = VideoFileClip(clip_dir + filename)
		originalClip = originalClip.resize((1280, 720))
		
		startTime = 0
		endTime = intervals[random.randint(0, intervals_len - 1)]
		duration = originalClip.duration

		#Add a new subclip to the array 
		while endTime <= duration:
			clips.append(originalClip.subclip(startTime, endTime))
			startTime = endTime
			stride = intervals[random.randint(0, intervals_len - 1)]
			endTime += stride
			numClips += 1

		if(endTime > duration):
			diff = endTime - duration
			clips.append(originalClip.subclip(startTime, endTime - diff))
			numClips += 1
			
		final_duration += duration
		
	random.shuffle(clips)
	
	final_clips = []
	current_duration = 0
	index = 0;
	while current_duration < target_duration and index < numClips:
		c = clips[index]
		final_clips.append(c)
		current_duration +=  c.duration
		index += 1;
		
	final_clips[0] = final_clips[0].crossfadein(1)
	for i in range(1, len(final_clips)):
		final_clips[i] = final_clips[i].set_start(final_clips[i - 1].end - 0.1)
		final_clips[i] = final_clips[i].crossfadein(0.1)

	final_clips[len(final_clips) - 1] = final_clips[len(final_clips) - 1].crossfadeout(0.2)

		
	finalClip = CompositeVideoClip(final_clips)
	
	if(audioClip is None):
		finalClip = finalClip.without_audio()
	else:
		finalClip = finalClip.set_audio(audioClip)
		
	newFileName = "Vid" + time.strftime("%Y%m%d-%H%M%S") + ".mp4"
	finalClip.write_videofile(newFileName, fps=24)		

def main():
	#intervals = [1, 2, 2]
	#intervals = [4, 7, 10]
	intervals = [3, 4, 5]
	#intervals = [10, 8, 6]
	filenames = getFilesInDir(clip_dir)
	audioClip = AudioFileClip(audio_dir + "Everybody's Circulation.mp3")
	finalClip = mixClips(filenames, intervals, audioClip.duration, audioClip)
	
	
if __name__ == "__main__":
	main()