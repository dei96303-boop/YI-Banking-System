import random
import hashlib
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

Window.clearcolor = (0.01, 0.01, 0.03, 1)

def encrypt_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('yibank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid TEXT PRIMARY KEY, name TEXT, mobile TEXT, password TEXT, acc_no TEXT, 
                  balance REAL, loan REAL, status TEXT, total_debit REAL, is_verified INTEGER, is_approved INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tx (uid TEXT, msg TEXT)''')
    conn.commit()
    conn.close()

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

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="TERMS & CONDITIONS", font_size='22sp', bold=True))
        scroll = ScrollView()
        terms = (
            "1. Password will be stored in SHA-256 encrypted format.\n"
            "2. Withdrawals over 50,000 RS require Aadhaar Face Authentication.\n"
            "3. Face ID must be approved by the System Admin.\n"
            "4. Post approval, limit increases to 4,00,000 RS.\n"
            "5. Paid services for tax-shielded transactions (Future Feature).\n"
            "6. Loan interest is 10% compounded thrice a year."
        )
        scroll.add_widget(Label(text=terms, size_hint_y=None, height='300dp', halign='left', text_size=(Window.width-40, None)))
        layout.add_widget(scroll)
        
        self.check = CheckBox(size_hint_y=None, height='40dp')
        l = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        l.add_widget(self.check)
        l.add_widget(Label(text="I agree to the terms"))
        layout.add_widget(l)
        
        btn = StyledButton(text="CONTINUE TO REGISTRATION")
        btn.bind(on_press=self.go_next)
        layout.add_widget(btn)
        self.add_widget(layout)

    def go_next(self, instance):
        if self.check.active:
            self.manager.current = 'register_form'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.name = TextInput(hint_text="Full Name", multiline=False, size_hint_y=None, height='45dp')
        self.mob = TextInput(hint_text="Mobile No", multiline=False, size_hint_y=None, height='45dp')
        self.pwd = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.name)
        layout.add_widget(self.mob)
        layout.add_widget(self.pwd)
        btn = StyledButton(text="CREATE ACCOUNT")
        btn.bind(on_press=self.save)
        layout.add_widget(btn)
        self.add_widget(layout)

    def save(self, instance):
        if self.name.text and self.pwd.text:
            uid = str(random.randint(1000, 9999))
            acc = "YIB" + str(random.randint(100000, 999999))
            epass = encrypt_pass(self.pwd.text)
            conn = sqlite3.connect('yibank.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (uid, self.name.text, self.mob.text, epass, acc, 1000.0, 0.0, 'Active', 0.0, 0, 0))
            conn.commit()
            conn.close()
            App.get_running_app().current_uid = uid
            self.manager.current = 'account_details'

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.amt = TextInput(hint_text="Amount", input_filter='int', multiline=False)
        layout.add_widget(self.amt)
        btn = StyledButton(text="WITHDRAW")
        btn.bind(on_press=self.process)
        layout.add_widget(btn)
        self.add_widget(layout)

    def process(self, instance):
        app = App.get_running_app()
        val = float(self.amt.text) if self.amt.text else 0
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT balance, total_debit, is_verified, is_approved FROM users WHERE uid=?", (app.current_uid,))
        b, td, iv, ia = c.fetchone()
        
        limit = 50000 if ia == 0 else 400000
        
        if (td + val) > 50000 and iv == 0:
            self.manager.current = 'face_verify'
        elif (td + val) > limit:
            self.add_widget(Label(text=f"LIMIT EXCEEDED! Max: {limit} RS", color=(1,0,0,1), pos_hint={'y':0.2}))
        elif b >= val:
            c.execute("UPDATE users SET balance = balance - ?, total_debit = total_debit + ? WHERE uid=?", (val, val, app.current_uid))
            c.execute("INSERT INTO tx VALUES (?, ?)", (app.current_uid, f"Withdraw: {val} RS"))
            conn.commit()
            self.manager.current = 'dashboard'
        conn.close()

class FaceVerifyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(text="LIMIT EXCEEDED (50K+)", font_size='20sp', color=(1,0.5,0,1)))
        layout.add_widget(Label(text="Verify Face via AadhaarFaceRD app"))
        btn = StyledButton(text="LAUNCH FACE AUTH")
        btn.bind(on_press=self.verify)
        layout.add_widget(btn)
        self.add_widget(layout)

    def verify(self, instance):
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("UPDATE users SET is_verified = 1 WHERE uid=?", (App.get_running_app().current_uid,))
        conn.commit()
        conn.close()
        self.add_widget(Label(text="Face Verified! Waiting for Admin Approval", color=(0,1,0,1)))

class AdminDashboard(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="ADMIN CONTROL", font_size='22sp'))
        
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT uid, name FROM users WHERE is_verified=1 AND is_approved=0")
        pending = c.fetchall()
        
        for uid, name in pending:
            row = BoxLayout(size_hint_y=None, height='50dp')
            row.add_widget(Label(text=f"{name} ({uid})"))
            btn = Button(text="APPROVE 4L", background_color=(0,1,0,1))
            btn.bind(on_press=lambda x, u=uid: self.approve(u))
            row.add_widget(btn)
            layout.add_widget(row)
        
        logout = StyledButton(text="BACK")
        logout.bind(on_press=lambda x: setattr(self.manager, 'current', 'start'))
        layout.add_widget(logout)
        conn.close()
        self.add_widget(layout)

    def approve(self, uid):
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("UPDATE users SET is_approved = 1 WHERE uid=?", (uid,))
        conn.commit()
        conn.close()
        self.on_pre_enter()

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        conn = sqlite3.connect('yibank.db')
        c = conn.cursor()
        c.execute("SELECT name, balance, is_approved FROM users WHERE uid=?", (App.get_running_app().current_uid,))
        u = c.fetchone()
        conn.close()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text=f"Welcome, {u[0]}", font_size='20sp'))
        layout.add_widget(Label(text=f"Balance: {u[1]:.2f} RS", color=(0,1,0.5,1), font_size='26sp'))
        
        if u[2] == 1:
            layout.add_widget(Label(text="LIMIT: 4,00,000 (VIP)", color=(1,0.8,0,1)))
            btn_paid = StyledButton(text="ACTIVATE TAX-SHIELD (PAID)", background_color=(0.5, 0, 0.5, 1))
            layout.add_widget(btn_paid)

        btns = [("WITHDRAW", 'withdraw'), ("HISTORY", 'history'), ("LOGOUT", 'start')]
        for t, s in btns:
            b = StyledButton(text=t)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            layout.add_widget(b)
        self.add_widget(layout)

class YIBankApp(App):
    current_uid = ""
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(TermsScreen(name='register'))
        sm.add_widget(RegistrationScreen(name='register_form'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(FaceVerifyScreen(name='face_verify'))
        sm.add_widget(AdminDashboard(name='admin_dash'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        # Adding missing screens from previous context
        from kivy.uix.screenmanager import Screen
        sm.add_widget(Screen(name='login')) 
        sm.add_widget(Screen(name='admin_login'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
        
