## IPC  RPC
### IPC
inter process communication 	进程间通信
### RPC
remote procedure call 	远程过程调用
# MapReduce框架
* MapReduce是一个编程模型，是一个用于处理和生成大规模数据集的相关实现。
* 用户自定义一个map函数处理一个Key-Value对以生成一批中间的Key-Value对，再定义一个reduce函数将所有这些中间的有相同key的Value合并起来。
## MapReduce模型
* Mapper端负责对数据的分析处理，最终转换为Key-Value的数据结构
* Reduce端获取Mapper出来的结果，对结果进行统计。
* Hadoop MapReduce 实现存储均衡，但未实现计算均衡，由编写MapReduce代码的程序员来保证。
## MapReduce框架组成
### Mapper和Reducer
### JobTracker
* 一个master服务，软件启动后JobTracker接收Job，负责调度Job的每一个子任务Task运行于TaskTracker上，并监控它们，若有失败的Task就重新运行它
### TaskTracker
* 是运行在多节点的slaver服务。TaskTracker主动与JobTracker通信接收作业，并负责直接执行每一个任务。
### JobClient
* 每一个Job都会在用户端通过JobClient类将应用程序以及配置参数Configuration打包成jAR文件存储到HDFS，并把路径提交到JobTracker的master服务，然后由master创建每一个Task将它们分发到各个TaskTracker服务中执行。
### JobInProgress
* JobClient提交Job后，JobTracker会创建一个JobInProgress来跟踪和调度这个Job，并把它添加到job队列里。JobInProgress会根据提交的任务JAR中定义
## mapreduce 作业提交
### 0. 配置文件
**mapred-site.xml 中 mapredece.framework(框架).name = local/yarn** 决定 submitJobInternal() 调用 LocalJobRunner 或 YARNJobRunner。
### 1.Local 本地模式
  -->Job.submit()
  -->JobSubmitter.submitJobInternal()
  -->LocalJobRunner.submtiJob(...)
  -->转换Job为LocalJobRunner.Job对象，线程，并启动
  -->LocalJobRunner.run()

	创建mapRunnables(切片数决定);
	runTasks(mapRunnable集合);
	创建reduceRunnables(手动设定);
	runTasks(reduceRunnable集合);
  -->runTasks(...)

	for( Runnable r : runnables){
		service.submit(r);
	}
  -->

	MapTaskRunnable.run() | ReduceTaskRunnable.run() {
		MapTask(ReduceTask) task = new MapTask(ReduceTask)();
		task.run();
	}
  -->

	MapTask.run{
		自定Mapper.run(){
			setup();
			while(){
				map();
			}
			cleanup();
		}
	}
### 完全分布式
  -->job.submit();
  -->JobSubmitter.submitJobInternal();
  -->YarnRunner.submitJob();
  -->RMDelegate.submitApplication(appCentext)//资源管理代理
  -->YarnClient.submitApplication(appContext)
  -->YarnClientImpl.submitApplication(...)
	
	submitApplicationRequest request = .. //创建请求报文
  -->ApplicationClientProtocolPBCClientImpl.submitApplication(request)
	
	SubmitApplicationRequestProto requestProto = request...
  -->ProtobufRpcEngineInvoke.invoke();
	
	RequestHeaderProto header = constructRpcRequestHeader(method);
	Message body = (Message)args[1];
	RpcResponseWrapper wrapper = (header,body);
  -->ipc.client.call(...)
	
	client.call(RPC.RpcKind.PRC_PROTOCOL_BUFFER, 
		new RpcRequestWrappper (rpcRequestHeader,theRequest), 
			remoteId, fallbackToSimpleAuth);
  -->ipc.client.call(...)
	
	Call call = createCall(rpckind,reqWrapper);
  -->Connection.sendRpcRequest(call);
## Shuffle阶段和Sort阶段
* Shuffle是指从Map的输出开始，包括系统执行排序以及传送Map输出到Reduce作为输入的过程。
* Sort是对Map端输出的Key进行排序。
* Map端的Shuffle
	1. Map任务开始产生输出时，先将结果数据写入循环内存缓冲区，默认大小100M。
		* 数据首先写入缓冲区，并作一些预排序，以提升效率
	2. 当缓冲区数据量达到阈值时（默认0.8）系统会启动一个后台线程把缓冲区的内容spill到磁盘。若缓冲区已满，则Map阻塞至spill完成。spill线程把缓冲区数据写到磁盘前，会对它进行二次快速排序。输出一个索引文件和数据文件。
		* 二次快速排序过程：首先根据数据所属的Partition排序，然后每个Partition中再按key排序
		* 如果设计了Combiner，将在排序的基础上进行。
		* Combiner就是一个Mini Reduce，它在执行Map任务的节点本身运行，先对Map的输出做一次简单Reduce，使得Map输出更紧凑，更少的数据会被写入Reduce端。
	3. 每当内存中达到spill阈值时，都会产生一个新的spill文件。即在Map写完最后一个输出记录时，可能会有多个spill文件。在Map任务完成前，所有的spill文件将会归并排序为一个索引文件和数据文件。
		* 归并排序是一个多路归并的过程，最大归并路数由`io.sort.factor`控制，默认是10
	4. 对写入到磁盘的数据进行压缩，有利于数据存储和传输。
	5. spill文件归并完后，Map将删除所有临时spill文件，并告知TaskTracker任务已完成。Reduce端通过HTTP获取对应的数据。
		* Map任务可能会在不同的时间内完成，只要有其中一个Map任务完成，Reduce就开始复制它的输出。称为Cope阶段。
		* Reduce任务拥有多个cope线程，可以并行的获取Map输出。设定`mapred.reduce.parallel.copies`来改变线程数，默认是5。
* Reduce端的Shuffle
	1. Copy阶段：Reduce进程启动一些数据copy线程，通过HTTP方式请求Map Task所在的TaskTracker获取Map Task的输出文件。
		* TaskTracker与JobTracker通知信息是通过心跳通信机制传输的。
		* Reduce端中有一个线程会间歇向JobTracker询问Map输出的地址，直至所有数据都被获取到。
		* Reduce取走Map输出之后，TaskTracker不会立即删除这些数据，因为Reduce可能会失败。整个作业完成后，JobTracker才删除。
	2. Merge阶段：Merge有三种形式：内存到内存，内存到磁盘，磁盘到磁盘。默认第一种形式不启用。当内存中的数据量达到一定阈值，就启动内存到磁盘的merge操作。第二种Merge方式一直在运行，直到没有Map端的数据时才结束。然后启动第三种磁盘到磁盘的Merge方式生成最终文件。
		* 缓冲区大小基于JVM的heap size设置，因为Shuffle过程中，Reduce不运行，应把大部分内存给Shuffle用。
		* 复制的数据叠加在磁盘上，有一个后台线程会将它们归并为更大的排序文件，节省后期归并排序时间
		* 归并文件的结果是部分已经归并好的文件和部分为归并的文件。这种做法并未改变归并次数，只是最小化写入磁盘的数据优化措施，因为最后一次归并的数据总是直接送到reduce函数那里。
	3. Reduce的输入文件：不断Merge操作后，会生成一个“最终文件”，它有可能存在于内存或磁盘。当Reduce的输入文件已定，整个shuffle才最终出现在内存。