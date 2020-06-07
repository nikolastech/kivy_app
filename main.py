from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.config import Config
from pytube import *
from kivy.properties import ObjectProperty
import os
from kivymd.uix.filemanager import MDFileManager
import time
import urllib.request
from moviepy.editor import*
import subprocess
from kivymd.toast import toast
import shutil
import json

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class Progress_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Converting..."


class Video_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Converted!"
        urllib.request.urlretrieve(self.app.yt.thumbnail_url, "Image_data/Thumb.jpg")
        self.ids.image.source = "Image_data/Thumb.jpg"
        self.ids.label.text = self.app.pre_main.title


class Audio_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Converted!"
        urllib.request.urlretrieve(self.app.yt.thumbnail_url, "Image_data/Thumb.jpg")
        self.ids.image.source = "Image_data/Thumb.jpg"
        self.ids.label.text = self.app.pre_main.title


class Settings_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Settings"
        with open("theme.json", "r+") as f:
            a = json.load(f)
            if a["theme"] == "dark":
                self.ids.mode.active = True
            else:
                self.ids.mode.active = False
                
    def change_mode(self, checkbox, value):
        if value:
            with open("theme.json", "r+") as f:
                f.write("{\"theme\": \"dark\"}")
            self.app.theme_cls.theme_style = "Dark"
        else:
            with open("theme.json", "r+") as f:
                f.write("{\"theme\":\"light\"}")
            self.app.theme_cls.theme_style = "Light"


class About_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "About Youtube Converter"


class Main_Page(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_pre_enter(self, *args):
        self.app.title = "Youtube Converter"
        self.app.set_theme()

    def wait(self):
        self.ids.wait.text = "Please Wait..."


class MyApp(MDApp):
    is1080p = ObjectProperty(True)
    is720p = ObjectProperty(None)
    is480p = ObjectProperty(None)
    ismp3 = ObjectProperty(None)
    ismp4 = ObjectProperty(None)
    pre_secondary = ObjectProperty(None)
    pre_main = ObjectProperty(None)
    video = ObjectProperty(None)
    audio = ObjectProperty(None)
    yt = ObjectProperty(None)
    percentage = ObjectProperty(0)
    link = ObjectProperty(None)
    final_mp3 = ObjectProperty(None)
    final_mp4 = ObjectProperty(None)
    final = ObjectProperty(None)
    path = ObjectProperty(None)

    def progress_function(self, stream, chunk, bytes_remaining):
        size = self.pre_main.filesize
        p = (abs(1 - (float(bytes_remaining) / float(size))) * float(100))
        self.percentage = round(p)
        print(self.percentage)

    def finalise_function(self):
        if self.ismp3:
            self.root.ids.screen_manager.current = "video_page"
        else:
            self.root.ids.screen_manager.current = "audio_page"

    def get_video(self):
        try:
            self.link = self.root.ids.screen_manager.get_screen("main_page").ids.link_container.text
            self.yt = YouTube(self.link)
            self.root.ids.screen_manager.current = "progress_page"
        except Exception as E:
            self.root.ids.screen_manager.get_screen("main_page").ids.link_container.text = "Error: Invalid Link"
            self.root.ids.screen_manager.get_screen("main_page").ids.wait.text = ""
            print(E)

    def grab_video(self):
        if self.ismp3:
            self.root.ids.screen_manager.get_screen("main_page").ids.wait.text = ""
            self.pre_main = self.yt.streams.filter(mime_type="audio/mp4").first()
            self.yt.register_on_progress_callback(self.progress_function)
            self.audio = self.pre_main.download()
            pre_conv = AudioFileClip(self.audio)
            self.final_mp3 = pre_conv.write_audiofile(self.pre_main.title.replace("|", "") + ".mp3")
            os.remove(self.audio)
            self.final = self.pre_main.title.replace("|", "") + ".mp3"
            self.root.ids.screen_manager.current = "audio_page"
            self.percentage = 0
        if self.ismp4:
            self.root.ids.screen_manager.get_screen("main_page").ids.wait.text = ""
            if self.is1080p:
                self.pre_main = self.yt.streams.filter(res="1080p").first()
                if not self.pre_main:
                    self.root.ids.screen_manager.current = "main_page"
                    self.root.ids.screen_manager.get_screen("main_page").ids.link_container.text = "Error: Resolution Unavailable"
                else:
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.video = self.pre_main.download(filename=self.pre_main.title.replace("|", ""))
                    self.pre_main = self.yt.streams.filter(mime_type="audio/mp4").first()
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.audio = self.pre_main.download(filename=self.pre_main.title.replace("|", "")+"2")
                    self.final_mp4 = VideoFileClip(self.video)
                    self.final_mp3 = AudioFileClip(self.audio)
                    final = self.final_mp4.set_audio(self.final_mp3)
                    final.write_videofile(self.pre_main.title.replace("|", "") + "_final" + ".mp4")
                    os.remove(self.audio)
                    os.remove(self.video)
                    self.final = self.pre_main.title.replace("|", "") + "_final" + ".mp4"
                    self.root.ids.screen_manager.current = "video_page"
                    self.percentage = 0
            if self.is720p:
                self.pre_main = self.yt.streams.filter(res="720p").first()
                if not self.pre_main:
                    self.root.ids.screen_manager.current = "main_page"
                    self.root.ids.screen_manager.get_screen(
                        "main_page").ids.link_container.text = "Error: Resolution Unavailable"
                else:
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.video = self.pre_main.download(filename=self.pre_main.title.replace("|", ""))
                    self.pre_main = self.yt.streams.filter(mime_type="audio/mp4").first()
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.audio = self.pre_main.download(filename=self.pre_main.title.replace("|", "") + "2")
                    self.final_mp4 = VideoFileClip(self.video)
                    self.final_mp3 = AudioFileClip(self.audio)
                    final = self.final_mp4.set_audio(self.final_mp3)
                    final.write_videofile(self.pre_main.title.replace("|", "") + "_final" + ".mp4")
                    os.remove(self.audio)
                    os.remove(self.video)
                    self.final = self.pre_main.title.replace("|", "") + "_final" + ".mp4"
                    self.root.ids.screen_manager.current = "video_page"
                    self.percentage = 0
            if self.is480p:
                self.pre_main = self.yt.streams.filter(res="480p").first()
                if not self.pre_main:
                    self.pre_main = self.yt.streams.filter(progressive=False, mime_type="video/mp4").first()
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.video = self.pre_main.download(filename=self.pre_main.title.replace("|", ""))
                    self.pre_main = self.yt.streams.filter(mime_type="audio/mp4").first()
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.audio = self.pre_main.download(filename=self.pre_main.title.replace("|", "") + "2")
                    self.final_mp4 = VideoFileClip(self.video)
                    self.final_mp3 = AudioFileClip(self.audio)
                    final = self.final_mp4.set_audio(self.final_mp3)
                    final.write_videofile(self.pre_main.title.replace("|", "") + "_final" + ".mp4")
                    self.final = self.pre_main.title.replace("|", "") + "_final" + ".mp4"
                    self.percentage = 0
                    os.remove(self.audio)
                    os.remove(self.video)
                    self.root.ids.screen_manager.current = "video_page"
                    self.percentage = 0
                else:
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.video = self.pre_main.download(filename=self.pre_main.title.replace("|", ""))
                    self.pre_main = self.yt.streams.filter(mime_type="audio/mp4").first()
                    self.yt.register_on_progress_callback(self.progress_function)
                    self.audio = self.pre_main.download(filename=self.pre_main.title.replace("|", "") + "2")
                    self.final_mp4 = VideoFileClip(self.video)
                    self.final_mp3 = AudioFileClip(self.audio)
                    final = self.final_mp4.set_audio(self.final_mp3)
                    final.write_videofile(self.pre_main.title.replace("|", "") + "_final" + ".mp4")
                    self.final = self.pre_main.title.replace("|", "") + "_final" + ".mp4"
                    os.remove(self.audio)
                    os.remove(self.video)
                    self.root.ids.screen_manager.current = "video_page"
                    self.percentage = 0

    def is_1080p(self, checkbox, value):
        if value:
            self.is1080p = True
            self.is720p = False
            self.is480p = False

    def is_720p(self, checkbox, value):
        if value:
            self.is1080p = False
            self.is720p = True
            self.is480p = False

    def is_480p(self, checkbox, value):
        if value:
            self.is1080p = False
            self.is720p = False
            self.is480p = True

    def is_mp3(self, checkbox, value):
        if value:
            self.ismp3 = True
            self.ismp4 = False
            self.root.ids.screen_manager.get_screen("main_page").ids.sd_check.disabled = True
            self.root.ids.screen_manager.get_screen("main_page").ids.hd_check.disabled = True
            self.root.ids.screen_manager.get_screen("main_page").ids.fullhd_check.disabled = True

    def is_mp4(self, checkbox, value):
        if value:
            self.ismp4 = True
            self.ismp3 = False
            self.root.ids.screen_manager.get_screen("main_page").ids.sd_check.disabled = False
            self.root.ids.screen_manager.get_screen("main_page").ids.hd_check.disabled = False
            self.root.ids.screen_manager.get_screen("main_page").ids.fullhd_check.disabled = False

    def select_path(self, path):
        self.exit_manager()
        self.path = path
        print(self.path)
        shutil.move(self.final, self.path.replace("\\", "/") + "/" + self.final)

    def set_theme(self):
        with open("theme.json", "r+") as f:
            a = json.load(f)
        if a['theme'] == "dark":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def file_manager_open(self):
        self.file_manager.show('\\')  # output manager to the screen
        self.manager_open = True

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def convert_again(self):
        try:
            os.remove(self.final)
        except FileNotFoundError:
            pass
        self.root.ids.screen_manager.current = "main_page"

    def build(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            previous=True
        )
        self.title = "Youtube Converter"
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.primary_hue = "900"
        return Builder.load_file("main.kv")


MyApp().run()

if __name__ == "__main__":
    MyApp().run()
