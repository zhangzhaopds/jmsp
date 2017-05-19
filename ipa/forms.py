from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(label=u'Username', max_length=30, error_messages={'required': "用户名不能为空"})
    email = forms.EmailField(label=u'Email Address', error_messages={'required': '邮箱不能为空'})
    password1 = forms.CharField(label=u'Password1', widget=forms.PasswordInput(), error_messages={'required': '密码不能为空'})
    password2 = forms.CharField(label=u'Password2', widget=forms.PasswordInput(), error_messages={'required': '密码不能为空'})

    def clean_username(self):
        if 'username' in self.cleaned_data:
            username = self.cleaned_data['username']
            return username
        # raise forms.ValidationError(u'用户名错误')

    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            return email

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password2 == password1:
                return password2
        # raise forms.ValidationError('密码有误')