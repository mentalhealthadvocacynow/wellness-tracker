[app]

# (str) Title of your application
title = Wellness Tracker

# (str) Package name
package.name = wellnesstracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mentalhealthadvocacy.wellnesstracker

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.1.0,kivymd==1.1.1

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (portrait, sensorPortrait, landscape, sensorLandscape)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (int) Android SDK version to use
android.sdk = 31

# (list) Android application meta-data to set (key=value format)
#android.add_src = src/android/

# (list) Android AAR archives to add
#android.add_aars = 

# (list) Gradle dependencies to add
#android.gradle_dependencies = 

# (list) Java files to add to the libs so they can be used by kivy
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = True

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past, was `android.arch` as we weren't supporting builds for multiple archs at the same time.
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
