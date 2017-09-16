# HA部署
## 
* nameservice ID有多个NN构成。
## 配置细节（hdfs-site.xml)
    1. dfs.nameservices，名称服务逻辑名。
    `dfs.nameservices=mycluster`
    2. dfs.ha.namenodes[nameservices ID]，指定该名称服务下有多少个namenode ID。
    `dfs.ha.namenodes.mycluster=nn1,nn2`
        * **注意**：当前最多支持2个NN。
    3. dfs.namenode.rpc-address.[nameservices ID].[name node ID]
    ````xml
        <property>
            <name>dfs.namenode.rpc-address.mycluster.nn1</name>
            <value>s100:8020</value>>
            <name>dfs.namenode.rpc-address.mycluster.nn2</name>
            <value>s200:8020</value>
        </property>
    ````
    4. dfs.namenode.http-address.[nameservice ID].[name node ID]，配置每个nn的web端口
    ````xml
        <property>
            <name>dfs.namenode.http-address.mycluster.nn1</name>
            <value>s100:50070</value>
            <name>dfs.namenode.http-address.mycluster.nn2</name>
            <value>s200:50070</value>
        </property>
    ````
    5. dfs.namenode.shared.edits.dir，配置JN上编辑日志存放地址。
    ````xml
        <property>
            <name>dfs.namenode.shared.edits.dir</name>
            <value>qjournal://s101:8485,s102:8485,s103:8485/mycluster</value>
        </property>
    ````
    6. dfs.client.failover.proxy.provider.[nameservice ID]，配置客户端代理供应商，客户端通过该类判断哪个nn是active状态，进行请求提交。
    ````xml
        <property>
            <name>dfs.client.failover.proxy.provider.mycluster</name>
            <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
        </property>
    ````
    7. dfs.ha.fencing.methods，防护方法，配置的是java类或者脚本列表，容灾时保护active NN。
    ````xml
        <property>
            <name>dfs.ha.fencing.methods</name>
            <value>sshfence</value>
        </property>
        <property>
            <name>dfs.ha.fencing.ssh.private-key-files</name>
            <value>/home/exampleuser/.ssh/id_rsa</value>
        </property>
    ````
    8.fs.defaultFS，[core-site.xml]
    ````xml
        <property>
            <name>fs.defaultFS</name>
            <value>hdfs://mycluster</value>
        </property>
    ````
    9. dfs.journalnode.edits.dir，JN存储edit文件的本地目录，绝对路径。可以冗余多个
    ````xml
        <property>
            <name>dfs.journalnode.edits.dir</name>
            <value>/path/to/journal/node/local/data</value>
        </property>
    ````
## 部署细节
1. 配置完成后，需要在JN上启动守护进程。执行命令：`$>hadoop-daemon.sh start journalnode`。
2. 启动JN守护进程后，对两个NN节点在disk-meta上进行同步。情况有三：
    *. a)如果搭建全新的HDFS集群，先在其中一个NN上格式化（`hdfs namenode -format`);
    *. b)如果已经格式化了NN，或者从非HA转换成HA，需要复制NN的元数据目录到另一个，在未格式化的NN上运行命令：`hdfs namenode -bootstartStandby`，该命令的作用是确保JN包含足够多的编辑日志能够启动两个NN。
    *. c)如果正在转换非HA NN到HA的NN，需要运行`hdfs namenode -initializeSharedEdits`命令，该命令会用本地的编辑日志目录初始化JN。
3. 单独启动NN,通过webUI查看状态，初始时都是standby状态。
## 管理命令
* hdfs haadmin -help
1. transitionToActive/transitionToStandby，切换状态
2. failover，initiate a failover between two NameNodes
3. getServiceState，查询服务状态
4. checkHealth，健康检查