import json, re, time, threading, requests, dns.resolver
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ================== AYAR ==================
BOT_TOKEN = "8495054462:AAFyt_rOuUZz03korJk5CARdxvZCAtQT5HI"  # Buraya kendi bot tokenini yaz
CHECK_INTERVAL = 900  # 15 dk
TURK_DNS = ["195.175.39.39", "195.175.39.40"]
BTK_KEYWORDS = ["5651", "erişim engellenmiştir", "btk"]
# ==========================================

def load_data():
    return json.load(open("data.json", encoding="utf-8"))

def save_data(data):
    json.dump(data, open("data.json","w",encoding="utf-8"), indent=2, ensure_ascii=False)

def next_domain(d):
    m = re.search(r"(.*?)(\d+)(\.[a-z]+)$", d)
    return f"{m.group(1)}{int(m.group(2))+1}{m.group(3)}" if m else d

def turk_dns(d):
    try:
        r = dns.resolver.Resolver()
        r.nameservers = TURK_DNS
        r.resolve(d)
        return True
    except:
        return False

def blocked(d):
    dns_ok = turk_dns(d)
    try:
        r = requests.get(f"http://{d}", timeout=8, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        return any(k in r.text.lower() for k in BTK_KEYWORDS) or not dns_ok
    except:
        return not dns_ok

# ================== OTOMATİK KONTROL ==================
def auto_check():
    bot = Bot(BOT_TOKEN)
    while True:
        data = load_data()
        for s in data["sites"]:
            if blocked(s["domain"]):
                old = s["domain"]
                s["domain"] = next_domain(old)
                bot.send_message(s["chat_id"], f"🚫 BTK ENGELİ\n{old} → {s['domain']}")
        save_data(data)
        time.sleep(CHECK_INTERVAL)

# ================== /durum KOMUTU ==================
def durum(update: Update, context: CallbackContext):
    data = load_data()
    msg = "📊 ANLIK DURUM\n\n"
    for s in data["sites"]:
        msg += f"{s['name']}\n{s['domain']} → {'🔴 ENGELLİ' if blocked(s['domain']) else '🟢 AÇIK'}\n\n"
    update.message.reply_text(msg)

# ================== MAIN ==================
def main():
    up = Updater(BOT_TOKEN, use_context=True)
    up.dispatcher.add_handler(CommandHandler("durum", durum))
    threading.Thread(target=auto_check, daemon=True).start()
    up.start_polling()
    up.idle()

main()
