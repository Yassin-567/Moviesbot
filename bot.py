import logging 
import os 
import telepot 
from telepot.loop import MessageLoop 
from moviepy.editor import VideoFileClip
  
# Set up logging 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO) 
logger = logging.getLogger() 
  
# Define the function to handle /start command 
def start(chat_id): 
    bot.sendMessage(chat_id, "Hello! Send me a video, and I'll compress it for you.") 
  
# Define the function to handle video messages 
def handle_video(msg): 
    content_type, chat_type, chat_id = telepot.glance(msg) 
    if content_type == 'video': 
        # Get the file path of the video on Telegram's servers 
        file_id = msg['video']['file_id'] 
        file_path = bot.getFile(file_id)['file_path'] 
  
        # Perform video compression using MoviePy 
        clip = VideoFileClip(file_path) 
  
        # Adjust the compression settings 
        compressed_file = "compressed_video.mp4" 
        codec = 'libx265'  # Change the codec to 'libvpx-vp9' for VP9 compression 
        bitrate = '250k'  # Adjust the bitrate as desired (e.g., '1M' for 1 Mbps) 
  
        # Compress the video with the specified codec and bitrate 
        clip.write_videofile(compressed_file, codec=codec, bitrate=bitrate) 
  
        # Send the compressed video 
        with open(compressed_file, 'rb') as f: 
            bot.sendVideo(chat_id, f) 
  
        # Clean up the temporary files 
        clip.close() 
        os.remove(compressed_file) 
  
# Set up the Telegram bot 
def app(*args, **kwargs):  # Allow for any arguments passed by Gunicorn 
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token 
    bot_token = '5909482823:AAFYOFK2Rsb5lphQHGZSMj_3krCN0MpZCKo' 
  
    # Initialize the bot 
    global bot 
    bot = telepot.Bot(bot_token) 
  
    # Add message handlers 
    MessageLoop(bot, {'chat': handle_video}).run_as_thread() 
  
    # Start the bot 
    logger.info("Bot started!") 
    return 'Bot is running' 
  
if __name__ == '__main__':
    app()  # Call the app() function without passing any arguments
