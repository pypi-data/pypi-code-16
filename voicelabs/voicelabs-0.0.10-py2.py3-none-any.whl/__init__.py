import sys

if (sys.version_info > (3, 0)):
	from voicelabs.voicelabs import VoiceInsights
else:
	from voicelabs import VoiceInsights
