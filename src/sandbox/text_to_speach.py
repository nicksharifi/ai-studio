from gtts import gTTS

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

text = "Hello, how are you today?"
filename = 'output.mp3'  # Specify your desired output file name

text_to_speech(text, filename)