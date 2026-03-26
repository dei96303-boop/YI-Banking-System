[app]
title = YI Bank
package.name = yibank
package.domain = org.yeanur
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy==2.3.0,sqlite3,libffi,openssl

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
