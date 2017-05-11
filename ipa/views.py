from django.shortcuts import render
from django.core.mail import send_mail
from . import tools
from .models import UserInfo


# Create your views here.

def index(request):
    return render(request, 'ipa/index.html', {'user': '大王'})

def login(request):
    return render(request, 'ipa/login.html')

def register(request):
    return render(request, 'ipa/register.html')

# 提交邮箱验证
def singup(request):
    if request.method == 'POST':
        print(request.POST['email'])
        email = request.POST['email']
        user = UserInfo.objects.create(email=email, is_active=0)
        user.save()

        token = tools.Token().generate_validate_token(key=email)

        print(token)
        print(tools.Token().confirm_validate_token(token=token))
        print(request.path)
        print(request.get_host())
        print(request.get_full_path())
        message = "\n".join([
            u'{0},欢迎您的加入'.format(request.POST['email']),
            u'请访问该链接，完成用户验证:',
            'http://' + request.get_host() + '/active?token=' + token
        ])
        print(message)
        # if request.POST['isCheck'] == "on":
        #     return render(request, 'ipa/register.html')
        # elif request.POST['email'] != '':
        #     send_mail(u'注册用户验证信息', )
        send_mail(u'注册用户验证信息', message, None, [email])
    return render(request, 'ipa/register.html')

# token验证
def active_user(request, token):
    return render(request)