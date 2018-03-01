# HDFS 使用

可以通过许多不同的方式从应用程序访问hdfs。在本质上，hdfs提供了一个供应用程序使用的文件系统java api。此java java api和rest api的c语言包装器也可用。另外还有一个http浏览器，也可以用来浏览hdfs实例的文件。通过使用nfs网关，可以将hdfs作为客户端本地文件系统的一部分加载。

## FS Shell

hdfs允许用户数据以文件和目录的形式组织。它提供了一个名为fs shell的命令行界面，可让用户与hdfs中的数据进行交互。这个命令集的语法类似于用户已经熟悉的其他shell（例如bash，csh）。

对于HDFS来说，fs是启动命令行的动作，一般形式“hadoop fs -cmd< args>","cmd"是子命令，而”args”是具体的命令操作。这里有一些示例动作/命令对：

| Action                                   | Command                                  |      |
| ---------------------------------------- | ---------------------------------------- | ---- |
| 创建一个目录 '/foodir'                   | `bin/hadoop dfs -mkdir /foodir`          |      |
| 查看一个文件的内容 '/foodir/myfile.txt'  | `bin/hadoop dfs -cat /foodir/myfile.txt` |      |
| 将一个文件从HDFS系统中复制到本地         | `hadoop fs -copyFromLocal <localsrc>URI` |      |
| 显示目录中所有文件大小，也可指定某一文件 | `hadoop fs -du URI`                      |      |
| 显示目标文件大小                         | `hadoop fs -dus <args>`                  |      |
| 清空回收站                               | `hadoop fs -expuge`                      |      |
| 复制文件到本地文件系统                   | `hadoop fs -get <locaodst>`              |      |
| 从本地可复制可多个源路径到目标文件系统   | `hadoop fs -put<localsrc> <dst>`         |      |
| 改变一个副本的复制份数                   | `hadoop fs -setrep [R] <path>`           |      |

注：文件并没有书写绝对路径，而是对相对路径进行了简化，绝对路径前的地址在搭建HDFS系统时已经通过core-site.xml进行了指定；大部分命令与 Linux 类似；`bin/hadoop dfs`等价于`Hadoop fs`。

fs shell针对需要脚本语言与存储数据进行交互的应用程序。

## DFSAdmin

dfsadmin命令集用于管理hdfs集群。这些是仅由hdfs管理员使用的命令。这里有一些示例动作/命令对：

| Action                      | Command                              |
| --------------------------- | ------------------------------------ |
| Put the cluster in Safemode | ` bin/hdfs dfsadmin -safemode enter` |
| 生成一个datanode列表        | `bin/hdfs dfsadmin -report`          |
| 重新调试或停用datanode（s） | ` bin/hdfs dfsadmin -refreshNodes`   |

## Browser Interface

一个典型的hdfs安装配置一个Web服务器，通过一个可配置的tcp端口公开hdfs命名空间。这允许用户使用Web浏览器来浏览hdfs命名空间并查看其文件的内容。

## 空间回收

### 文件删除和取消删除

如果启用垃圾箱配置，则不会立即从hdfs中删除由fs shell删除的文件。相反，hdfs将其移动到垃圾目录（每个用户在/user/\<username>/.trash下都有自己的垃圾目录）。只要文件保留在垃圾箱中，该文件可以快速恢复。

最近删除的文件将移至当前的垃圾目录（/user/\<username>/.trash/current），并且在可配置的时间间隔内，hdfs会创建检查点（位于/user/\<username>/.Trash/\<date>）查找当前垃圾目录中的文件，并在旧的检查点过期时删除它们。请参阅[清除fs shell 命令](http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html#expunge)中关于检查垃圾桶的命令。

在垃圾箱中的生命到期后，namenode将从hdfs命名空间中删除该文件。删除文件会导致与该文件关联的块被释放。请注意，在用户删除文件的时间与hdfs中相应增加空闲空间的时间之间可能存在明显的时间延迟。

以下是一个将显示如何通过fs shell从hdfs中删除文件的示例。我们在目录delete下创建了2个文件（test1＆test2）

```shell
$ hadoop fs -mkdir -p delete/test1
$ hadoop fs -mkdir -p delete/test2
$ hadoop fs -ls delete/
Found 2 items
drwxr-xr-x   - hadoop hadoop          0 2015-05-08 12:39 delete/test1
drwxr-xr-x   - hadoop hadoop          0 2015-05-08 12:40 delete/test2
```

我们将删除文件test1。下面的信息显示该文件已被移至垃圾目录。

```shell
$ hadoop fs -rm -r delete/test1
Moved: hdfs://localhost:9820/user/hadoop/delete/test1 to trash at: hdfs://localhost:9820/user/hadoop/.Trash/Current
```

现在我们将使用skiptrash选项删除文件，该选项不会将文件发送到垃圾箱，它将从hdfs中完全删除。

```shell
$ hadoop fs -rm -r -skipTrash delete/test2
Deleted delete/test2
```

我们现在可以看到垃圾目录仅包含文件test1。

```shell
$ hadoop fs -ls .Trash/Current/user/hadoop/delete/
Found 1 items\
drwxr-xr-x   - hadoop hadoop          0 2015-05-08 12:39 .Trash/Current/user/hadoop/delete/test1
```

### 减少副本因子

当文件的复制因子减少时，NameNode会选择可以删除的多余副本。下一次心跳将该信息传输到数据节点。DataNode然后删除相应的块，并在群集中出现相应的空闲空间。再次说明，在完成setreplication API调用和集群中可用空间的出现之间可能存在一段时间延迟。

## 链接：

[Hadoop Java API ](http://hadoop.apache.org/docs/current/api/)

[HDFS source code](http://hadoop.apache.org/version_control.html)