import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

Window.clearcolor = (0.05, 0.05, 0.1, 1)

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0.5, 0.8, 1)
        self.font_size = '18sp'
        self.bold = True
        self.size_hint_y = None
        self.height = '50dp'

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        
        layout.add_widget(Label(text="YI BANKING SYSTEM", font_size='28sp', bold=True, color=(0, 0.8, 1, 1)))
        layout.add_widget(Label(text="Create Your Secure Account", font_size='14sp', color=(0.7, 0.7, 0.7, 1)))
        
        self.name_input = TextInput(hint_text="Full Name", multiline=False, size_hint_y=None, height='40dp')
        self.dob_input = TextInput(hint_text="DOB (DD/MM/YYYY)", multiline=False, size_hint_y=None, height='40dp')
        self.mobile_input = TextInput(hint_text="Mobile No (Mandatory)", multiline=False, size_hint_y=None, height='40dp')
        self.pass_input = TextInput(hint_text="Set Password", password=True, multiline=False, size_hint_y=None, height='40dp')
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.dob_input)
        layout.add_widget(self.mobile_input)
        layout.add_widget(self.pass_input)
        
        reg_btn = StyledButton(text="REGISTER & GET 1000 RS")
        reg_btn.bind(on_press=self.register_user)
        layout.add_widget(reg_btn)
        self.add_widget(layout)

    def register_user(self, instance):
        if self.name_input.text and self.mobile_input.text:
            app = App.get_running_app()
            app.user_data = {
                'name': self.name_input.text,
                'dob': self.dob_input.text,
                'mobile': self.mobile_input.text,
                'password': self.pass_input.text,
                'user_id': str(random.randint(1000, 9999)),
                'acc_no': "YI" + str(random.randint(100000, 999999)),
                'balance': 1000
            }
            self.manager.current = 'otp_verify'

class OTPVerifyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        self.msg = Label(text="Verify Your Mobile", font_size='20sp')
        self.layout.add_widget(self.msg)
        
        self.otp_input = TextInput(hint_text="Enter 4-Digit OTP", multiline=False, size_hint_y=None, height='50dp', font_size='24sp')
        self.layout.add_widget(self.otp_input)
        
        v_btn = StyledButton(text="VERIFY")
        v_btn.bind(on_press=self.check_otp)
        self.layout.add_widget(v_btn)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.generated_otp = str(random.randint(1000, 9999))
        print(f"\n[REAL SMS SIMULATION] OTP for YI Bank: {self.generated_otp}")

    def check_otp(self, instance):
        if self.otp_input.text == self.generated_otp:
            self.manager.current = 'login'
        else:
            self.msg.text = "Invalid OTP! Try Again"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="MEMBER LOGIN", font_size='24sp', bold=True))
        
        self.id_input = TextInput(hint_text="System User ID", multiline=False, size_hint_y=None, height='45dp')
        self.pw_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height='45dp')
        
        layout.add_widget(self.id_input)
        layout.add_widget(self.pw_input)
        
        l_btn = StyledButton(text="LOGIN TO PORTAL")
        l_btn.bind(on_press=self.do_login)
        layout.add_widget(l_btn)
        
        f_btn = Button(text="Forgot Credentials?", background_color=(0,0,0,0), color=(0, 0.6, 1, 1))
        f_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'forgot'))
        layout.add_widget(f_btn)
        self.add_widget(layout)

    def do_login(self, instance):
        app = App.get_running_app()
        if self.id_input.text == app.user_data.get('user_id') and self.pw_input.text == app.user_data.get('password'):
            self.manager.current = 'dashboard'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        with layout.canvas.before:
            Color(0.1, 0.1, 0.2, 1)
            self.rect = Rectangle(size=Window.size, pos=layout.pos)

        layout.add_widget(Label(text=f"Welcome, {app.user_data['name']}", font_size='22sp', bold=True))
        layout.add_widget(Label(text=f"Account No: {app.user_data['acc_no']}", color=(0.8, 0.8, 0.8, 1)))
        layout.add_widget(Label(text=f"Balance: {app.user_data['balance']} RS", font_size='26sp', color=(0, 1, 0.4, 1)))
        
        btns = [("DEPOSIT (UPI)", 'deposit'), ("WITHDRAWAL", 'withdraw'), ("LOGOUT", 'login')]
        for text, screen in btns:
            b = StyledButton(text=text)
            if text == "LOGOUT": b.background_color = (0.8, 0.2, 0.2, 1)
            b.bind(on_press=lambda x, s=screen: self.change_screen(s))
            layout.add_widget(b)
        self.add_widget(layout)

    def change_screen(self, screen):
        self.manager.current = screen

class DepositScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        layout.add_widget(Label(text="SEND MONEY TO: try@upi", font_size='18sp', color=(1, 1, 0, 1)))
        self.amt = TextInput(hint_text="Enter Amount", input_filter='int', multiline=False)
        layout.add_widget(self.amt)
        
        d_btn = StyledButton(text="CONFIRM PAYMENT")
        d_btn.bind(on_press=self.finish)
        layout.add_widget(d_btn)
        self.add_widget(layout)

    def finish(self, instance):
        if self.amt.text:
            app = App.get_running_app()
            app.user_data['balance'] += int(self.amt.text)
            self.manager.current = 'dashboard'

class YIBankApp(App):
    user_data = {}
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(OTPVerifyScreen(name='otp_verify'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(DepositScreen(name='deposit'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
    
