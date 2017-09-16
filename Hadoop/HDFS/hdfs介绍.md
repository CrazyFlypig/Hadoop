# HDFS
## Hadoop Distributed File System
1. 易于扩展的分布式文件系统
2. 运行在大量廉价机器，提供容错机制
3. 为大量用户提供系能不错的文件存取服务。
### 优点
* 高容错性
    - 数据自动保存多个副本
    - 副本丢失后，自动恢复
* 适合批处理
    - 移动计算而非数据
    - 数据位置暴露给计算框架
* 适合大数据处理
    - GB、TB甚至PB级数据
    - 百万规模上的文件数量
    - 10K+节点规模
* 流式文件访问
    - 一次写入，多次读取
    - 保证数据一致性
* 可构建在廉价机器上
    - 通过多副本提高可靠性
    - 提供容错和恢复机制
### 缺点
* 不适合低延迟数据访问
    * 比如毫秒级
    * 低延迟与高吞吐量，牺牲低延迟提高吞吐量
* 不适合小文件存储
    * 采用M/S结构，小文件数量多时，占用namenode大量内存
    * 读小文件时，寻道时间超过读取时间，不利于大数据处理
    * 提供小文件合并，解决这个缺点
* 不适合并发写入、随机修改
    * 一个文件只能有一个写入者
    * 仅支持append操作
## HDFS基本架构和原理
### 架构
* Master-Slave结构
    * ActiveNameNode
        * 主Master（只有一个）；
        * 管理HDFS的名称空间；
        * 管理数据块映射信息；
        * 配置副本策略；
        * 处理客户端读写请求。
    * StandbyNameNode
        * NameNode的热备份；
        * 定期合并fsimage和fsedits，推送给NameNode；
        * 当ActiveNameNode出现故障时，快速切换为新的ActiveNameNode。
    * DataNode
        * Slave（有多个）；
        * 存储实际的数据块；
        * 执行数据块读/写。
    * Client
        * 文件切分
        * 与NameNode交互，获取文件位置信息；
        * 与DataNode交互，读取或写入数据；
        * 管理HDFS；
        * 访问HDFS。 
* HDFS数据块（block）
    - 文件被切分成固定大小的数据块
        + 默认64M，可配置
        + 若一个文件大小不到64MB，则单独成一个块。
    - 数据块大小设置原则
        + 数据传输时间远大于寻道时间（高吞吐率）
    - 一个文件的存储方式
        + 按大小被切分成若干个block，存储到不同节点上
        + 默认情况下每个block有三个副本
* HDFS的写流程
![](http://i.imgur.com/tFL8sjF.png)
* HDFS的读流程
![](http://i.imgur.com/cNrvbhA.png)
* HDFS典型物理拓扑
![](http://i.imgur.com/D9FMNNj.png)
    * 节点距离：两个节点到达最近的共同的祖先的跃点（经过交换机的次数）数。
    * 同一个节点的两个进程： 0
    * 同一机架不同节点的两个进程： 2
    * 不同一机架不同节点的两个进程： 4
* 副本节点的选择（机架感知 Rack Awarence）
1. hadoop2.7.2
    * 第一个副本在client所处的节点上。如果客户端在集群外，在随机选择一个节点。
    * 第二个副本和第一个副本相同机架，不同节点
    * 第三个副本位于不同机架
2. 自定义机架感知
    1. 创建类实现DNSToSwitchMapping接口
    2. 配置文件````core-site.xml````,进行分发
    ````xml
    <property>
        <name>net.topology.node.switch.mapping.impl</name>
        <value>org.apache.hadoop.net.ScriptBasedMapping</value>
    </property>
    ````
    3. 编译程序，打成jar，分发所有节点的hadoop的classpath下
        * /hadoop/shared/common/lib
    4. 分发jar
## HDFS的可靠性策略
1. 文件损坏
    * 文件完整性：为每个block设置校验码
        - CRC32校验
        - 用其它副本文件取代损坏文件
2. 网络或机器失效
    * Heartbeat
        - Datanode定期向Namenode发heartbeat
3. NameNode挂掉
    * 元数据信息
        - FSImage（文件系统镜像）、Editlog（操作日志）
        - 多份存储
        - 主备NameNode实时切换