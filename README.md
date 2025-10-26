# ai-studio

for setup run setup.sh

for backup DB deploy ./script/backup_manager.py


making picture:
openJourney
diffusion-ai


Text to Audio:
offer SRT to:

gTTS (google Text to Speach)
pyttsx3 (text to speach)

Auto Subtitle:
Autosub
Whisper
Subtitles-Generator
Google Cloud Speech-to-Text API

Cross-platform publishing:
- Add your channels to the DB with `ai_channels.type` set to `youtube`, `tiktok`, or `instagram`.
- The main loop discovers all active channels and uses a platform-specific publisher.
- YouTube is fully implemented; TikTok and Instagram are stubbed to record uploads in DB (replace with real API calls later).

Files of interest:
- `src/publisher_factory.py`: maps channel type to publisher
- `src/publisher_tiktok.py`, `src/publisher_instagram.py`: minimal short-video publishers
- `src/__main__.py`: now iterates all active channels via the publisher factory
