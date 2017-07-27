# HBase 分布式部署
1. 配置JDK
2. HBase安装\
3. 修改系统变量
4. 修改````/hbase/conf/hbase-env.sh````,为其添加````JAVA_HOME````。
## 伪分布 psesudo
## 完全分布式
1. 安装Zookeeper
2. 修改配置文件
* 配置[conf/hbase-site.xml]文件
	* hbase.rootdir=hdfs://Master:9000/hbase	是RegionServer的共享目录，用来持久化HBase
	* dfs.replication=3		
	* hbase.cluster.distributed=true	HBase的运行模式。若为false，HBase和Zookeeper会运行在同一个JVM中，默认false
	* hbase.zookeeper.quorm=node1,node2,node3	Zookeeper主机，默认是localhost。hbase-env.sh中设置HBASE_MANAGES_ZK为true，则Zookeeper节点就和Hbase一起启动。
	* hbase.zookeeper.property.dataDir=/home/hadoop/zookeeperdata	设置Zookeeper快照的存储位置，默认/tmp
* 配置[regionservers]文件
	* 列出运行RegionServer主机，一行一个主机名
* 配置[hbase-env.sh]
	* HBASE_MANAGES_ZK=true		让HBase和Zookeeper同时启动，默认值是true。
3. 替换Hadoop的jar包
* 复制Hadoop安装路径的lib目录下的hadoop-core-*.jar包到HBase的lib目录下覆盖HBase自带的Hadoop jar包。
4. 分发配置
* 向各个主机分发hbase目录
5. 重启客户机
6. 启动hbase集群，在namenode上启动
* start-hbase.sh
* stop-hbase.sh
7. 查看进程
	* xcall jps
	* hmaster	//master
	* hregionserver		//reginserver
	* hquorumpeer		//zk
## zookeeper安装
1. 下载zk
2. 安装jdk
3. 安装zookeeper
4. 配置环境变量
	1. ZOOKEEPER_HOME
	2. PATH
5. 配置zookeeper
	1. [conf/zoo_sample.conf]
	````xml
		# 每次心跳的毫秒数
		tickTime=2000
		#开始同步阶段的心跳数
		initLimit=10
		#发送请求和得到确认之间可以传递的心跳个数
		syncLimit=5
		# 存放zk的快照目录，不要存在/tmp下
		dataDir=/tmp/zookeeper
		#客户端连接的端口
		clientPort=2181
		#客户端最大连接数
		maxClientCnxns=60
		#在datadir保留的快照数量
		#autopurge.snapRetainCount=3
		#丢弃任务的间隔时间（小时数）
		#autopurge。purgeInterval=1
	````
6. 部署zookeeper
	1. 单机版
		1. 创建配置````conf/zoo.cfg````配置
		````xml
			tickTime=2000
			dataDir=/path/to/zookeeper/data
			clientPort=2181
			initLimit=5
			syncLimit=2
		````
		2. 启动zkServer
			* $>bin/zkServer.sh start
		3. 启动zkClient
			* $>zkCli.sh
	2. 伪分布 
	3. 完全分布式
		1. 确定主机
		2. 配置````${datadir}/myid````文件
		3. 配置zoo.fcg,默认的配置文件
# 配置HBase使用外部独立Zookeeper集群
