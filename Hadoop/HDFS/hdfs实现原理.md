# HDFS实现原理
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
* 高吞吐量，适合大数据处理
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
### 数据复制

HDFS将每个文件存储为一系列块，一个文件中除了最后一个块，其余块都具有相同的大小。文件块的复制提供数据容错。块大小和块副本数都是可配置的，应用程序可以指定文件的副本数量。副本因子可以在文件创建时指定也可以在后面进行更改。

NameNode 决定着所有备份块的相关信息。它定期接收集群中每个DataNode的一个心跳和一个块报告，收到心跳意味着这个DataNode的功能正常，块报告包含了这个DataNode的所有块信息列表。

#### 副本放置：第一步

副本放置采用机架感知的目的是提高数据的可靠性、可用性和网络带宽的利用率。NameNode 通过[机架感知]()决定了每个 NameNode 属于哪个机架。

一个简单的副本放置策略是将每个数据块放置在不同的机架上，有效防止了因整个机架挂掉而导致的数据丢失，同时也允许了使用多个机架的带宽进行读数据。并且当组件出问题时也可以使数据均衡的负载在集群中。但是这个策略提升了写数据的代价，因为一个写线程需要在多个机架上传送。

常见的副本放置策略，如 Hadoop2.7.2 的副本节点选择策略。这个放置策略，削减了机架间的写数据的通信成本。并且没有降低数据的可靠性和可用性。但是，相比于三个机架，它的确降低了在读取数据时总的网络带宽使用率。并且文件的副本不均匀的分布在机架上。总体上说，这种副本放置策略，提高了数据的写性能，但不影响数据的可靠性和读性能。

如果复制因子大于3，则第四个副本和之后的副本基于每个机架同时保证副本数量低于上限。（取决于：$(replics - 1)/racks +2$）。

在支持[存储类型和存储策略](http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/ArchivalStorage.html)后，除了机架感知 NameNode 也考虑副本放置的存储策略。The NameNode chooses nodes based on rack awareness at first, then checks that the candidate node have storage required by the policy associated with the file. If the candidate node does not have the storage type, the NameNode looks for another node. If enough nodes to place replicas can not be found in the first path, the NameNode looks for nodes having fallback storage types in the second path.

#### 副本选择

为了减少全局带宽消耗和降低延迟，HDFS 尝试满足读请求的副本是离客户端最近的。选择范围由同一机架不同节点、同一数据中心不同机架和不同数据中心逐渐扩大。

-   HDFS典型物理拓扑
    ![](http://i.imgur.com/D9FMNNj.png)
    -   节点距离：两个节点到达最近的共同的祖先的跃点（经过交换机的次数）数。
    -   同一个节点的两个进程： 0
    -   同一机架不同节点的两个进程： 2
    -   不同一机架不同节点的两个进程： 4
-   副本节点的选择（机架感知 Rack Awarence）

1.  hadoop2.7.2

    -   第一个副本在client所处的节点上。如果客户端在集群外，在随机选择一个节点。
    -   第二个副本和第一个副本相同机架，不同节点
    -   第三个副本位于不同机架

2.  自定义机架感知

    1.  创建类实现DNSToSwitchMapping接口
    2.  配置文件````core-site.xml````,进行分发

    ```xml
    <property>
        <name>net.topology.node.switch.mapping.impl</name>
        <value>org.apache.hadoop.net.ScriptBasedMapping</value>
    </property>
    ```

    1.  编译程序，打成jar，分发所有节点的hadoop的classpath下
        -   /hadoop/shared/common/lib
    2.  分发jar



#### 安全模式

在启动时，NameNode 会首先进入安全模式。安全模式下，数据复制不会发生。NameNode接收来自所有 DataNode  的心跳和块报告信息。一份块报告，包含了一个 DataNode 的块列表。每个块都有一个指定的最小副本数。当 NameNode检测确认某个数据块的副本数目达到这个最小值，则认为该数据块是副本安全的(safely replicated)的。在一个百分比（参数可配）的数据块被确认为安全后（加上额外的30秒等待时间），NameNode 将退出安全模式。并对不安全的数据块进行副本复制。

### 文件系统元数据的持久化

NameNode 使用 EditLog 的事务日志记录 NameNode对任何文件系统元数据的操作，EditLog被存储在本地文件系统中。整个文件系统的名字空间，包括数据块到文件的映射、文件的属性等，都被存储在 FsImage中，FsImage同样被存储在本地文件系统。

NameNode在内存中保存着整个文件系统的名字空间和文件数据块映射(Blockmap)的映像。当 NameNode启动时，它从硬盘读取 EditLog和 FsImage，将所有的 EditLog中的事务作用在内存中的 FsImage上，并将这个新版本的 FsImage保存到硬盘上，然后删除 EditLog，这个过程称为一个**检查点(checkpoint)**。

Datanode将HDFS数据以文件的形式存储在本地的文件系统中，它并不知道有关HDFS文件的信息。它把每个HDFS数据块存储在本地文件系统的一个单独的文件中。Datanode并不在同一个目录创建所有的文件，实际上，它用试探的方法来确定每个目录的最佳文件数目，并且在适当的时候创建子目录。在同一个目录中创建所有的本地文件并不是最优的选择，这是因为本地文件系统可能无法高效地在单个目录中支持大量的文件。当一个 DataNode启动时，它会扫描本地文件系统，产生一个这些本地文件对应的所有HDFS数据块复制列表，然后作为报告发送到 NameNode，这个状态就是块状态报告。

### 通信协议

所有的HDFS通信协议都是建立在TCP/IP协议上。客户端通过一个可配置的TCP端口连接到NameNode，通过ClientProtocol协议与NameNode交互。而DataNode使用DatanodeProtocol协议与NameNode交互。一个远程过程调用(RPC)模型被抽象出来封装ClientProtocol和DatanodeProtocol协议上。在设计上，Namenode不会主动发起RPC，而是响应来自客户端或 Datanode 的RPC请求。

### 健壮性

HDFS的主要目标就是即使在出错的情况下也要保证数据存储的可靠性。常见的三种出错情况是：Namenode出错, Datanode出错和网络割裂(network partitions)。

#### 磁盘数据错误、心跳检测和重新复制

每个Datanode节点周期性地向Namenode发送心跳信号。网络割裂可能导致一部分DataNode跟NameNode失去联系。NameNode通过心跳信号的缺失来检测这一情况，并将这些近期不再发送心跳信号的DataNode标记为宕机，不会再发送新的IO请求给它们。任何存储在宕机DataNode上的数据将不再有效。DataNode宕机可能会引起一些数据块的副本系数低于指定值，Namenode不断地检测这些需要复制的数据块，一旦发现就启动复制操作。在下列情况下，可能需要重新复制：某个Datanode节点失效，某个副本遭到损坏，Datanode上的硬盘错误，或者文件的副本系数增大。

为了避免由于数据节点状态抖动而导致的复制风暴，标记datanode的超时时间过于保守（默认情况下超过10分钟）。

#### 集群均衡

HDFS的架构支持数据均衡策略。如果某个Datanode节点上的空闲空间低于特定的临界点，按照均衡策略系统就会自动地将数据从这个Datanode移动到其他空闲的Datanode。当对某个文件的请求突然增加，那么也可能启动一个计划创建该文件新的副本，并且同时重新平衡集群中的其他数据。这些均衡策略目前还没有实现。

#### 数据完整性

从某个Datanode获取的数据块有可能是损坏的，损坏可能是由Datanode的存储设备错误、网络错误或者软件bug造成的。HDFS客户端软件实现了对HDFS文件内容的校验和(checksum)检查。当客户端创建一个新的HDFS文件时，会计算这个文件每个数据块的校验和，并将校验和作为一个单独的隐藏文件保存在同一HDFS的名字空间下。当客户端获取文件内容后，它会检验从DataNode获取的数据跟相应的校验和是否匹配。如果不匹配，客户端可以选择从其他Datanode获取该数据块的副本。

#### 元数据磁盘错误

FsImage和Editlog是HDFS的核心数据结构。如果这些文件损坏了，整个HDFS实例都将失效。因而，Namenode可以配置成支持维护多个FsImage和Editlog的副本。任何对FsImage或者Editlog的修改，都将同步到它们的副本上。这种多副本的同步操作可能会降低Namenode每秒处理的名字空间事务数量。然而这个代价是可以接受的，因为即使HDFS的应用是数据密集的，它们也非元数据密集的。当Namenode重启的时候，它会选取最近的完整的FsImage和Editlog来使用。

另一个选择是启动高可用，使用多个NameNode。对于元数据信息，可以使用NFS共享存储或使用分布式编辑日志。推荐使用分布式编辑日志。

#### 快照

快照支持存储的副本数据在一个特定的瞬间的时间。一个使用快照功能可能是回滚一个损坏的HDFS实例之前已知正确的时间点。

### 数据组织

#### 数据块

HDFS被设计成支持大文件，适用HDFS的是那些需要处理大规模的数据集的应用。这些应用都是只写入数据一次，但却读取一次或多次，并且读取速度应能满足流式读取的需要。 一个典型的数据块大小是128MB。因而，HDFS中的文件总是按照64M被切分成不同的块，每个块尽可能地存储于不同的Datanode中。

-   数据块大小设置原则
    -   数据传输时间远大于寻道时间（高吞吐率）
-   一个文件的存储方式
    -   按大小被切分成若干个block，存储到不同节点上
    -   默认情况下每个block有三个副本

#### 流水线复制

当客户端向HDFS写入一个副本数为3的文件时，NameNode通过副本选择算法得到一个DataNode列表，这个列表包含了托管该块副本的DataNode。然后客户端向第一个DataNode写数据，第一个DataNode开始接收部分数据，将每个部分写入本地存储库，并且传输该部分数据到列表中的第二个DataNode。第二个DataNode又开始接收数据块的每个部分，将该部分写入其存储库，然后将该部分刷新到第三个DataNode。最后，第三个DataNode将数据写入其本地存储库。因此数据节点可以从流水线中的前一个数据节点接收数据，并且将数据转发给流水线中的下一个数据节点。因此,数据从一个DataNode管线式到下一个。

HDFS写流程：

![](http://i.imgur.com/tFL8sjF.png)

HDFS读流程：

![](http://i.imgur.com/cNrvbhA.png)