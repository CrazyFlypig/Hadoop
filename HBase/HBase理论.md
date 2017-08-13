## 特性
1. 数据矩阵横向和纵向两个维度所支持的数据量级都非常具有弹性。
2. 面向列的存储和权限控制，并支持独立检索。
	1. 数据按列存储
	2. 数据即索引
	3. 并发处理性能高
	4. 数据类型一致，数据特征相似，可以高效压缩
3. 良好的可扩展性
## 核心功能模块
### 客户端Client
* 管理类操作，client与HMaster进行RPC通信
* 数据读写类操作，Client与RegionServer进行RPC交互
### 协调服务模块Zookeeper
* 存储HBase元数据信息、实时监控RegionServer、存储所有Region的寻址入口，保证HBase集群只有一个HMaster节点，其它HMaster作为备选时刻准备
### 主节点 HMaster
* 主要负责Table和Region的管理工作
	* 管理用户对Table的增、删、改、查
	* 管理RegionServer的负载均衡，调整Region分布
	* 在Region分裂后，负责新的Region的分配
	* 在RegionServer死机后，负责失效RegionServer上的Region迁移
### Region节点RegionServer
* HRegionServer负责响应用户I/O请求，向HDFS文件系统中读写数据
## 优点
1. 存储大量数据
2. 高吞吐量
3. 可扩展
4. 数据格式无限制
5. 业务场景简单
# 数据模型
* HBase的表由行（Row）和列（Column）共同构成，HBase有一个列族（Column Family）的概念，它将一列或多列组织在一起，HBase的列必须属于某一列族。
* 行和列的交叉点称为单元格（cell）。单元格的内容也就是列的值是不可分割的**字节数组**，以**二进制形式存储**。
## 逻辑模型
* 以表的形式存放数据，可以多表存储
* 表由行与列组成，每个列属于某个列族，由行和列确定的存储单元称为元素
* 每个元素保存同一份数据的多个版本，由时间戳区分
* HBase都是插入数据。删除也是插入一条新的记录，然后加以标记。
* 稀疏数据
### 行键
* 行键是数据行在表里的唯一标示，并作为检索记录的主键
* 访问表里的行的三中方式：
	1. 单个行键访问
	2. 给定范围访问
	3. 全表扫描
* 行键长度不超过64KB的任意字符串，并按照字典序存储
* 对于要一起读的行，要对行键值进行精心设计，以便他们可以放在一起存储。保证连续性，进行范围扫描更快
## 列族与列
* 列族提前制定好，限定符在插入数据时制定。列族是固定的，列是动态的
* 列表示：<列族>:<限定符>
* 磁盘上按照列族存储数据
* 列族元素最好有相同的读写方式（长度，类型），提高性能
### 元素结构
![](http://i.imgur.com/cgHXkEO.jpg)
* 首先是 Key 的长度和 Value 的长度，接下来是行长度 行 列族长度 列族 限定符 时间戳 key类型 value
### 时间戳
* 一般手工生成，由用户显式赋值
* HBase支持两种数据版本的回收方式：
	1. 每个数据单元，只存储制定个数的最新版本。（以元素个数作为保留依据）
	2. 保存指定时间长度的版本（以数据保存时间长短作为保留依据）
* 常见客户端时间查询：“某个时刻起的最新数据”或“给我全部版本的数据”
* 元素由 行键，列族:限定符，时间戳唯一确定
## 物理存储模型
* HBase是按照列存储的稀疏行/列矩阵。在多个列族存在时，只有其中一个列族有数据就是稀疏。当同一个行键同一个时间戳查询的时候，同一个列族数据有一个，访问效率高。
* 设计HBase表格的时候就要考虑，数据最好能够稀疏存储。
### 物理存储模型
![](http://i.imgur.com/ZuIWMNy.jpg)
* 在物理存储模型中，所有列族都在一个列，这样行数就会增加。
### 物理架构
![](http://i.imgur.com/KJsKPvU.jpg)
### 存储机制
* 数据的插入、更新和删除都是在对应的表中增加记录
* 在将StoreFile合并成一个大文件时，在表中做的dml都会新增记录，这时候会将过期数据，含有删除标记的行键数据，都会抛掉
* 一旦写入hdfs文件，只能整体进行更新。数据库管理人员可以在hbase数据库中进行更新操作，以这种方式控制hdfs中的数据
* 在hadoop中存储是均匀的，hbase的hfile就会分布在datanode上。整体上进行了两次分布。
### Region 和 Region 服务器
* 表在行方向上，按照行键范围划分成若干个Region
* 每个表最初只有一个region，当记录数超过某个阈值时，开始分裂成两个region
* 物理上所有数据放在HDFS，由Region服务器提供region给的管理
	* 如果有一个hregionServer宕机或下线 Hmaster 会将 hregion 交给其他 hregionserver管理
* 一台物理节点只能跑一个HRegionServer
* 一个Hregionserver可以管理多个Region实例
* 一个Region实例包括Hlog日志和存放数据的Store
### HLog
* 用于灾难恢复
* 预写式日志（WAL），操作记录进日志，数据才会写入。
* 每个Region服务器只维护一个Hlog，来自不同表的Region日志是混合在一起的
* Hlog会被定期回滚
### Store
* 每个 Region 有一个或多个 Store 组成，每个Store 保存一个列族的所有数据
* 每个 Store 由一个memStore 和零个或多个StoreFile组成
* StoreFile以Hfile的格式存储在HDFS上，这些文件是B树结构
### 客户端更新操作流程
* 先连接有关的HRegionServer，然后向 Region 提交变更
* 提交数据首先写入WAL和MemStore
* 当MemStore中的数据量达到某个阈值，Hregionserver会启动flashcache 进程写入 StoreFile
* 当StoreFile文件数量增长到一定阈值后，系统会将多个StoreFile进行合并，在合并过程中会进行版本呢合并和删除工作，形成更大StoreFile
* 当单个StoreFile大小超过一定阈值后，会把当前的Region 分割成两个Refgions，并由Hmaster分配到相应的RegionServer，实现负载均衡
* 客户端检索数据时，先在MemStore找，再去StoreFile
### 元数据表
* HBase中由两张特殊的Table，-ROOT-和.META.
* .META.：记录了用户表的Region信息，.META. 可以有多个region
* -ROOT-：记录了.META. 表的Region信息，-ROOT-只有一个region
* Zookeeper 中记录了-ROOT-表的location
* .META. 表的Regions 全部保存在内存中
* 客户端会将查询过的位置信息缓存起来，且缓存不会主动失效
# Zookeeper
* 协同服务，保证高可靠、高可用
* 集中式服务，用于配置信息、名称服务、分布式同步处理
## zk组件
1. client
	* 向server周期性发送信息，表明自己还活着。sever向client发送确认信息
	* client没有收到回应，自动重定向消息到其他server
2. server
	* 一个zk节点，向client提供所有服务。通知client，server是alive的
3. ensemble
	* 全体，一组zk节点，需要最小值3
4. leader
	* 领袖，特殊的zk节点。zk集群启动时，推选leader，leader在follower故障进行处理
5. follower
	* 随从，听命于leader的指令
## zk的namespace 等级结构
1. 驻留在内存的
2. 树上的每个节点都是znode
3. 每个znode都有name，而且使用‘/’分割
4. 每个节点都有stat对象
	1. version：与之关联数据发生改变，版本增加
	2. acl：action control list
	3. timetamp
	4. datalength
## zk node节点类型
1. 持久节点
2. 临时节点
3. 顺序节点
## HBase在zk中的数据结构ls

