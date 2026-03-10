import random
import math
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
        layout.add_widget(Label(text="YI BANK REGISTRATION", font_size='24sp', bold=True, color=(0, 0.8, 1, 1)))
        
        self.name_in = TextInput(hint_text="Full Name", multiline=False, size_hint_y=None, height='40dp')
        self.mob_in = TextInput(hint_text="Mobile Number", multiline=False, size_hint_y=None, height='40dp')
        self.pass_in = TextInput(hint_text="Set Password", password=True, multiline=False, size_hint_y=None, height='40dp')
        
        layout.add_widget(self.name_in)
        layout.add_widget(self.mob_in)
        layout.add_widget(self.pass_in)
        
        tc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        self.tc_check = CheckBox(size_hint_x=0.1)
        tc_label = Label(text="I accept all Terms & Conditions", font_size='12sp')
        tc_layout.add_widget(self.tc_check)
        tc_layout.add_widget(tc_label)
        layout.add_widget(tc_layout)
        
        btn_tc = Button(text="Read Terms & Conditions", size_hint_y=None, height='30dp', background_color=(0,0,0,0), color=(0,0.5,1,1))
        btn_tc.bind(on_press=self.show_tc)
        layout.add_widget(btn_tc)
        
        reg_btn = StyledButton(text="CREATE ACCOUNT")
        reg_btn.bind(on_press=self.process_reg)
        layout.add_widget(reg_btn)
        self.add_widget(layout)

    def show_tc(self, instance):
        self.manager.current = 'terms'

    def process_reg(self, instance):
        if self.tc_check.active and self.name_in.text:
            app = App.get_running_app()
            app.user_data = {
                'name': self.name_in.text,
                'mobile': self.mob_in.text,
                'password': self.pass_in.text,
                'user_id': str(random.randint(1000, 9999)),
                'acc_no': "YIB" + str(random.randint(100000, 999999)),
                'balance': 1000,
                'loan': 0,
                'transactions': ["Initial Credit: 1000 RS"]
            }
            self.manager.current = 'account_details'

class TermsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        scroll = ScrollView()
        text = (
            "YI BANK TERMS AND CONDITIONS\n\n"
            "1. Minimum balance threshold is 2000 RS.\n"
            "2. If balance falls below 2000 RS, 10% of threshold (200 RS) will be debited as penalty.\n"
            "3. After exhausting 1000 RS free credit, further usage will be treated as a LOAN.\n"
            "4. Loan interest is 10% per annum, compounded thrice a year (n=3).\n"
            "5. User must pay interest and principal on time.\n"
        )
        scroll.add_widget(Label(text=text, size_hint_y=None, height='400dp', halign='left', valign='top', text_size=(Window.width-40, None)))
        layout.add_widget(scroll)
        
        back_btn = StyledButton(text="BACK TO REGISTRATION")
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class AccountDetailsScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="ACCOUNT CREATED SUCCESSFULLY", color=(0,1,0,1), bold=True))
        layout.add_widget(Label(text=f"User ID: {app.user_data['user_id']}", font_size='20sp'))
        layout.add_widget(Label(text=f"Account No: {app.user_data['acc_no']}"))
        layout.add_widget(Label(text="Please save these details for login."))
        
        next_btn = StyledButton(text="PROCEED TO LOGIN")
        next_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(next_btn)
        self.add_widget(layout)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="LOGIN", font_size='24sp', bold=True))
        self.uid = TextInput(hint_text="User ID", multiline=False, size_hint_y=None, height='45dp')
        self.pwd = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        layout.add_widget(self.uid)
        layout.add_widget(self.pwd)
        btn = StyledButton(text="LOGIN")
        btn.bind(on_press=self.do_login)
        layout.add_widget(btn)
        self.add_widget(layout)

    def do_login(self, instance):
        app = App.get_running_app()
        if self.uid.text == app.user_data.get('user_id') and self.pwd.text == app.user_data.get('password'):
            self.manager.current = 'dashboard'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text=f"Hello, {app.user_data['name']}", font_size='22sp'))
        layout.add_widget(Label(text=f"Balance: {app.user_data['balance']} RS", color=(0,1,0.5,1), font_size='24sp'))
        
        if app.user_data['loan'] > 0:
            interest = app.user_data['loan'] * (pow((1 + 0.10/3), 3) - 1)
            total_due = app.user_data['loan'] + interest
            layout.add_widget(Label(text=f"LOAN DUE: {total_due:.2f} RS", color=(1,0,0,1)))

        btns = [("WITHDRAW (UPI)", 'withdraw'), ("E-BANKING DOC", 'docs'), ("TRANSACTIONS", 'history'), ("LOGOUT", 'login')]
        for t, s in btns:
            b = StyledButton(text=t)
            b.bind(on_press=lambda x, sc=s: setattr(self.manager, 'current', sc))
            layout.add_widget(b)
        self.add_widget(layout)

class WithdrawScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.upi = TextInput(hint_text="Enter UPI ID (e.g. user@bank)", multiline=False)
        self.amt = TextInput(hint_text="Amount", input_filter='int', multiline=False)
        layout.add_widget(self.upi)
        layout.add_widget(self.amt)
        
        btn = StyledButton(text="CONFIRM WITHDRAW")
        btn.bind(on_press=self.process_withdraw)
        layout.add_widget(btn)
        self.add_widget(layout)

    def process_withdraw(self, instance):
        app = App.get_running_app()
        amount = int(self.amt.text) if self.amt.text else 0
        
        if amount > 0:
            app.user_data['balance'] -= amount
            app.user_data['transactions'].append(f"Withdraw: {amount} RS via UPI")
            
            if app.user_data['balance'] < 2000:
                penalty = 200
                app.user_data['balance'] -= penalty
                app.user_data['transactions'].append(f"Penalty: {penalty} RS (Low Balance)")
            
            if app.user_data['balance'] < 0:
                loan_amt = abs(app.user_data['balance'])
                app.user_data['loan'] += loan_amt
                app.user_data['balance'] = 0
                app.user_data['transactions'].append(f"Loan Created: {loan_amt} RS")
                
            self.manager.current = 'dashboard'

class HistoryScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text="TRANSACTION LOG", bold=True, size_hint_y=None, height='40dp'))
        scroll = ScrollView()
        list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for tx in app.user_data['transactions']:
            list_layout.add_widget(Label(text=tx, size_hint_y=None, height='30dp'))
        
        scroll.add_widget(list_layout)
        layout.add_widget(scroll)
        btn = StyledButton(text="BACK")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn)
        self.add_widget(layout)

class DocScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text="E-BANKING DOCUMENT", font_size='22sp', bold=True))
        doc_text = (
            f"Account Holder: {app.user_data['name']}\n"
            f"Account Number: {app.user_data['acc_no']}\n"
            f"Mobile: {app.user_data['mobile']}\n"
            f"Current Balance: {app.user_data['balance']} RS\n"
            f"Current Loan: {app.user_data['loan']} RS\n"
            "Status: Active"
        )
        layout.add_widget(Label(text=doc_text, halign='center'))
        btn = StyledButton(text="BACK")
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn)
        self.add_widget(layout)

class YIBankApp(App):
    user_data = {}
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(TermsScreen(name='terms'))
        sm.add_widget(AccountDetailsScreen(name='account_details'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(WithdrawScreen(name='withdraw'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(DocScreen(name='docs'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
        
