# bili_video_history_record
在某个心理学实验研究项目中，用来统计被试b站视频浏览记录的简易爬虫。
需要用户主动授权，扫码登陆才能实现后续功能。

## 使用
该程序已使用pyinstaller打包为exe文件，您可以在最新的release中找到：https://github.com/SherlockChiang/bili_video_history_record/releases/tag/packed

双击bili.exe文件即可运行

运行后会呈现终端，并打开一张二维码图片。此时，需要使用b站app扫码登陆。

b站扫码步骤：打开右下角“我的”界面，扫一扫在最上方的位置
![image](https://github.com/SherlockChiang/bili_video_history_record/assets/98642231/e9db33d2-09d5-4829-b394-25b49f6425bf)

点击确认即可获取浏览记录信息

**在这里，我们仅仅用到您观看不同种类视频的数量，也就是最后产生的tensor.xls文件中记录的信息**

之后，屏幕上会呈现一个您浏览记录的观看报告，您可以自行保存

报告生成即代表程序已运行完毕，之后您可以随时关闭并删除程序

但是，请务必将tensor.xls文件发送给主试，因为本程序没有将数据发送到我的服务器，完全通过手动提交数据以保证隐私
