import logging
import os
import telepot
from telepot.namedtuple import Update
from moviepy.editor import VideoFileClip

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the function to handle /start command
def start(chat_id):
    bot.sendMessage(chat_id, "Hello! Send me a video, and I'll compress it for you.")

# Define the function to handle video messages
def handle_video(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    
    if content_type == 'video':
        # Get the file_id of the video
        file_id = msg['video']['file_id']
        
        # Get the file path of the video on Telegram's servers
        file_info = bot.getFile(file_id)
        file_path = file_info['file_path']

        # Perform video compression using MoviePy
        clip = VideoFileClip(file_path)

        # Adjust the compression settings
        compressed_file = "compressed_video.mp4"
        codec = 'libx265'  # Change the codec to 'libvpx-vp9' for VP9 compression
        bitrate = '250k'  # Adjust the bitrate as desired (e.g., '1M' for 1 Mbps)

        # Compress the video with the specified codec and bitrate
        clip.write_videofile(compressed_file, codec=codec, bitrate=bitrate)

        # Send the compressed video
        bot.sendVideo(chat_id, open(compressed_file, 'rb'))

        # Clean up the temporary files
        clip.close()
        os.remove(compressed_file)

# Create a callable class for the Gunicorn entry point
class TelegramBotApp:
    def __init__(self):
        # Replace 'YOUR_BOT_TOKEN' with your actual bot token
        self.bot_token = '5909482823:AAHOTwjj5qkbjpVN15aZuZArFCqHaR60uyg'
        self.bot = telepot.Bot(self.bot_token)

    def __call__(self, env, start_response):
        try:
            content_length = int(env.get('CONTENT_LENGTH', 0))
            body = env['wsgi.input'].read(content_length).decode()
            update = telepot.glance(telepot.flavor.TurboGears2, body, self.bot_token)
            handle_video(update[2])
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"OK"]
        except Exception as e:
            logger.error(str(e))
            start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
            return [b"Error"]

if __name__ == '__main__':
    # Create an instance of the TelegramBotApp
    app = TelegramBotApp()
    # Start the bot using Gunicorn
    from gunicorn.app.base import BaseApplication
    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:10000',
        'workers': 1,  # You can increase this if needed
    }
    StandaloneApplication(app, options).run()
