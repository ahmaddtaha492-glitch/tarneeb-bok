import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)

SUITS = {'♠': 'سبيت', '♥': 'هارت', '♦': 'ديناري', '♣': 'كلاوب'}
CARDS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
user_sessions = {}

def get_session(uid):
    if uid not in user_sessions:
        user_sessions[uid] = {'hand': [], 'trump': None}
    return user_sessions[uid]

def make_menu():
    kb = [
        [InlineKeyboardButton("🎯 ابدأ المزاودة", callback_data="bidding")],
        [InlineKeyboardButton("🃏 إدخال أوراق اليد", callback_data="choose_suit")],
        [InlineKeyboardButton("📊 حالة الكروت (Tracker)", callback_data="tracker")],
        [InlineKeyboardButton("🔄 إعادة ضبط", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "أهلاً بك في مساعد الطرنيب 41 التكتيكي 🃏🔥"
    if update.message:
        await update.message.reply_text(msg, reply_markup=make_menu())
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg, reply_markup=make_menu())

async def handle_bidding(q):
    kb = [
        [InlineKeyboardButton("❌ Pass", callback_data="main_menu"), InlineKeyboardButton("♠ سبيت", callback_data="t_♠")],
        [InlineKeyboardButton("♥ هارت", callback_data="t_♥"), InlineKeyboardButton("♦ ديناري", callback_data="t_♦")],
        [InlineKeyboardButton("♣ كلاوب", callback_data="t_♣")]
    ]
    await q.message.edit_text("اختر الطرنيب لمزاودتك:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_choose_suit(q):
    kb = [
        [InlineKeyboardButton("♠ سبيت", callback_data="s_♠"), InlineKeyboardButton("♥ هارت", callback_data="s_♥")],
        [InlineKeyboardButton("♦ ديناري", callback_data="s_♦"), InlineKeyboardButton("♣ كلاوب", callback_data="s_♣")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    await q.message.edit_text("اختر البدلة:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_card_pick(q, suit):
    kb = []
    row = []
    for c in CARDS:
        row.append(InlineKeyboardButton(f"{c}{suit}", callback_data=f"c_{suit}_{c}"))
        if len(row) == 4:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
    await q.message.edit_text(f"اختر كروت بدلة {SUITS.get(suit, '')}:", reply_markup=InlineKeyboardMarkup(kb))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    session = get_session(uid)
    d = q.data

    if d == "bidding":
        await handle_bidding(q)
        return

    if d == "choose_suit":
        await handle_choose_suit(q)
        return

    if d.startswith("t_"):
        session['trump'] = d.split("_")[1]
        name = SUITS.get(session['trump'], '')
        await q.message.edit_text(f"✅ تم تثبيت الطرنيب: {name}", reply_markup=make_menu())
        return

    if d.startswith("s_"):
        await handle_card_pick(q, d.split("_")[1])
        return

    if d.startswith("c_"):
        parts = d.split("_")
        card = f"{parts[2]}{parts[1]}"
        if card not in session['hand']:
            session['hand'].append(card)
        txt = " ".join(session['hand'])
        await q.message.edit_text(f"🃏 أوراقك: {txt}", reply_markup=make_menu())
        return

    if d == "tracker":
        await q.message.edit_text("📊 تتبع الكروت: البوت يراقب الأوراق النافذة.", reply_markup=make_menu())
        return

    if d == "reset":
        user_sessions[uid] = {'hand': [], 'trump': None}
        await q.message.edit_text("🔄 تم مسح الذاكرة بنجاح.", reply_markup=make_menu())
        return

    if d == "main_menu":
        await q.message.edit_text("القائمة الرئيسية:", reply_markup=make_menu())
        return

def run():
    token = "8932575812:AAHfy3ZklX6Kaltch6YZqx8rYgTqP_-HEnM"
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()

run()
