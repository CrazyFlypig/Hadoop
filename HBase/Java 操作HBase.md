# Java 操作HBase
````java
package com.xiyou.mybase;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.*;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.security.User;
import org.apache.hadoop.hbase.util.Bytes;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * 增删改查的api操作
 *
 * @author cc
 * @create 2017-07-24-16:10
 */

public class TestCRUD {
    Configuration conf = null;
    public Connection conn = null;
    Admin admin = null ;
    @Before
    public void inConn(){
        conf = HBaseConfiguration.create();
        try {
            conn = ConnectionFactory.createConnection(conf);
            //创建admin对象
            admin = conn.getAdmin();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    /*
    *登录获取权限
     */
    @Test
    public void Login () throws IOException {
        Configuration conf = HBaseConfiguration.create();
        boolean flag = User.isHBaseSecurityEnabled(conf);
        System.out.println("Security : "+flag);
    }
    /*
    *创建名字空间
     */
    @Test
    public void createNamespace () throws IOException {
        //创建名字空间描述符
        NamespaceDescriptor.Builder builder = NamespaceDescriptor.create("ns2");
        NamespaceDescriptor nsd = builder.build();
        //创建名字空间
        admin.createNamespace(nsd);
        admin.close();
    }
    /*
    *删除名字空间
     */
    @Test
    public void deleteNamespace () throws IOException {
        //删除名字空间
        admin.deleteNamespace("ns1");
        admin.close();
    }
    @Test
    /*
    *创建表
     */
    public void createTable() throws IOException {
        //创建表描述符
        HTableDescriptor tabledes = new HTableDescriptor(TableName.valueOf("ns2:t1"));
        //创建列族描述符
        HColumnDescriptor columndes = new HColumnDescriptor(Bytes.toBytes("cf1"));
        //向表描述符中添加列族描述符
        tabledes.addFamily(columndes);
        //创建表
        admin.createTable(tabledes);
    }
    /*
    * drop 表
     */
    @Test
    public void dropTable() {
        try {
            //禁用表
            admin.disableTable(TableName.valueOf("t2"));
            //删除表
            admin.deleteTable(TableName.valueOf("t2"));
            System.out.println("delete successfully!");
            admin.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    /*
    *   put == insert
     */
    @Test
    public void put() throws IOException {
        HTable table = new HTable(conf,TableName.valueOf("ns2:t1"));
        Put put = new Put(Bytes.toBytes("row1"));
        put.add(Bytes.toBytes("cf1"),Bytes.toBytes("no"),Bytes.toBytes("no002"));
        table.put(put);
        table.close();
    }
    /*
    *   put == update
     */
    @Test
    public void put4update() throws IOException {
        Table table = conn.getTable(TableName.valueOf("ns2:t1"));
        Put put = new Put(Bytes.toBytes("row2"));
        put.addColumn(Bytes.toBytes("cf1"), Bytes.toBytes("no"),Bytes.toBytes("no004"));
        table.put(put);
        table.close();
    }
    /*
    *   put List
    *   以二进制字节数组字典排序
     */
    @Test
    public void putList() throws IOException {
        Table table = conn.getTable(TableName.valueOf("ns2:t1"));
        List<Put> list = new ArrayList<Put>();
        Put put = null;
        for (int i = 0; i <= 100 ;i++){
            put = new Put(Bytes.toBytes("row"+i));
            put.addColumn(Bytes.toBytes("cf1"),Bytes.toBytes("no"),Bytes.toBytes("no"+i));
            list.add(put);
        }
        table.put(list);
        table.close();
    }
    /*
    *   getCell
     */
    @Test
    public void getVaule() throws IOException {
        Table table = conn.getTable(TableName.valueOf("ns2:t1"));
        Get get = new Get(Bytes.toBytes("row22"));
        Result result = table.get(get);
        String no = Bytes.toString(result.getValue(Bytes.toBytes("cf1"),Bytes.toBytes("no")));
        System.out.println("ns2:t1----cf1----no----"+no);
    }
    /*
    * scan
    */
    @Test
    public void get() throws IOException {
        Table table = conn.getTable(TableName.valueOf("ns2:t1"));
        Scan scan = new Scan(Bytes.toBytes("row22"), Bytes.toBytes("row80"));
        ResultScanner results = table.getScanner(scan);
        Iterator<Result> iterator = results.iterator();
        while (iterator.hasNext()) {
            Result result = iterator.next();
            String no = Bytes.toString(result.getValue(Bytes.toBytes("cf1"), Bytes.toBytes("no")));
            System.out.println("ns2:t1----cf1----no----" + no);
        }
    }
    /*
    * delete
     */
    @Test
    public void delete() throws IOException {
        Table table = conn.getTable(TableName.valueOf("ns2:t1"));
        Delete delete = new Delete(Bytes.toBytes("row22"));
        delete.addColumn(Bytes.toBytes("cf1"),Bytes.toBytes("no"));
        table.delete(delete);
        table.close();
    }
}
````