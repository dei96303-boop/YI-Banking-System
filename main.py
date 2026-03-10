import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

class RegistrationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Welcome to YI Bank", font_size=30))
        
        self.name_input = TextInput(hint_text="Full Name", multiline=False)
        self.dob_input = TextInput(hint_text="DOB (DD/MM/YYYY)", multiline=False)
        self.mobile_input = TextInput(hint_text="Mobile No", multiline=False)
        self.email_input = TextInput(hint_text="Email (Optional)", multiline=False)
        self.pass_input = TextInput(hint_text="Set Password", password=True, multiline=False)
        
        layout.add_widget(self.name_input)
        layout.add_widget(self.dob_input)
        layout.add_widget(self.mobile_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.pass_input)
        
        reg_btn = Button(text="Open Account", background_color=(0, 0.7, 0, 1))
        reg_btn.bind(on_press=self.register_user)
        layout.add_widget(reg_btn)
        
        self.add_widget(layout)

    def register_user(self, instance):
        app = App.get_running_app()
        app.user_data['name'] = self.name_input.text
        app.user_data['dob'] = self.dob_input.text
        app.user_data['mobile'] = self.mobile_input.text
        app.user_data['password'] = self.pass_input.text
        app.user_data['user_id'] = str(random.randint(1000, 9999))
        app.user_data['acc_no'] = str(random.randint(100000, 999999))
        app.user_data['balance'] = 1000
        
        self.manager.current = 'login'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text="Login to YI Bank", font_size=25))
        
        self.id_input = TextInput(hint_text="User ID", multiline=False)
        self.pw_input = TextInput(hint_text="Password", password=True, multiline=False)
        
        layout.add_widget(self.id_input)
        layout.add_widget(self.pw_input)
        
        login_btn = Button(text="Login", background_color=(0, 0.5, 1, 1))
        login_btn.bind(on_press=self.verify_login)
        layout.add_widget(login_btn)
        
        forgot_btn = Button(text="Forgot Credentials?", size_hint=(1, 0.5))
        forgot_btn.bind(on_press=self.go_to_forgot)
        layout.add_widget(forgot_btn)
        
        self.add_widget(layout)

    def verify_login(self, instance):
        app = App.get_running_app()
        if self.id_input.text == app.user_data['user_id'] and self.pw_input.text == app.user_data['password']:
            self.manager.current = 'dashboard'
        else:
            print("Invalid Login")

    def go_to_forgot(self, instance):
        self.manager.current = 'forgot'

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.clear_widgets()
        app = App.get_running_app()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text=f"Hello, {app.user_data['name']}", font_size=20))
        layout.add_widget(Label(text=f"Acc No: {app.user_data['acc_no']}"))
        layout.add_widget(Label(text=f"Balance: {app.user_data['balance']} RS"))
        
        dep_btn = Button(text="Deposit (via UPI)")
        dep_btn.bind(on_press=self.go_to_deposit)
        layout.add_widget(dep_btn)
        
        with_btn = Button(text="Withdrawal")
        with_btn.bind(on_press=self.go_to_withdraw)
        layout.add_widget(with_btn)
        
        exit_btn = Button(text="Logout")
        exit_btn.bind(on_press=self.logout)
        layout.add_widget(exit_btn)
        
        self.add_widget(layout)

    def go_to_deposit(self, instance): self.manager.current = 'deposit'
    def go_to_withdraw(self, instance): self.manager.current = 'withdraw'
    def logout(self, instance): self.manager.current = 'login'

class DepositScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Label(text="Pay to: try@upi", font_size=20))
        self.amount_input = TextInput(hint_text="Enter Amount", multiline=False)
        self.layout.add_widget(self.amount_input)
        
        confirm_btn = Button(text="Confirm Deposit")
        confirm_btn.bind(on_press=self.do_deposit)
        self.layout.add_widget(confirm_btn)
        self.add_widget(self.layout)

    def do_deposit(self, instance):
        app = App.get_running_app()
        app.user_data['balance'] += int(self.amount_input.text)
        self.manager.current = 'dashboard'

class ForgotScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.mob_input = TextInput(hint_text="Enter Registered Mobile", multiline=False)
        layout.add_widget(self.mob_input)
        
        recover_btn = Button(text="Recover Credentials")
        recover_btn.bind(on_press=self.recover)
        layout.add_widget(recover_btn)
        self.add_widget(layout)

    def recover(self, instance):
        app = App.get_running_app()
        if self.mob_input.text == app.user_data['mobile']:
            print(f"ID: {app.user_data['user_id']} | PW: {app.user_data['password']}")
            self.manager.current = 'login'

class YIBankApp(App):
    user_data = {}
    def build(self):
        sm = ScreenManager()
        sm.add_widget(RegistrationScreen(name='register'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(DepositScreen(name='deposit'))
        sm.add_widget(ForgotScreen(name='forgot'))
        return sm

if __name__ == '__main__':
    YIBankApp().run()
