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
IDLE = "IDLE"

INCOME_TYPE = "INCOME_TYPE"
INCOME_AMOUNT = "INCOME_AMOUNT"

EXPENSE_CATEGORY = "EXPENSE_CATEGORY"
EXPENSE_AMOUNT = "EXPENSE_AMOUNT"

ASK_MORE = "ASK_MORE"

def category_keyboard():

    keyboard = [
        [InlineKeyboardButton("🍚 Makan", callback_data="Makan")],
        [InlineKeyboardButton("🏠 Kebutuhan sehari-hari", callback_data="Kebutuhan")],
        [InlineKeyboardButton("🎓 Kuliah", callback_data="Kuliah")],
        [InlineKeyboardButton("🚗 Transportasi", callback_data="Transportasi")],
        [InlineKeyboardButton("🎮 Hiburan", callback_data="Hiburan")],
    ]

    return InlineKeyboardMarkup(keyboard)
# =========== /pemasukan ========

async def income(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["state"] = INCOME_TYPE
    keyboard = [
        [
            InlineKeyboardButton(
                "💵 Pemasukan tetap",
                callback_data="income_fixed"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ Pemasukan tambahan",
                callback_data="income_additional"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💰 Pilih jenis pemasukan:",
        reply_markup=reply_markup
    )

# ========== /expense ========

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["state"] = EXPENSE_CATEGORY
    reply_markup=category_keyboard()

    await update.message.reply_text(
        "💰 Pilih kategori pengeluaran:",
        reply_markup=reply_markup
    )

# select pemasukan

async def income_type_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    income_type = query.data

    context.user_data["income_type"] = income_type
    context.user_data["state"] = INCOME_AMOUNT

    if income_type == "income_fixed":

        await query.edit_message_text(
            "💵 Pemasukan tetap\n\n"
            "Masukkan nominal pemasukan:\n"
        )

    elif income_type == "income_additional":

        await query.edit_message_text(
            "➕ Pemasukan tambahan\n\n"
            "Masukkan nominal pemasukan:\n"
        )

# select pengeluaran

async def category_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    category = query.data

    context.user_data["category"] = category
    context.user_data["state"] = EXPENSE_AMOUNT

    await query.edit_message_text(
        f"Kategori: {category}\n\n"
        "💰 Nominal pengeluaran:\n"
    )
# ========= Nominal Pemasukan =======
async def receive_income(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message.text.strip()
    message = message.replace("k", "000")
    message = message.replace("jt", "000000")
    try:
        amount = int(message)

    except ValueError:

        await update.message.reply_text(
            "❌ Nominal harus berupa angka.\n\n"
        )

        return

    income_type = context.user_data.get("income_type")

    if income_type is None:

        return

    if income_type == "income_fixed":

        await update.message.reply_text(
            f"✅ Pemasukan tetap dicatat!\n\n"
            f"💰 Rp{amount:,}\n\n"
            "Untuk sementara kita belum membuat siklusnya."
        )

    elif income_type == "income_additional":

        await update.message.reply_text(
            f"✅ Pemasukan tambahan dicatat!\n\n"
            f"💰 Rp{amount:,}\n\n"
            "Untuk sementara kita belum menyimpan ke saldo."
        )

    context.user_data.pop("income_type", None)


#  ======= Menerima nominal =======
async def receive_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message.text.strip()

    message = message.replace("k", "000")
    message = message.replace("jt", "000000")

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
    
    if choice == "Ga":

        # Hapus data sementara
        context.user_data.clear()

        await query.edit_message_text(
            "✅ Selesai!\n\n"
            "Semua pengeluaran sudah dicatat."
        )

        return


# ======= Handler Message =========
async def next_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    choice = query.data

    if choice == "next_income":

        context.user_data["state"] = INCOME_TYPE

        keyboard = [
            [
                InlineKeyboardButton(
                    "💵 Pemasukan tetap",
                    callback_data="income_fixed"
                )
            ],
            [
                InlineKeyboardButton(
                    "➕ Pemasukan tambahan",
                    callback_data="income_additional"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "💰 Pilih jenis pemasukan:",
            reply_markup=reply_markup
        )

    elif choice == "next_expense":

        context.user_data["state"] = EXPENSE_CATEGORY

        await query.edit_message_text(
            "💸 Pilih kategori pengeluaran:",
            reply_markup=category_keyboard()
        )

async def continue_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    choice = query.data

    if choice == "continue_yes":

        keyboard = [
            [
                InlineKeyboardButton(
                    "💰 Pemasukan",
                    callback_data="next_income"
                )
            ],
            [
                InlineKeyboardButton(
                    "💸 Pengeluaran",
                    callback_data="next_expense"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "💰 Pilih jenis transaksi:",
            reply_markup=reply_markup
        )

    elif choice == "continue_no":

        context.user_data["state"] = IDLE

        await query.edit_message_text(
            "✅ Sesi pencatatan selesai."
        )

async def ask_continue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["state"] = ASK_MORE

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Ya",
                callback_data="continue_yes"
            ),
            InlineKeyboardButton(
                "❌ Tidak",
                callback_data="continue_no"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Ada transaksi lagi?",
        reply_markup=reply_markup
    )

async def receive_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message.text.strip()

    state = context.user_data.get("state")


    if state == INCOME_AMOUNT:

        await update.message.reply_text(
            f"✅ Pemasukan tercatat!\n\n"
            f"💰 Rp{message}"
        )

        await ask_continue(update, context)


    elif state == EXPENSE_AMOUNT:

        await update.message.reply_text(
            f"✅ Pengeluaran tercatat!\n\n"
            f"💰 Rp{message}"
        )

        await ask_continue(update, context)


    else:

        await update.message.reply_text(
            "Gunakan /in atau /out terlebih dahulu."
        )
# ============ MAIN ==================

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CallbackQueryHandler(
        continue_transaction,
        pattern="^(continue_yes|continue_no)$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        next_transaction,
        pattern="^(next_income|next_expense)$"
    )
)


app.add_handler(
    CommandHandler("in", income)
)

app.add_handler(
    CommandHandler("out", expense)
)

# Tombol Kategory
app.add_handler(
    CallbackQueryHandler(
        income_type_selected,
        pattern="^(income_fixed|income_additional)$"
    )
)

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
        receive_message
    )
)


print("Bot sedang berjalan...")

app.run_polling()