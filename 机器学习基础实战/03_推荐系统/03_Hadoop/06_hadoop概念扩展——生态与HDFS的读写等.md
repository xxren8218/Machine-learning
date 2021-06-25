## hadoop概念扩展

课程目标：

- 知道hadoop生态组成
- 了解hdfs读写流程
- 说出Hadoop发行版本的选择



### 1. Hadoop生态系统

**狭义的Hadoop VS 广义的Hadoop**

- 狭义的Hadoop:HDFS、MapReduce、YARN。

- 广义的Hadoop：指的是Hadoop生态系统，Hadoop生态系统是一个很庞大的概念，hadoop是其中最重要最基础的一个部分，生态系统中每一子系统只解决某一个特定的问题域（甚至可能更窄），不搞统一型的全能系统，而是小而精的多个小系统；

![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/hadoop-生态.png)

Hive:数据仓库——操作MapReuce来操作HDFS（我们的感觉是写SQL，Hive将SQL写成MapReduce的方式。）

R:数据分析

Mahout:机器学习库

pig：脚本语言，跟Hive类似

Oozie:工作流引擎，管理作业执行顺序

Zookeeper:用户无感知，主节点挂掉选择从节点作为主的。分布式集群协调工具。数据改变的同步。

Flume:日志收集框架——将特定目录日志放到HDFS中去。

Sqoop:数据交换框架，例如：关系型数据库（MySQL、Oracle）与HDFSorHBase之间的数据交换介质。

Hbase : ——`列式存储`（MySQL为`行式存储`——连续存放）海量数据中的查询，相当于分布式文件系统中的数据库

Spark: 分布式的计算框架基于内存 ——有python的API：pyspark scala写的（java的虚拟机语言）

- spark core——对应MapReduce
- spark sql——对应Hive
- spark streaming 准实时 不算是一个标准的流式计算 对应——storm flink
- spark ML spark MLlib 机器学习的库

Kafka: 消息队列

Storm: 分布式的流式计算框架  不适合用python操作storm 

Flink: 分布式的流式计算框架

**Hadoop生态系统的特点**

- 开源、社区活跃

- 囊括了大数据处理的方方面面
- 成熟的生态圈



### 2. HDFS 读写流程 & 高可用

- HDFS读写流程

  ![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/hdfs_read_write/a.jpg)

  ![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/hdfs_read_write/b.jpg)

  ![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/hdfs_read_write/c.jpg)

  ![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/hdfs_read_write/d.jpg)

  - 客户端向NameNode发出写文件请求。

  - 检查是否已存在文件、检查权限。若通过检查，直接先将操作写入EditLog，并返回输出流对象。 
    （注：WAL，write ahead log，先写Log，再写内存，因为EditLog记录的是最新的HDFS客户端执行所有的写操作。如果后续真实写操作失败了，由于在真实写操作之前，操作就被写入EditLog中了，故EditLog中仍会有记录，我们不用担心后续client读不到相应的数据块，因为在第5步中DataNode收到块后会有一返回确认信息，若没写成功，发送端没收到确认信息，会一直重试，直到成功）

  - client端按128MB的块切分文件。

  - client将NameNode返回的分配的可写的DataNode列表和Data数据一同发送给最近的第一个DataNode节点，此后client端和NameNode分配的多个DataNode构成pipeline管道，client端向输出流对象中写数据。client每向第一个DataNode写入一个packet，这个packet便会直接在pipeline里传给第二个、第三个…DataNode。 
    （注：并不是写好一个块或一整个文件后才向后分发）

  - 每个DataNode写完一个块后，会返回确认信息。 
    （注：并不是每写完一个packet后就返回确认信息，个人觉得因为packet中的每个chunk都携带校验信息，没必要每写一个就汇报一下，这样效率太慢。正确的做法是写完一个block块后，对校验信息进行汇总分析，就能得出是否有块写错的情况发生）

  - 写完数据，关闭输输出流。

  - 发送完成信号给NameNode。

    （注：发送完成信号的时机取决于集群是强一致性还是最终一致性，强一致性则需要所有DataNode写完后才向NameNode汇报。最终一致性则其中任意一个DataNode写完后就能单独向NameNode汇报，HDFS一般情况下都是强调强一致性） 

- HDFS如何实现高可用(HA)

  - 数据存储故障容错
    - 磁盘介质在存储过程中受环境或者老化影响,数据可能错乱
    - 对于存储在 DataNode 上的数据块，计算并存储校验和（CheckSum)
    - 读取数据的时候, 重新计算读取出来的数据校验和, 校验不正确抛出异常, 从其它DataNode上读取备份数据
  - 磁盘故障容错
    - DataNode 监测到本机的某块磁盘损坏
    - 将该块磁盘上存储的所有 BlockID 报告给 NameNode
    - NameNode 检查这些数据块在哪些DataNode上有备份,
    - 通知相应DataNode, 将数据复制到其他服务器上
  - DataNode故障容错
    - 通过心跳和NameNode保持通讯
    - 超时未发送心跳, NameNode会认为这个DataNode已经宕机
    - NameNode查找这个DataNode上有哪些数据块, 以及这些数据在其它DataNode服务器上的存储情况
    - 从其它DataNode服务器上复制数据
  - NameNode故障容错
    - 主从热备： 必须通过zookeeper  secondary namenode，对namenode数据的备份
    - zookeeper配合： ①master节点选举， ②负责数据一致性的保证。（namenode变化，其余保证也要变化。）



### 3. Hadoop发行版的选择

- Apache Hadoop

  - 开源社区版
  - 最新的Hadoop版本都是从Apache Hadoop发布的
  - Hadoop Hive Flume  版本不兼容的问题 jar包  spark scala  Java->.class->.jar ->JVM

- CDH: Cloudera Distributed Hadoop

  - Cloudera 在社区版的基础上做了一些修改

  - http://archive.cloudera.com/cdh5/cdh/5/

    ![](/img/cdh.png)

  - hadoop-2.6.0-cdh-5.7.0 和 Flume*****-cdh5.7.0 cdh版本一致 的各个组件配合是有不会有兼容性问题

  - CDH版本的这些组件 没有全部开源

- HDP: Hortonworks Data Platform

