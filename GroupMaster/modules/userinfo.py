import html
from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

import GroupMaster.modules.sql.userinfo_sql as sql
from GroupMaster import dispatcher, SUDO_USERS, OWNER_ID
from GroupMaster.modules.disable import DisableAbleCommandHandler
from GroupMaster.modules.helper_funcs.chat_status import user_admin, user_not_admin
from GroupMaster.modules.helper_funcs.extraction import extract_user


@run_async
def about_me(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text("*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(username + " vẫn chưa đặt một thông báo thông tin về họ!")
    else:
        update.effective_message.reply_text("Bạn chưa đặt một thông báo thông tin về bản thân!")


@run_async
@user_admin
def set_about_me(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    user_id = message.from_user.id
    text = message.text
    info = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            message.reply_text("Đã cập nhật thông tin của bạn!")
        else:
            message.reply_text(
                "Thông tin của bạn cần phải ở dưới {} nhân vật! Bạn có {}.".format(MAX_MESSAGE_LENGTH // 4, len(info[1])))


@run_async
def about_bio(bot: Bot, update: Update, args: List[str]):
    message = update.effective_message  # type: Optional[Message]

    user_id = extract_user(message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text("*{}*:\n{}".format(user.first_name, escape_markdown(info)),
                                            parse_mode=ParseMode.MARKDOWN)
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text("{} chưa có một thông điệp nào về bản thân họ!".format(username))
    else:
        update.effective_message.reply_text("Bạn vẫn chưa có một bộ tiểu sử về bản thân!")


@run_async
@user_admin
def set_about_bio(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    sender = update.effective_user  # type: Optional[User]
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id == message.from_user.id:
            message.reply_text("Ha, bạn không thể thiết lập tiểu sử của riêng bạn! Bạn đang ở trong lòng thương xót của những người khác ở đây ...")
            return
        elif user_id == bot.id and sender.id not in SUDO_USERS:
            message.reply_text("Erm ... vâng, tôi chỉ tin tưởng những người dùng sudo đặt LMAO sinh học của tôi.")
            return
        elif user_id in SUDO_USERS and sender.id not in SUDO_USERS:
            message.reply_text("Erm ... vâng, tôi chỉ tin tưởng người dùng sudo đặt LMAO sinh học cho người dùng sudo.")
            return
        elif user_id == OWNER_ID:
            message.reply_text("Bạn không đặt LMAO tiểu sử chính của tôi.")
            return

        text = message.text
        bio = text.split(None, 1)  # use python's maxsplit to only remove the cmd, hence keeping newlines.
        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text("Đã cập nhật {}'s bio!".format(repl_message.from_user.first_name))
            else:
                message.reply_text(
                    "A bio needs to be under {} characters! You tried to set {}.".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])))
    else:
        message.reply_text("Reply to someone's message to set their bio!")


def __user_info__(user_id, chat_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return "<b>Về người dùng:</b>\n{me}\n<b>Những người khác nói gì:</b>\n{bio}".format(me=me, bio=bio)
    elif bio:
        return "<b>Những người khác nói gì:</b>\n{bio}\n".format(me=me, bio=bio)
    elif me:
        return "<b>Về người dùng:</b>\n{me}""".format(me=me, bio=bio)
    else:
        return ""


def __gdpr__(user_id):
    sql.clear_user_info(user_id)
    sql.clear_user_bio(user_id)


__help__ = """
 - /setbio <text>: trong khi trả lời, sẽ lưu tiểu sử của một người dùng khác
 - /bio: sẽ lấy tiểu sử của bạn hoặc của người dùng khác. Điều này không thể được thiết lập bởi chính bạn.
 - /setme <text>: sẽ thiết lập thông tin của bạn
 - /me: sẽ lấy thông tin của bạn hoặc của người dùng khác
"""

__mod_name__ = "Thêm Bio 🗣"

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio, pass_args=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me, pass_args=True)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)

