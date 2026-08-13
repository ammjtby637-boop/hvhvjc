import os
import sys
import requests
import redis
from pyrogram import Client, idle

# ============================================================
# Railway configuration
# Add these variables in Railway:
# BOT_TOKEN = your Telegram bot token
# OWNER_ID  = your Telegram user ID
# REDIS_URL = Railway Redis connection URL
# ============================================================

token = os.getenv("BOT_TOKEN", "").strip()
owner_raw = os.getenv("OWNER_ID", "").strip()

if not token:
    print("[-] BOT_TOKEN is missing. Add BOT_TOKEN in Railway Variables.")
    sys.exit(1)

if not owner_raw:
    print("[-] OWNER_ID is missing. Add OWNER_ID in Railway Variables.")
    sys.exit(1)

try:
    owner_id = int(owner_raw)
except ValueError:
    print("[-] OWNER_ID must be a number.")
    sys.exit(1)

Dev_Neptune = token.split(":", 1)[0]

# ------------------------------------------------------------
# Redis: Railway normally provides REDIS_URL.
# Also supports REDIS_PUBLIC_URL if REDIS_URL is not available.
# ------------------------------------------------------------
redis_url = (
    os.getenv("REDIS_URL", "").strip()
    or os.getenv("REDIS_PUBLIC_URL", "").strip()
)

try:
    if redis_url:
        r = redis.from_url(redis_url, decode_responses=True)
    else:
        # Optional manual Redis variables
        redis_host = os.getenv("REDISHOST", "127.0.0.1")
        redis_port = int(os.getenv("REDISPORT", "6379"))
        redis_password = os.getenv("REDISPASSWORD", "")
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password or None,
            decode_responses=True,
        )

    r.ping()
    print("[+] Redis connected.")
except Exception as e:
    print(f"[-] Redis connection failed: {e}")
    print("[-] Make sure a Redis service is added to Railway and REDIS_URL is available.")
    sys.exit(1)

print("""
Loading…
█▒▒▒▒▒▒▒▒▒
""")

# ------------------------------------------------------------
# Keep the generated config.py compatible with the existing
# Plugins without requiring any changes to all plugin files.
# ------------------------------------------------------------
try:
    username_response = requests.get(
        f"https://api.telegram.org/bot{token}/getMe",
        timeout=15
    ).json()

    username = username_response.get("result", {}).get("username", "unknown")
except Exception:
    username = "unknown"

to_config = f"""import redis
import os

redis_url = os.getenv("REDIS_URL", "").strip() or os.getenv("REDIS_PUBLIC_URL", "").strip()

if redis_url:
    r = redis.from_url(redis_url, decode_responses=True)
else:
    r = redis.Redis(
        host=os.getenv("REDISHOST", "127.0.0.1"),
        port=int(os.getenv("REDISPORT", "6379")),
        password=os.getenv("REDISPASSWORD") or None,
        decode_responses=True
    )

token = {token!r}
Dev_Neptune = token.split(':')[0]
sudo_id = {owner_id}
owner_id = {owner_id}
botUsername = {username!r}

from kvsqlite.sync import Client as DB

ytdb = DB('ytdb.sqlite')
sounddb = DB('sounddb.sqlite')
wsdb = DB('wsdb.sqlite')
"""

with open("config.py", "w", encoding="utf-8") as w:
    w.write(to_config)

r.set(f"{Dev_Neptune}botowner", owner_id)

print("""
30%
█████▒▒▒▒▒
""")

# ------------------------------------------------------------
# Start Pyrogram bot
# ------------------------------------------------------------
app = Client(
    f"{Dev_Neptune}Neptune",
    28850159,
    "09a3e7d212b434aec973ad5ea10d8ec6",
    bot_token=token,
    plugins={"root": "Plugins"},
)

if not r.get(f"{Dev_Neptune}:botkey"):
    r.set(f"{Dev_Neptune}:botkey", "⇜")

if not r.get(f"{Dev_Neptune}botname"):
    r.set(f"{Dev_Neptune}botname", "Jack")

print("""
50%
███████▒▒▒
""")

try:
    app.start()
    print("• 𝖲𝖮𝖴𝖱𝖢𝖤 𝖩𝖠𝖢𝖪 𝖨𝖲 𝖴𝖯 𝖠𝖭𝖣 𝖱𝖴𝖭𝖭I𝖭𝖦 ...")
    print("100%")
    print("██████████")
    idle()
finally:
    try:
        app.stop()
    except Exception:
        pass
