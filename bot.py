import time
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from config import BOT_TOKEN, BOT_NAME, ADSTERRA_LINK

# --- قاعدة البيانات ---
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# إنشاء جدول المستخدمين إذا لم يكن موجودًا
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    jumps INTEGER DEFAULT 0
)
''')
conn.commit()

# --- دوال البوت ---
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    c.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))
    conn.commit()
    update.message.reply_text(
        f"أهلاً بك في {BOT_NAME}!\n"
        f"اضغط الأزرار للتحكم بالقفزات والاستثمار.",
        reply_markup=main_menu()
    )

def main_menu():
    keyboard = [
        [InlineKeyboardButton("مشاهدة الإعلان/مهام", callback_data='watch')],
        [InlineKeyboardButton("استثمار", callback_data='invest')],
        [InlineKeyboardButton("استلام الأرباح", callback_data='collect')],
        [InlineKeyboardButton("رصيدي الحالي", callback_data='balance')]
    ]
    return InlineKeyboardMarkup(keyboard)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    c.execute("SELECT balance, jumps FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    balance, jumps = result if result else (0,0)

    if query.data == 'watch':
        # إضافة رصيد من مشاهدة الإعلان/مهام
        earned = 0.5  # مثال: كل مهمة 0.5$
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (earned, user_id))
        conn.commit()
        query.answer(f"لقد ربحت ${earned} من المشاهدة!")
        query.edit_message_text("تمت إضافة الأرباح!", reply_markup=main_menu())

    elif query.data == 'invest':
        # قائمة استثمارية
        invest_buttons = [
            [InlineKeyboardButton("1$ → 400 قفزة", callback_data='invest_1')],
            [InlineKeyboardButton("2$ → 600 قفزة", callback_data='invest_2')],
            [InlineKeyboardButton("3$ → 1200 قفزة", callback_data='invest_3')],
            [InlineKeyboardButton("10$ → 10000 قفزة", callback_data='invest_10')],
            [InlineKeyboardButton("عودة", callback_data='back')]
        ]
        query.edit_message_text("اختر المبلغ للاستثمار:", reply_markup=InlineKeyboardMarkup(invest_buttons))

    elif query.data.startswith('invest_'):
        amount_map = {'invest_1': (1,400),'invest_2': (2,600),'invest_3': (3,1200),'invest_10': (10,10000)}
        amount, jumps_added = amount_map[query.data]
        if balance >= amount:
            balance -= amount
            jumps += jumps_added
            c.execute("UPDATE users SET balance=?, jumps=? WHERE user_id=?", (balance, jumps, user_id))
            conn.commit()
            query.answer(f"تم الاستثمار! حصلت على {jumps_added} قفزة.")
            query.edit_message_text("تم الاستثمار بنجاح!", reply_markup=main_menu())
        else:
            query.answer("رصيدك غير كافٍ للاستثمار.", show_alert=True)

    elif query.data == 'collect':
        collected = jumps * 0.025  # قيمة كل قفزة بالدولار
        c.execute("UPDATE users SET balance = balance + ?, jumps = 0 WHERE user_id=?", (collected, user_id))
        conn.commit()
        query.answer(f"تم تحويل {collected}$ إلى رصيدك!")
        query.edit_message_text("تم استلام الأرباح!", reply_markup=main_menu())

    elif query.data == 'balance':
        query.edit_message_text(f"رصيدك الحالي: ${balance}\nعدد القفزات: {jumps}", reply_markup=main_menu())

    elif query.data == 'back':
        query.edit_message_text("العودة إلى القائمة الرئيسية", reply_markup=main_menu())

# --- تشغيل البوت ---
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button_handler))

print(f"{BOT_NAME} بدأ العمل!")
updater.start_polling()
updater.idle()
