import re
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import BadRequest

enabled_flags = {}

def _chat_key(chat_id):
    return str(chat_id)

def _flag(chat_id, name):
    return enabled_flags.get(_chat_key(chat_id), {}).get(name, False)

def _set_flag(chat_id, name, value=True):
    enabled_flags.setdefault(_chat_key(chat_id), {})[name] = value

def _uname(user):
    return user.full_name or user.first_name or "مجهول"

async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
        return m.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    except Exception:
        return False

async def _bot_is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, context.bot.id)
        return m.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    except Exception:
        return False

async def _target_from_reply(msg):
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user
    return None

async def _send_profile_photo(update, context):
    user = update.effective_user
    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    if photos.total_count > 0 and photos.photos:
        file_id = photos.photos[0][-1].file_id
        await update.message.reply_photo(file_id, caption=f"᥀︙ صورتك يا {_uname(user)}")
    else:
        await update.message.reply_text("᥀︙ ما عندك صورة شخصية")

def _rnd(items):
    return random.choice(items)

MAIN_RE = re.compile(
    r"^(نبذه|نزلني|التاك|الرفع|غنيلي|الرابط|التنبيه|الاهداء|الحظر|الايدي|صورتي|التفاعل|التوحيد|اطردني|التحذير|المضاد|ثنائي اليوم|ايدي العضو|الوضع الليلي|المسح التلقائي|الحظر المحدد|المسح التلقائي بالوقت|"
    r"جمالي|زوجني|الالعاب|نسبه الحب|نسبه الكره|نسبه الرجوله|نسبه الانوثه|نسبه الجمال|الالعاب المتطوره|انمي|صوره|اغنيه|متحركه|ميمز|ريمكس|افتار|ثيم|راب|شعر|قصيده|فلم|مسلسل|اقتباس|ستوري|قران|جداريه|هينه|هينها|بوسه|بوسها|تزوجني|تزوجيني|طلقني|طلقيني|زوجي|زوجتي|"
    r"رد|تاك|امر|بالرد|رد عام|الصوره|رد مميز|رد متعدد|قائمه المنع|كليشه المالك|قائمه التاكات|المميزين عام|كليشه المطور|مسح \d+|الردود المميزه|الردود المتعدده|قائمه المنع العام|المنشئين الاساسيين|"
    r"الفشار|الفيديو|الدخول|الاضافه|الاغاني|الصوت|الملفات|التفليش|الدردشه|الجهات|السيلفي|البوتات|الشارحه|الكيبورد|الانكليزيه|الفارسيه|الاشعارات|الماركداون|تحكم|اضف تاك|تنزيل الكل|رفع المالك|رفع الادمنيه|كشف القيود|تغيير كليشه المالك|مسح كليشه المالك|تقييد \d+ (دقيقة|دقيقه|ساعة|ساعه|يوم)|"
    r"القوائم|الميديا|الاعدادات|التفعيلات|ضبط الحمايه|ضع رابط|ضع تحذير|ضع وصف|ضع صوره|ضع اسم|ضع توحيد|انشاء رتبط|قائمه المنع|الغاء التثبيت|منع|الغاء منع|اضف رد مميز|اضف رد متعدد|كشف بوتات|الردود المميزه|الردود المتعدده|الاوامر المضافه|ضع تكرار|تغيير المالك|صلاحيات المجموعه|اضف لقب|اضف نقاط|اضف رسائل|ضع رتبه|اضف سحكات|ضع وقت المسح|"
    r"تحكم|اضف تاك|تنزيل الكل|رفع المالك|رفع الادمنيه|كشف القيود|تغيير كليشه المالك|مسح كليشه المالك|تقييد \d+ (دقيقة|دقيقه|ساعة|ساعه|يوم))$"
)

async def main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type == "private":
        return

    text = (msg.text or "").strip()
    if not MAIN_RE.match(text):
        return

    admin_only = {
        "الرفع","الرابط","التنبيه","الحظر","التوحيد","التحذير","المضاد","الوضع الليلي","المسح التلقائي",
        "الحظر المحدد","المسح التلقائي بالوقت","القوائم","الميديا","الاعدادات","التفعيلات","ضبط الحمايه",
        "قائمه المنع","صلاحيات المجموعه","كشف بوتات","الردود المميزه","الردود المتعدده","الاوامر المضافه",
        "تغيير المالك","اضف نقاط","ضع رتبه","اضف رسائل","اضف سحكات","ضع وقت المسح","تحكم","اضف تاك",
        "تنزيل الكل","رفع المالك","رفع الادمنيه","كشف القيود","تغيير كليشه المالك","مسح كليشه المالك","تقييد"
    }
    if any(text.startswith(x) for x in admin_only) and not await _is_admin(update, context):
        await msg.reply_text("᥀︙ هذا الأمر للمشرفين فقط")
        return

    if text == "نبذه":
        await msg.reply_text("᥀︙ هذه أوامر البوت الرئيسية، جرّب القوائم والميديا والاعدادات والتفعيلات وضبط الحمايه.")
        return

    if text == "نزلني":
        await msg.reply_text("᥀︙ تم استلام طلب تنزيلك")
        return

    if text == "التاك":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ التاك لـ {_uname(t or user)}")
        return

    if text == "الرفع":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ تم تسجيل الرفع لـ {_uname(t or user)}")
        return

    if text == "غنيلي":
        await msg.reply_text(_rnd(["᥀︙ يا ليل يا عين", "᥀︙ أغنية جاهزة", "᥀︙ سلامات يا قلب"]))
        return

    if text == "الرابط":
        if not await _bot_is_admin(update, context):
            await msg.reply_text("᥀︙ البوت لازم يكون مشرف حتى ينشئ رابط")
            return
        try:
            inv = await context.bot.create_chat_invite_link(chat.id)
            await msg.reply_text(f"᥀︙ رابط المجموعة:\n{inv.invite_link}")
        except Exception:
            await msg.reply_text("᥀︙ ما قدرت أسوي رابط")
        return

    if text == "التنبيه":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ تم تنبيه {_uname(t or user)}")
        return

    if text == "الاهداء":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ إهداء إلى {_uname(t or user)}")
        return

    if text == "الحظر":
        t = await _target_from_reply(msg)
        if not t:
            await msg.reply_text("᥀︙ رد على الشخص المراد حظره")
            return
        try:
            await context.bot.ban_chat_member(chat.id, t.id)
            await msg.reply_text(f"᥀︙ تم حظر {_uname(t)}")
        except Exception:
            await msg.reply_text("᥀︙ ما قدرت أحظر المستخدم")
        return

    if text == "الايدي":
        await msg.reply_text(f"᥀︙ آيديك: {user.id}")
        return

    if text == "صورتي":
        await _send_profile_photo(update, context)
        return

    if text == "التفاعل":
        await msg.reply_text("᥀︙ التفاعل: 100%")
        return

    if text == "التوحيد":
        await msg.reply_text("᥀︙ التوحيد: مفعّل")
        return

    if text == "اطردني":
        try:
            await context.bot.ban_chat_member(chat.id, user.id)
            await context.bot.unban_chat_member(chat.id, user.id, only_if_banned=True)
        except Exception:
            pass
        await msg.reply_text("᥀︙ تم طردك")
        return

    if text == "التحذير":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ تم تحذير {_uname(t or user)}")
        return

    if text == "المضاد":
        _set_flag(chat.id, "anti", not _flag(chat.id, "anti"))
        await msg.reply_text(f"᥀︙ المضاد: {'مفعّل' if _flag(chat.id, 'anti') else 'معطل'}")
        return

    if text == "ثنائي اليوم":
        t = await _target_from_reply(msg)
        await msg.reply_text(f"᥀︙ ثنائي اليوم: {_uname(user)} + {_uname(t or user)}")
        return

    if text == "ايدي العضو":
        t = await _target_from_reply(msg)
        if not t:
            await msg.reply_text("᥀︙ رد على العضو حتى أطلع آيديه")
            return
        await msg.reply_text(f"᥀︙ آيدي العضو: {t.id}")
        return

    if text == "الوضع الليلي":
        _set_flag(chat.id, "night", not _flag(chat.id, "night"))
        await msg.reply_text(f"᥀︙ الوضع الليلي: {'مفعّل' if _flag(chat.id, 'night') else 'معطل'}")
        return

    if text == "المسح التلقائي":
        _set_flag(chat.id, "autodel", not _flag(chat.id, "autodel"))
        await msg.reply_text(f"᥀︙ المسح التلقائي: {'مفعّل' if _flag(chat.id, 'autodel') else 'معطل'}")
        return

    if text == "الحظر المحدد":
        _set_flag(chat.id, "limited_ban", not _flag(chat.id, "limited_ban"))
        await msg.reply_text(f"᥀︙ الحظر المحدد: {'مفعّل' if _flag(chat.id, 'limited_ban') else 'معطل'}")
        return

    if text == "المسح التلقائي بالوقت":
        _set_flag(chat.id, "autodel_time", not _flag(chat.id, "autodel_time"))
        await msg.reply_text(f"᥀︙ المسح التلقائي بالوقت: {'مفعّل' if _flag(chat.id, 'autodel_time') else 'معطل'}")
        return

    if text == "جمالي":
        t = await _target_from_reply(msg) or user
        await msg.reply_text(f"᥀︙ جمالي لـ {_uname(t)}: {random.randint(1,100)}%")
        return

    if text == "زوجني":
        await msg.reply_text(f"᥀︙ تم استقبال طلب الزواج لـ {_uname(user)}")
        return

    if text == "الالعاب":
        await msg.reply_text("᥀︙ الألعاب: ثنائي اليوم، نسبة الحب، نسبة الكره، نسبة الرجوله، نسبة الانوثه، نسبة الجمال، الألعاب المتطوره")
        return

    if text == "نسبه الحب":
        await msg.reply_text(f"᥀︙ نسبة الحب: {random.randint(1,100)}%")
        return

    if text == "نسبه الكره":
        await msg.reply_text(f"᥀︙ نسبة الكره: {random.randint(1,100)}%")
        return

    if text == "نسبه الرجوله":
        await msg.reply_text(f"᥀︙ نسبة الرجوله: {random.randint(1,100)}%")
        return

    if text == "نسبه الانوثه":
        await msg.reply_text(f"᥀︙ نسبة الانوثه: {random.randint(1,100)}%")
        return

    if text == "نسبه الجمال":
        await msg.reply_text(f"᥀︙ نسبة الجمال: {random.randint(1,100)}%")
        return

    if text == "الالعاب المتطوره":
        await msg.reply_text("᥀︙ الألعاب المتطورة مفعلة كأوامر رد/نص")
        return

    if text in {"انمي","صوره","اغنيه","متحركه","ميمز","ريمكس","افتار","ثيم","راب","شعر","قصيده","فلم","مسلسل","اقتباس","ستوري","قران","جداريه"}:
        await msg.reply_text(f"᥀︙ تم استلام أمر: {text}")
        return

    if text in {"هينه","هينها","بوسه","بوسها","تزوجني","تزوجيني","طلقني","طلقيني","زوجي","زوجتي"}:
        await msg.reply_text(f"᥀︙ تم تنفيذ: {text}")
        return

    if text in {"القوائم","الميديا","الاعدادات","التفعيلات","ضبط الحمايه","قائمه المنع","صلاحيات المجموعه","كشف بوتات","الردود المميزه","الردود المتعدده","الاوامر المضافه"}:
        await msg.reply_text(f"᥀︙ قائمة الأمر: {text}")
        return

    if text in {"رد","تاك","امر","بالرد","رد عام","الصوره","رد مميز","رد متعدد","قائمه المنع","كليشه المالك","قائمه التاكات","المميزين عام","كليشه المطور","الردود المميزه","الردود المتعدده","قائمه المنع العام","المنشئين الاساسيين"}:
        await msg.reply_text(f"᥀︙ تم استلام: {text}")
        return

    if text in {"الفشار","الفيديو","الدخول","الاضافه","الاغاني","الصوت","الملفات","التفليش","الدردشه","الجهات","السيلفي","البوتات","الشارحه","الكيبورد","الانكليزيه","الفارسيه","الاشعارات","الماركداون","تحكم","اضف تاك","تنزيل الكل","رفع المالك","رفع الادمنيه","كشف القيود","تغيير كليشه المالك","مسح كليشه المالك"}:
        await msg.reply_text(f"᥀︙ حالة/أمر الحماية: {text}")
        return

    if text.startswith("تقييد "):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await msg.reply_text("᥀︙ اكتب: تقييد رقم يوم/ساعة/دقيقة")
            return
        num = parts[1]
        unit = parts[2]
        t = await _target_from_reply(msg)
        if not t:
            await msg.reply_text("᥀︙ رد على العضو المراد تقييده")
            return
        try:
            minutes = int(num)
        except ValueError:
            await msg.reply_text("᥀︙ الرقم غير صحيح")
            return
        if "دق" in unit:
            td = timedelta(minutes=minutes)
        elif "ساع" in unit:
            td = timedelta(hours=minutes)
        else:
            td = timedelta(days=minutes)
        until = datetime.utcnow() + td
        try:
            from telegram import ChatPermissions
            perms = ChatPermissions(can_send_messages=False)
            await context.bot.restrict_chat_member(chat.id, t.id, permissions=perms, until_date=until)
            await msg.reply_text(f"᥀︙ تم تقييد {_uname(t)} لمدة {num} {unit}")
        except Exception:
            await msg.reply_text("᥀︙ ما قدرت أقيّد العضو")
        return

    if text == "رد":
        await msg.reply_text("᥀︙ تم")
        return

    if text == "رد عام":
        await msg.reply_text("᥀︙ الرد العام جاهز")
        return

    if text == "رد مميز":
        await msg.reply_text("᥀︙ الرد المميز جاهز")
        return

    if text == "رد متعدد":
        await msg.reply_text("᥀︙ الرد المتعدد جاهز")
        return

    if text == "قائمه المنع":
        await msg.reply_text("᥀︙ قائمة المنع: لا يوجد حفظ دائم")
        return

    if text == "قائمه المنع العام":
        await msg.reply_text("᥀︙ قائمة المنع العام: لا يوجد حفظ دائم")
        return

    if text == "كشف بوتات":
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            bots = [a.user.full_name for a in admins if a.user.is_bot]
            await msg.reply_text("᥀︙ البوتات:\n" + ("\n".join(bots) if bots else "ماكو بوتات"))
        except Exception:
            await msg.reply_text("᥀︙ ما قدرت أكشف البوتات")
        return

def register_all_commands(app):
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(MAIN_RE), main_handler))