import telebot
from telebot import types
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7300105507
CHANNEL_USERNAME = "hgnicedkwinofficialchannel"
PROOF_CHANNEL = "paymentbotproof"
DATA_FILE = "data.json"
REF_AMOUNT = 100
MIN_WITHDRAW = 2000

bot = telebot.TeleBot(TOKEN)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_member(user_id, channel):
    try:
        member = bot.get_chat_member(f"@{channel}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False


def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("👤 প্রোফাইল"),
               types.KeyboardButton("💰 ব্যালেন্স"),
               types.KeyboardButton("🔗 রেফার লিংক"),
               types.KeyboardButton("📤 উইথড্র"),
               types.KeyboardButton("🆘 সাহায্য"))
    return markup


def join_channel_message(chat_id):
    join_markup = types.InlineKeyboardMarkup()
    join_markup.add(
        types.InlineKeyboardButton("✅ চ্যানেল জয়েন করুন",
                                   url=f"https://t.me/{CHANNEL_USERNAME}"))
    join_markup.add(
        types.InlineKeyboardButton("♻️ আবার চেক করুন",
                                   callback_data="check_join"))
    bot.send_message(chat_id, "❗️ প্রথমে আমাদের চ্যানেলে জয়েন করুন।\n\n"
                     "এই বট দিয়ে আপনি রেফার করে ফ্রিতে ইনকাম করতে পারবেন।\n"
                     f"প্রতি রেফারে পাবেন *{REF_AMOUNT} টাকা*!",
                     reply_markup=join_markup,
                     parse_mode='Markdown')


def join_proof_channel_message(chat_id):
    join_markup = types.InlineKeyboardMarkup()
    join_markup.add(
        types.InlineKeyboardButton("✅ পেমেন্ট প্রুফ চ্যানেল জয়েন করুন",
                                   url=f"https://t.me/{PROOF_CHANNEL}"))
    join_markup.add(
        types.InlineKeyboardButton("♻️ আবার চেক করুন",
                                   callback_data="check_proof_join"))
    bot.send_message(chat_id, "❗️ পেমেন্ট প্রুফ চ্যানেল জয়েন করা আবশ্যক!\n\n"
                     "👇 নিচের বাটন থেকে জয়েন করুন।",
                     reply_markup=join_markup)


admin_states = {}  # admin user_id -> state


@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = str(message.from_user.id)
    data = load_data()

    # মেইন চ্যানেল জয়েন চেক
    if not is_member(message.from_user.id, CHANNEL_USERNAME):
        join_channel_message(message.chat.id)
        return

    # পেমেন্ট প্রুফ চ্যানেল জয়েন চেক
    if not is_member(message.from_user.id, PROOF_CHANNEL):
        join_proof_channel_message(message.chat.id)
        return

    args = message.text.split()
    ref = None
    if len(args) > 1:
        ref = args[1]

    if user_id not in data:
        data[user_id] = {
            "balance": 0,
            "ref_by": None,
            "name": message.from_user.first_name,
            "ref_count": 0
        }
        # রেফার যোগ করুন যদি মান্য হয়
        if ref and ref != user_id and ref in data:
            data[ref]["balance"] += REF_AMOUNT
            data[ref]["ref_count"] += 1
            data[user_id]["ref_by"] = ref
            # Notify referrer about new referral
            try:
                bot.send_message(
                    int(ref),
                    f"🎉 নতুন রেফারেল! আপনার ব্যালেন্সে +{REF_AMOUNT} টাকা যুক্ত হয়েছে।"
                )
            except:
                pass
        save_data(data)

    first_name = message.from_user.first_name
    bot_username = bot.get_me().username

    text = (
        f"👋 *স্বাগতম* `{first_name}`!\n\n"
        f"💸 আপনার বর্তমান ব্যালেন্স: *{data[user_id]['balance']} টাকা*\n\n"
        f"🔗 আপনার রেফার লিংক:`https://t.me/{bot_username}?start={user_id}`\n\n"
        f"📢 প্রতি রেফারে পাবেন *{REF_AMOUNT} টাকা*।\n\n"
        f"✅ আপনার মোট রেফার: *{data[user_id]['ref_count']}*\n\n"
        f"🛠️ নিচের মেনু থেকে পছন্দসই অপশন নির্বাচন করুন।")
    bot.send_message(message.chat.id,
                     text,
                     reply_markup=main_menu(),
                     parse_mode='Markdown')


@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join_callback(call):
    if is_member(call.from_user.id, CHANNEL_USERNAME):
        bot.answer_callback_query(call.id, "✅ চ্যানেল জয়েন নিশ্চিত হয়েছে!")
        start_handler(call.message)
    else:
        bot.answer_callback_query(call.id,
                                  "❌ আপনি এখনো চ্যানেলে জয়েন করেননি!",
                                  show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data == "check_proof_join")
def check_proof_join_callback(call):
    if is_member(call.from_user.id, PROOF_CHANNEL):
        bot.answer_callback_query(call.id,
                                  "✅ পেমেন্ট প্রুফ চ্যানেল জয়েন নিশ্চিত!")
        start_handler(call.message)
    else:
        bot.answer_callback_query(
            call.id,
            "❌ আপনি এখনো পেমেন্ট প্রুফ চ্যানেলে জয়েন করেননি!",
            show_alert=True)


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    user_id = str(message.from_user.id)
    data = load_data()

    # Check channel joins again on every button press
    if not is_member(message.from_user.id, CHANNEL_USERNAME):
        join_channel_message(message.chat.id)
        return

    if not is_member(message.from_user.id, PROOF_CHANNEL):
        join_proof_channel_message(message.chat.id)
        return

    if user_id not in data:
        bot.send_message(message.chat.id, "❌ দয়া করে /start দিয়ে শুরু করুন।")
        return

    # Admin panel: handle admin states
    if message.from_user.id == ADMIN_ID:
        state = admin_states.get(user_id)
        if state == "broadcast":
            if message.text == "/cancel":
                admin_states[user_id] = None
                bot.send_message(message.chat.id,
                                 "❌ ব্রডকাস্ট বাতিল করা হয়েছে।")
            else:
                # Broadcast message to all users
                for uid in data.keys():
                    try:
                        bot.send_message(
                            int(uid),
                            f"📢 *ব্রডকাস্ট মেসেজ*\n\n{message.text}",
                            parse_mode="Markdown")
                    except:
                        pass
                admin_states[user_id] = None
                bot.send_message(message.chat.id,
                                 "✅ ব্রডকাস্ট মেসেজ পাঠানো হয়েছে।")
            return

        if message.text == "/broadcast":
            admin_states[user_id] = "broadcast"
            bot.send_message(
                message.chat.id,
                "📢 ব্রডকাস্ট মেসেজ লিখুন। বাতিল করতে /cancel লিখুন।")
            return

    text = message.text

    if text == "👤 প্রোফাইল":
        user = data[user_id]
        txt = (
            f"👤 *আপনার প্রোফাইল তথ্য*\n\n"
            f"📇 নাম: `{user.get('name', 'NA')}`\n\n"
            f"💰 ব্যালেন্স: *{user.get('balance', 0)} টাকা*\n\n"
            f"🔗 মোট রেফার: *{user.get('ref_count', 0)}*\n\n"
            f"🎁 রেফার লিংক:`https://t.me/{bot.get_me().username}?start={user_id}`"
        )
        bot.send_message(message.chat.id, txt, parse_mode='Markdown')

    elif text == "💰 ব্যালেন্স":
        bal = data[user_id].get("balance", 0)
        bot.send_message(message.chat.id,
                         f"💰 আপনার ব্যালেন্স: *{bal} টাকা*",
                         parse_mode='Markdown')

    elif text == "🔗 রেফার লিংক":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_message(message.chat.id,
                         f"🎁 আপনার রেফার লিংক:`{ref_link}`",
                         parse_mode='Markdown')

    elif text == "📤 উইথড্র":
        bal = data[user_id].get("balance", 0)
        if bal < MIN_WITHDRAW:
            bot.send_message(
                message.chat.id,
                f"❌ উইথড্র করার জন্য ন্যূনতম ব্যালেন্স *{MIN_WITHDRAW} টাকা*।\nআপনার ব্যালেন্স: *{bal} টাকা*",
                parse_mode='Markdown')
            return
        msg = bot.send_message(message.chat.id,
                               "📲 আপনার bKash অথবা Nagad নাম্বার দিন:")
        bot.register_next_step_handler(msg, process_withdraw)

    elif text == "🆘 সাহায্য":
        bot.send_message(message.chat.id,
                         "📞 সাহায্যের জন্য যোগাযোগ করুন: @falco1013")

    else:
        bot.send_message(message.chat.id,
                         "❓ বুঝতে পারিনি, নিচের মেনু থেকে নির্বাচন করুন।",
                         reply_markup=main_menu())


def process_withdraw(message):
    number = message.text.strip()
    user_id = str(message.from_user.id)
    data = load_data()
    amount = data[user_id].get("balance", 0)

    if amount < MIN_WITHDRAW:
        bot.send_message(
            message.chat.id,
            f"❌ আপনার ব্যালেন্স কম। ন্যূনতম {MIN_WITHDRAW} টাকা প্রয়োজন।")
        return

    data[user_id]["balance"] = 0
    save_data(data)

    bot.send_message(
        message.chat.id, f"✅ আপনার উইথড্র অনুরোধ গ্রহণ করা হয়েছে!\n\n"
        f"💸 পরিমাণ: {amount} টাকা\n"
        f"📱 নাম্বার: {number}\n\n"
        f"শীঘ্রই আপনার উইথড্র প্রক্রিয়া করা হবে। ধন্যবাদ!")

    bot.send_message(
        ADMIN_ID, f"🆕 নতুন উইথড্র অনুরোধ:\n"
        f"👤 ব্যবহারকারী: {message.from_user.first_name}\n"
        f"🆔 আইডি: {user_id}\n"
        f"💰 পরিমাণ: {amount} টাকা\n"
        f"📱 নাম্বার: {number}")


bot.infinity_polling()
