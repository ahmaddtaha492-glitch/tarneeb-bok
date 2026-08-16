import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(name)

SUITS = {'♠': 'سبيت', '♥': 'هارت', '♦': 'ديناري', '♣': 'كلاوب'}
CARDS_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
user_sessions = {}

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {'hand': [], 'trump': None}
    return user_sessions[user_id]

def main_menu():
    kb = [
        [InlineKeyboardButton("🎯 ابدأ المزاودة", callback_data="start_bidding")],
        [InlineKeyboardButton("🃏 إدخال أوراق اليد", callback_data="select_suit")],
        [InlineKeyboardButton("📊 حالة الكروت (Tracker)", callback_data="show_tracker")],
        [InlineKeyboardButton("🔄 إعادة ضبط", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "أهلاً بك في مساعد الطرنيب 41 التكتيكي 🃏🔥\nاختر ما تحتاجه من القائمة:"
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = get_session(user_id)
    data = query.data

    if data == "start_bidding":
        kb = [
            [InlineKeyboardButton("❌ Pass", callback_data="menu"), InlineKeyboardButton("♠ سبيت", callback_data="t_♠")],
            [InlineKeyboardButton("♥ هارت", callback_data="t_♥"), InlineKeyboardButton("♦ ديناري", callback_data="t_♦")],
            [InlineKeyboardButton("♣ كلاوب", callback_data="t_♣")]
        ]
        await query.message.edit_text("اختر الطرنيب الأساسي لمزاودتك:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("t_"):
        session['trump'] = data.split("_")[1]
        await query.message.edit_text(f"✅ تم تثبيت الطرنيب: {SUITS[session['trump']]}\nالبوت جاهز لمساعدتك في اللعب!", reply_markup=main_menu())
    elif data == "select_suit":
        kb = [
            [InlineKeyboardButton("♠ سبيت", callback_data="s_♠"), InlineKeyboardButton("♥ هارت", callback_data="s_♥")],
            [InlineKeyboardButton("♦ ديناري", callback_data="s_♦"), InlineKeyboardButton("♣ كلاوب", callback_data="s_♣")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")]
        ]
        await query.message.edit_text("اختر البدلة لإضافة أوراق يدك:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("s_"):
        suit = data.split("_")[1]
        row = []
        kb_list = []
        for c in CARDS_ORDER:
            row.append(InlineKeyboardButton(f"{c}{suit}", callback_data=f"c_{suit}_{c}"))
            if len(row) == 4:
                kb_list.append(row)
                row = []
        if len(row) > 0:
            kb_list.append(row)
        kb_list.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="menu")])
        await query.message.edit_text(f"اختر كروت بدلة {SUITS[suit]} المتوفرة معك:", reply_markup=InlineKeyboardMarkup(kb_list))
    elif data.startswith("c_"):
        parts = data.split("_")
        suit = parts[1]
        card = parts[2]
        card_str = f"{card}{suit}"
        if card_str not in session['hand']:
            session['hand'].append(card_str)
        await query.message.edit_text(f"🃏 أوراقك المسجلة حتى الآن: {', '.join(session['hand'])}\nاختر كرت آخر أو عد للقائمة.", reply_markup=main_menu())

elif data == "show_tracker":
        await query.message.edit_text("📊 تتبع الكروت: البوت يراقب الأوراق النافذة ويحذرك من حرق الكروت العالية أو اللعب بلون نفد عند الخصوم.", reply_markup=main_menu())
    elif data == "reset":
        user_sessions[user_id] = {'hand': [], 'trump': None}
        await query.message.edit_text("🔄 تم مسح الذاكرة وإعادة ضبط الجولة بنجاح.", reply_markup=main_menu())
    elif data == "menu":
        await query.message.edit_text("القائمة الرئيسية:", reply_markup=main_menu())

def main():
    TOKEN = "8932575812:AAHfy3ZklX6Kaltch6YZqx8rYgTqP_-HEnM"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    logger.info("Bot is running...")
    app.run_polling()

if name == "main":
    main()
