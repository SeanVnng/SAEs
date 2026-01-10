import socket
import threading
import json
import os
import base64
import time
import sys
from datetime import datetime
import random

# Media Libs
import cv2
import pyaudio
import numpy as np

# Kivy
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.cache import Cache  # <--- IMPORT TRÈS IMPORTANT

# KivyMD
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage 
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, TwoLineAvatarListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton, MDFillRoundFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout

# --- CONFIGURATION ---
# METS TON IP HAMACHI ICI
SERVER_IP = "25.47.174.224" 
SERVER_PORT = 5000
UDP_PORT = 9999

def resource_path(relative_path):
    """ Obtient le chemin absolu pour PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CallManager:
    def __init__(self, app, server_ip, udp_port):
        self.app = app
        self.server_ip = server_ip
        self.udp_port = udp_port
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.in_call = False
        self.target_user = None
        self.cam_active = True
        self.mic_active = True
        self.is_video_call = False 
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000 
        self.p = pyaudio.PyAudio()
        self.silence_threshold = 300 
        
    def register_udp(self, username):
        try:
            msg = json.dumps({"type": "REGISTER_UDP", "username": username}).encode('utf-8')
            self.udp_sock.sendto(msg, (self.server_ip, self.udp_port))
            threading.Thread(target=self.receive_udp_loop, daemon=True).start()
        except: pass

    def request_call(self, target_user, with_video=True):
        self.target_user = target_user
        self.is_video_call = with_video
        self.app.send_json({
            "type": "CALL_REQUEST", 
            "target": target_user, 
            "media": "video" if with_video else "audio"
        })
        self.app.show_calling_dialog(target_user)

    def start_call(self, target_user, with_video=True):
        self.target_user = target_user
        self.is_video_call = with_video
        self.cam_active = with_video
        self.mic_active = True
        self.in_call = True
        threading.Thread(target=self.send_video_loop, daemon=True).start()
        threading.Thread(target=self.send_audio_loop, daemon=True).start()

    def stop_call(self):
        self.in_call = False
        try:
            if hasattr(self, 'cap'): self.cap.release()
        except: pass

    def send_video_loop(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 320)
        self.cap.set(4, 240)
        while self.in_call:
            if self.cam_active and self.is_video_call:
                ret, frame = self.cap.read()
                if ret:
                    Clock.schedule_once(lambda dt: self.app.update_local_video(frame))
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
                    data_bytes = buffer.tobytes()
                    prefix = f"{self.target_user}|||V:".encode('utf-8')
                    if len(data_bytes) < 60000:
                        try: self.udp_sock.sendto(prefix + data_bytes, (self.server_ip, self.udp_port))
                        except: pass
            time.sleep(0.05)

    def send_audio_loop(self):
        try:
            stream = self.p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
            while self.in_call:
                if self.mic_active:
                    try:
                        data = stream.read(self.chunk, exception_on_overflow=False)
                        np_data = np.frombuffer(data, dtype=np.int16)
                        if len(np_data) > 0: rms = np.sqrt(np.mean(np_data**2))
                        else: rms = 0
                        if rms > self.silence_threshold:
                            prefix = f"{self.target_user}|||A:".encode('utf-8')
                            self.udp_sock.sendto(prefix + data, (self.server_ip, self.udp_port))
                    except Exception as e: print(f"Erreur mic: {e}")
                else: time.sleep(0.01)
        except Exception as e: print(f"Erreur init micro: {e}")

    def receive_udp_loop(self):
        while True:
            try:
                data, _ = self.udp_sock.recvfrom(60000)
                if not self.in_call: continue 
                if data.startswith(b"V:"):
                    nparr = np.frombuffer(data[2:], np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    Clock.schedule_once(lambda dt: self.app.update_remote_video(frame))
                elif data.startswith(b"A:"):
                    if not hasattr(self, 'audio_out'):
                        self.audio_out = self.p.open(format=self.format, channels=self.channels, rate=self.rate, output=True)
                    try: self.audio_out.write(data[2:])
                    except OSError: pass
            except: pass

class CircularAvatar(ButtonBehavior, MDBoxLayout):
    source = StringProperty()

class AddFriendBanner(MDBoxLayout):
    target_username = StringProperty()

class ChatBubble(MDBoxLayout):
    sender = StringProperty()
    message = StringProperty()
    is_me = BooleanProperty(False)
    msg_type = StringProperty("text")
    file_path = StringProperty("")

class UserListItem(TwoLineAvatarListItem):
    username = StringProperty()
    last_msg = StringProperty("Appuyez pour discuter")
    unread_count = NumericProperty(0)

class NewChatContent(MDBoxLayout): pass
class GroupCreateContent(MDBoxLayout): pass
class AddFriendContent(MDBoxLayout): pass

class GlowWidget(Widget):
    glow_color = ListProperty([1, 0, 0, 0.5])

# ECRANS
class LoginScreen(MDScreen): pass
class RegisterScreen(MDScreen): pass
class MainScreen(MDScreen): pass
class ProfileScreen(MDScreen): pass
class VideoCallScreen(MDScreen): pass
class AudioCallScreen(MDScreen): 
    avatar_source = StringProperty("assets/default_avatar.png")
    status_text = StringProperty("Appel en cours...")

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<CircularAvatar>:
    size_hint: None, None
    size: dp(56), dp(56)
    radius: [dp(28),]
    md_bg_color: get_color_from_hex("#262626")
    FitImage:
        source: root.source if root.source else "assets/default_avatar.png"
        radius: [dp(28),]
        size_hint: 1, 1
        pos_hint: {"center_x": .5, "center_y": .5}

<InstaTextField@MDTextField>:
    mode: "rectangle"
    fill_color_normal: get_color_from_hex("#262626") 
    fill_color_focus: get_color_from_hex("#262626")
    line_color_normal: get_color_from_hex("#333232")
    line_color_focus: get_color_from_hex("#A8A8A8") 
    text_color_normal: 1, 1, 1, 1
    hint_text_color_normal: get_color_from_hex("#A8A8A8")
    radius: [10,]

<AddFriendContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"
    InstaTextField:
        id: phone_input
        hint_text: "Numéro de téléphone"
        input_filter: "int"
        icon_right: "phone-plus"

<GroupCreateContent>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "200dp"
    InstaTextField:
        id: group_name
        hint_text: "Nom du groupe"
    InstaTextField:
        id: group_members
        hint_text: "Membres (pseudos)"
        helper_text: "Entrez les prénoms séparés par virgule"
        helper_text_mode: "persistent"

<AddFriendBanner>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(50)
    md_bg_color: get_color_from_hex("#FF9800")
    padding: dp(10)
    spacing: dp(10)
    MDLabel:
        text: "Cette personne n'est pas dans vos contacts"
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        font_size: "12sp"
        valign: "center"
    MDRaisedButton:
        text: "AJOUTER"
        md_bg_color: 1, 1, 1, 1
        text_color: 0, 0, 0, 1
        on_release: app.add_contact_direct(root.target_username)

<ChatBubble>:
    size_hint_y: None
    height: self.minimum_height
    size_hint_x: None
    width: dp(300) if root.msg_type == 'image' else (msg_label.texture_size[0] + dp(32))
    padding: [dp(16), dp(8), dp(16), dp(12)]
    spacing: dp(2)
    orientation: 'vertical'
    radius: [dp(22), dp(22), dp(4), dp(22)] if root.is_me else [dp(22), dp(22), dp(22), dp(4)]
    md_bg_color: get_color_from_hex("#2E2745") if root.is_me else get_color_from_hex("#262626")
    pos_hint: {'right': 1} if root.is_me else {'left': 1}
    
    MDLabel:
        text: root.sender if not root.is_me else ""
        font_size: "10sp"
        theme_text_color: "Custom"
        text_color: get_color_from_hex("#9D84FD")
        size_hint_y: None
        height: dp(12) if not root.is_me else 0
        opacity: 1 if not root.is_me else 0
        
    MDLabel:
        id: msg_label
        text: root.message
        theme_text_color: "Custom"
        text_color: (1, 1, 1, 1) if root.msg_type != 'call_log' else (1, 0.8, 0, 1)
        font_style: "Body1" if root.msg_type != 'call_log' else "Caption"
        italic: True if root.msg_type == 'call_log' else False
        font_size: "15sp"
        size_hint_y: None
        height: self.texture_size[1] if root.msg_type != 'image' else 0
        opacity: 1 if root.msg_type != 'image' else 0
        text_size: dp(280), None 
        valign: 'middle'
        halign: 'left'
        
    AsyncImage:
        id: message_image
        source: root.file_path if root.msg_type == 'image' else ""
        size_hint_y: None
        height: dp(200) if root.msg_type == 'image' else 0
        allow_stretch: True
        keep_ratio: True
        opacity: 1 if root.msg_type == 'image' else 0
        nocache: True

<UserListItem>:
    text: root.username
    secondary_text: root.last_msg
    on_release: app.load_conversation(root.username)
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    secondary_theme_text_color: "Custom"
    secondary_text_color: get_color_from_hex("#A8A8A8")
    md_bg_color: 0, 0, 0, 0
    ImageLeftWidget:
        source: app.default_avatar_path
        radius: [25, 25, 25, 25]
    
    MDLabel:
        text: str(root.unread_count) if root.unread_count > 0 else ""
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        md_bg_color: get_color_from_hex("#FF4444") if root.unread_count > 0 else (0,0,0,0)
        radius: [dp(10),]
        font_size: "11sp"
        bold: True
        halign: "center"
        valign: "center"
        size_hint: None, None
        size: dp(22), dp(22)
        pos_hint: {"center_y": .5, "right": 0.95}
        canvas.before:
            Color:
                rgba: self.md_bg_color
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(11),]

<LoginScreen>:
    md_bg_color: get_color_from_hex("#333232")
    MDBoxLayout:
        size_hint: None, None
        size: dp(350), dp(500)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        orientation: "vertical"
        spacing: dp(15)
        padding: dp(20)
        canvas.before:
            Color:
                rgba: get_color_from_hex("#262626")
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20,]
        FitImage:
            source: app.default_avatar_path
            size_hint: None, None
            size: dp(80), dp(80)
            radius: [40,]
            pos_hint: {"center_x": 0.5}
        MDLabel:
            text: "WhatsApp SAE"
            font_style: "H5"
            bold: True
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(50)
        InstaTextField:
            id: user
            hint_text: "Nom d'utilisateur"
        InstaTextField:
            id: password
            hint_text: "Mot de passe"
            password: True
        MDLabel:
            id: error_label
            text: ""
            theme_text_color: "Error"
            halign: "center"
            size_hint_y: None
            height: dp(30)
        MDFillRoundFlatButton:
            text: "Se connecter"
            font_size: "14sp"
            pos_hint: {"center_x": 0.5}
            size_hint_x: 1
            md_bg_color: get_color_from_hex("#2E2745")
            text_color: 1, 1, 1, 1
            on_release: app.login(user.text, password.text)
        MDFlatButton:
            text: "Pas de compte ? Inscrivez-vous"
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#9D84FD")
            pos_hint: {"center_x": 0.5}
            on_release: app.go_to_register()

<RegisterScreen>:
    md_bg_color: get_color_from_hex("#333232")
    MDBoxLayout:
        size_hint: None, None
        size: dp(350), dp(550)
        pos_hint: {"center_x": 0.5, "center_y": 0.5}
        orientation: "vertical"
        spacing: dp(15)
        padding: dp(20)
        canvas.before:
            Color:
                rgba: get_color_from_hex("#262626")
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20,]
        MDLabel:
            text: "Créer un compte"
            font_style: "H5"
            bold: True
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
        InstaTextField:
            id: reg_user
            hint_text: "Nom d'utilisateur"
        InstaTextField:
            id: reg_password
            hint_text: "Mot de passe"
            password: True
        MDLabel:
            id: reg_error_label
            text: ""
            theme_text_color: "Error"
            halign: "center"
            size_hint_y: None
            height: dp(30)
        MDFillRoundFlatButton:
            text: "S'inscrire"
            font_size: "14sp"
            pos_hint: {"center_x": 0.5}
            size_hint_x: 1
            md_bg_color: get_color_from_hex("#2E2745")
            on_release: app.register_action()
        MDFlatButton:
            text: "Retour à la connexion"
            theme_text_color: "Custom"
            text_color: get_color_from_hex("#A8A8A8")
            pos_hint: {"center_x": 0.5}
            on_release: app.go_to_login()

<MainScreen>:
    MDBoxLayout:
        orientation: "horizontal"
        md_bg_color: get_color_from_hex("#333232")
        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.3
            md_bg_color: get_color_from_hex("#262626")
            padding: 0
            spacing: 0
            MDBoxLayout:
                size_hint_y: None
                height: dp(70)
                padding: [dp(20), dp(10)]
                spacing: dp(15)
                CircularAvatar:
                    size: dp(40), dp(40)
                    radius: [dp(20),]
                    pos_hint: {"center_y": .5}
                    source: app.my_avatar_path
                    on_release: app.show_profile_screen()
                MDLabel:
                    text: app.username
                    font_style: "Subtitle1"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    valign: "center"
                MDIconButton:
                    icon: "plus-box-multiple-outline"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    pos_hint: {"center_y": .5}
                    on_release: app.open_menu_dialog()
            MDBoxLayout:
                size_hint_y: None
                height: dp(60)
                padding: [dp(20), dp(10)]
                MDBoxLayout:
                    radius: [dp(10),]
                    md_bg_color: get_color_from_hex("#333232")
                    padding: [dp(10), 0]
                    MDIcon:
                        icon: "magnify"
                        theme_text_color: "Custom"
                        text_color: get_color_from_hex("#A8A8A8")
                        pos_hint: {"center_y": .5}
                    TextInput:
                        id: search_field
                        hint_text: "Rechercher"
                        hint_text_color: get_color_from_hex("#A8A8A8")
                        foreground_color: 1, 1, 1, 1
                        background_color: 0, 0, 0, 0
                        cursor_color: 1, 1, 1, 1
                        font_size: "14sp"
                        multiline: False
                        pos_hint: {"center_y": .5}
                        on_text: app.filter_conversations(self.text)
            MDLabel:
                text: "Discussions"
                font_style: "Subtitle2"
                bold: True
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(40)
                padding_x: dp(24)
            MDScrollView:
                bar_width: 0
                MDList:
                    id: conversations_list
        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.7
            md_bg_color: get_color_from_hex("#333232")
            MDBoxLayout:
                id: chat_header_box
                size_hint_y: None
                height: self.minimum_height
                orientation: "vertical"
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    padding: [dp(20), 0]
                    spacing: dp(15)
                    canvas.after:
                        Color:
                            rgba: get_color_from_hex("#262626")
                        Line:
                            points: [self.x, self.y, self.right, self.y]
                            width: 1
                    CircularAvatar:
                        id: chat_target_avatar
                        size: dp(36), dp(36)
                        radius: [dp(18),]
                        pos_hint: {"center_y": .5}
                        source: app.default_avatar_path
                    MDLabel:
                        id: chat_title_label
                        text: "WhatsApp SAE"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        valign: "center"
                    MDIconButton:
                        icon: "phone-outline"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: app.try_call("audio")
                    MDIconButton:
                        icon: "video-outline"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: app.try_call("video")
                    MDIconButton:
                        icon: "information-outline"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        on_release: app.get_target_info()
            MDScrollView:
                id: chat_scroll
                MDBoxLayout:
                    id: chat_box
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [dp(20), dp(20)]
                    spacing: dp(8)
            MDBoxLayout:
                size_hint_y: None
                height: dp(80)
                padding: [dp(20), dp(20)]
                spacing: dp(10)
                md_bg_color: get_color_from_hex("#333232")
                MDBoxLayout:
                    size_hint: 1, None
                    height: dp(44)
                    radius: [dp(22),]
                    md_bg_color: get_color_from_hex("#262626")
                    padding: [dp(15), 0]
                    MDBoxLayout:
                        orientation: "horizontal"
                        MDIconButton:
                            icon: "paperclip"
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1
                            pos_hint: {"center_y": .5}
                            on_release: app.open_file_picker()
                        TextInput:
                            id: msg_input
                            hint_text: "Votre message..."
                            hint_text_color: get_color_from_hex("#A8A8A8")
                            background_color: 0,0,0,0
                            foreground_color: 1,1,1,1
                            cursor_color: 1,1,1,1
                            font_size: "15sp"
                            multiline: False
                            on_text_validate: app.send_message()
                            padding_y: [self.height / 2.0 - (self.line_height / 2.0) * len(self._lines), 0]
                        MDIconButton:
                            icon: "send"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#9D84FD")
                            pos_hint: {"center_y": .5}
                            on_release: app.send_message()

<GlowWidget>:
    canvas:
        Color:
            rgba: root.glow_color[0], root.glow_color[1], root.glow_color[2], 0.05
        Ellipse:
            pos: self.center_x - dp(100), self.center_y - dp(100)
            size: dp(200), dp(200)
        Color:
            rgba: root.glow_color[0], root.glow_color[1], root.glow_color[2], 0.1
        Ellipse:
            pos: self.center_x - dp(80), self.center_y - dp(80)
            size: dp(160), dp(160)
        Color:
            rgba: root.glow_color[0], root.glow_color[1], root.glow_color[2], 0.2
        Ellipse:
            pos: self.center_x - dp(60), self.center_y - dp(60)
            size: dp(120), dp(120)

<VideoCallScreen>:
    name: "video_call_screen"
    md_bg_color: 0, 0, 0, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        MDCard:
            size_hint: 1, 0.45
            radius: [25,]
            md_bg_color: 0.1, 0.1, 0.1, 1
            clip_to_radius: True
            MDFloatLayout:
                Image:
                    id: remote_video
                    source: app.default_avatar_path
                    allow_stretch: True
                    keep_ratio: False
                    size_hint: 1, 1
                    pos_hint: {"center_x": .5, "center_y": .5}
                MDCard:
                    size_hint: None, None
                    size: dp(100), dp(30)
                    radius: [15,]
                    md_bg_color: 0, 0, 0, 0.6
                    pos_hint: {"center_x": 0.5, "bottom": 0.05}
                    MDLabel:
                        text: app.call_manager.target_user if app.call_manager.target_user else "..."
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Caption"
                        bold: True
        MDCard:
            size_hint: 1, 0.45
            radius: [25,]
            md_bg_color: 0.15, 0.15, 0.15, 1
            clip_to_radius: True
            MDFloatLayout:
                Image:
                    id: local_video
                    allow_stretch: True
                    keep_ratio: False
                    size_hint: 1, 1
                    pos_hint: {"center_x": .5, "center_y": .5}
                    canvas.before:
                        PushMatrix
                        Scale:
                            x: -1
                            origin: self.center
                    canvas.after:
                        PopMatrix
                MDCard:
                    size_hint: None, None
                    size: dp(80), dp(30)
                    radius: [15,]
                    md_bg_color: 0, 0, 0, 0.6
                    pos_hint: {"center_x": 0.5, "bottom": 0.05}
                    MDLabel:
                        text: "Moi"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        font_style: "Caption"
                        bold: True
        MDBoxLayout:
            size_hint: 1, 0.1
            orientation: "horizontal"
            spacing: dp(30)
            alignment: "center"
            MDIconButton:
                icon: "camera"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 0.2, 0.2, 0.2, 1
                on_release: app.toggle_camera()
            MDIconButton:
                icon: "microphone"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 0.2, 0.2, 0.2, 1
                on_release: app.toggle_mic()
            MDIconButton:
                icon: "phone-hangup"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 1, 0.2, 0.2, 1
                on_release: app.action_hangup(None)

<AudioCallScreen>:
    name: "audio_call_screen"
    md_bg_color: get_color_from_hex("#161616")
    MDFloatLayout:
        GlowWidget:
            center: self.parent.center
            glow_color: [1, 0, 0, 0.6] if root.status_text == "Appel terminé" else [0.2, 0.6, 1, 0.6]
        CircularAvatar:
            size: dp(120), dp(120)
            radius: [dp(60),]
            pos_hint: {"center_x": .5, "center_y": .55}
            source: root.avatar_source
        MDLabel:
            text: app.call_manager.target_user if app.call_manager.target_user else "Unknown"
            halign: "center"
            pos_hint: {"center_x": .5, "center_y": .68}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H4"
            bold: True
        MDLabel:
            text: root.status_text
            halign: "center"
            pos_hint: {"center_x": .5, "center_y": .43}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H6"
            bold: True
        MDBoxLayout:
            orientation: "horizontal"
            size_hint: 0.9, None
            height: dp(100)
            pos_hint: {"center_x": 0.5, "bottom": 0.08}
            spacing: dp(40)
            alignment: "center"
            MDIconButton:
                icon: "microphone-off" if not app.call_manager.mic_active else "microphone"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 1, 1, 1, 0.2
                on_release: app.toggle_mic()
            MDIconButton:
                icon: "phone-hangup"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 1, 0.2, 0.2, 1
                on_release: app.action_hangup(None)
            MDIconButton:
                icon: "volume-high"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                md_bg_color: 1, 1, 1, 0.2

<ProfileScreen>:
    md_bg_color: get_color_from_hex("#333232")
    MDBoxLayout:
        orientation: "vertical"
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: dp(10)
            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.go_back_to_main()
            MDLabel:
                text: "Modifier profil"
                font_style: "H6"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                pos_hint: {"center_y": .5}
        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(30)
                spacing: dp(25)
                size_hint_y: None
                height: self.minimum_height
                alignment: "center_x"
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(160)
                    alignment: "center"
                    spacing: dp(15)
                    CircularAvatar:
                        size: dp(100), dp(100)
                        radius: [dp(50),]
                        pos_hint: {"center_x": .5}
                        source: app.my_avatar_path
                        on_release: app.open_file_manager()
                    MDLabel:
                        text: "Changer la photo de profil"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: get_color_from_hex("#9D84FD")
                        font_style: "Body1"
                InstaTextField:
                    id: profile_username
                    hint_text: "Pseudo"
                    text: app.username
                    disabled: True
                InstaTextField:
                    id: profile_infos
                    hint_text: "Bio"
                    multiline: True
                InstaTextField:
                    id: profile_phone
                    hint_text: "Téléphone"
                    input_filter: "int"
                MDFillRoundFlatButton:
                    text: "Enregistrer"
                    font_size: "14sp"
                    size_hint_x: 1
                    height: dp(50)
                    md_bg_color: get_color_from_hex("#2E2745")
                    on_release: app.save_profile()
'''

class WhatsAppClientApp(MDApp):
    dialog = None 
    call_dialog = None
    active_call_dialog = None
    username = StringProperty("")
    
    default_avatar_path = resource_path(os.path.join("assets", "default_avatar.png"))
    my_avatar_path = StringProperty(default_avatar_path)
    has_heart_asset = BooleanProperty(False)
    
    my_friends = ListProperty([])
    asking_for_chat_ui = BooleanProperty(False)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        Window.size = (1100, 750)
        
        self.sock = None
        self.is_connected = False
        self.current_target = None
        self.conversations_data = [] 
        self.unread_counts = {}
        self.asking_for_chat_ui = False

        if os.path.exists(resource_path(os.path.join("assets", "heart.png"))):
            self.has_heart_asset = True

        self.call_manager = CallManager(self, SERVER_IP, UDP_PORT)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.file_mode = "profile"

        Builder.load_string(KV)
        self.sm = MDScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(RegisterScreen(name="register"))
        self.sm.add_widget(MainScreen(name="chat_interface"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(VideoCallScreen(name="video_call_screen")) 
        self.sm.add_widget(AudioCallScreen(name="audio_call_screen"))
        return self.sm

    # --- GESTION DU CACHE ET TÉLÉCHARGEMENT ---
    def get_cache_path(self, filename):
        # Utiliser un chemin absolu dans APPDATA pour éviter les erreurs de permissions
        # et s'assurer que c'est le même pour le .exe et le .py
        cache_dir = os.path.join(os.environ.get("APPDATA", "."), "WhatsAppSAE_Cache")
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir)
            except OSError: pass
        return os.path.abspath(os.path.join(cache_dir, filename))

    def download_image_if_needed(self, filename, is_avatar=False):
        if not filename or filename == "default_avatar":
            return self.default_avatar_path
            
        local_path = self.get_cache_path(filename)
        
        if os.path.exists(local_path):
            return local_path 
        else:
            print(f"Demande de téléchargement pour : {filename}")
            self.send_json({"type": "DOWNLOAD_IMAGE", "filename": filename})
            return self.default_avatar_path 

    # ... [Le reste des méthodes call, UI, etc. est identique à v2.2] ...
    # Je ne remets que la partie critique handle_response pour économiser l'espace
    # Copie les méthodes : try_call, show_calling_dialog, show_incoming_call_dialog, 
    # action_accept_call, action_decline_call, action_hangup, go_back_to_main, 
    # retry_call, update_local_video, update_remote_video, toggle_camera, toggle_mic,
    # open_menu_dialog, open_add_friend_dialog, add_friend_action, add_contact_direct,
    # start_new_chat_flow, show_users_dialog, select_user_for_chat, open_group_create,
    # create_group, get_target_info, show_target_info_dialog...
    # Elles sont strictement identiques au code précédent.

    # ... [Méthodes identiques ici] ...
    # Pour que tu aies un fichier COMPLET, je te recolle TOUT pour éviter les erreurs de copier-coller.
    
    def try_call(self, media_type):
        if self.current_target:
            self.call_manager.request_call(self.current_target, with_video=(media_type=="video"))

    def show_calling_dialog(self, target):
        self.active_call_dialog = MDDialog(
            title=f"Appel vers {target}...",
            text="En attente de réponse...",
            buttons=[
                MDFillRoundFlatButton(text="RACCROCHER", md_bg_color=(1, 0, 0, 1), on_release=lambda x: self.action_hangup(target))
            ],
            auto_dismiss=False
        )
        self.active_call_dialog.open()

    def show_incoming_call_dialog(self, sender, media_type):
        self.call_dialog = MDDialog(
            title="Appel entrant",
            text=f"{sender} vous appelle en {media_type}...",
            buttons=[
                MDFlatButton(text="REFUSER", theme_text_color="Error", on_release=lambda x: self.action_decline_call(sender)),
                MDFillRoundFlatButton(text="ACCEPTER", md_bg_color=(0, 0.8, 0, 1), on_release=lambda x: self.action_accept_call(sender, media_type))
            ],
            auto_dismiss=False
        )
        self.call_dialog.open()

    def action_accept_call(self, sender, media_type):
        if self.call_dialog: self.call_dialog.dismiss()
        self.send_json({"type": "CALL_RESPONSE", "target": sender, "response": "accept"})
        if media_type == "video":
            self.sm.current = "video_call_screen"
        else:
            self.sm.current = "audio_call_screen"
        self.call_manager.start_call(sender, with_video=(media_type == "video"))

    def action_decline_call(self, sender):
        if self.call_dialog: self.call_dialog.dismiss()
        self.send_json({"type": "CALL_RESPONSE", "target": sender, "response": "decline"})

    def action_hangup(self, target=None):
        tgt = target if target else self.call_manager.target_user
        if self.active_call_dialog: self.active_call_dialog.dismiss()
        self.call_manager.stop_call()
        if tgt:
            self.send_json({"type": "END_CALL", "target": tgt})
            self.send_message_log(tgt, "📞 Appel terminé", "call_log")
            
        toast("Appel terminé")
        if self.sm.current == "video_call_screen":
             self.sm.current = "audio_call_screen"
        screen = self.sm.get_screen('audio_call_screen')
        screen.status_text = "Appel terminé"
        Clock.schedule_once(lambda dt: self.go_back_to_main(), 2)

    def go_back_to_main(self):
        self.sm.current = "chat_interface"

    def retry_call(self):
        target = self.call_manager.target_user
        if target:
            self.sm.current = "chat_interface"
            self.try_call("video")

    def update_local_video(self, frame):
        try:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.sm.get_screen('video_call_screen').ids.local_video.texture = texture
        except: pass

    def update_remote_video(self, frame):
        try:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.sm.get_screen('video_call_screen').ids.remote_video.texture = texture
        except: pass

    def toggle_camera(self):
        self.call_manager.cam_active = not self.call_manager.cam_active
        toast(f"Caméra {'activée' if self.call_manager.cam_active else 'désactivée'}")

    def toggle_mic(self):
        self.call_manager.mic_active = not self.call_manager.mic_active
        toast(f"Micro {'activé' if self.call_manager.mic_active else 'désactivé'}")

    def open_menu_dialog(self):
        self.dialog = MDDialog(
            title="Menu",
            type="simple",
            items=[
                OneLineAvatarIconListItem(text="Ajouter un ami", on_release=lambda x: self.open_add_friend_dialog()),
                OneLineAvatarIconListItem(text="Nouvelle discussion", on_release=lambda x: self.start_new_chat_flow()),
                OneLineAvatarIconListItem(text="Créer un groupe", on_release=lambda x: self.open_group_create())
            ],
        )
        self.dialog.open()

    def open_add_friend_dialog(self):
        if self.dialog: self.dialog.dismiss()
        content = AddFriendContent()
        self.dialog = MDDialog(
            title="Ajouter un ami",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog.dismiss()),
                MDFillRoundFlatButton(text="AJOUTER", on_release=lambda x: self.add_friend_action(content.ids.phone_input.text))
            ]
        )
        self.dialog.open()

    def add_friend_action(self, phone):
        if not phone: return
        self.send_json({"type": "ADD_FRIEND", "phone": phone})
        if self.dialog: self.dialog.dismiss()

    def add_contact_direct(self, target_username):
        self.send_json({"type": "ADD_FRIEND_DIRECT", "target_username": target_username})

    def start_new_chat_flow(self):
        if self.dialog: self.dialog.dismiss()
        self.asking_for_chat_ui = True
        self.send_json({"type": "GET_FRIENDS"})

    def show_users_dialog(self, users_list):
        if not users_list:
            toast("Aucun ami trouvé. Ajoutez-en d'abord !")
            return

        items = []
        for user in users_list:
            items.append(
                OneLineAvatarIconListItem(
                    text=user,
                    on_release=lambda x, u=user: self.select_user_for_chat(u)
                )
            )

        self.dialog = MDDialog(
            title="Mes Amis",
            type="simple",
            items=items,
            buttons=[MDFlatButton(text="FERMER", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def select_user_for_chat(self, user):
        if self.dialog: self.dialog.dismiss()
        found = False
        for c in self.conversations_data:
            if c['username'] == user: found = True
        
        if not found:
            self.conversations_data.insert(0, {'username': user, 'last_msg': 'Nouvelle discussion', 'unread_count': 0, 'timestamp': ''})
            
        self.load_conversation(user)
        self.refresh_sidebar()

    def open_group_create(self):
        if self.dialog: self.dialog.dismiss()
        content = GroupCreateContent()
        self.dialog = MDDialog(
            title="Créer un groupe",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="ANNULER", on_release=lambda x: self.dialog.dismiss()),
                MDFillRoundFlatButton(text="CRÉER", on_release=lambda x: self.create_group(content))
            ]
        )
        self.dialog.open()

    def create_group(self, content):
        name = content.ids.group_name.text
        members_str = content.ids.group_members.text
        if not name or not members_str: return
        members = [m.strip() for m in members_str.split(',') if m.strip()]
        if len(members) > 50:
            toast("Erreur: Max 50 membres")
            return
        self.send_json({"type": "CREATE_GROUP", "name": name, "members": members})
        if self.dialog: self.dialog.dismiss()

    def get_target_info(self):
        if self.current_target:
            self.send_json({"type": "GET_TARGET_INFO", "target": self.current_target})

    def show_target_info_dialog(self, data):
        info_text = f"Bio: {data.get('infos', '')}\nTél: {data.get('phone_number', '')}"
        self.dialog = MDDialog(
            title=f"Infos de {data.get('username')}",
            text=info_text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    # --- HANDLE RESPONSE (AVEC LE FIX CACHE) ---
    def handle_response(self, resp):
        t = resp.get("type")

        if t == "INCOMING_CALL":
            self.show_incoming_call_dialog(resp.get("sender"), resp.get("media"))

        elif t == "CALL_RESPONSE_REPLY":
            response = resp.get("response")
            responder = resp.get("responder")
            if response == "accept":
                if self.active_call_dialog: self.active_call_dialog.dismiss()
                if self.call_manager.is_video_call:
                    self.sm.current = "video_call_screen"
                else:
                    self.sm.current = "audio_call_screen"
                self.call_manager.start_call(responder, with_video=self.call_manager.is_video_call)
            else:
                if self.active_call_dialog: self.active_call_dialog.dismiss()
                toast("Appel refusé.")
                self.call_manager.stop_call()

        elif t == "CALL_ENDED":
            sender = resp.get("sender")
            self.call_manager.stop_call()
            if self.active_call_dialog: self.active_call_dialog.dismiss()
            if self.call_dialog: self.call_dialog.dismiss()
            self.sm.current = "audio_call_screen"
            screen = self.sm.get_screen('audio_call_screen')
            screen.status_text = "Appel terminé"
            Clock.schedule_once(lambda dt: self.go_back_to_main(), 2)

        # --- LE GROS FIX EST ICI ---
        elif t == "IMAGE_DOWNLOAD_REPLY":
            if resp.get("success"):
                filename = resp.get("filename")
                img_data = resp.get("data")
                save_path = self.get_cache_path(filename)
                
                try:
                    # 1. Ecriture sécurisée
                    with open(save_path, "wb") as f:
                        f.write(base64.b64decode(img_data))
                    
                    # 2. NETTOYAGE DU CACHE KIVY (CRUCIAL)
                    # On force Kivy à oublier l'ancienne version de cette image
                    Cache.remove('kv.image', save_path)
                    Cache.remove('kv.texture', save_path)

                    # 3. Mise à jour de l'interface
                    if filename in self.my_avatar_path:
                        self.my_avatar_path = save_path
                    
                    if self.current_target:
                        print(f"Image reçue et cache vidé pour {filename}. Refresh...")
                        # Un petit délai pour être sûr que le fichier est clos
                        Clock.schedule_once(lambda dt: self.load_conversation(self.current_target), 0.5)
                    
                except Exception as e:
                    print(f"Erreur sauvegarde image: {e}")

        elif t == "LOGIN_REPLY":
            if resp.get("success"):
                self.sm.transition.direction = "left"
                self.sm.current = "chat_interface"
                self.send_json({"type": "GET_CONVERSATIONS"})
                self.send_json({"type": "GET_FRIENDS"}) 
                self.send_json({"type": "GET_PROFILE"})
            else:
                self.sm.get_screen('login').ids.error_label.text = "Identifiants invalides"

        elif t == "REGISTER_REPLY":
            if resp.get("success"):
                self.show_alert_dialog("Félicitations", "Vous vous êtes bien inscrit !")
                self.go_to_login()
            else:
                toast("Ce pseudo est déjà pris")
                screen = self.sm.get_screen('register')
                screen.ids.reg_error_label.text = "Pseudo indisponible"

        elif t == "ADD_FRIEND_REPLY":
            if resp.get("success"):
                friend_name = resp.get("message")
                if friend_name == self.current_target:
                    self.my_friends.append(friend_name)
                    self.load_conversation(self.current_target)
                toast(f"{friend_name} est maintenant votre ami !")
            else:
                toast(f"Erreur: {resp.get('message')}")

        elif t == "FRIENDS_LIST":
            self.my_friends = resp.get("data", [])
            if self.asking_for_chat_ui:
                self.show_users_dialog(self.my_friends)
                self.asking_for_chat_ui = False

        elif t == "PROFILE_DATA":
            data = resp.get("data", {})
            if data.get("username") == self.username:
                screen = self.sm.get_screen('profile')
                screen.ids.profile_infos.text = data.get("infos", "")
                screen.ids.profile_phone.text = data.get("phone_number", "")
                server_filename = data.get("profile_pic_path", "")
                if server_filename and server_filename != "default_avatar":
                        self.my_avatar_path = self.download_image_if_needed(server_filename, is_avatar=True)
                else:
                        self.my_avatar_path = self.default_avatar_path
            elif data.get("username") == self.current_target:
                 server_filename = data.get("profile_pic_path", "")
                 header_avatar = self.sm.get_screen('chat_interface').ids.chat_target_avatar
                 if server_filename and server_filename != "default_avatar":
                     header_avatar.source = self.download_image_if_needed(server_filename, is_avatar=True)
                 else:
                     header_avatar.source = self.default_avatar_path
            else:
                 self.show_target_info_dialog(data)

        elif t == "CONVERSATIONS_LIST":
            self.conversations_data = resp.get("data", [])
            self.refresh_sidebar()

        elif t == "NEW_MESSAGE":
            sender = resp.get("sender")
            content = resp.get("content")
            m_type = resp.get("msg_type", "text")
            f_path = resp.get("file_path")
            
            full_path = ""
            if f_path:
                full_path = self.download_image_if_needed(f_path, is_avatar=False)

            if sender == self.current_target or (resp.get("is_group") and resp.get("group_name") == self.current_target):
                self.add_message_bubble(sender, content, False, m_type, full_path)
            else:
                target = resp.get("group_name") if resp.get("is_group") else sender
                found = False
                for c in self.conversations_data:
                    if c['username'] == target:
                        c['last_msg'] = content if m_type == 'text' else m_type
                        c['unread_count'] += 1
                        found = True
                        break
                if not found:
                    self.conversations_data.insert(0, {'username': target, 'last_msg': content, 'unread_count': 1, 'timestamp': ''})
                self.refresh_sidebar()
                toast(f"Message de {sender}")
                
        # --- AJOUTE CE BLOC DANS handle_response ---
        elif t == "NEW_GROUP_NOTIFICATION":
            grp_name = resp.get("name")
            creator = resp.get("creator")
            
            # Vérifier si on a déjà ce groupe dans la liste pour éviter les doublons
            found = False
            for c in self.conversations_data:
                if c['username'] == grp_name:
                    found = True
                    break
            
            if not found:
                # On ajoute le groupe en haut de la liste
                self.conversations_data.insert(0, {
                    'username': grp_name, 
                    'last_msg': f"Groupe créé par {creator}", 
                    'unread_count': 1, 
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.refresh_sidebar()
                toast(f"Vous avez été ajouté au groupe : {grp_name}")

        elif t == "HISTORY_REPLY":
            if resp.get("target") == self.current_target:
                chat_box = self.sm.get_screen('chat_interface').ids.chat_box
                chat_box.clear_widgets()
                for msg in resp.get("data", []):
                    full_path = ""
                    if msg.get("file_path"):
                        full_path = self.download_image_if_needed(msg.get("file_path"), is_avatar=False)
                        
                    self.add_message_bubble(msg["sender"], msg["content"], msg["sender"] == self.username, msg.get("type", "text"), full_path)

        elif t == "TARGET_INFO_REPLY":
            pass

        elif t == "GROUP_CREATED":
            grp = resp.get("name")
            self.conversations_data.insert(0, {'username': grp, 'last_msg': 'Groupe créé', 'unread_count': 0, 'timestamp': ''})
            self.load_conversation(grp)
            self.refresh_sidebar()

    def connect_socket(self):
        if not self.is_connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((SERVER_IP, SERVER_PORT))
                self.is_connected = True
                threading.Thread(target=self.receive_loop, daemon=True).start()
                return True
            except:
                toast("Impossible de joindre le serveur")
                return False
        return True

    def send_json(self, data):
        if self.sock:
            try: self.sock.send(json.dumps(data).encode('utf-8'))
            except: pass

    def receive_loop(self):
        while self.is_connected:
            try:
                data = self.sock.recv(1024 * 1024 * 5).decode('utf-8')
                if not data: break
                try:
                    msg = json.loads(data)
                    Clock.schedule_once(lambda dt: self.handle_response(msg))
                except json.JSONDecodeError: pass
            except: break
        self.is_connected = False

    def refresh_sidebar(self, filter_text=""):
        conversations_list = self.sm.get_screen('chat_interface').ids.conversations_list
        conversations_list.clear_widgets()
        for item_data in self.conversations_data:
            user = item_data['username']
            l_msg = item_data['last_msg']
            count = item_data['unread_count']
            if filter_text.lower() in user.lower():
                item = UserListItem(username=user, last_msg=str(l_msg), unread_count=count)
                conversations_list.add_widget(item)

    def filter_conversations(self, text):
        self.refresh_sidebar(text)

    def load_conversation(self, target_user):
        self.current_target = target_user
        screen = self.sm.get_screen('chat_interface')
        screen.ids.chat_title_label.text = target_user
        screen.ids.chat_box.clear_widgets()
        
        self.send_json({"type": "GET_TARGET_INFO", "target": target_user})
        
        header_box = screen.ids.chat_header_box
        for child in header_box.children[:]:
            if isinstance(child, AddFriendBanner):
                header_box.remove_widget(child)
        
        is_friend = target_user in self.my_friends
        if not is_friend:
             banner = AddFriendBanner(target_username=target_user)
             header_box.add_widget(banner, index=len(header_box.children)) 

        for c in self.conversations_data:
            if c['username'] == target_user:
                c['unread_count'] = 0
        self.refresh_sidebar()
        self.send_json({"type": "HISTORY", "target": target_user})

    def send_message(self):
        screen = self.sm.get_screen('chat_interface')
        txt_field = screen.ids.msg_input
        msg = txt_field.text.strip()
        if msg and self.current_target:
            self.add_message_bubble(self.username, msg, True, "text")
            self.send_json({"type": "MESSAGE", "receiver": self.current_target, "content": msg, "msg_type": "text"})
            txt_field.text = ""
            found = False
            for c in self.conversations_data:
                if c['username'] == self.current_target:
                    c['last_msg'] = msg
                    found = True
                    self.conversations_data.remove(c)
                    self.conversations_data.insert(0, c)
                    break
            if not found:
                 self.conversations_data.insert(0, {'username': self.current_target, 'last_msg': msg, 'unread_count': 0, 'timestamp': ''})
            self.refresh_sidebar()

    def send_message_log(self, target, content, m_type):
        self.add_message_bubble(self.username, content, True, m_type)
        self.send_json({"type": "MESSAGE", "receiver": target, "content": content, "msg_type": m_type})

    def add_message_bubble(self, sender, message, is_me, msg_type="text", file_path=""):
        chat_box = self.sm.get_screen('chat_interface').ids.chat_box
        bubble = ChatBubble(sender=sender, message=message, is_me=is_me, msg_type=msg_type, file_path=file_path)
        chat_box.add_widget(bubble)
        scroll_view = self.sm.get_screen('chat_interface').ids.chat_scroll
        Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0), 0.1)

    def go_to_register(self): self.sm.transition.direction = "left"; self.sm.current = "register"
    def go_to_login(self): self.sm.transition.direction = "right"; self.sm.current = "login"
    def show_profile_screen(self): self.sm.transition.direction = "right"; self.sm.current = "profile"; self.send_json({"type": "GET_PROFILE"})
    def go_back_to_main(self): self.sm.transition.direction = "left"; self.sm.current = "chat_interface"
    def show_alert_dialog(self, title, text): self.dialog = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]); self.dialog.open()
    
    def register_action(self):
        screen = self.sm.get_screen('register')
        user_text = screen.ids.reg_user.text.strip()
        pass_text = screen.ids.reg_password.text.strip()
        if not user_text or not pass_text:
            screen.ids.reg_error_label.text = "Veuillez remplir tous les champs !"
            toast("Champs vides")
            return
        if self.connect_socket():
            self.send_json({"type": "REGISTER", "username": user_text, "password": pass_text})
        else:
            screen.ids.reg_error_label.text = "Serveur inaccessible"
            toast("Erreur serveur")
    
    def login(self, user, pwd):
        if not user: return
        if self.connect_socket(): self.username = user; self.call_manager.register_udp(user); self.send_json({"type": "LOGIN", "username": user, "password": pwd})
    
    def save_profile(self):
        screen = self.sm.get_screen('profile')
        self.send_json({"type": "UPDATE_PROFILE", "infos": screen.ids.profile_infos.text, "phone": screen.ids.profile_phone.text})
    
    def open_file_picker(self):
        self.file_mode = "send"
        self.file_manager.show(os.path.expanduser("~"))

    def open_file_manager(self): 
        self.file_mode = "profile"
        self.file_manager.show(os.path.expanduser("~"))

    def select_path(self, path):
        self.exit_file_manager()
        if self.file_mode == "profile":
            if not path.lower().endswith(('.png', '.jpg', '.jpeg')): return
            self.upload_profile_pic(path)
        elif self.file_mode == "send":
            self.send_file(path)

    def exit_file_manager(self, *args): self.file_manager.close()

    def upload_profile_pic(self, path):
        try:
            with open(path, "rb") as f: self.send_json({"type": "UPDATE_PROFILE_PIC", "image_data": base64.b64encode(f.read()).decode('utf-8'), "extension": path.split('.')[-1]})
        except: pass

    def send_file(self, path):
        if not self.current_target: return
        try:
            ext = path.split('.')[-1].lower()
            msg_type = "image" if ext in ['png', 'jpg', 'jpeg', 'gif'] else "file"
            
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode('utf-8')
                
            self.send_json({
                "type": "MESSAGE", 
                "receiver": self.current_target, 
                "content": f"Fichier: {os.path.basename(path)}",
                "msg_type": msg_type,
                "file_data": data,
                "file_ext": ext
            })
            self.add_message_bubble(self.username, os.path.basename(path), True, msg_type, path)
            for c in self.conversations_data:
                if c['username'] == self.current_target:
                    c['last_msg'] = f"Fichier: {os.path.basename(path)}"
            self.refresh_sidebar()
            
        except Exception as e:
            toast(f"Erreur envoi fichier: {e}")

if __name__ == "__main__":
    WhatsAppClientApp().run()
