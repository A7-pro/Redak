import os
import telebot
import sqlite3
import time

# 🔹 تحميل التوكن من بيئة Render
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# 🔹 إزالة أي Webhook مفعّل قبل تشغيل البوت
bot.remove_webhook()

# 🔹 قائمة المطورين (أنا الأساسي)
DEVELOPER_ID = 7601607055
developers = [DEVELOPER_ID]

# 🔹 إنشاء قاعدة بيانات لحفظ الأذكار
conn = sqlite3.connect("azkar.db", check_same_thread=False)
cursor = conn.cursor()

# 🔹 إنشاء جدول الأذكار إذا لم يكن موجودًا
cursor.execute('''CREATE TABLE IF NOT EXISTS azkar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    content TEXT,
                    file_id TEXT,
                    file_type TEXT)''')

# 🔹 إنشاء جدول المطورين إذا لم يكن موجودًا
cursor.execute('''CREATE TABLE IF NOT EXISTS developers (
                    user_id INTEGER PRIMARY KEY)''')

# 🔹 إضافة المطور الأساسي للجدول إذا لم يكن موجودًا
cursor.execute("INSERT OR IGNORE INTO developers (user_id) VALUES (?)", (DEVELOPER_ID,))
conn.commit()

# 🔹 أوامر لوحة التحكم
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in developers:
        bot.reply_to(message, "🔹 *لوحة التحكم*\n\n"
                              "📌 /add_zekr - إضافة ذكر جديد\n"
                              "📌 /delete_zekr - حذف ذكر\n"
                              "📌 /list_azkar - عرض جميع الأذكار\n"
                              "📌 /add_dev - إضافة مطور\n"
                              "📌 /remove_dev - إزالة مطور\n"
                              "📌 /list_devs - قائمة المطورين\n", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام لوحة التحكم.")

# 🔹 إضافة ذكر جديد
@bot.message_handler(commands=['add_zekr'])
def add_zekr(message):
    if message.from_user.id in developers:
        bot.reply_to(message, "📥 *أرسل الذكر الآن:*", parse_mode="Markdown")
        bot.register_next_step_handler(message, save_zekr_text)
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")

def save_zekr_text(message):
    zekr_name = message.text
    bot.reply_to(message, "📎 *أرسل محتوى الذكر (نص/صورة/ملف):*", parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda msg: save_zekr_content(msg, zekr_name))

def save_zekr_content(message, zekr_name):
    file_id, file_type, content = None, None, None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.text:
        content = message.text
        file_type = "text"

    cursor.execute("INSERT INTO azkar (name, content, file_id, file_type) VALUES (?, ?, ?, ?)",
                   (zekr_name, content, file_id, file_type))
    conn.commit()
    bot.reply_to(message, "✅ تم إضافة الذكر بنجاح!")

# 🔹 حذف ذكر
@bot.message_handler(commands=['delete_zekr'])
def delete_zekr(message):
    if message.from_user.id in developers:
        bot.reply_to(message, "🗑 *أرسل اسم الذكر الذي تريد حذفه:*", parse_mode="Markdown")
        bot.register_next_step_handler(message, confirm_delete_zekr)
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")

def confirm_delete_zekr(message):
    zekr_name = message.text
    cursor.execute("DELETE FROM azkar WHERE name = ?", (zekr_name,))
    conn.commit()
    bot.reply_to(message, f"✅ تم حذف الذكر: {zekr_name}")

# 🔹 عرض جميع الأذكار
@bot.message_handler(commands=['list_azkar'])
def list_azkar(message):
    cursor.execute("SELECT name FROM azkar")
    azkar = cursor.fetchall()
    if azkar:
        response = "📜 *قائمة الأذكار:*\n" + "\n".join([f"🔹 {row[0]}" for row in azkar])
    else:
        response = "❌ لا يوجد أذكار مضافة بعد."
    bot.reply_to(message, response, parse_mode="Markdown")

# 🔹 إضافة مطور
@bot.message_handler(commands=['add_dev'])
def add_dev(message):
    if message.from_user.id in developers:
        bot.reply_to(message, "👤 *أرسل معرف (ID) المطور الجديد:*", parse_mode="Markdown")
        bot.register_next_step_handler(message, save_dev)
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")

def save_dev(message):
    try:
        new_dev_id = int(message.text)
        cursor.execute("INSERT OR IGNORE INTO developers (user_id) VALUES (?)", (new_dev_id,))
        conn.commit()
        bot.reply_to(message, f"✅ تم إضافة المطور الجديد: {new_dev_id}")
    except ValueError:
        bot.reply_to(message, "❌ الرجاء إرسال رقم معرف صحيح.")

# 🔹 إزالة مطور
@bot.message_handler(commands=['remove_dev'])
def remove_dev(message):
    if message.from_user.id in developers:
        bot.reply_to(message, "👤 *أرسل معرف (ID) المطور الذي تريد إزالته:*", parse_mode="Markdown")
        bot.register_next_step_handler(message, confirm_remove_dev)
    else:
        bot.reply_to(message, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")

def confirm_remove_dev(message):
    try:
        dev_id = int(message.text)
        cursor.execute("DELETE FROM developers WHERE user_id = ?", (dev_id,))
        conn.commit()
        bot.reply_to(message, f"✅ تم إزالة المطور: {dev_id}")
    except ValueError:
        bot.reply_to(message, "❌ الرجاء إرسال رقم معرف صحيح.")

# 🔹 عرض قائمة المطورين
@bot.message_handler(commands=['list_devs'])
def list_devs(message):
    cursor.execute("SELECT user_id FROM developers")
    devs = cursor.fetchall()
    if devs:
        response = "👤 *قائمة المطورين:*\n" + "\n".join([f"🔹 {row[0]}" for row in devs])
    else:
        response = "❌ لا يوجد مطورين مسجلين."
    bot.reply_to(message, response, parse_mode="Markdown")

# 🔹 تشغيل البوت مع إعادة التشغيل التلقائي في حالة حدوث خطأ
while True:
    try:
        print("🚀 بوت رضاك يعمل الآن...")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"⚠️ خطأ في تشغيل البوت: {e}")
        time.sleep(5)  # انتظر 5 ثوانٍ ثم حاول التشغيل مرة أخرى