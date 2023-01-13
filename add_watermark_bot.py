import telegram
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import subprocess, os
import time
import datetime
import qrcode

import creds

token = creds.tbot_token
updater = Updater(token, use_context=True)
bot = telegram.Bot(token=token)

def runBot(update: Update, context: CallbackContext):
    # Check if the sender is allowed
    if update.message.chat_id not in creds.tbot_chat_id_whitelist:
        return

    # Check if the video contains text to use as a name
    if update.message.caption == None:
        update.message.reply_text(
            "Video has no name. Resend with a name."     
        )
        return

    # Get the current time to add to filename to prevent repeats
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S");

    filename = update.message.caption.replace(" ", "") + "_" + current_time + ".mp4"

    # Get the video and download it to the tmp folder
    context.bot.get_file(update.message.video).download(custom_path="tmp/tmp_"+filename)
    script_path = os.getcwd() + "/"
    
    # Superpose the "logo.png" image on top of the video
    cmd_ffmpeg = "/usr/bin/ffmpeg -i %s -i %slogo.png -filter_complex \"[0:v][1:v] overlay=0:0\" -c:a copy %s" % (script_path+"tmp/tmp_"+filename, script_path, script_path+"tmp/"+filename)
    p = subprocess.Popen(cmd_ffmpeg, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    out, err = p.communicate()

    # Error control for ffmpeg
    if p.returncode != 0:
        update.message.reply_text(
            "Couldn't put watermark to: " + update.message.caption + "      Send it again."     
        )
        return

    rclone_drive = creds.rclone_drive

    # Move the file from local disk to RClone drive
    cmd_rclone = "/usr/bin/rclone move %s %s:" % (script_path+"tmp/"+filename, rclone_drive)
    p = subprocess.Popen(cmd_rclone, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    out, err = p.communicate()

    # Error control for uploading to RClone
    if p.returncode != 0:
        update.message.reply_text(
            "Couldn't upload to Drive: " + update.message.caption + "      Send it again."     
        )
        return

    update.message.reply_text(
        "Watermark added and uploaded to the drive. Filename: \"" + filename + "\""    
    )

    # Get the link from the RClone drive
    cmd_rclone_link = "/usr/bin/rclone link %s:%s" % (rclone_drive, filename)
    p = subprocess.Popen(cmd_rclone_link, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    
    # Create a QR code with the url of the uploaded video
    img = qrcode.make(out)
    qr_file = script_path+"tmp/"+filename+".png"
    img.save(qr_file)

    # Return the QR code
    bot.send_photo(update.message.chat_id, open(qr_file, 'rb'))

    # Clean the files from local disk
    os.remove("tmp/tmp_"+filename)
    os.remove("tmp/"+filename)
    os.remove(qr_file)


updater.dispatcher.add_handler(MessageHandler(Filters.video, runBot))

updater.start_polling()

