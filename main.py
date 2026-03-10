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

def get_db_path():
    from android.storage import app_storage_path
    return os.path.join(app_storage_path(), 'yibank.db')

def encrypt_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    try:
        db_path = 'yibank.db'
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, 
                      balance REAL, loan REAL, status TEXT, total_debit REAL, is_verified INTEGER, is_approved INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tx (uid TEXT, msg TEXT)''')
        conn.commit()
        conn.close()
    except:
        pass

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
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="YI PRIVATE BANK", font_size='32sp', bold=True, color=(0,0.9,1,1)))
        btns = [("LOGIN", 'login'), ("CREATE ACCOUNT", 'register'), ("ADMIN CONSOLE", 'admin_login')]
        for t, s in btns:
            b = StyledButton(text=t)
            if t == "ADMIN CONSOLE": b.background_color = (0.6, 0.1, 0.1, 1)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            layout.add_widget(b)
        self.add_widget(layout)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="USER LOGIN", font_size='24sp', bold=True))
        self.uid = TextInput(hint_text="User ID", multiline=False, size_hint_y=None, height='45dp')
        self.pwd = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.uid)
        layout.add_widget(self.pwd)
        btn = StyledButton(text="LOGIN")
        btn.bind(on_press=self.verify)
        layout.add_widget(btn)
        self.add_widget(layout)

    def verify(self, instance):
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        epass = encrypt_pass(self.pwd.text)
        c.execute("SELECT uid, status FROM users WHERE uid=? AND password=?", (self.uid.text, epass))
        res = c.fetchone()
        conn.close()
        if res:
            if res[1] == 'Active':
                App.get_running_app().current_uid = res[0]
                self.manager.current = 'dashboard'
            else:
                self.add_widget(Label(text="ACCOUNT BLOCKED", color=(1,0,0,1)))

class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="ADMIN LOGIN", font_size='22sp', color=(1,0.2,0.2,1)))
        self.aid = TextInput(hint_text="Admin ID", multiline=False, size_hint_y=None, height='45dp')
        self.apw = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.aid)
        layout.add_widget(self.apw)
        btn = StyledButton(text="VERIFY ADMIN", background_color=(0.5,0,0,1))
        btn.bind(on_press=self.check)
        layout.add_widget(btn)
        self.add_widget(layout)

    def check(self, instance):
        if self.aid.text == "uitdei" and self.apw.text == "uit123":
            self.manager.current = 'admin_dash'

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="TERMS & CONDITIONS", font_size='22sp', bold=True))
        scroll = ScrollView()
        terms = "1. Passwords Encrypted (SHA-256)\n2. 50K Limit needs Face ID\n3. 10% Loan Interest\n4. Admin Approval Required."
        scroll.add_widget(Label(text=terms, size_hint_y=None, height='200dp'))
        layout.add_widget(scroll)
        self.check = CheckBox(size_hint_y=None, height='40dp')
        layout.add_widget(self.check)
        btn = StyledButton(text="ACCEPT & CONTINUE")
        btn.bind(on_press=self.go)
        layout.add_widget(btn)
        self.add_widget(layout)

    def go(self, instance):
        if self.check.active: self.manager.current = 'register_form'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.n = TextInput(hint_text="Name", multiline=False)
        self.m = TextInput(hint_text="Mobile", multiline=False)
        self.p = TextInput(hint_text="Password", password=True)
        layout.add_widget(self.n); layout.add_widget(self.m); layout.add_widget(self.p)
        btn = StyledButton(text="CREATE")
        btn.bind(on_press=self.save)
        layout.add_widget(btn)
        self.add_widget(layout)

    def save(self, instance):
        if self.n.text:
            uid = str(random.randint(1000, 9999))
            acc = "YIB" + str(random.randint(100, 999))
            ep = encrypt_pass(self.p.text)
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?)", (uid,self.n.text,self.m.text,ep,acc,1000.0,0.0,'Active',0.0,0,0))
            conn.commit(); conn.close()
            App.get_running_app().current_uid = uid
            self.manager.current = 'account_details'

class AccountDetailsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT uid, acc_no FROM users WHERE uid=?", (App.get_running_app().current_uid,))
        r = c.fetchone()
        conn.close()
        l = BoxLayout(orientation='vertical', padding=30)
        l.add_widget(Label(text=f"UID: {r[0]}\nACC: {r[1]}", font_size='22sp'))
        b = StyledButton(text="LOGIN NOW")
        b.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        l.add_widget(b); self.add_widget(l)

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT name, balance, is_approved FROM users WHERE uid=?", (App.get_running_app().current_uid,))
        u = c.fetchone()
        conn.close()
        l = BoxLayout(orientation='vertical', padding=20, spacing=10)
        l.add_widget(Label(text=f"Welcome {u[0]}\nBal: {u[1]:.2f} RS", font_size='22sp'))
        btns = [("WITHDRAW", 'withdraw'), ("HISTORY", 'history'), ("LOGOUT", 'start')]
        for t, s in btns:
            b = StyledButton(text=t)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            l.add_widget(b)
        self.add_widget(l)

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.amt = TextInput(hint_text="Amount", input_filter='int')
        layout.add_widget(self.amt)
        btn = StyledButton(text="SEND")
        btn.bind(on_press=self.pay)
        layout.add_widget(btn)
        self.add_widget(layout)

    def pay(self, instance):
        uid = App.get_running_app().current_uid
        val = float(self.amt.text) if self.amt.text else 0
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT balance, total_debit, is_verified, is_approved FROM users WHERE uid=?", (uid,))
        b, td, iv, ia = c.fetchone()
        if (td + val) > 50000 and iv == 0:
            self.manager.current = 'face_verify'
        elif b >= val:
            c.execute("UPDATE users SET balance=balance-?, total_debit=total_debit+? WHERE uid=?", (val,val,uid))
            conn.commit()
            self.manager.current = 'dashboard'
        conn.close()

class FaceVerifyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=40)
        l.add_widget(Label(text="FACE AUTH REQUIRED"))
        b = StyledButton(text="START AUTH")
        b.bind(on_press=self.done)
        l.add_widget(b); self.add_widget(l)
    def done(self, x):
        conn = sqlite3.connect('yibank.db'); c = conn.cursor()
        c.execute("UPDATE users SET is_verified=1 WHERE uid=?", (App.get_running_app().current_uid,))
        conn.commit(); conn.close()
        self.manager.current = 'dashboard'

class AdminDashboard(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        l = BoxLayout(orientation='vertical', padding=20)
        l.add_widget(Label(text="ADMIN: PENDING APPROVALS"))
        conn = sqlite3.connect('yibank.db'); c = conn.cursor()
        c.execute("SELECT uid, name FROM users WHERE is_verified=1 AND is_approved=0")
        for u, n in c.fetchall():
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=n))
            btn = Button(text="APPROVE", on_press=lambda x, uid=u: self.appr(uid))
            row.add_widget(btn); l.add_widget(row)
        b = StyledButton(text="BACK"); b.bind(on_press=lambda x: setattr(self.manager, 'current', 'start'))
        l.add_widget(b); conn.close(); self.add_widget(l)
    def appr(self, uid):
        conn = sqlite3.connect('yibank.db'); c = conn.cursor()
        c.execute("UPDATE users SET is_approved=1 WHERE uid=?", (uid,))
        conn.commit(); conn.close(); self.on_pre_enter()

class HistoryScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        l = BoxLayout(orientation='vertical', padding=20)
        l.add_widget(Label(text="TRANSACTIONS"))
        b = StyledButton(text="BACK", on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        l.add_widget(b); self.add_widget(l)

class YIBankApp(App):
    current_uid = ""
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AdminLoginScreen(name='admin_login'))
        sm.add_widget(TermsScreen(name='register'))
        sm.add_widget(RegistrationScreen(name='register_form'))
        sm.add_widget(AccountDetailsScreen(name='account_details'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(FaceVerifyScreen(name='face_verify'))
        sm.add_widget(AdminDashboard(name='admin_dash'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
        
