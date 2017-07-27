## HBase shell 操作
````shell
start-hbase.sh				//启动集群
stop-hbase.sh				//停止集群

````
## 端口访问
* Master分别访问node1~3上的2181端口
* node1~2访问Master上的16000端口
* node1~3之间相互访问2181端口
* node1~3自访问50010 datanode端口
* 2181 zookeeper服务器
## HBase shell
````shell
//进入hbase shell
>./bin/hbase shell

//Display HBase Shell Help Text				
>help	

//查看特定命令帮助					
>help 'command'

//查看组帮助					
>help 'general'
	
//create a table				
>create 'Table_name','ColumnFamily_name'

//list information about your table	
>lit 'Table_name'				

//Put data into your table
>put 'T_n','row_num','CF_n:column','value'	 

//Scan the table for all data at once.
>scan 'T_n'			

//Get a single row fo data	
>get 'T_n','row_num'		
	
//Disable a table.If you want to delete a table or change it settings,as well as in some other situations, you need to disable the table first.
>disable 'T_n'		

//Drop（delete） the table			
>drop 'T_n'			

//Exit the HBase shell	
>quit 	
			
````

