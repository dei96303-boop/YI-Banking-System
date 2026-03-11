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
from kivy.core.window import Window

Window.clearcolor = (0.01, 0.01, 0.03, 1)

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
        self.add_widget(l)

    def verify(self, x):
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path)
        c = conn.cursor()
        hp = hashlib.sha256(self.pwd.text.encode()).hexdigest()
        c.execute("SELECT uid FROM users WHERE uid=? AND password=?", (self.uid.text, hp))
        res = c.fetchone()
        conn.close()
        if res:
            app.current_uid = res[0]
            self.manager.current = 'dashboard'

class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=40, spacing=15)
        l.add_widget(Label(text="ADMIN LOGIN", color=(1,0,0,1)))
        self.aid = TextInput(hint_text="Admin ID"); self.apw = TextInput(hint_text="Password", password=True)
        l.add_widget(self.aid); l.add_widget(self.apw)
        b = StyledButton(text="VERIFY"); b.bind(on_press=self.check); l.add_widget(b)
        self.add_widget(l)
    def check(self, x):
        if self.aid.text == "uitdei" and self.apw.text == "uit123":
            self.manager.current = 'admin_dash'

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=20)
        l.add_widget(Label(text="TERMS & CONDITIONS", font_size='22sp'))
        scroll = ScrollView()
        scroll.add_widget(Label(text="1. SHA-256 Security\n2. 50K Face ID Limit\n3. 10% Interest", size_hint_y=None, height='200dp'))
        l.add_widget(scroll)
        self.cb = CheckBox(size_hint_y=None, height='40dp')
        l.add_widget(self.cb)
        b = StyledButton(text="ACCEPT"); b.bind(on_press=self.go); l.add_widget(b)
        self.add_widget(l)
    def go(self, x):
        if self.cb.active: self.manager.current = 'register'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.n = TextInput(hint_text="Name"); self.m = TextInput(hint_text="Mobile"); self.p = TextInput(hint_text="Password", password=True)
        l.add_widget(self.n); l.add_widget(self.m); l.add_widget(self.p)
        b = StyledButton(text="REGISTER"); b.bind(on_press=self.save); l.add_widget(b)
        self.add_widget(l)
    def save(self, x):
        app = App.get_running_app()
        uid = str(random.randint(1000, 9999))
        hp = hashlib.sha256(self.p.text.encode()).hexdigest()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", (uid,self.n.text,self.m.text,hp,"YIB"+uid,1000.0,0.0,'Active',0.0,0,0))
        conn.commit(); conn.close()
        app.current_uid = uid
        self.manager.current = 'dashboard'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("SELECT name, balance, loan FROM users WHERE uid=?", (app.current_uid,))
        u = c.fetchone()
        conn.close()
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"Welcome {u[0]}\nBal: {u[1]:.2f} RS", font_size='22sp'))
        for t, s in [("WITHDRAW", 'withdraw'), ("LOGOUT", 'start')]:
            b = StyledButton(text=t); b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc)); l.add_widget(b)
        self.add_widget(l)

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=30)
        self.amt = TextInput(hint_text="Amount", input_filter='int')
        l.add_widget(self.amt)
        b = StyledButton(text="SEND"); b.bind(on_press=self.pay); l.add_widget(b)
        self.add_widget(l)
    def pay(self, x):
        app = App.get_running_app()
        val = float(self.amt.text) if self.amt.text else 0
        conn = sqlite3.connect(app.db_path); c = conn.cursor()
        c.execute("UPDATE users SET balance=balance-? WHERE uid=?", (val, app.current_uid))
        conn.commit(); conn.close()
        self.manager.current = 'dashboard'

class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Admin Dashboard Coming Soon"))

class YIBankApp(App):
    current_uid = ""
    db_path = ""

    def build(self):
        # অ্যান্ড্রয়েডের জন্য সঠিক পাথ সেট করা
        self.db_path = os.path.join(self.user_data_dir, 'yibank.db')
        self.init_db()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AdminLoginScreen(name='admin_login'))
        sm.add_widget(TermsScreen(name='terms'))
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(AdminDashboard(name='admin_dash'))
        return sm

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, 
                      balance REAL, loan REAL, status TEXT, total_debit REAL, is_verified INTEGER, is_approved INTEGER)''')
        conn.commit(); conn.close()

if __name__ == '__main__':
    YIBankApp().run()
    
