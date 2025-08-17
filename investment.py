# investment.py
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_user, update_balance, set_investment, collect_profit

# بيانات الباقات
packages = {
    1: {"jumps": 400, "profit": 10},
    2: {"jumps": 600, "profit": 15},
    3: {"jumps": 1200, "profit": 30},
    10: {"jumps": 10000, "profit": 250}
}

async def invest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1$", "2$"], ["3$", "10$"], ["🔙 رجوع"]]
    await update.message.reply_text("💸 اختر باقة الاستثمار:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_investment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    text = update.message.text.replace("$", "")
    if not text.isdigit():
        return
    amount = int(text)
    if amount not in packages:
        return

    if user[1] < amount:
        await update.message.reply_text("❌ رصيدك غير كافي!")
        return

    # خصم المبلغ
    update_balance(user_id, -amount)
    jumps = packages[amount]["jumps"]
    profit = packages[amount]["profit"]
    set_investment(user_id, jumps, profit)

    # محاكاة القفزات
    for i in range(5):
        await update.message.reply_text("⚫⬆⬇ يقفز...")
        await asyncio.sleep(0.5)

    await update.message.reply_text(
        f"✅ انتهت القفزات!\n💵 أرباحك {profit}$ بانتظار الاستلام.\nاضغط (استلم) لنقلها إلى محفظتك.",
        reply_markup=ReplyKeyboardMarkup([["استلم"], ["🔙 رجوع"]], resize_keyboard=True)
    )

async def collect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profit = collect_profit(user_id)
    await update.message.reply_text(f"✅ تم استلام {profit}$ إلى محفظتك!")
