from GroupMaster.modules.sql.translation import switch_to_locale, prev_locale
from GroupMaster.modules.translations.strings import tld
from telegram.ext import CommandHandler
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from GroupMaster import dispatcher
from GroupMaster.modules.translations.list_locale import list_locales
from GroupMaster.modules.helper_funcs.chat_status import user_admin
from telegram.ext import CallbackQueryHandler
import re

from GroupMaster.modules.connection import connected


@user_admin
def locale(bot, update, args):
    chat = update.effective_chat
    if len(args) > 0:
        locale = args[0].lower()
        if locale in list_locales:
            if locale in ('en', 'vi'):
                switch_to_locale(chat.id, locale)
                update.message.reply_text(tld(chat.id, 'Chuyển sang {} thành công!').format(list_locales[locale]))
            else:
                update.message.reply_text("{} chưa được hỗ trợ!".format(list_locales[locale]))
        else:
            update.message.reply_text("Đó có phải là một mã ngôn ngữ hợp lệ không? Sử dụng mã ISO được quốc tế chấp nhận!")
    else:
        LANGUAGE = prev_locale(chat.id)
        if LANGUAGE:
            locale = LANGUAGE.locale_name
            native_lang = list_locales[locale]
            update.message.reply_text("Current locale for this chat is: *{}*".format(native_lang), parse_mode = ParseMode.MARKDOWN)
        else:
            update.message.reply_text("Current locale for this chat is: *English*", parse_mode=ParseMode.MARKDOWN)

@user_admin
def locale_button(bot, update):
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]
    query = update.callback_query
    lang_match = re.findall(r"en|vi", query.data)
    if lang_match:
        if lang_match[0]:
            switch_to_locale(chat.id, lang_match[0])
            query.answer(text="Language changed!")
        else:
            query.answer(text="Error!", show_alert=True)

    try:
        LANGUAGE = prev_locale(chat.id)
        locale = LANGUAGE.locale_name
        curr_lang = list_locales[locale]
    except:
        curr_lang = "English"

    text = "*Select language* \n"
    text += "User language : `{}`".format(curr_lang)

    conn = connected(bot, update, chat, user.id, need_admin=False)

    if not conn == False:
        try:
            chatlng = prev_locale(conn).locale_name
            chatlng = list_locales[chatlng]
            text += "\nConnected chat language : `{}`".format(chatlng)
        except:
            chatlng = "English"

    text += "*\n\nSelect new user language:*"

    query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup([[
                                            InlineKeyboardButton("English 🇺🇸", callback_data="set_lang_en")]] + [[
                                            InlineKeyboardButton("Vietnamese 🇻🇳", callback_data="set_lang_vi"),]] + [[
                                            InlineKeyboardButton("⬅️ Back", callback_data="bot_start")]]))

    print(lang_match)
    query.message.delete()
    bot.answer_callback_query(query.id)


LOCALE_HANDLER = CommandHandler(["set_locale", "locale", "lang", "setlang"], locale, pass_args=True)
locale_handler = CallbackQueryHandler(locale_button, pattern="chng_lang")
set_locale_handler = CallbackQueryHandler(locale_button, pattern=r"set_lang_")

dispatcher.add_handler(LOCALE_HANDLER)
dispatcher.add_handler(locale_handler)
dispatcher.add_handler(set_locale_handler)
