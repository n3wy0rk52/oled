[app]

title = OLED
package.name = oledgym
package.domain = org.oled
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,flet,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
