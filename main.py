import discord
from discord.ext import commands
import cv2
import numpy as np
from PIL import Image
import io
import os
import subprocess
from urllib.request import urlopen
import tempfile

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper function to process video files
async def process_video(ctx, video_url, process_func, *args):
    try:
        # Download video
        temp_input = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_output = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        
        await ctx.send("Processing video... Please wait.")
        
        # Process frames
        cap = cv2.VideoCapture(temp_input.name)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_output.name, fourcc, fps, (width, height))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Apply the effect
            processed_frame = process_func(frame, *args)
            out.write(processed_frame)
            
        cap.release()
        out.release()
        
        # Send processed video
        await ctx.send(file=discord.File(temp_output.name))
        
        # Cleanup
        os.unlink(temp_input.name)
        os.unlink(temp_output.name)
        
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Effect functions
def greyscale(frame):
    return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)

def hsl_adjust(frame, hue, saturation, brightness):
    hls = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS)
    h, l, s = cv2.split(hls)
    
    h = (h + hue) % 180
    s = cv2.multiply(s, saturation)
    l = cv2.multiply(l, brightness)
    
    merged = cv2.merge([h, l, s])
    return cv2.cvtColor(merged, cv2.COLOR_HLS2BGR)

def contrast_brightness(frame, contrast, brightness):
    return cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)

def sepia(frame, intensity=1):
    sepia_matrix = np.array([
        [0.393 + 0.607 * (1 - intensity), 0.769 - 0.769 * (1 - intensity), 0.189 - 0.189 * (1 - intensity)],
        [0.349 - 0.349 * (1 - intensity), 0.686 + 0.314 * (1 - intensity), 0.168 - 0.168 * (1 - intensity)],
        [0.272 - 0.272 * (1 - intensity), 0.534 - 0.534 * (1 - intensity), 0.131 + 0.869 * (1 - intensity)]
    ])
    return cv2.transform(frame, sepia_matrix)

def invert(frame):
    return cv2.bitwise_not(frame)

# Bot commands
@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')

@bot.command()
async def help(ctx):
    help_text = """
    **KermitVideo Bot Commands:**
    !help - Show this help message
    !greyscale - Convert video to greyscale
    !hsl [hue] [saturation] [brightness] - Adjust HSL values
    !cb [contrast] [brightness] - Adjust contrast and brightness
    !sepia [intensity] - Apply sepia effect
    !invert - Invert video colors
    !pitch [-36 to +36] - Adjust video pitch
    !pitchmix [2-16] - Mix video pitch
    !lut [url] - Apply LUT from URL
    !fisheye [1-10] - Apply fisheye effect
    !pinch [1-10] - Apply pinch effect
    !swirl [size] [degrees] - Apply swirl effect
    !wave [h/v] [amplitude] [length] - Apply wave effect
    !rotate - Rotate video
    !fxscript [code] - Apply custom effects script
    !ffmpeg [command] - Run custom FFmpeg command
    """
    await ctx.send(help_text)

@bot.command()
async def greyscale(ctx):
    if ctx.message.attachments:
        video_url = ctx.message.attachments[0].url
        await process_video(ctx, video_url, greyscale)
    else:
        await ctx.send("Please attach a video file!")

@bot.command()
async def hsl(ctx, hue: float, saturation: float, brightness: float):
    if ctx.message.attachments:
        video_url = ctx.message.attachments[0].url
        await process_video(ctx, video_url, hsl_adjust, hue, saturation, brightness)
    else:
        await ctx.send("Please attach a video file!")

@bot.command()
async def cb(ctx, contrast: float, brightness: float):
    if ctx.message.attachments:
        video_url = ctx.message.attachments[0].url
        await process_video(ctx, video_url, contrast_brightness, contrast, brightness)
    else:
        await ctx.send("Please attach a video file!")

@bot.command()
async def sepia(ctx, intensity: float = 1.0):
    if ctx.message.attachments:
        video_url = ctx.message.attachments[0].url
        await process_video(ctx, video_url, sepia, intensity)
    else:
        await ctx.send("Please attach a video file!")

@bot.command()
async def invert(ctx):
    if ctx.message.attachments:
        video_url = ctx.message.attachments[0].url
        await process_video(ctx, video_url, invert)
    else:
        await ctx.send("Please attach a video file!")

# Run the bot
bot.run('YOUR_BOT_TOKEN_HERE')
