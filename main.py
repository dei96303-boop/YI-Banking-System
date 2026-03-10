import random
import math
import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window

Window.clearcolor = (0.02, 0.02, 0.05, 1)

def init_db():
    conn = sqlite3.connect('yibank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, balance REAL, loan REAL, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tx (uid TEXT, msg TEXT)''')
    try:
        c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Active'")
    except:
        pass
    conn.commit()
    conn.close()

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0.4, 0.7, 1)
        self.bold = True
        self.size_hint_y = None
        self.height = '50dp'

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text="YI BANKING CONSOLE", font_size='28sp', bold=True, color=(0,0.8,1,1)))
        
        btn_u = StyledButton(text="USER PORTAL")
        btn_u.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn_u)
        
        btn_a = StyledButton(text="ADMIN CONSOLE", background_color=(0.7, 0.2, 0.2, 1))
        btn_a.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_login'))
        layout.add_widget(btn_a)
        
        btn_r = Button(text="New User? Register here", background_color=(0,0,0,0), color=(0,0.5,1,1))
        btn_r.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(btn_r)
        self.add_widget(layout)

class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="ADMIN AUTHENTICATION", font_size='22sp', color=(1,0.2,0.2,1)))
        self.aid = TextInput(hint_text="Admin ID", multiline=False, size_hint_y=None, height='45dp')
        self.apw = TextInput(hint_text="Admin Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.aid)
        layout.add_widget(self.apw)
        btn = StyledButton(text="LOGIN AS ADMIN", background_color=(0.5,0,0,1))
        btn.bind(on_press=self.verify_admin)
        layout.add_widget(btn)
        self.add_widget(layout)

    def verify_admin(self, instance):
        if self.aid.text == "uitdei" and self.apw.text == "uit123":
            self.manager.current = 'admin_dash'

class AdminDashboard(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="SYSTEM CONTROLS", font_size='22sp', bold=True))
        
        self.target_uid = TextInput(hint_text="Target User UID", size_hint_y=None, height='40dp')
        self.amount = TextInput(hint_text="Amount", input_filter='int', size_hint_y=None, height='40dp')
        self.reason = TextInput(hint_text="Reason (for debit)", size_hint_y=None, height='40dp')
        
        layout.add_widget(self.target_uid)
        layout.add_widget(self.amount)
        layout.add_widget(self.reason)
        
        btns = [("CREDIT FUND", self.credit), ("DEBIT FUND", self.debit), ("BLOCK USER", self.block), ("RUSTICATE", self.rusticate), ("LOGOUT", self.logout)]
        for t, f in btns:
            b = StyledButton(text=t)
            if t in ["BLOCK USER", "RUSTICATE"]: b.background_color = (0.8, 0.3, 0, 1)
            b.bind(on_press=f)
            layout.add_widget(b)
        self.add_widget(layout)

    def credit(self, instance):
        if self.target_uid.text and self.amount.text:
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ? WHERE uid=?", (float(self.amount.text), self.target_uid.text))
            c.execute("INSERT INTO tx VALUES (?, ?)", (self.target_uid.text, f"Admin Credit: {self.amount.text} RS"))
            conn.commit()
            conn.close()

    def debit(self, instance):
        if self.target_uid.text and self.amount.text:
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("UPDATE users SET balance = balance - ? WHERE uid=?", (float(self.amount.text), self.target_uid.text))
            c.execute("INSERT INTO tx VALUES (?, ?)", (self.target_uid.text, f"Admin Debit: {self.amount.text} RS ({self.reason.text})"))
            conn.commit()
            conn.close()

    def block(self, instance):
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("UPDATE users SET status = 'Blocked' WHERE uid=?", (self.target_uid.text,))
        conn.commit()
        conn.close()

    def rusticate(self, instance):
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE uid=?", (self.target_uid.text,))
        c.execute("DELETE FROM tx WHERE uid=?", (self.target_uid.text,))
        conn.commit()
        conn.close()

    def logout(self, instance):
        self.manager.current = 'start'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="YI BANK REGISTRATION", font_size='24sp', bold=True, color=(0, 0.8, 1, 1)))
        self.name_in = TextInput(hint_text="Full Name", multiline=False, size_hint_y=None, height='40dp')
        self.mob_in = TextInput(hint_text="Mobile Number", multiline=False, size_hint_y=None, height='40dp')
        self.pass_in = TextInput(hint_text="Set Password", password=True, multiline=False, size_hint_y=None, height='40dp')
        layout.add_widget(self.name_in)
        layout.add_widget(self.mob_in)
        layout.add_widget(self.pass_in)
        self.tc_check = CheckBox(size_hint_y=None, height='40dp')
        layout.add_widget(self.tc_check)
        reg_btn = StyledButton(text="OPEN ACCOUNT")
        reg_btn.bind(on_press=self.save_user)
        layout.add_widget(reg_btn)
        self.add_widget(layout)

    def save_user(self, instance):
        if self.tc_check.active and self.name_in.text:
            uid = str(random.randint(1000, 9999))
            acc = "YIB" + str(random.randint(100000, 999999))
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                      (uid, self.name_in.text, self.mob_in.text, self.pass_in.text, acc, 1000.0, 0.0, 'Active'))
            c.execute("INSERT INTO tx VALUES (?, ?)", (uid, "Initial Credit: 1000 RS"))
            conn.commit()
            conn.close()
            App.get_running_app().current_uid = uid
            self.manager.current = 'account_details'

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
        c.execute("SELECT uid, status FROM users WHERE uid=? AND password=?", (self.uid.text, self.pwd.text))
        res = c.fetchone()
        conn.close()
        if res:
            if res[1] == 'Active':
                App.get_running_app().current_uid = res[0]
                self.manager.current = 'dashboard'
            else:
                self.add_widget(Label(text="ACCOUNT BLOCKED/RESTRICTED", color=(1,0,0,1), pos_hint={'y':0.1}))

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT name, balance, loan FROM users WHERE uid=?", (app.current_uid,))
        u = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f"Welcome, {u[0]}", font_size='20sp'))
        layout.add_widget(Label(text=f"Balance: {u[1]:.2f} RS", color=(0,1,0.5,1), font_size='26sp'))
        if u[2] > 0:
            interest = u[2] * (pow((1 + 0.10/3), 3) - 1)
            layout.add_widget(Label(text=f"LOAN DUE: {u[2]+interest:.2f} RS", color=(1,0,0,1)))
        
        btns = [("WITHDRAW (UPI)", 'withdraw'), ("E-DOC", 'docs'), ("HISTORY", 'history'), ("LOGOUT", 'start')]
        for t, s in btns:
            b = StyledButton(text=t)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            layout.add_widget(b)
        self.add_widget(layout)

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.upi = TextInput(hint_text="Receiver UPI ID", multiline=False)
        self.amt = TextInput(hint_text="Amount", input_filter='int', multiline=False)
        layout.add_widget(self.upi)
        layout.add_widget(self.amt)
        btn = StyledButton(text="SEND VIA UPI")
        btn.bind(on_press=self.pay)
        layout.add_widget(btn)
        self.add_widget(layout)

    def pay(self, instance):
        app = App.get_running_app()
        val = int(self.amt.text) if self.amt.text else 0
        if val > 0:
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("SELECT balance, loan FROM users WHERE uid=?", (app.current_uid,))
            b, l = c.fetchone()
            new_b = b - val
            new_l = l
            c.execute("INSERT INTO tx VALUES (?, ?)", (app.current_uid, f"UPI Sent: {val} RS to {self.upi.text}"))
            if new_b < 2000:
                new_b -= 200
                c.execute("INSERT INTO tx VALUES (?, ?)", (app.current_uid, "Threshold Penalty: 200 RS"))
            if new_b < 0:
                new_l += abs(new_b)
                new_b = 0
            c.execute("UPDATE users SET balance=?, loan=? WHERE uid=?", (new_b, new_l, app.current_uid))
            conn.commit()
            conn.close()
            self.manager.current = 'dashboard'

class HistoryScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20)
        scroll = ScrollView()
        list_l = BoxLayout(orientation='vertical', size_hint_y=None)
        list_l.bind(minimum_height=list_l.setter('height'))
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT msg FROM tx WHERE uid=?", (App.get_running_app().current_uid,))
        for r in c.fetchall():
            list_l.add_widget(Label(text=r[0], size_hint_y=None, height='30dp'))
        conn.close()
        scroll.add_widget(list_l)
        layout.add_widget(scroll)
        btn = StyledButton(text="BACK")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn)
        self.add_widget(layout)

class AccountDetailsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT uid, acc_no FROM users WHERE uid=?", (App.get_running_app().current_uid,))
        res = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="REGISTRATION SUCCESSFUL", color=(0,1,0,1)))
        layout.add_widget(Label(text=f"User ID: {res[0]}", font_size='22sp'))
        layout.add_widget(Label(text=f"Account No: {res[1]}"))
        btn = StyledButton(text="PROCEED TO LOGIN")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn)
        self.add_widget(layout)

class DocScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE uid=?", (App.get_running_app().current_uid,))
        u = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=20)
        doc = f"Holder: {u[1]}\nAcc: {u[4]}\nMobile: {u[2]}\nBalance: {u[5]} RS\nLoan: {u[6]} RS\nStatus: {u[7]}"
        layout.add_widget(Label(text=doc, font_size='18sp'))
        btn = StyledButton(text="BACK")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn)
        self.add_widget(layout)

class YIBankApp(App):
    current_uid = ""
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(AdminLoginScreen(name='admin_login'))
        sm.add_widget(AdminDashboard(name='admin_dash'))
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(AccountDetailsScreen(name='account_details'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(DocScreen(name='docs'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
        
