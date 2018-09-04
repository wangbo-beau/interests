背景：我们宿舍有一个路由器，大家回去玩手机基本都连得它，然后没想到把免费流量给用超了，两个月超了60块，好心疼，
于是我就写了这个程序。

功能：程序的功能主要是当在使用电脑时，运行它，它会自动判断宿舍人的账号谁的剩余流量最多，并自动登录外网认证系
统，基本上也就不担心路由器登一个人的账号造成流量不够用，也省去了手动登录外网认证系统的麻烦，windows下
只要双击bat文件即可，linux或mac下需要python netflow.py来运行。

程序基于python3，需要自行安装bs4模块和selenium，用pip安装超级简单。文件说明如下：
1. user.conf里面存储校园网的认证登录用户名和密码，每一行放一个账户，数量>=1即可；
2. login_log.txt里面存储最近一次登录的用户名；
3. currentInfos.txt里面存储最近一次查询的各个账户的流量使用信息；
4. netflow.py是程序的源码；
5. run_netflow.bat是windows下的脚本文件，双击可直接运行，相当于在cmd里输入python netflow.py;
6. 使用前确保已经安装过Python的bs4和selenium模块，如果没有则自行安装，可在命令行下输入以下命令：

   安装bs4：pip install bs4   安装selenium：pip install selenium
