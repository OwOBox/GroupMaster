import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown, mention_html

from GroupMaster import dispatcher, updater
from GroupMaster.modules.disable import DisableAbleCommandHandler
from GroupMaster.modules.helper_funcs.chat_status import bot_admin, can_promote, user_admin, can_pin
from GroupMaster.modules.helper_funcs.extraction import extract_user
from GroupMaster.modules.log_channel import loggable
from GroupMaster.modules.sql import admin_sql as sql
from GroupMaster.modules.translations.strings import tld

from GroupMaster.modules.connection import connected

@run_async
@bot_admin
@user_admin
@loggable
def promote(bot: Bot, update: Update, args: List[str]) -> str:
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chatD = dispatcher.bot.getChat(conn)
    else:
        chatD = update.effective_chat
        if chat.type == "private":
            exit(1)

    if not chatD.get_member(bot.id).can_promote_members:
        update.effective_message.reply_text("I can't promote/demote people here! "
                                            "Make sure I'm admin and can appoint new admins.")
        exit(1)

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(tld(chat.id, "You don't seem to be referring to a user."))
        return ""

    user_member = chatD.get_member(user_id)
    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text(tld(chat.id, "How am I meant to promote someone that's already an admin?"))
        return ""

    if user_id == bot.id:
        message.reply_text(tld(chat.id, "I can't promote myself! Get an admin to do it for me."))
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chatD.get_member(bot.id)

    bot.promoteChatMember(chatD.id, user_id,
                          #can_change_info=bot_member.can_change_info,
                          can_post_messages=bot_member.can_post_messages,
                          can_edit_messages=bot_member.can_edit_messages,
                          can_delete_messages=bot_member.can_delete_messages,
                          #can_invite_users=bot_member.can_invite_users,
                          can_restrict_members=bot_member.can_restrict_members,
                          can_pin_messages=bot_member.can_pin_messages,
                          can_promote_members=bot_member.can_promote_members)

    message.reply_text(tld(chat.id, f"Đã thăng cấp thành công trong *{chatD.title}*!"), parse_mode=ParseMode.MARKDOWN)
    return f"<b>{html.escape(chatD.title)}:</b>" \
            "\n#PROMOTED" \
           f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}" \
           f"\n<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"


@run_async
@bot_admin
@user_admin
@loggable
def demote(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chatD = dispatcher.bot.getChat(conn)
    else:
        chatD = update.effective_chat
        if chat.type == "private":
            exit(1)

    if not chatD.get_member(bot.id).can_promote_members:
        update.effective_message.reply_text("I can't promote/demote people here! "
                                            "Make sure I'm admin and can appoint new admins.")
        exit(1)

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(tld(chat.id, "You don't seem to be referring to a user."))
        return ""

    user_member = chatD.get_member(user_id)
    if user_member.status == 'creator':
        message.reply_text(tld(chat.id, "Người này ĐÃ TẠO cuộc trò chuyện, tôi sẽ hạ cấp họ như thế nào?"))
        return ""

    if not user_member.status == 'administrator':
        message.reply_text(tld(chat.id, "Can't demote what wasn't promoted!"))
        return ""

    if user_id == bot.id:
        message.reply_text(tld(chat.id, "I can't demote myself!"))
        return ""

    try:
        bot.promoteChatMember(int(chatD.id), int(user_id),
                              can_change_info=False,
                              can_post_messages=False,
                              can_edit_messages=False,
                              can_delete_messages=False,
                              can_invite_users=False,
                              can_restrict_members=False,
                              can_pin_messages=False,
                              can_promote_members=False)
        message.reply_text(tld(chat.id, f"Đã hạ cấp thành công trong *{chatD.title}*!"), parse_mode=ParseMode.MARKDOWN)
        return f"<b>{html.escape(chatD.title)}:</b>" \
                "\n#DEMOTED" \
               f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}" \
               f"\n<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"

    except BadRequest:
        message.reply_text(
            tld(chat.id, "Không thể hạ cấp. Tôi có thể không phải là quản trị viên hoặc trạng thái quản trị viên được chỉ định bởi một người dùng khác, vì vậy tôi không thể hành động dựa trên họ!")
            )
        return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(bot: Bot, update: Update, args: List[str]) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    is_group = chat.type != "private" and chat.type != "channel"

    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower() == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            bot.pinChatMessage(chat.id, prev_message.message_id, disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        return f"<b>{html.escape(chat.title)}:</b>" \
                "\n#PINNED" \
               f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"

    return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(bot: Bot, update: Update) -> str:
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    return f"<b>{html.escape(chat.title)}:</b>" \
           "\n#UNPINNED" \
           f"\n<b>Admin:</b> {mention_html(user.id, user.first_name)}"


@run_async
@bot_admin
@user_admin
def invite(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if not conn == False:
        chatP = dispatcher.bot.getChat(conn)
    else:
        chatP = update.effective_chat
        if chat.type == "private":
            exit(1)

    if chatP.username:
        update.effective_message.reply_text(chatP.username)
    elif chatP.type == chatP.SUPERGROUP or chatP.type == chatP.CHANNEL:
        bot_member = chatP.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = chatP.invite_link
            #print(invitelink)
            if not invitelink:
                invitelink = bot.exportChatInviteLink(chatP.id)

            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(tld(chat.id, "I don't have access to the invite link, try changing my permissions!"))
    else:
        update.effective_message.reply_text(tld(chat.id, "I can only give you invite links for supergroups and channels, sorry!"))


@run_async
def adminlist(bot, update):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if not conn == False:
        chatP = dispatcher.bot.getChat(conn)
    else:
        chatP = update.effective_chat
        if chat.type == "private":
            exit(1)
    
    administrators = chatP.get_administrators()

    text = tld(chat.id, "Quản trị viên trong") + " *{}*:".format(chatP.title or tld(chat.id, "nhóm này"))
    for admin in administrators:
        user = admin.user
        status = admin.status
        if status == "creator":
            name = user.first_name + (user.last_name or "") + tld(chat.id, " (Chủ group)")
        else:
            name = user.first_name + (user.last_name or "")
        text += f"\n• `{name}`"

    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@user_admin
@run_async
def reaction(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    if len(args) >= 1:
        var = args[0]
        print(var)
        if var == "False":
            sql.set_command_reaction(chat.id, False)
            update.effective_message.reply_text("Disabled reaction on admin commands for users")
        elif var == "True":
            sql.set_command_reaction(chat.id, True)
            update.effective_message.reply_text("Enabled reaction on admin commands for users")
        else:
            update.effective_message.reply_text("Please enter True or False!", parse_mode=ParseMode.MARKDOWN)
    else:
        status = sql.command_reaction(chat.id)
        if status == False:
            update.effective_message.reply_text("Reaction on admin commands for users now `disabled`!", parse_mode=ParseMode.MARKDOWN)
        else:
            update.effective_message.reply_text("Reaction on admin commands for users now `enabled`!", parse_mode=ParseMode.MARKDOWN)
        

__help__ = """
 - /adminlist | /admins: danh sách quản trị viên trong cuộc trò chuyện

*Admin only:*
 - /pin: âm thầm ghim tin nhắn đã trả lời - add 'loud' or 'notify' to give notifs to users.
 - /unpin: bỏ ghim tin nhắn hiện được ghim
 - /invitelink: được invitelink
 - /promote: set admin cho người dùng
 - /demote: hủy admin cho người dùng
"""

__mod_name__ = "Admin"

PIN_HANDLER = DisableAbleCommandHandler("pin", pin, pass_args=True, filters=Filters.group)
UNPIN_HANDLER = DisableAbleCommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = CommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, pass_args=True)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, pass_args=True)

REACT_HANDLER = DisableAbleCommandHandler("reaction", reaction, pass_args=True, filters=Filters.group)

ADMINLIST_HANDLER = DisableAbleCommandHandler(["adminlist", "admins"], adminlist)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(REACT_HANDLER)
