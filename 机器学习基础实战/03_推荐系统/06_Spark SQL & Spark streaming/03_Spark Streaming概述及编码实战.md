# 掌握目标

- 说出Spark Streaming的特点
- 说出DStreaming的常见操作api
- 能够应用Spark Streaming实现实时数据处理
- 能够应用Spark Streaming的状态操作解决实际问题
- 独立实现foreachRDD向mysql数据库的数据写入
- 独立实现Spark Streaming对接kafka实现实时数据处理

## 1、sparkStreaming概述

### 1.1 SparkStreaming是什么

- 它是一个**可扩展**，**高吞吐**具有**容错性**的**流式计算框架**

  吞吐量：单位时间内成功传输数据的数量

之前我们接触的spark-core和spark-sql都是处理属于**离线批处理**任务，数据一般都是在固定位置上，通常我们写好一个脚本，每天定时去处理数据，计算，保存数据结果。这类任务通常是T+1(一天一个任务)，对实时性要求不高。

![ss1](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/ss1.png)

但在企业中存在很多实时性处理的需求，例如：双十一的京东阿里，通常会做一个实时的数据大屏，显示实时订单。这种情况下，对数据实时性要求较高，仅仅能够容忍到延迟1分钟或几秒钟。

![ss2](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/ss2.png)

**实时计算框架对比**

Storm

- 流式计算框架
- 以record为单位处理数据
- 也支持micro-batch方式（Trident）
- 没有处理机器学习的生态
- 没有离线计算的框架
- 对python不友好

Spark

- 批处理计算框架
- 以RDD为单位处理数据
- 支持micro-batch流式处理数据（Spark Streaming）
- 有机器学习相关的库

对比：

- 吞吐量：Spark Streaming优于Storm
- 延迟：Spark Streaming差于Storm

### 1.2 Spark Streaming的组件

- Streaming Context
  - 一旦一个Context已经启动(调用了Streaming Context的start()),就不能有新的流算子(Dstream)建立或者是添加到context中
  - 一旦一个context已经停止,不能重新启动(Streaming Context调用了stop方法之后 就不能再次调 start())
  - 在JVM(java虚拟机)中, 同一时间只能有一个Streaming Context处于活跃状态, 一个SparkContext创建一个Streaming Context
  - 在Streaming Context上调用Stop方法, 也会关闭SparkContext对象, 如果只想仅关闭Streaming Context对象,设置stop()的可选参数为false
  - 一个SparkContext对象可以重复利用去创建多个Streaming Context对象(不关闭SparkContext前提下), 但是需要关一个再开下一个
- DStream (离散流)
  - 代表一个连续的数据流
  - 在内部, DStream由一系列连续的RDD组成
  - DStreams中的每个RDD都包含确定时间间隔内的数据
  - 任何对DStreams的操作都转换成了对DStreams隐含的RDD的操作
  - 数据源
    - 基本源
      - TCP/IP Socket
      - FileSystem
    - 高级源
      - Kafka
      - Flume

## 2、Spark Streaming编码实践

**Spark Streaming编码步骤：**

- 1，创建一个StreamingContext
- 2，从StreamingContext中创建一个数据对象
- 3，对数据对象进行Transformations操作
- 4，输出结果
- 5，开始和停止

**利用Spark Streaming实现WordCount**

需求：监听某个端口上的网络数据，实时统计出现的不同单词个数。

1，需要安装一个nc工具：sudo yum install -y nc

2，执行指令：nc -lk 9999 -v

```python
import os

# 配置spark driver和pyspark运行时，所使用的python解释器路径
PYSPARK_PYTHON = "/home/hadoop/miniconda3/envs/datapy365spark23/bin/python"
JAVA_HOME='/home/hadoop/app/jdk1.8.0_191'
SPARK_HOME = "/home/hadoop/app/spark-2.3.0-bin-2.6.0-cdh5.7.0"
# 当存在多个版本时，不指定很可能会导致出错
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON
os.environ['JAVA_HOME']=JAVA_HOME
os.environ["SPARK_HOME"] = SPARK_HOME

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

if __name__ == "__main__":
    
    sc = SparkContext("local[2]",appName="NetworkWordCount")
    # 参数2：指定执行计算的时间间隔
    ssc = StreamingContext(sc, 1)
    # 监听ip，端口上的上的数据 （需要打开端口）【nc -lk 9999 -v】
    lines = ssc.socketTextStream('localhost',9999) 
    # 将数据按空格进行拆分为多个单词
    words = lines.flatMap(lambda line: line.split(" "))
    # 将单词转换为(单词，1)的形式
    pairs = words.map(lambda word:(word,1))
    # 统计单词个数
    wordCounts = pairs.reduceByKey(lambda x,y:x+y)
    # 打印结果信息，会使得前面的transformation操作执行
    wordCounts.pprint() # pprint() 对RDD的操作
    # 启动StreamingContext
    ssc.start()
    # 等待计算结束(不是交互式环境的话需要加这个参数，不然很快就停了)
    ssc.awaitTermination()
```

可视化查看效果：http://192.168.199.188:4040

点击streaming，查看效果

