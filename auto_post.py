# ============================================================
#   Auto Post v1.0  Ultra Pro
#   Created by: sina nemati
# ============================================================

import os, sys, json, re, asyncio, time, threading
from datetime import datetime
from telethon import TelegramClient

# -------------------- مسیر فایل‌ها ----------------------
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE     = os.path.join(BASE_DIR, "config.json")
LOG_FILE        = os.path.join(BASE_DIR, "post_log.txt")
LAST_SEEN_FILE  = os.path.join(BASE_DIR, "last_seen.json")  # { "@source1": last_id, "@source2": last_id, ... }

# -------------------- رنگ‌ها ---------------------------
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# -------------------- ASCII Art پویا ----------------
ASCII = r"""
   ___        _   _            ____             _   _  __     ___  
  / _ \ _ __ | |_(_) ___ ___  |  _ \ ___  _ __ | |_| |/ /    / _ \ 
 | | | | '_ \| __| |/ __/ _ \ | |_) / _ \| '_ \| __| ' /    | | | |
 | |_| | | | | |_| | (_|  __/ |  __/ (_) | | | | |_| . \    | |_| |
  \___/|_| |_|\__|_|\___\___| |_|   \___/|_| |_|\__|_|\_\    \___/ 

                🌟 Auto Post v1.0 Ultra Pro 🌟
"""

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def banner():
    clear()
    print(Colors.CYAN + ASCII + Colors.ENDC)

# -------------------- ورودی/تنظیمات -----------------
def ask_user_config():
    print(Colors.GREEN + "\n📝 Enter your Telegram API credentials" + Colors.ENDC)
    print(Colors.YELLOW + "   1) Go to https://my.telegram.org" + Colors.ENDC)
    print(Colors.YELLOW + "   2) API development tools -> Create new application" + Colors.ENDC)
    api_id = input("🔹 API ID: ").strip()
    api_hash = input("🔹 API Hash: ").strip()

    print(Colors.GREEN + "\n📡 Enter source channels (comma separated, use @username):" + Colors.ENDC)
    sources = [s.strip() for s in input("🔹 Sources: ").strip().split(',') if s.strip()]

    print(Colors.GREEN + "\n🎯 Enter target channels (comma separated, use @username):" + Colors.ENDC)
    targets = [t.strip() for t in input("🔹 Targets: ").strip().split(',') if t.strip()]

    # replacements
    print(Colors.YELLOW + "\n🔧 ID replacements (old=new, comma separated, optional):" + Colors.ENDC)
    repl_raw = input("🔹 Replacements: ").strip()
    replacements = {}
    if repl_raw:
        for item in repl_raw.split(','):
            if '=' in item:
                old, new = item.split('=', 1)
                if old.strip():
                    replacements[old.strip()] = new.strip()

    # interval
    print(Colors.GREEN + "\n⏰ Check interval seconds (e.g., 3600 for 1 hour):" + Colors.ENDC)
    try:
        interval = int(input("🔹 Interval seconds: ").strip())
        if interval <= 0:
            raise ValueError
    except Exception:
        print(Colors.RED + "❌ Invalid input, using default 3600 seconds." + Colors.ENDC)
        interval = 3600

    cfg = {
        "api_id": api_id,
        "api_hash": api_hash,
        "source_channels": sources,
        "target_channels": targets,
        "replacements": replacements,
        "check_interval": interval
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return cfg

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return ask_user_config()

# -------------------- فایل last_seen -----------------
def load_last_seen():
    if os.path.exists(LAST_SEEN_FILE):
        try:
            with open(LAST_SEEN_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_last_seen(d):
    with open(LAST_SEEN_FILE, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# -------------------- لاگ -----------------
def log_line(text):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} | {text}\n")

# -------------------- پاکسازی متن -----------------
def clean_and_tag_text(text, dest, replacements):
    # جایگزینی‌های دلخواه
    for old, new in (replacements or {}).items():
        if old:
            text = text.replace(old, new)

    # حذف تمام لینک‌ها
    text = re.sub(r'https?://\S+', '', text, flags=re.IGNORECASE)

    # افزودن @کانال مقصد اگر موجود نبود
    tag = f"@{dest.strip('@')}"
    if tag not in text:
        if text.strip():
            text = text.rstrip() + f"\n\n{tag}"
        else:
            text = tag
    return text

# -------------------- ترمینکس بوت -----------------
def setup_autorun():
    boot_dir = os.path.expanduser("~/.termux/boot")
    if not os.path.exists(boot_dir):
        os.makedirs(boot_dir)
    start_script = os.path.join(boot_dir, "start_auto_post.sh")
    if not os.path.exists(start_script):
        with open(start_script, "w") as f:
            f.write(f"""#!/data/data/com.termux/files/usr/bin/bash
cd {BASE_DIR}
python3 {os.path.basename(__file__)}
""")
        os.chmod(start_script, 0o755)
        print(Colors.GREEN + "✅ Auto-boot setup completed (Termux:Boot)." + Colors.ENDC)

# -------------------- کنترل pause/resume -----------------
pause_flag = False
def listen_for_pause():
    global pause_flag
    while True:
        try:
            cmd = input()
        except Exception:
            # وقتی از Boot اجرا می‌شود، ورودی ندارد؛ خطا نده
            time.sleep(5)
            continue
        c = cmd.strip().lower()
        if c == "pause":
            pause_flag = True
            print(Colors.YELLOW + "⏸️ Paused. Type 'resume' to continue." + Colors.ENDC)
        elif c == "resume":
            pause_flag = False
            print(Colors.GREEN + "▶️ Resumed." + Colors.ENDC)

# -------------------- منطق اصلی -----------------
async def bootstrap_channel(client, channel, last_seen):
    """
    اگر کانال قبلاً last_id ندارد، آخرین پیام فعلی را به عنوان نقطه شروع ثبت می‌کنیم
    تا پست‌های قدیمی ارسال نشوند.
    """
    if channel in last_seen:
        return
    msg = await client.get_messages(channel, limit=1)
    if msg and msg[0]:
        last_seen[channel] = msg[0].id
        save_last_seen(last_seen)
        print(Colors.YELLOW + f"🟡 Bootstrap {channel}: set last_id={msg[0].id} (no backfill)." + Colors.ENDC)
        log_line(f"BOOTSTRAP {channel} last_id={msg[0].id}")
    else:
        # کانال خالی
        last_seen[channel] = 0
        save_last_seen(last_seen)
        print(Colors.YELLOW + f"🟡 Bootstrap {channel}: channel empty (last_id=0)." + Colors.ENDC)
        log_line(f"BOOTSTRAP {channel} last_id=0")

async def process_channel(client, source, targets, replacements, last_seen):
    """
    فقط پیام‌هایی که id آنها > last_seen[source] باشد را جمع کرده و
    به ترتیب قدیمی→جدید ارسال می‌کنیم، سپس last_id را به آخرین ارسال‌شده به‌روزرسانی می‌کنیم.
    """
    min_id = int(last_seen.get(source, 0))
    # فقط پیام‌های جدیدتر را می‌خوانیم
    new_msgs = []
    async for m in client.iter_messages(source, min_id=min_id):
        if m and m.id and m.id > min_id:
            new_msgs.append(m)

    if not new_msgs:
        print(Colors.BLUE + f"ℹ️ {source}: no new posts." + Colors.ENDC)
        return

    # قدیمی → جدید
    new_msgs.sort(key=lambda x: x.id)

    sent_any = False
    latest_id = min_id

    for m in new_msgs:
        try:
            text = (m.text or "")  # متن یا کپشن
            for dest in targets:
                final_text = clean_and_tag_text(text, dest, replacements)
                if m.media:
                    path = await m.download_media()
                    try:
                        await client.send_file(dest, path, caption=final_text)
                    finally:
                        try:
                            if path and os.path.exists(path):
                                os.remove(path)
                        except Exception:
                            pass
                else:
                    await client.send_message(dest, final_text)

            latest_id = m.id
            sent_any = True
            print(Colors.GREEN + f"✅ Sent post {m.id} -> {targets}" + Colors.ENDC)
            log_line(f"SENT {source} id={m.id} -> {targets}")
        except Exception as e:
            print(Colors.RED + f"❌ Failed {source} id={m.id}: {e}" + Colors.ENDC)
            log_line(f"ERROR {source} id={m.id}: {e}")

    if sent_any and latest_id > min_id:
        last_seen[source] = latest_id
        save_last_seen(last_seen)
        print(Colors.YELLOW + f"📌 Updated last_id for {source} -> {latest_id}" + Colors.ENDC)

async def forward_loop(client, cfg):
    sources  = cfg["source_channels"]
    targets  = cfg["target_channels"]
    repl     = cfg.get("replacements", {})
    interval = int(cfg.get("check_interval", 3600))

    # Bootstrap برای هر کانال
    last_seen = load_last_seen()
    for s in sources:
        await bootstrap_channel(client, s, last_seen)

    # نخِ کنترل pause/resume
    threading.Thread(target=listen_for_pause, daemon=True).start()

    while True:
        if pause_flag:
            await asyncio.sleep(1)
            continue

        print(Colors.HEADER + "\n🚀 Forwarding Posts..." + Colors.ENDC)
        for s in sources:
            print(Colors.BLUE + f"📡 Checking {s} ..." + Colors.ENDC)
            await process_channel(client, s, targets, repl, last_seen)

        # نمایش زمان دور بعدی
        next_ts = datetime.now().timestamp() + interval
        human = datetime.fromtimestamp(next_ts).strftime("%H:%M:%S")
        print(Colors.BLUE + f"⏰ Next check in {interval} sec (≈ at {human})" + Colors.ENDC)
        await asyncio.sleep(interval)

# -------------------- اجرای برنامه -----------------
async def main():
    banner()
    setup_autorun()
    cfg = load_config()

    # اتصال به تلگرام
    client = TelegramClient(os.path.join(BASE_DIR, 'auto_post_ultra_session'), cfg["api_id"], cfg["api_hash"])
    await client.start()
    print(Colors.GREEN + "✅ Telegram client started." + Colors.ENDC)

    try:
        await forward_loop(client, cfg)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Colors.YELLOW + "\n🛑 Exiting by user." + Colors.ENDC)
