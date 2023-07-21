import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputFile
from moviepy.editor import VideoFileClip
import threading

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot and dispatcher
# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = '5909482823:AAGNtdionMCBuhdfZXD4e9sPAiCH25gg0ko'
bot = Bot(token=bot_token)
dispatcher = Dispatcher(bot)
dp = dispatcher  # Shorter alias for the dispatcher

# Middleware to log messages
dp.middleware.setup(LoggingMiddleware())

# Define the function to handle /start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Hello! Send me a video, and I'll compress it for you.")

# Define the function to handle video messages
@dp.message_handler(content_types=types.ContentTypes.VIDEO)
async def handle_video(message: types.Message):
    # Get the file path of the video on Telegram's servers
    video = message.video
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path

    # Perform video compression using MoviePy
    clip = VideoFileClip(file_path)

    # Adjust the compression settings
    compressed_file = "compressed_video.mp4"
    codec = 'libx265'  # Change the codec to 'libvpx-vp9' for VP9 compression
    bitrate = '250k'  # Adjust the bitrate as desired (e.g., '1M' for 1 Mbps)

    # Compress the video with the specified codec and bitrate
    clip.write_videofile(compressed_file, codec=codec, bitrate=bitrate)

    # Send the compressed video
    with open(compressed_file, 'rb') as video_file:
        await message.answer_video(InputFile(video_file))

    # Clean up the temporary files
    clip.close()
    os.remove(compressed_file)

# Run the bot in a separate coroutine
async def on_startup(dp):
    await bot.send_message(chat_id="YOUR_ADMIN_CHAT_ID", text="Bot started!")  # Replace with your admin chat ID
    await bot.delete_webhook()

async def run_bot():
    await bot.start_polling(skip_updates=True, on_startup=on_startup)

if __name__ == '__main__':
    # Create the asyncio event loop
    loop = asyncio.get_event_loop()

    # Run the bot in the event loop
    loop.run_until_complete(run_bot())

    # Start the Streamlit app in a separate thread
    def run_streamlit():
        os.system("streamlit run your_streamlit_app.py")

    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.start()

    # Run the event loop indefinitely
    loop.run_forever()
