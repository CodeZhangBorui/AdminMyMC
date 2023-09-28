from users import *

# Top menus for normal users
menus = [
    {
        "text": "首页",
        "href": "/"
    },
    {
        "text": "子服务器管理",
        "href": "/servers"
    }
]

# Top menus for admin
adminmenus = [
    {
        "text": "计划任务",
        "href": "/tasks"
    },
]

# Personal menus
personalmenus = [
    {
        "text": "API 与 API 密钥",
        "href": "/apikey"
    },
    {
        "text": "修改密码",
        "href": "/changepass"
    },
    {
        "text": "退出登录",
        "href": "/logout"
    }
]

def render_menus(session):
    if(check_permission(session['username']) == 10):
        return menus + adminmenus
    else:
        return menus