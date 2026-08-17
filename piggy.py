from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8663495346:AAGwSiaJJfzWVt-0L0711qknF7nsjbYyES0"

def category_keyboard():

    keyboard = [
        [InlineKeyboardButton("🍚 Makan", callback_data="Makan")],
        [InlineKeyboardButton("🏠 Kebutuhan sehari-hari", callback_data="Kebutuhan")],
        [InlineKeyboardButton("🎓 Kuliah", callback_data="Kuliah")],
        [InlineKeyboardButton("🚗 Transportasi", callback_data="Transportasi")],
        [InlineKeyboardButton("🎮 Hiburan", callback_data="Hiburan")],
    ]

    return InlineKeyboardMarkup(keyboard)
# =========================
# 1. /expense
# =========================

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_markup=category_keyboard()

    await update.message.reply_text(
        "💰 Pilih kategori pengeluaran:",
        reply_markup=reply_markup
    )


# =========================
# 2. Ketika tombol diklik
# =========================

async def category_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    category = query.data

    context.user_data["category"] = category

    await query.edit_message_text(
        f"Kategori: {category}\n\n"
        "💰 Nominal pengeluaran:\n"
    )

# 3. Menerima nominal

async def receive_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message.text.strip()

    message = message.replace("k" or "K", "000")

    try:
        amount = int(message)

    except ValueError:

        await update.message.reply_text(
            "❌ Format salah.\n\n"
            "Coba kek:\n"
            "15000 / 15k / 15K"
        )

        return

    category = context.user_data.get("category")

    if category is None:

        await update.message.reply_text(
            "Gunakan /expense terlebih dahulu."
        )

        return

    await update.message.reply_text(
        f"✅ Pengeluaran tercatat!\n\n"
        f"Kategori: {category}\n"
        f"💰 Rp{amount:,}"
    )

    # Nanya lagi
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Ada",
                callback_data="Ada"
            ),
            InlineKeyboardButton(
                "❌ Ga",
                callback_data="Ga"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)    

    await update.message.reply_text(
        "Ada pengeluaran lagi?",
        reply_markup=reply_markup
    )

# ============ Nanya ==================
async def continue_expense(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    choice = query.data

    if choice == "Ada":

        await query.edit_message_text(
            "💰 Pilih kategori pengeluaran:",
            reply_markup=category_keyboard()
        )

        return
    
    if choice == "no":

        # Hapus data sementara
        context.user_data.clear()

        await query.edit_message_text(
            "✅ Selesai!\n\n"
            "Semua pengeluaran sudah dicatat."
        )

        return



# ============ MAIN ==================

app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler("expense", expense)
)

# Tombol Kategory
app.add_handler(
    CallbackQueryHandler(
        category_selected,
        pattern="^(Makan|Kebutuhan|Kuliah|Transportasi|Hiburan)$")
)

# Tombol Ya / Tidak
app.add_handler(
    CallbackQueryHandler(
        continue_expense,
        pattern="^(Ada|Ga)$"
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_amount
    )
)


print("Bot sedang berjalan...")

app.run_polling()