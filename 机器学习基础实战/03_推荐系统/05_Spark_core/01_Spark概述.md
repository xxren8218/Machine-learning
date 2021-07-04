## spark 入门

掌握目标：

- 了解spark概念
- 知道spark的特点（与hadoop对比）
- 独立实现spark local模式的启动



早期应用的是Hadoop进行计算的（HDFS和MR），但是存在一个很重要的问题。没有充分利用内存。MR在处理时，将数据再内存和磁盘来回转换。磁盘速度慢。——出现了Spark，来解决这个问题。

- 解决计算慢
- MR只有M和R两个阶段，比较单一。Spark引入很多的API，来实现一些统计功能。
- 注意：仅仅涉及到计算，只负责算，不负责存，在离线计算时，类比的看成MR。



### 1.1 spark概述

- 1、什么是spark

  - 基于内存的计算引擎，它的计算速度非常快。但是仅仅只涉及到数据的计算，并没有涉及到数据的存储。

- 2、为什么要学习spark

  **MapReduce框架局限性**

  - 1，Map结果写磁盘，Reduce写HDFS，多个MR之间通过HDFS交换数据
  - 2，任务调度和启动开销大
  - 3，无法充分利用内存
  - 4，不适合迭代计算（如机器学习、图计算等等），交互式处理（数据挖掘）
  - 5，不适合流式处理（点击日志分析）
  - 6，MapReduce编程不够灵活，仅支持Map和Reduce两种操作

  **Hadoop生态圈**

  - 批处理：MapReduce、Hive、Pig
  - 流式计算：Storm
  - 交互式计算：Impala、presto

  需要一种灵活的框架可同时进行批处理、流式计算、交互式计算

  - 内存计算引擎，提供cache机制来支持需要反复迭代计算或者多次数据共享，减少数据读取的IO开销
  - DAG引擎，较少多次计算之间中间结果写到HDFS的开销
  - 使用多线程模型来减少task启动开销，shuffle过程中避免不必要的sort操作以及减少磁盘IO

  spark的缺点是：吃内存，不太稳定

- 3、spark特点

  - 1、速度快（比mapreduce在内存中快100倍，在磁盘中快10倍）
    - spark中的job中间结果可以不落地，可以存放在内存中。
    - mapreduce中map和reduce任务都是以进程的方式运行着，而spark中的job是以线程方式运行在进程中。
  - 2、易用性（可以通过java/scala/python/R开发spark应用程序）
  - 3、通用性（可以使用spark sql/spark streaming/mlib/Graphx）
  - 4、兼容性（spark程序可以运行在standalone/yarn/mesos）

### 1.2 spark启动（local模式）和WordCount(演示)

- 启动pyspark

  - 在$SPARK_HOME/sbin目录下执行

    - ./pyspark

  - ![](/img/pyspark.png)

    ``` python
    spark = SparkSession.builder.appNane("text").getOrCreate()
    sc = spark.sparkContext # Spqrk的上下文（运行的环境），代表了和集群之间的链接。可以访问spark集群的东西。
    
    words = sc.textFile('file:///home/hadoop/tmp/word.txt') \
                .flatMap(lambda line: line.split(" ")) \
                .map(lambda x: (x, 1)) \
              .reduceByKey(lambda a, b: a + b).collect()
    ```

  - 输出结果：
  
    ```shell
    [('python', 2), ('hadoop', 1), ('bc', 1), ('foo', 4), ('test', 2), ('bar', 2), ('quux', 2), ('abc', 2), ('ab', 1), ('you', 1), ('ac', 1), ('bec', 1), ('by', 1), ('see', 1), ('labs', 2), ('me', 1), ('welcome', 1)]
    
    ```









