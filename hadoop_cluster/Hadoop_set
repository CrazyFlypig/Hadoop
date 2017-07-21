# Hadoop安装及配置
## Hadoop组成
1. common
2. hdfs
      * hadoop distributed file system    //分布式文件系统
      * NameNode    //名称节点
      * DataNode    //数据节点
      * SecondaryNameNode    //辅助数据节点
3. yarn
  资源调度框架
      * ResourceManager    //资源管理器
      * NodeManager    //节点管理器
4. mpred
  编程模型，map+reduce
## hadoop分类
1. standalone/local（默认）
    本地模式
    所有的程序运行在一个JVM中。不需要启动hadoop进程。应用的文件系统是本地文件系统
2. pseudo
    伪分布模式
    完全类似于完全分布，但是只有一个节点
    [配置文件xml文件格式]
````xml
    [core-site.xml]
    fs.defaultFS=hdfs://localhost/
    [hdfs-site.xml]
    dfs.dreplication=1
    [mapreduce-site.xml]
    mapreduce.framework.name=yarn
    [yarn-site.xml]
    yarn.resourcemanager.hostname=localhost
    yarn.nodemanager.aux-services=shuffle
````
3. full distributed
    完全分布式
## ssh
 配置安全登录
 1. 安装ssh。````sudo apt-get install ssh````
 2. 查看进程。
````shell
ps -Af | grep ssh        //查看ssh服务
....sshd            //守护进程
````
3. 远程配置无密登陆。    ````ssh-copy-id -i user@hostname````
3. 生成公私密钥。````ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa ````
4. 生成公钥和私钥
````shell
~/.ssh/id_rsa    //私钥
~/.ssh/id_rsa.pub    //公钥
````
 5. 添加公钥到授权key文件
```` cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys````
 6. 登录localhost
````ssh localhost    //首次登录需要确认yes````
 7. 退出。    ````exit````
## 使用web访问hadoop hdfs
1. hdfs web。
    http://localhost:50070/
2. data node
    http://localhost:50075/
3. 2name node
    http://localhost:50090/
## 完全分布式
1. 准备客户机
2. 安装jdk
3. 配置环境变量
4. 安装hadoop
5. 配置环境变量
6. 安装ssh，配置无密登录
7. 配置文件
````XML
[.../hadoop/etc/hadoop/core-site.xml]
    fs.defaultFS=hdfs://'主机名':9000
[.../hadoop/etc/hadoop/hdfs-site.xml]
    replication=3
[.../hadoop/etc/hadoop/yarn-site.xml]
    yran.resourcemanager.hostname='主机名'
[.../hadoop/etc/hadoop/slaves]
````
8. 在集群上分发以上三个文件
````shell
    cd XXX/hadoop/etc/hadoop
    sxync.py core-site.xml
    xsync.py yarn-site.xml
    xsync.py slaves
````
9. 格式化namenode
10. 启动集群
## rsync
 远程同步工具，主要用于备份和镜像
 支持链接，设备等
 速度快，避免复制相同内容
 不支持两个远程主机之间的复制````rsync -rvl 文件 用户@地址：路径````
## 自定义脚本 xsync
 循环复制文件到所有节点的相同目录下，基于rsync命令
## 考察本地文件内容
1. Master/XXX/dfs/name/current/VERSION-------namenode
````
    #Tue Jul 18 08:46:18 CST 2017
    namespaceID=500535175
    clusterID=CID-d630c1a2-caff-428b-871b-9887a0b556b9
    cTime=0
    storageType=NAME_NODE
    blockpoolID=BP-1354839561-192.168.1.108-1500338778223
    layoutVersion=-60
````
2.Node1/XXX/dfs/data/current/VERSION------datanode
````
    #Tue Jul 18 13:32:30 CST 2017
    storageID=DS-7b236e7b-3d17-47fa-911d-675e8fd89f1a
    clusterID=CID-d630c1a2-caff-428b-871b-9887a0b556b9
    cTime=0
    datanodeUuid=00cd448e-12ad-40a0-a014-02f989214fc4
    storageType=DATA_NODE
    layoutVersion=-56
````
3.Node2 XXX/dfs/data/current/VERSION------datanode
````
    #Tue Jul 18 08:51:46 CST 2017
    storageID=DS-3cf965c5-20b0-4059-a4c5-26cb5b0a86c3
    clusterID=CID-d630c1a2-caff-428b-871b-9887a0b556b9
    cTime=0
    datanodeUuid=cd34f66f-26f5-408a-bc7e-c12331cc9c82
    storageType=DATA_NODE
    layoutVersion=-56
````