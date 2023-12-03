查看mysql数据库
netstat -tunlp | grep 3306

挂载
mount [-t 文件系统] 设备文件名 挂载点

awk 命令
[root@zhangRabbitMQ zhang]# vi /tmp/student.txt
id      name    java    linux   mysql
1       bilei   88      88      88
2       zhang   60      60      60
[root@zhangRabbitMQ zhang]# awk '{printf $2 "\t" $5 "\n"}' /tmp/student.txt
name	mysql
bilei	88
zhang	60

sed命令
sed 是一种几乎包括在所有 UNIX 平台（包括 Linux）的轻量级流编辑器。sed主要是用来将数据进行选取、替换、删除、新增的命令。
[root@localhost ~]# sed [选项] ‘[动作]’ 文件名
选项：  
    -n：  一般sed命令会把所有数据都输出到屏幕 ，  如果加入此选择，则只会把经过           		sed命令处  理的行输出到屏幕。 
    -e： 允许对输入数据应用多条sed命令编辑 
    -i：  用sed的修改结果直接修改读取数据的文件，  而不是由屏幕输出
 
动作：  
    a \：  追加，在当前行后添加一行或多行。添加多行时，除最后 一行  外，每行末尾需要用“\”代	     		表数据未完结。 
    c \：  行替换，用c后面的字符串替换原数据行，替换多行时，除最  后一行外，每行末尾需“\”代   		表数据未完结。
    i \：  插入，在当期行前插入一行或多行。插入多行时，除最后 一行  外，每行末尾需要“\”代
表数据未完结。 
    d：  删除，删除指定的行。 
    p：  打印，输出指定的行。 
    s：  字串替换，用一个字符串替换另外一个字符串。格式为“行范  围s/旧字串/新字串/g”（和vim
中的替换格式类似）。

sort命令
[root@localhost ~]# sort [选项] 文件名
选项： 
    -f：  忽略大小写  
    -n：  以数值型进行排序，默认使用字符串型排序  
    -r：  反向排序  
    -t：  指定分隔符，默认是分隔符是制表符  
    -k n[,m]： 按照指定的字段范围排序。从第n字段开始，m字段结束（默认到行尾）  

wc命令
[root@localhost ~]# wc [选项] 文件名
选项：  
    -l： 只统计行数  
    -w： 只统计单词数  
    -m： 只统计字符数
 