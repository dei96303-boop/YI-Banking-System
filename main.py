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
                 (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, balance REAL, loan REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tx (uid TEXT, msg TEXT)''')
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

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="YI BANK SECURE PORTAL", font_size='24sp', bold=True, color=(0, 0.8, 1, 1)))
        self.name_in = TextInput(hint_text="Full Name", multiline=False, size_hint_y=None, height='40dp')
        self.mob_in = TextInput(hint_text="Mobile Number", multiline=False, size_hint_y=None, height='40dp')
        self.pass_in = TextInput(hint_text="Set Password", password=True, multiline=False, size_hint_y=None, height='40dp')
        layout.add_widget(self.name_in)
        layout.add_widget(self.mob_in)
        layout.add_widget(self.pass_in)
        tc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.tc_check = CheckBox(size_hint_x=0.1)
        tc_layout.add_widget(self.tc_check)
        tc_layout.add_widget(Label(text="Accept Terms & Loan Conditions", font_size='12sp'))
        layout.add_widget(tc_layout)
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
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (uid, self.name_in.text, self.mob_in.text, self.pass_in.text, acc, 1000.0, 0.0))
            c.execute("INSERT INTO tx VALUES (?, ?)", (uid, "Initial Credit: 1000 RS"))
            conn.commit()
            conn.close()
            app = App.get_running_app()
            app.current_uid = uid
            self.manager.current = 'account_details'

class AccountDetailsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT uid, acc_no FROM users WHERE uid=?", (app.current_uid,))
        res = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="SAVE YOUR CREDENTIALS", color=(0,1,0,1), bold=True))
        layout.add_widget(Label(text=f"User ID: {res[0]}", font_size='22sp'))
        layout.add_widget(Label(text=f"Account No: {res[1]}"))
        btn = StyledButton(text="GO TO LOGIN")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn)
        self.add_widget(layout)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="BANK LOGIN", font_size='24sp', bold=True))
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
        c.execute("SELECT uid FROM users WHERE uid=? AND password=?", (self.uid.text, self.pwd.text))
        res = c.fetchone()
        conn.close()
        if res:
            app = App.get_running_app()
            app.current_uid = res[0]
            self.manager.current = 'dashboard'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT name, balance, loan, acc_no FROM users WHERE uid=?", (app.current_uid,))
        u = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f"Welcome, {u[0]}", font_size='20sp'))
        layout.add_widget(Label(text=f"Balance: {u[1]:.2f} RS", color=(0,1,0.5,1), font_size='26sp'))
        if u[2] > 0:
            interest = u[2] * (pow((1 + 0.10/3), 3) - 1)
            layout.add_widget(Label(text=f"LOAN + INT: {u[2]+interest:.2f} RS", color=(1,0,0,1)))
        btns = [("WITHDRAW (UPI)", 'withdraw'), ("E-DOC", 'docs'), ("HISTORY", 'history'), ("LOGOUT", 'login')]
        for t, s in btns:
            b = StyledButton(text=t)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            layout.add_widget(b)
        self.add_widget(layout)

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.upi = TextInput(hint_text="UPI ID", multiline=False)
        self.amt = TextInput(hint_text="Amount", input_filter='int', multiline=False)
        layout.add_widget(self.upi)
        layout.add_widget(self.amt)
        btn = StyledButton(text="CONFIRM")
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
            c.execute("INSERT INTO tx VALUES (?, ?)", (app.current_uid, f"Withdraw: {val} RS"))
            if new_b < 2000:
                new_b -= 200
                c.execute("INSERT INTO tx VALUES (?, ?)", (app.current_uid, "Low Balance Penalty: 200 RS"))
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
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20)
        scroll = ScrollView()
        list_l = BoxLayout(orientation='vertical', size_hint_y=None)
        list_l.bind(minimum_height=list_l.setter('height'))
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT msg FROM tx WHERE uid=?", (app.current_uid,))
        for r in c.fetchall():
            list_l.add_widget(Label(text=r[0], size_hint_y=None, height='30dp'))
        conn.close()
        scroll.add_widget(list_l)
        layout.add_widget(scroll)
        btn = StyledButton(text="BACK")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn)
        self.add_widget(layout)

class DocScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE uid=?", (app.current_uid,))
        u = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=20)
        doc = f"Holder: {u[1]}\nAcc: {u[4]}\nMobile: {u[2]}\nBalance: {u[5]} RS\nLoan: {u[6]} RS"
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
