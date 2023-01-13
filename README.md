# Telegram Bot to update to RClone with QR
Telegram bot that uploads a video to an RClone drive and returns a QR code with a link to it (only tried with Google Drive, should work with any RClone drive that allows the link option to create a QR from it).

**This was a quick bot done as a favour to someone else. There's a lot of room for improvement, but it works.**

## Requirements
- `ffmpeg`
- `rclone` with a drive set up
- `python3` with `telegram` and `qrcode` installed
- Folder named `tmp` inside the same directory with the script
- `logo.png` file with the watermark. Must be same size as the video taken and have transparent background, since all this bot does is put the PNG file on top of the video.
