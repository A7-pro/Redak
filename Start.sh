#!/bin/bash
python bot.py &  # تشغيل البوت في الخلفية
gunicorn --bind 0.0.0.0:$PORT wsgi:app  # تشغيل Flask لإبقاء السيرفر نشطًا
