## HDFS客户端命令
对于HDFS来说，fs是启动命令行的动作，一般形式“hadoop fs -cmd< args>","cmd"是子命令，而”args”是具体的命令操作。例如对于帮助文件的获取，

    $hadoop fs -help
HDFS常用的文件操作命令如下：
**1.cat**
使用方法：hadoop fs -cat URI
说明：将路径指定的文件输出到屏幕上
实例：

    hadoop fs -cat hdfs://host1:port1/file
    hadoop fs -cat file://file3
**2.-copyFromaLocal**
使用方法:

    hadoop fs -copyFromLocal <localsrc>URI
说明：将一个文件从HDFS系统中复制到本地文件夹。
**4.-cp**
使用方法：

    hadoop fs -cp URI
说明：将文件从源路径复制到目标路径。这个命令可以复制多个源路径，但是目标路径必须是一个目录。
示例：

    hadoop fs -cp /user/file /user/files
    Hadoop fs -cp /user/file1 /user/files /user/dir
**5.du**
使用方法：

    hadoop fs -du URI
说明：显示目录中所有文件大小，或者指定一个文件时，显示此文件的大小。
示例：

    hadoop fs -du /user/dir1
    Hadoop fs -du hdfs://host:port/user/file
**6.-dus**
使用方法：

    hadoop fs -dus <args>
说明：显示目标文件大小
**7.-expunge**
使用方法：

    hadoop fs -expuge
说明：用于清空回收站
**8.-get**
使用方法：

    hadoop fs -get <locaodst>
说明：复制文件到本地文件系统
示例：

    hadoop fs -get /user/file localfile
    Hadoop fs -get hdfs://host:port/file localfile
**9.-ls**
使用方法：

    hadoop fs -ls <arg>
说明：浏览本地文件夹，并按如下格式返回文件信息。
文件名<副本数> 文件大小 修改日期 权限 用户ID/组ID
如果浏览的是一个目录，则返回其子文件的一个列表，信息如下：
目录名< dir> 修改日期 修改时间 权限 用户ID/组ID
**10.-lsr**
使用方法：

    hadoop fs -lsr
说明：递归地查阅文件内容
**11.-mkdir**
使用方法：

    hadoop fs -mkdir<path>
说明；创建相应的文件目录，并直接创建相应的父目录
示例：

    hadoop fs -mkdir /user/dir1/dir2/dir3/file
    Hadoop fs -mkdir hdfs://host:port/user/dir
**12.-mv**
使用方法：

    hadoop fs -mv URI <dest>
说明：将源文件移动到目标路径，目标路径可以有多个，但不允许在不同的文件系统中移动。
示例：

    hadoop fs -mv /user/file1 /user/file2
    Hadoop fs -mv hdfs://host:poor/file hdfs://host:port/file2
**13.-put**
使用方法：

    hadoop fs -put<localsrc> <dst>
说明：从本地文件系统复制单个或多个源路径到目标文件系统
示例：

    hadoop fs -put localfile /user/file
    hadoop fs -put localfile hdfs://host:port/user/file
**14.-rm**
使用方法；

    hadoop fs -rm URI
说明：删除指定文件，且要求非空的目录和文件。
示例：

    hadoop fs -rm hdfs://host:port/file
**15.-rmr**
使用方法:

    hadoop fs -rmr URI
说明：递给地删除指定文件中的空目录
**16.-Setrep**
使用方法：

    hadoop fs -setrep [R] <path>
说明：改变一个副本的复制份数
示例；

    hadoop fs -setrep -w 3 -R /user/file
**17.-Test**
使用方法:

    hadoop fs -test -[ezd] URI
说明；使用ezd对文件进行检查
**-e**检查文件是否存在，若存在返回值为0
**-z**检查文件中是否为0字节，如果是，返回0；
**-d**检查路径是否为目录，如果是，返回1，否则返回0
**18.-text**
使用方法；

    hadoop fs -text <src>
说明：将源文件输出为文本格式，运行格式是zip以及Text类

提示：文件并没有书写绝对路径，而是对相对路径进行了简化，绝对路径前的地址在搭建HDFS系统时已经通过core-site.xml进行了指定。