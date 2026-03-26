import random
import hashlib
import sqlite3
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.core.window import Window

Window.clearcolor = (0.01, 0.01, 0.03, 1)

class SignatureLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Developed by Yeanur"
        self.font_size = '12sp'
        self.color = (0.5, 0.5, 0.5, 1)
        self.size_hint_y = None
        self.height = '30dp'

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0.3, 0.6, 1)
        self.bold = True
        self.size_hint_y = None
        self.height = '50dp'

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=50, spacing=20)
        l.add_widget(Label(text="YI PRIVATE BANK", font_size='32sp', bold=True, color=(0,0.9,1,1)))
        for t, s in [("LOGIN", 'login'), ("CREATE ACCOUNT", 'terms'), ("ADMIN CONSOLE", 'admin_login')]:
            b = StyledButton(text=t)
            if t == "ADMIN CONSOLE": b.background_color = (0.6, 0.1, 0.1, 1)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=40, spacing=15)
        l.add_widget(Label(text="USER LOGIN", font_size='24sp'))
        self.uid = TextInput(hint_text="User ID", multiline=False, size_hint_y=None, height='45dp')
        self.pwd = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        l.add_widget(self.uid); l.add_widget(self.pwd)
        b = StyledButton(text="LOGIN"); b.bind(on_press=self.verify); l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)

    def verify(self, x):
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        hp = hashlib.sha256(self.pwd.text.encode()).hexdigest()
        c.execute("SELECT uid, status FROM users WHERE uid=? AND password=?", (self.uid.text, hp))
        res = c.fetchone()
        conn.close()
        if res:
            if res[1] == 'Seized':
                popup = Popup(title='Account Frozen', content=Label(text='Your account is seized by Admin!'), size_hint=(0.8, 0.4))
                popup.open()
            else:
                app.current_uid = res[0]
                self.manager.current = 'dashboard'

class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=40, spacing=15)
        l.add_widget(Label(text="ADMIN ACCESS", color=(1,0,0,1), font_size='24sp'))
        self.aid = TextInput(hint_text="Admin ID", multiline=False, size_hint_y=None, height='45dp')
        self.apw = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        l.add_widget(self.aid); l.add_widget(self.apw)
        b = StyledButton(text="AUTHORIZE", background_color=(0.7,0,0,1))
        b.bind(on_press=self.check); l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)
    def check(self, x):
        if self.aid.text == "admin" and self.apw.text == "yeanur123":
            self.manager.current = 'admin_dash'

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text="LEGAL TERMS & DISCLAIMER", font_size='20sp', bold=True, color=(1,0.8,0,1)))
        
        terms_text = (
            "1. TEST APPLICATION: This is a simulation/test app for educational purposes.\n"
            "2. NO REAL MONEY: No real currency is involved. All balances are virtual.\n"
            "3. DATA PRIVACY: Your data is stored locally using SHA-256 encryption.\n"
            "4. ADMIN POWER: Admin reserves the right to seize or freeze accounts for testing.\n"
            "5. NO LIABILITY: Developer 'Yeanur' is not responsible for any data loss.\n"
            "6. AGREEMENT: By clicking 'Accept', you agree this is NOT a real bank."
        )
        
        scroll = ScrollView(size_hint=(1, 0.6))
        self.content = Label(text=terms_text, size_hint_y=None, text_size=(Window.width-40, None), halign='left', valign='top')
        self.content.bind(texture_size=self.content.setter('size'))
        scroll.add_widget(self.content)
        l.add_widget(scroll)

        cb_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        self.cb = CheckBox(size_hint_x=None, width='40dp')
        cb_layout.add_widget(self.cb)
        cb_layout.add_widget(Label(text="I agree to the test terms", halign='left'))
        l.add_widget(cb_layout)

        b = StyledButton(text="PROCEED"); b.bind(on_press=self.go); l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)

    def go(self, x):
        if self.cb.active: self.manager.current = 'register'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text="CREATE VIRTUAL ACCOUNT", font_size='20sp'))
        self.n = TextInput(hint_text="Full Name", multiline=False); self.m = TextInput(hint_text="Mobile", multiline=False)
        self.p = TextInput(hint_text="Security Password", password=True, multiline=False)
        l.add_widget(self.n); l.add_widget(self.m); l.add_widget(self.p)
        b = StyledButton(text="CONFIRM REGISTER"); b.bind(on_press=self.save); l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)
    def save(self, x):
        app = App.get_running_app()
        uid = str(random.randint(1000, 9999))
        hp = hashlib.sha256(self.p.text.encode()).hexdigest()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", (uid,self.n.text,self.m.text,hp,"YIB"+uid,5000.0,0.0,'Active',0.0,0,0))
        conn.commit(); conn.close()
        app.current_uid = uid
        self.manager.current = 'dashboard'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("SELECT name, balance, status FROM users WHERE uid=?", (app.current_uid,))
        u = c.fetchone()
        conn.close()
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"VIRTUAL WALLET\nUser: {u[0]}\nStatus: {u[2]}", font_size='18sp', halign='center'))
        l.add_widget(Label(text=f"{u[1]:.2f} YC", font_size='40sp', bold=True, color=(0,1,0,1)))
        for t, s in [("WITHDRAW", 'withdraw'), ("LOGOUT", 'start')]:
            b = StyledButton(text=t); b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc)); l.add_widget(b)
        l.add_widget(SignatureLabel())
        self.add_widget(l)

class AdminDashboard(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text="ADMIN CONTROL PANEL", font_size='22sp', color=(1,0,0,1)))
        
        self.target_uid = TextInput(hint_text="Enter User ID to Manage", multiline=False, size_hint_y=None, height='45dp')
        l.add_widget(self.target_uid)

        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height='50dp')
        b1 = Button(text="SEIZE", background_color=(1,0,0,1)); b1.bind(on_press=self.seize)
        b2 = Button(text="ACTIVATE", background_color=(0,1,0,1)); b2.bind(on_press=self.activate)
        btn_layout.add_widget(b1); btn_layout.add_widget(b2)
        l.add_widget(btn_layout)

        b3 = StyledButton(text="EXIT ADMIN"); b3.bind(on_press=lambda x: setattr(self.manager, 'current', 'start'))
        l.add_widget(b3)
        l.add_widget(SignatureLabel())
        self.add_widget(l)

    def seize(self, x):
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("UPDATE users SET status='Seized', balance=0.0 WHERE uid=?", (self.target_uid.text,))
        conn.commit(); conn.close()

    def activate(self, x):
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("UPDATE users SET status='Active' WHERE uid=?", (self.target_uid.text,))
        conn.commit(); conn.close()

class YIBankApp(App):
    current_uid = ""
    db_path = ""
    def build(self):
        self.db_path = os.path.join(self.user_data_dir, 'yibank.db')
        self.init_db()
        sm = ScreenManager()
        screens = [StartScreen(name='start'), LoginScreen(name='login'), AdminLoginScreen(name='admin_login'),
                   TermsScreen(name='terms'), RegistrationScreen(name='register'), DashboardScreen(name='dashboard'),
                   AdminDashboard(name='admin_dash'), Screen(name='withdraw')]
        for s in screens: sm.add_widget(s)
        return sm

    def init_db(self):
        conn = sqlite3.connect(self.db_path); c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, 
                      balance REAL, loan REAL, status TEXT, total_debit REAL, is_verified INTEGER, is_approved INTEGER)''')
        conn.commit(); conn.close()

if __name__ == '__main__':
    YIBankApp().run()
    
