import json
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включим логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== ТВОИ ДАННЫЕ ======
TOKEN = '8583869049:AAFHSW-sA26F03O_8uHUktatSqA_5FjYGhA'
ADMIN_CHAT_ID = 123456789  # ← ЗАМЕНИ НА СВОЙ ID
WEB_APP_URL = "https://cafe-menu-gzgz.onrender.com"  # твой адрес меню
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение с кнопкой для открытия мини-приложения."""
    button = KeyboardButton(
        text="🍕 Открыть меню и заказать",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в наше кафе! 👋\n"
        "Нажми кнопку ниже, чтобы увидеть меню и сделать заказ.",
        reply_markup=reply_markup
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает данные из мини-приложения (заказ)."""
    data = update.effective_message.web_app_data.data
    
    if not data:
        return

    try:
        order = json.loads(data)
        
        items_list = ""
        for item in order['items']:
            items_list += f"  • {item['name']} x{item['quantity']} = {item['price'] * item['quantity']}₽\n"
        
        # Получаем комментарий и время
        comment = order.get('comment', '')
        ready_time = order.get('readyTime', 'Не указано')
        
        comment_text = f"\n💬 Комментарий: {comment}" if comment else ""
        
        message_to_admin = (
            f"🆕 <b>НОВЫЙ ЗАКАЗ!</b>\n\n"
            f"<b>Состав заказа:</b>\n{items_list}\n"
            f"<b>Итого:</b> {order['total']}₽\n"
            f"⏰ <b>Время готовности:</b> {ready_time}\n"
            f"{comment_text}\n\n"
            f"<b>Клиент:</b> {update.effective_user.full_name}\n"
            f"<b>Username:</b> @{update.effective_user.username}\n"
            f"<b>ID:</b> {update.effective_user.id}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin, parse_mode='HTML')
        await update.message.reply_text("✅ Спасибо! Ваш заказ принят. Мы скоро свяжемся с вами для уточнения деталей.")

    except json.JSONDecodeError:
        logger.error(f"Ошибка парсинга JSON: {data}")
        await update.message.reply_text("Произошла ошибка при обработке заказа. Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Что-то пошло не так. Мы уже чиним!")

def main():
    """Запуск бота."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    port = int(os.environ.get('PORT', 8080))
    print(f"✅ Бот запущен на порту {port}")
    print(f"📱 Адрес приложения: {WEB_APP_URL}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
