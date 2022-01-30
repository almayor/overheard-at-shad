import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


RULES = """
Добро пожаловать в группу! Чтобы нам здесь всем было уютно, в группе действуют следующие правила:

1. Пожалуйста, относитесь друг к другу с уважением. Мы не приемлем оскорблений, а также дискриминацию по признаку пола, внешности, национальности, сексуальной ориентации и гендерной идентичности.

2. Мы не публикуем откровенно сексуальный графический контент и спам.

В остальном же у вас есть полная свобода действия! Если ваш пост одобрен модераторами, он будет опубликован в t.me/overheard_at_shad в ближайшее время.
"""


def escape(s):
    """Escape characters forbidden by Telegram API"""
    to_escape = '_*~[]()`>#+-=|{}.!'
    for c in to_escape:
        s = s.replace(c, '\\' + c)
    return s


def start_command(update: Update, context: CallbackContext) -> None:
    """Return a welcome message and rules"""
    logger.info("Someone's initiated a contact")
    update.message.reply_text(text=RULES, parse_mode=ParseMode.HTML)


def receive_post(update: Update, context: CallbackContext) -> None:
    """A new post has been submitted -- ask the user if they want to add tags"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("#содержательное", callback_data='tag-содержательное')],
        [InlineKeyboardButton("без тега", callback_data='tag-none')],
    ])

    logger.info("Received someone's post")
    response = f"<b>Твой пост:</b>\n\n{update.message.text}\n\n<b>Хочешь добавить тег?</b>"
    update.message.reply_text(escape(response), reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def tag_post(update: Update, context: CallbackContext) -> None:
    """A post has been tagged -- ask the user if they are ready for submission"""

    query = update.callback_query
    query.answer()

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить ✅", callback_data='confirm-yes')],
        [InlineKeyboardButton("Отменить ⛔️", callback_data='confirm-no')]
    ])
    post_body = '\n'.join(query.message.text.split('\n')[2:-2])

    if query.data != 'tag-none':
        tag = query.data.split('-')[1]
        post_body += f"\n#{tag}"

    response = f"*Твой пост:*\n\n{post_body}\n\n*Готово?*"
    query.edit_message_text(text=escape(response), reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def confirm_post(update: Update, context: CallbackContext) -> None:
    """A user has confirmed submission of a post -- send it to the moderator's group for approval"""

    query = update.callback_query
    query.answer()

    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("👍", callback_data='approve-yes'),
        InlineKeyboardButton("👎", callback_data='approve-no')
    ]])
    post_body = '\n'.join(query.message.text.split('\n')[2:-2])

    if query.data == 'confirm-no':
        query.delete_message()
    else:
        response = f"🔥 <b>Пост отправлен</b> 🔥\n\n{post_body}\n\n"
        query.edit_message_text(text=escape(response), parse_mode=ParseMode.HTML)

        bot = Bot(token=os.environ['TOKEN'])
        bot.send_message(chat_id=os.environ['MOD_CHAT_ID'], text=escape(post_body), reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def approve_post(update: Update, context: CallbackContext) -> None:
    """A moderator has reviewed a post -- either delete or publish it"""

    query = update.callback_query
    query.answer()

    post_body = query.message.text

    if str(query.message.chat.id) != os.environ['MOD_CHAT_ID']:
        # This callback should only be called from the moderators' group
        logger.warning("Someone's trying to impersonate a moderator")
        return
    
    if query.data == 'approve-yes':
        query.delete_message()
        bot = Bot(token=os.environ['TOKEN'])
        bot.send_message(chat_id=os.environ['CHANNEL_ID'], text=escape(post_body), parse_mode=ParseMode.HTML)
    else:
        query.delete_message()


def main() -> None:
    updater = Updater(os.environ["TOKEN"])

    # Add handlers
    updater.dispatcher.add_handler(CommandHandler('start', start_command))
    updater.dispatcher.add_handler(CommandHandler('help', start_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(tag_post, pattern="^tag-"))
    updater.dispatcher.add_handler(CallbackQueryHandler(confirm_post, pattern="^confirm-"))
    updater.dispatcher.add_handler(CallbackQueryHandler(approve_post, pattern="^approve-"))
    updater.dispatcher.add_handler(MessageHandler(Filters.update.message, receive_post))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
