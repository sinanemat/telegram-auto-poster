Auto Post v2.0 Ultra Pro

Created by: sina nemati TG:  @sina_nemat0
Program Name: Auto Post v2.0 Ultra Pro
Purpose: Automatically forward posts from source Telegram channels to target channels with text replacement, media support, and auto-link cleanup.

---

1. Requirements

- Android device with Termux installed
- Active Telegram account
- Internet connection
- Basic knowledge of Telegram API (API ID & API Hash)

---

2. Install Termux

1. Download Termux from F-Droid (recommended for latest updates).
2. Open Termux and allow storage access:

   termux-setup-storage

---

3. Update Termux & Install Dependencies

Run the following commands:

   pkg update && pkg upgrade -y
   pkg install python git -y
   pip install --upgrade pip
   pip install telethon

Optional dependencies: If you plan to use advanced features (media download), make sure ffmpeg is installed:

   pkg install ffmpeg -y

---

4. Download Auto Post

1. Clone or download the auto_post folder.
2. Place the auto_post.py file in the folder.
3. Make sure the folder has write permissions (all generated files will be stored here).

---

5. Telegram API Setup

1. Go to https://my.telegram.org
2. Login with your Telegram account.
3. Click API development tools -> Create new application
4. Enter app title and short name.
5. Copy your API ID and API Hash.

Keep them private. They will be used by the script to connect your Telegram account.

---

6. Running Auto Post

1. Open Termux and navigate to the folder:

   cd /path/to/auto_post

2. Run the script:

   python3 auto_post.py

3. Follow on-screen prompts:

- Enter API ID and API Hash
- Enter source channel(s) (comma-separated, include @username)
- Enter target channel(s) (comma-separated, include @username)
- Optional: setup ID replacements
- Set check interval (how often the script checks for new posts)

The script supports text and media posts, removes unwanted links, and automatically appends the target channel ID if missing.

---

7. Auto Startup on Device Boot

- The script automatically sets up Termux:Boot if available.
- It will run every time the device starts.

To enable:

1. Install Termux:Boot from F-Droid.
2. Open Termux:Boot once to grant permissions.
3. Your auto_post.py will run automatically on device startup.

---

8. File Storage

All auxiliary files (logs, JSON configs, sent messages, session) are stored inside the same folder as auto_post.py:

- config.json - stores API & channel configuration
- sent_messages.txt - keeps track of already forwarded posts
- post_log.txt - logs all forwarded messages
- auto_post_ultra_session.session - Telegram session file

---

9. Pause / Resume

- During execution, type "pause" to stop the script temporarily.
- Type "resume" to continue.

---

10. Notes / Best Practices

- Only use this script for your own channels or authorized channels.
- Do not forward content from private channels without permission.
- Avoid excessively frequent forwarding to prevent account restrictions.
- Supports media, text replacement, and auto link removal.
- Make sure your Termux has proper storage permissions.

---

11. Support

For issues, contact sina nemati (TG: @sina_nemat0) or check the script comments for guidance.

Enjoy Auto Post v2.0 Ultra Pro! 🚀
