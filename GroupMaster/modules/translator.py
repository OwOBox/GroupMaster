from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from GroupMaster import dispatcher, LOGGER
from GroupMaster.modules.disable import DisableAbleCommandHandler

from googletrans import Translator


@run_async
def do_translate(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message # type: Optional[Message]
    lan = " ".join(args)
    try:
        to_translate_text = msg.reply_to_message.text
    except:
        return
    translator = Translator()
    try:
        translated = translator.translate(to_translate_text, dest=lan)
        src_lang = translated.src
        translated_text = translated.text
        msg.reply_text("**Dịch từ {} sang {}.**\n\n {}".format(src_lang, lan, translated_text))
    except :
        msg.reply_text("Lỗi")


__help__ = """- /dich (language code) như trả lời một tin nhắn dài.
"""
__mod_name__ = "Dịch 💬"

dispatcher.add_handler(DisableAbleCommandHandler("dich", do_translate, pass_args=True))
