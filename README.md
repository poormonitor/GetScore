# GetScore
分数，拿来！

欢迎使用GetScore，本项目旨在快速从浙江省教育考试院获取你的考试成绩。

本项目使用Selenium模拟浏览器行为，腾讯云提供的API作验证码识别

## Usage

1. Clone本项目

2. 安装requirements:

   ```bash
   pip(3) install -r requirements.txt
   ```

   随后，从[Selenium网站](https://www.selenium.dev/documentation/zh-cn/webdriver/driver_requirements/)下载你所用浏览器的驱动，并放置在系统环境下。

   **注意，如果你使用的不是Firefox，那么需要将34行的Firefox改为你自己的浏览器。**

3. 修改config.json

   其中，tencent_id和tencent_key为你在腾讯云申请的id和key，id为教育考试院注册用的身份证号，passwd为你的密码。

4. 运行

   使用Python命令执行index.py

   ```bash
   python(3) index.py
   ```

5. 查看

   在result.png中存有相应的屏幕截图，而index.html中是查分界面的网页代码。

## License 

[GPL v3](https://www.gnu.org/licenses/gpl-3.0-standalone.html)

