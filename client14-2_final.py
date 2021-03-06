'''
    主要思路:
        1. 点击图片按钮后选择图片发送
        2. 先将图片发送到服务端缓存文件夹,发送完成后发信息通知各个客户端
        3. 客户端收到后会从服务端的缓存文件夹中下载对应的图片并打印到聊天界面,
           同样是在接收后进行判断进行操作
    继续第3步: 将print打印替换成从图片服务端下载图片到缓存文件夹
'''

import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
import time
import requests
from tkinter import filedialog
import vchat, achat
import os
from time import sleep
from PIL import ImageGrab

IP = ''
PORT = ''
user = ''
# _users = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
online_users = []  # 在线用户列表
chat = '----------群聊----------'  # 聊天对象, 默认为群聊

## 登录窗口
root1 = tkinter.Tk()
root1.title('登录')
root1['height'] = 110
root1['width'] = 270
root1.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:50007')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')

# 服务器标签
labelIP = tkinter.Label(root1, text='服务器地址')
labelIP.place(x=30, y=10, width=80, height=20)

entryIP = tkinter.Entry(root1, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(root1, text='用户名')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(root1, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)

# 登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user = entryUser.get()
    s_login = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_login.connect((IP, PORT))
    s_login.send('_@'.encode())
    data = s_login.recv(1024)
    data = data.decode()
    # 没有捕获到异常则表示接收到的是在线用户列表
    _users = data
    if user in _users:
        s_login.close()
        tkinter.messagebox.showerror('登录失败', message='用户名重复')
    else:
        s_login.close()
        root1.destroy()  # 关闭窗口
root1.bind('<Return>', login)  # 回车绑定登录功能

but = tkinter.Button(root1, text='登录', command=login)
but.place(x=100, y=70, width=70, height=30)

root1.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

## 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title(user)  # 窗口命名为用户名
root['height'] = 390
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.insert(tkinter.END, '欢迎进入聊天室!', 'blue')

###### 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
# 将图片打开存入变量中
p1 = tkinter.PhotoImage(file = './表情/捂脸.png')
p2 = tkinter.PhotoImage(file = './表情/奸笑.png')
p3 = tkinter.PhotoImage(file = './表情/皱眉.png')
p4 = tkinter.PhotoImage(file = './表情/机智.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**':p1, 'bb**':p2, 'cc**':p3, 'dd**':p4}
ee = 0  # 判断表情面板开关的标志
# 发送表情图标记的函数, 在按钮点击事件中调用
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    global ee
    mes = exp + ':;' + user + ':;' + chat
    s.send(mes.encode())
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0
    
# 四个对应的函数
def bb1():
    mark('aa**')
def bb2():
    mark('bb**')
def bb3():
    mark('cc**')
def bb4():
    mark('dd**')
def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT ,bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT ,bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT ,bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT ,bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()
    
# 创建表情按钮
eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)

###### 图片功能代码部分
# 从图片服务端的缓存文件夹中下载图片到客户端缓存文件夹中
def fileGet(name):
    PORT3 = 50009
    ss2 = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    ss2.connect((IP, PORT3))
    message = 'get ' + name
    ss2.send(message.encode())
    fileName = '.\\客户端图片缓存\\' + name
    print('开始下载文件!')
    with open(fileName, 'wb') as f:
        while True:
            data = ss2.recv(1024)
            if data == 'EOF'.encode():
                print('下载完成!')
                break
            f.write(data)
    time.sleep(0.1)
    ss2.send('quit'.encode())

# 将图片上传到图片服务端的缓存文件夹中
def filePut(fileName):
    PORT3 = 50009
    ss = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    ss.connect((IP, PORT3))
    # 截取文件名
    name = fileName.split('/')[-1]
    message = 'put  ' + name
    ss.send(message.encode())
    time.sleep(0.1)
    print('开始上传文件!')
    with open(fileName, 'rb') as f:
        while True:
            a = f.read(1024)
            if not a:
                break
            ss.send(a)
        time.sleep(0.1)  # 延时确保文件发送完整
        ss.send('EOF'.encode())
        print('文件上传成功')
    ss.send('quit'.encode())
    time.sleep(0.1)
    # 上传成功后发一个信息给所有客户端
    mes = '``#' + name + ':;' + user + ':;' + chat
    s.send(mes.encode())


def picture():
    # 选择对话框
    fileName = tkinter.filedialog.askopenfilename(title='选择上传文件')
    # 如果有选择文件才继续执行
    if fileName:
        # 调用发送图片函数
        filePut(fileName)
    
# 创建发送图片按钮
pBut = tkinter.Button(root, text='图片', command=picture)
pBut.place(x=65, y=320, width=60, height=30)
#截屏函数如下所示
class MyCapture:
    def __init__(self, png):
        #变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        #屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        #创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        #不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top,bg='white', width=screenWidth, height=screenHeight)
        #显示全屏截图，在全屏截图上进行区域截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(screenWidth/2, screenHeight/2, image=self.image)
        #鼠标左键按下的位置
        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            #开始截图
            self.sel = True
        self.canvas.bind('<Button-1>', onLeftButtonDown)
        #鼠标左键移动，显示选取的区域
        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                #删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='black')
        self.canvas.bind('<B1-Motion>', onLeftButtonMove)
        #获取鼠标左键抬起的位置，保存区域截图
        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            sleep(0.1)
            #考虑鼠标左键从右下方按下而从左上方抬起的截图
            left, right = sorted([self.X.get(), event.x])
            top, bottom = sorted([self.Y.get(), event.y])
            pic = ImageGrab.grab((left+1, top+1, right, bottom))
            #弹出保存截图对话框
            fileName = tkinter.filedialog.asksaveasfilename(title='保存截图', filetypes=[('image', '*.jpg *.png')])
            if fileName:
                pic.save(fileName)
            #关闭当前窗口
            self.top.destroy()
        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
#让canvas充满窗口，并随窗口自动适应大小
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

 #开始截图
def buttonCaptureClick():
    #最小化主窗口
    root.state('icon')
    sleep(0.2)
    filename = 'temp.png'
#grab()方法默认对全屏幕进行截图
    im = ImageGrab.grab()
    im.save(filename)
    im.close()
    #显示全屏幕截图
    w = MyCapture(filename)
    buttonCapture.wait_window(w.top)
    #截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    root.state('normal')
    os.remove(filename)
# 创建截屏按钮
sBut = tkinter.Button(root, text='截屏', command=buttonCaptureClick)
sBut.place(x=125, y=320, width=60, height=30)

###### 文件功能代码部分
## 将在文件功能窗口用到的组件名都列出来, 方便重新打开时会对面板进行更新
list2 = ''  # 列表框
label = ''  # 显示路径的标签
upload = ''  # 上传按钮
close = ''  # 关闭按钮
def fileClient():
    PORT2 = 50008    # 聊天室的端口为50007
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect((IP, PORT2))

    # 修改root窗口大小显示文件管理的组件
    root['height'] = 390
    root['width'] = 760

    # 创建列表框
    list2 = tkinter.Listbox(root)
    list2.place(x=580, y=25, width=175, height=325)

    # 将接收到的目录文件列表打印出来(dir), 显示在列表框中, 在pwd函数中调用
    def recvList(enter, lu):
        s.send(enter.encode())
        data = s.recv(4096)  
        data = json.loads(data.decode())
        list2.delete(0, tkinter.END)  # 清空列表框
        lu = lu.split('\\')
        if len(lu) != 1:
            list2.insert(tkinter.END, ' 返回上一级目录')
            list2.itemconfig(0, fg='green')
        for i in range(len(data)):
            list2.insert(tkinter.END, (' '+data[i]))
            if not '.' in data[i]:
                list2.itemconfig(tkinter.END, fg='orange')
            else:
                list2.itemconfig(tkinter.END, fg='blue')

    # 创建标签显示服务端工作目录
    def lab():
        global label
        data = s.recv(1024)  # 接收目录
        lu = data.decode()
        try:
            label.destroy()
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        except:
            label = tkinter.Label(root, text=lu)
            label.place(x=580, y=0, )
        recvList('dir', lu)

    # 进入指定目录(cd)
    def cd(message):
        s.send(message.encode())

    # 刚连接上服务端时进行一次面板刷新    
    cd('cd same')
    lab()

    # 接收下载文件(get)
    def get(message):
        name = message.split()
        name = name[1]  # 获取命令的第二个参数(文件名)
        # 选择对话框, 选择文件的保存路径
        fileName = tkinter.filedialog.asksaveasfilename(title='保存文件到',
                                            initialfile=name)
        # 如果文件名非空才进行下载
        if fileName:
            s.send(message.encode())
            with open(fileName, 'wb') as f:
                while True:
                    data = s.recv(1024)
                    if data == 'EOF'.encode():
                        tkinter.messagebox.showinfo(title='提示',
                                                    message='下载成功!')
                        break
                    f.write(data)

    # 创建用于绑定在列表框上的函数
    def run(*args):
        indexs = list2.curselection()
        index = indexs[0]
        content = list2.get(index)
        # 如果有一个 . 则为文件
        if '.' in content:
            content = 'get' + content
            get(content)
            cd('cd same')
        elif content == ' 返回上一级目录':
            content = 'cd ..'
            cd(content)
        else:
            content = 'cd ' + content
            cd(content)
        lab()  # 刷新显示页面
        
    # 在列表框上设置绑定事件
    list2.bind('<ButtonRelease-1>', run)

    # 上传客户端所在文件夹中指定的文件到服务端, 在函数中获取文件名, 不用传参数
    def put():
        # 选择对话框
        fileName = tkinter.filedialog.askopenfilename(title='选择上传文件')
        # 如果有选择文件才继续执行
        if fileName:
            name = fileName.split('/')[-1]
            message = 'put ' + name
            s.send(message.encode())
            with open(fileName, 'rb') as f:
                while True:
                    a = f.read(1024)
                    if not a:
                        break
                    s.send(a)
                time.sleep(0.1)  # 延时确保文件发送完整
                s.send('EOF'.encode())
                tkinter.messagebox.showinfo(title='提示',
                                            message='上传成功!')
        cd('cd same')
        lab()  # 上传成功后刷新显示页面

    # 创建上传按钮, 并绑定上传文件功能
    upload = tkinter.Button(root, text='上传文件', command=put)
    upload.place(x=600, y=353, height=30, width=80)

    # 关闭文件管理器, 待完善
    def closeFile():
        root['height'] = 390
        root['width'] = 580
        # 关闭连接
        s.send('quit'.encode())
        s.close()

    # 创建关闭按钮
    close = tkinter.Button(root, text='关闭', command=closeFile)
    close.place(x=685, y=353, height=30, width=70) 

def file():
    fileClient()
    
# 创建文件按钮
fBut = tkinter.Button(root, text='文件', command=file)
fBut.place(x=185, y=320, width=60, height=30)

# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)  
listbox1.place(x=445, y=0, width=130, height=320)

def users():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1
    
# 查看在线用户按钮
button1 = tkinter.Button(root, text='在线用户', command=users)
button1.place(x=505, y=320, width=70, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=348, width=570, height=40)


def call_robot(url, apikey, msg):
    data = {
        "reqType": 0,
        "perception": {
            # 用户输入文文信息
            "inputText": {  # inputText文本信息
                "text": msg
            },
            # 用户输入图片url
            "inputImage": {  # 图片信息，后跟参数信息为url地址，string类型
                "url": "https://cn.bing.com/images/"
            },
            # 用户输入音频地址信息
            "inputMedia": {  # 音频信息，后跟参数信息为url地址，string类型
                "url": "https://www.1ting.com/"
            },
            # 客户端属性信息
            "selfInfo": {  # location 为selfInfo的参数信息，
                "location": {  # 地理位置信息
                    "city": "杭州",  # 所在城市，不允许为空
                    "province": "浙江省",  # 所在省份，允许为空
                    "street": "灵隐街道"  # 所在街道，允许为空
                }
            },
        },
        "userInfo": {
            "apiKey": "ee19328107fa41e987a42a064a68d0da",  # 你注册的apikey,机器人标识,32位
            "userId": "Brandon"  # 随便填，用户的唯一标识，长度小于等于32位
        }
    }
    headers = {'content-type': 'application/json'}  # 必须是json
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return r.json()


def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    global online_users
    online_users.append('----------群聊----------')
    online_users.append('Robot')
    print(chat)
    if chat not in online_users:
        tkinter.messagebox.showerror('发送失败', message='没有聊天对象!')
        return
    if chat == 'Robot':
        print('Robot')
    if chat == user:
        tkinter.messagebox.showerror('发送失败', message='不能私聊自己!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息

########################################################################################
IsOpen = False
Resolution = 0
Version = 4
ShowMe = True
AudioOpen = True


def video_invite():
    global IsOpen, Version, AudioOpen
    host_name = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    invite = 'INVITE' + host_name + ':;' + user + ':;' + chat  # 添加聊天对象标记
    s.send(invite.encode())
    if not IsOpen:
        vserver = vchat.Video_Server(10087, Version)
        if AudioOpen:
            aserver = achat.Audio_Server(10088, Version)
            aserver.start()
        vserver.start()
        IsOpen = True


def video_accept(host_name):
    global IsOpen, Resolution, ShowMe, Version, AudioOpen
    vclient = vchat.Video_Client(host_name, 10087, ShowMe, Resolution, Version)
    if AudioOpen:
        aclient = achat.Audio_Client(host_name, 10088, Version)
        aclient.start()
    vclient.start()
    IsOpen = False


def kill_process(port):
    taskinfo = os.popen('netstat -ano | findstr ' + str(port))
    line = taskinfo.readline()
    aList = line.split()
    taskinfo.close()
    pid = aList[4]
    os.popen('taskkill /pid %s /f' % pid)



def video_terminate():
    kill_process(10087)
    kill_process(10088)


def video_connect_option():
    global Resolution, ShowMe, Version, AudioOpen

    video_connect_option = tkinter.Toplevel()
    video_connect_option.geometry('160x450')
    video_connect_option.title('Connection option')

    var1 = tkinter.StringVar()
    label1 = tkinter.Label(video_connect_option, bg='yellow', width=20, text='Resolution   ')
    label1.pack()

    def print_resolution():
        global Resolution
        Resolution = var1.get()
        label1.config(text='Resolution   ' + Resolution)

    r0 = tkinter.Radiobutton(video_connect_option, text='0', variable=var1, value='0', command=print_resolution)
    r0.pack()
    r1 = tkinter.Radiobutton(video_connect_option, text='1', variable=var1, value='1', command=print_resolution)
    r1.pack()
    r2 = tkinter.Radiobutton(video_connect_option, text='2', variable=var1, value='2', command=print_resolution)
    r2.pack()
    r3 = tkinter.Radiobutton(video_connect_option, text='3', variable=var1, value='3', command=print_resolution)
    r3.pack()
    r4 = tkinter.Radiobutton(video_connect_option, text='4', variable=var1, value='4', command=print_resolution)
    r4.pack()

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(video_connect_option, bg='yellow', width=20, text='Protocol version   ')
    label2.pack()

    def print_version():
        global Version
        Version = var2.get()
        label2.config(text='Version   IPv' + Version)

    v0 = tkinter.Radiobutton(video_connect_option, text='IPv4', variable=var2, value='4', command=print_version)
    v0.pack()
    v1 = tkinter.Radiobutton(video_connect_option, text='IPv6', variable=var2, value='6', command=print_version)
    v1.pack()

    var3 = tkinter.StringVar()
    label3 = tkinter.Label(video_connect_option, bg='yellow', width=20, text='Show yourself   ')
    label3.pack()

    def print_show():
        global ShowMe
        if var3.get() == '1':
            ShowMe = True
            txt = 'Yes'
        else:
            ShowMe = False
            txt = 'No'
        label3.config(text='Show yourself   ' + txt)

    s0 = tkinter.Radiobutton(video_connect_option, text='Yes', variable=var3, value='1', command=print_show)
    s0.pack()
    s1 = tkinter.Radiobutton(video_connect_option, text='No', variable=var3, value='0', command=print_show)
    s1.pack()

    var4 = tkinter.StringVar()
    label4 = tkinter.Label(video_connect_option, bg='yellow', width=20, text='Audio open   ')
    label4.pack()

    def print_audio():
        global AudioOpen
        if var4.get() == '1':
            AudioOpen = True
            txt = 'Yes'
        else:
            AudioOpen = False
            txt = 'No'
        label4.config(text='Audio open   ' + txt)

    a0 = tkinter.Radiobutton(video_connect_option, text='Yes', variable=var4, value='1', command=print_audio)
    a0.pack()
    a1 = tkinter.Radiobutton(video_connect_option, text='No', variable=var4, value='0', command=print_audio)
    a1.pack()

    def option_enter():
        video_connect_option.destroy()

    Enter = tkinter.Button(video_connect_option, text="Enter", command=option_enter)
    Enter.place(x=10, y=400, width=40, height=35)
    Start = tkinter.Button(video_connect_option, text="Start", command=video_invite)
    Start.place(x=60, y=400, width=40, height=35)
    Kill = tkinter.Button(video_connect_option, text="Kill", command=video_terminate)
    Kill.place(x=110, y=400, width=40, height=35)


buttonCapture = tkinter.Button(root, text="Video", command=video_connect_option)
buttonCapture.place(x=240, y=320, width=60, height=30)

########################################################################################
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '----------群聊----------':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)

# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)
# 用于时刻接收服务端发送的信息并打印,
def recv():
    global online_users
    while True:
        data = s.recv(1024)
        data = data.decode()
        # _users = data # Testing
        # data = json.loads(data)
        print('in client, recv data = ',data)
        print('in client, len(data) = ',len(data))
        print('in client, type(data) = ',type(data))
        print('data[0] = ',data[0])
        print('data[-1] = ',data[-1])
        # Just Testing
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            tmp = []
            if '][' in data:
                data = ','.join(data.split(']['))
            data = json.loads(data)
            online_users = data
            for x in online_users:
                if x not in tmp:
                    tmp.append(x)
            online_users = tmp
            if '_@' in online_users:
                online_users.remove('_@')
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('     在线人数: ' + str(len(online_users)) + ' 人')
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END,fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '----------群聊----------')
            listbox1.insert(tkinter.END, 'Robot')
            listbox1.itemconfig(tkinter.END,fg='green')
            for i in range(len(online_users)):
                listbox1.insert(tkinter.END, (online_users[i]))
                listbox1.itemconfig(tkinter.END,fg='green') 
        except:
            print('in except')
            data = data.split(':;')
            if not (len(data) == 3 or len(data) == 4):
                continue
            data1 = data[0].strip()  # 消息
            data2 = data[1]  # 发送信息的用户名
            data3 = data[2]  # 聊天对象
            if 'INVITE' in data1:
                if data3 == 'Robot':
                    tkinter.messagebox.showerror('连接失败', message='不能与机器人视频聊天!')
                elif data3 == '----------群聊----------':
                    tkinter.messagebox.showerror('连接失败', message='暂不支持群视频聊天!')
                else:
                    video_accept(data1[data1.index('INVITE')+6:])
                continue
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '----------群聊----------':
                    if data2 == '\n' + user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行 
                if pic[0] == '``':
                    # 从服务端下载发送的图片
                    fileGet(pic[1])
                else:
                    # 将表情图贴到聊天框
                    listbox.image_create(tkinter.END, image=dic[markk])
            else:
                data1 = '\n' + data1
                if data3 == '----------群聊----------':
                    if data2 == '\n' + user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'red')
                elif data3 == 'Robot':
                    print('Here:Robot')
                    apikey = 'ee19328107fa41e987a42a064a68d0da'
                    url = 'http://openapi.tuling123.com/openapi/api/v2'
                    print('msg = ', data1)
                    listbox.insert(tkinter.END, data1, 'blue')
                    reply = call_robot(url, apikey, data1.split('：')[1])
                    reply_txt = '\nRobot:' + reply['results'][0]['values']['text']
                    listbox.insert(tkinter.END, reply_txt, 'red')
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行 
            listbox.see(tkinter.END)  # 显示在最后
            
        
r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
