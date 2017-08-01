# mapreduce 作业提交
## 0. 配置文件
**mapred-site.xml 中 mapredece.framework(框架).name = local/yarn** 决定 submitJobInternal() 调用 LocalJobRunner 或 YARNJobRunner。
## 1.Local 本地模式
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
## 完全分布式
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
## IPC  RPC
### IPC
inter process communication 	进程间通信
### RPC
remote procedure call 	远程过程调用