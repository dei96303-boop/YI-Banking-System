[app]
title = YI Bank
package.name = yibank
package.domain = org.yeanur
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# এখানে sqlite3 এবং openssl যোগ করা হয়েছে (hashlib এর জন্য openssl প্রয়োজন)
requirements = python3,kivy==2.3.0,sqlite3,openssl,hostpython3

orientation = portrait
fullscreen = 0

# Android API সেটিংস
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# স্টোরেজ পারমিশন (ডেটাবেস সেভ করার জন্য জরুরি)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
