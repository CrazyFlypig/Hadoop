## 网络拓扑
* 节点距离：两个节点到达最近的共同的祖先的跃点（经过交换机的次数）数。
	* 同一个节点的两个进程： 0
	* 同一机架不同节点的两个进程： 2
	* 不同一机架不同节点的两个进程： 4
## 副本节点的选择（机架感知 Rack Awarence）
1.hadoop2.7.2
	* 第一个副本在client所处的节点上。如果客户端在集群外，在随机选择一个节点。
	* 第二个副本和第一个副本相同机架，不同节点
	* 第三个副本位于不同机架
## 自定义机架感知
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
## HDFS架构
* 运行在廉价硬件之上，成本较低，访问大型数据集，具有容错特性，容错机制
* hdfs是master/slave架构，由一个名称节点以及多个数据节点构成。namenode负责namespace管理以及client访问。
* 内部文件被切块存储在数据节点
### Namenode
* 存放元数据，包含Filename,numReplicas,block列表，权限，不包括数据节点
* 使用oiv和oev查看namenode的镜像文件和编辑日志文件
	* 离线工具，不需要启动集群
	* hdfs oiv -p XML -i inputfilepath -o outputfilepath	//fsimage
	* hdfs eiv -p XML -i inputfilepath -o outputfilepath	//edit log
1. 
