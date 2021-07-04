## 1. spark-core概述

掌握目标：

- 知道RDD的概念
- 独立实现RDD的创建

### 1.1 什么是RDD

- RDD（Resilient Distributed Dataset）叫做**弹性分布式数据集**，是Spark中最基本的数据抽象，它代表一个**不可变、可分区**、里面的元素**可并行**计算的集合.
  - Dataset:一个数据集，简单的理解为集合，用于存放数据的
  - Distributed：它的数据是分布式存储，并且可以做分布式的计算
  - Resilient：弹性的
    - 它表示的是数据可以保存在磁盘，也可以保存在内存中——弹性的一种表现
    - 数据分布式也是弹性的
    - 弹性:并不是指他可以动态扩展，而是容错机制。
      - RDD会在多个节点上存储，就和hdfs的分布式道理是一样的。**hdfs**文件被**切分为多个block存储在各个节点上**，而**RDD**是被切分为多个**partition**。**不同的partition**可能在**不同的节点**上
      - spark读取hdfs的场景下，spark把hdfs的block读到内存就会抽象为spark的partition。
      - spark计算结束，一般会把数据做持久化到hive，hbase，hdfs等等。我们就拿hdfs举例，将RDD持久化到hdfs上，RDD的每个partition就会存成一个文件，如果文件小于128M，就可以理解为一个partition对应hdfs的一个block。反之，如果大于128M，就会被且分为多个block，这样，一个partition就会对应多个block。
  - 不可变
  - 可分区
  - 并行计算

### 1.2 RDD的创建

- 第一步 创建sparkContext

  - SparkContext, Spark程序的入口. SparkContext代表了和Spark集群的链接, 在Spark集群中通过SparkContext来创建RDD
  - SparkConf  创建SparkContext的时候需要一个SparkConf， 用来传递Spark应用的基本信息

  ``` python
  conf = SparkConf().setAppName(appName).setMaster(master)
  sc = SparkContext(conf=conf)
  ```

- 创建RDD

  - 进入pyspark环境

  ```shell
  [hadoop@hadoop000 ~]$ pyspark
  Python 3.5.0 (default, Nov 13 2018, 15:43:53)
  [GCC 4.8.5 20150623 (Red Hat 4.8.5-28)] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  19/03/08 12:19:55 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
  Setting default log level to "WARN".
  To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
  Welcome to
        ____              __
       / __/__  ___ _____/ /__
      _\ \/ _ \/ _ `/ __/  '_/
     /__ / .__/\_,_/_/ /_/\_\   version 2.3.0
        /_/
  
  Using Python version 3.5.0 (default, Nov 13 2018 15:43:53)
  SparkSession available as 'spark'.
  >>> sc
  <SparkContext master=local[*] appName=PySparkShell>
  ```

  - 在spark shell中 已经为我们创建好了 SparkContext 通过sc直接使用
  - 可以在spark UI中看到当前的Spark作业 在浏览器访问当前centos的4040端口

  ![](./img/sparkui.png)
  - Parallelized Collections方式创建RDD

    - 调用`SparkContext`的 `parallelize` 方法并且传入已有的可迭代对象或者集合

    ```python
    data = [1, 2, 3, 4, 5]
    distData = sc.parallelize(data)
    ```

    ``` shell
    >>> data = [1, 2, 3, 4, 5]
    >>> distData = sc.parallelize(data)
    >>> data
    [1, 2, 3, 4, 5]
    >>> distData
    ParallelCollectionRDD[0] at parallelize at PythonRDD.scala:175
    ```

    - 在spark ui中观察执行情况

    ![createrdd](./img/createrdd.png)

    - 在通过`parallelize`方法创建RDD 的时候可以指定分区数量

    ```shell
    >>> distData = sc.parallelize(data,5) # 5表示数据分区的数量，最终一个分区对应一个task
    >>> distData.reduce(lambda a, b: a + b)
    15
    ```

    - 在spark ui中观察执行情况

    ![](./img/createrdd2.png)

    -  Spark将为群集的每个分区（partition）运行一个任务（task）。 通常，可以根据CPU核心数量指定分区数量（每个CPU有2-4个分区）如未指定分区数量，Spark会自动设置分区数。

  - 通过外部数据创建RDD

    - PySpark可以**从Hadoop支持的任何存储源创建RDD**，包括本地文件系统，HDFS，Cassandra，HBase，Amazon S3等
    - 支持整个目录、多文件、通配符
    - 支持压缩文件

    ```shell
    >>> rdd1 = sc.textFile('file:///home/hadoop/tmp/word.txt')
    >>> rdd1.collect()
    ['foo foo quux labs foo bar quux abc bar see you by test welcome test', 'abc labs foo me python hadoop ab ac bc bec python']
    ```

- 加载了数据以后接下来就是计算了。

## 2. spark-core RDD常用算子练习

掌握目标

- 说出RDD的三类算子
- 掌握transformation和action算子的基本使用

### 2.1 RDD 常用操作

- RDD 支持两种类型的操作：
  - transformation
    - 从一个已经存在的数据集创建一个新的数据集
      - rdd a ----->transformation ----> rdd b
    - 比如， map就是一个transformation 操作，把数据集中的每一个元素传给一个函数并**返回一个新的RDD**，代表transformation操作的结果 
  - action
    - 获取对数据进行运算操作之后的结果
    - 比如， reduce 就是一个action操作，使用某个函数聚合RDD所有元素的操作，并**返回最终计算结果**

- 所有的transformation操作都是惰性的（lazy）
  - 不会立即计算结果
  - 只记下应用于数据集的transformation操作
  - 只有调用action一类的操作之后才会计算所有transformation
  - 这种设计使Spark运行效率更高
  - 例如map reduce 操作，map创建的数据集将用于reduce，map阶段的结果不会返回，仅会返回reduce结果。
- *persist* 操作
  - *persist*操作用于将数据缓存 可以缓存在内存中 也可以缓存到磁盘上， 也可以复制到磁盘的其它节点上

### 2.2 RDD Transformation算子

- map: map(func)——**进来几个元素，出去几个元素。**

  - 将func函数作用到数据集的每一个元素上，生成一个新的RDD返回

  ``` shell
  >>> rdd1 = sc.parallelize([1,2,3,4,5,6,7,8,9],3)
  >>> rdd2 = rdd1.map(lambda x: x+1)
  >>> rdd2.collect() # collect就属于 action。若不调用拿不到结果。
  [2, 3, 4, 5, 6, 7, 8, 9, 10]
  
  >>> # 注意：减的话存在问题：
  >>> rdd1 = sc.parallelize([1,2,3,4,5,6,7,8,9])
  >>> rdd2 = rdd1.map(lambda x,y: x-y)
  >>> rdd2 -> -3 # 按理来说是1-2-3-4-5-6-7-8-9，但不是，因为默认分成了几块partition
  >>> 若为 rdd1 = sc.parallelize([1,2,3,4,5,6,7,8,9], 1)，则正确。
  
  ```

  ```shell
  >>> rdd1 = sc.parallelize([1,2,3,4,5,6,7,8,9],3)
  >>> def add(x):
  ...     return x+1
  ...
  >>> rdd2 = rdd1.map(add)
  >>> rdd2.collect()
  [2, 3, 4, 5, 6, 7, 8, 9, 10]
  ```

  

  ![](./img/rdd_map.png)

- filter

  - filter(func) 选出所有func返回值为true的元素，生成一个新的RDD返回

  ```shell
  >>> rdd1 = sc.parallelize([1,2,3,4,5,6,7,8,9],3)
  >>> rdd2 = rdd1.map(lambda x:x*2)
  >>> rdd3 = rdd2.filter(lambda x:x>4)
  >>> rdd3.collect()
  [6, 8, 10, 12, 14, 16, 18]
  ```

- flatmap

  - flatMap会先执行map的操作，再将所有对象合并为一个对象

  ```shell
  >>> rdd1 = sc.parallelize(["a b c","d e f","h i j"])
  >>> rdd2 = rdd1.flatMap(lambda x:x.split(" "))
  >>> rdd2.collect()
  ['a', 'b', 'c', 'd', 'e', 'f', 'h', 'i', 'j']
  ```

  - flatMap和map的区别：flatMap在map的基础上将结果合并到一个list中

  ```shell
  >>> rdd1 = sc.parallelize(["a b c","d e f","h i j"])
  >>> rdd2 = rdd1.map(lambda x:x.split(" "))
  >>> rdd2.collect()
  [['a', 'b', 'c'], ['d', 'e', 'f'], ['h', 'i', 'j']]
  ```

- union

  - 对两个RDD求并集

  ```shell
  >>> rdd1 = sc.parallelize([("a",1),("b",2)])
  >>> rdd2 = sc.parallelize([("c",1),("b",3)])
  >>> rdd3 = rdd1.union(rdd2)
  >>> rdd3.collect()
  [('a', 1), ('b', 2), ('c', 1), ('b', 3)]
  ```

- intersection

  - 对两个RDD求交集

  ```python
  >>> rdd1 = sc.parallelize([("a",1),("b",2)])
  >>> rdd2 = sc.parallelize([("c",1),("b",3)])
  >>> rdd3 = rdd1.union(rdd2)
  >>> rdd4 = rdd3.intersection(rdd2)
  >>> rdd4.collect()
  [('c', 1), ('b', 3)]
  ```

- groupByKey

  - 以元组中的第0个元素作为key，进行分组，返回一个新的RDD

  ```shell
  >>> rdd1 = sc.parallelize([("a",1),("b",2)])
  >>> rdd2 = sc.parallelize([("c",1),("b",3)])
  >>> rdd3 = rdd1.union(rdd2)
  >>> rdd4 = rdd3.groupByKey()
  >>> rdd4.collect()
  [('a', <pyspark.resultiterable.ResultIterable object at 0x7fba6a5e5898>), ('c', <pyspark.resultiterable.ResultIterable object at 0x7fba6a5e5518>), ('b', <pyspark.resultiterable.ResultIterable object at 0x7fba6a5e5f28>)]
  
  ```

  - groupByKey之后的结果中 value是一个Iterable

  ```python
  >>> result[2]
  ('b', <pyspark.resultiterable.ResultIterable object at 0x7fba6c18e518>)
  >>> result[2][1]
  <pyspark.resultiterable.ResultIterable object at 0x7fba6c18e518>
  >>> list(result[2][1])
  [2, 3]
  ```

  - reduceByKey

    - 将key相同的键值对，按照Function进行计算

    ```python
    >>> rdd = sc.parallelize([("a", 1), ("b", 1), ("a", 1)])
    >>> rdd.reduceByKey(lambda x,y:x+y).collect()
    [('b', 1), ('a', 2)]
    ```

  - sortByKey

    - `sortByKey`(*ascending=True*, *numPartitions=None*, *keyfunc=<function RDD.<lambda>>*)

      Sorts this RDD, which is assumed to consist of (key, value) pairs.

    ```python
    >>> tmp = [('a', 1), ('b', 2), ('1', 3), ('d', 4), ('2', 5)]
    >>> sc.parallelize(tmp).sortByKey().first()
    ('1', 3)
    >>> sc.parallelize(tmp).sortByKey(True, 1).collect()
    [('1', 3), ('2', 5), ('a', 1), ('b', 2), ('d', 4)]
    >>> sc.parallelize(tmp).sortByKey(True, 2).collect()
    [('1', 3), ('2', 5), ('a', 1), ('b', 2), ('d', 4)]
    >>> tmp2 = [('Mary', 1), ('had', 2), ('a', 3), ('little', 4), ('lamb', 5)]
    >>> tmp2.extend([('whose', 6), ('fleece', 7), ('was', 8), ('white', 9)])
    >>> sc.parallelize(tmp2).sortByKey(True, 3, keyfunc=lambda k: k.lower()).collect()
    [('a', 3), ('fleece', 7), ('had', 2), ('lamb', 5),...('white', 9), ('whose', 6)]
    ```

    

### 2.3 RDD Action算子

- collect——大数据慎用！

  - 返回一个list，list中包含 RDD中的所有元素
  - 只有当数据量较小的时候使用Collect 因为所有的结果都会加载到内存中

- reduce

  - **reduce**将**RDD**中元素两两传递给输入函数，同时产生一个新的值，新产生的值与RDD中下一个元素再被传递给输入函数直到最后只有一个值为止。

  ```shell
  >>> rdd1 = sc.parallelize([1,2,3,4,5])
  >>> rdd1.reduce(lambda x,y : x+y)
  15
  ```

- first

  - 返回RDD的第一个元素

  ```python
  >>> sc.parallelize([2, 3, 4]).first()
  2
  ```

- take

  - 返回RDD的前N个元素
  - `take`(*num*)

  ``` shell
  >>> sc.parallelize([2, 3, 4, 5, 6]).take(2)
  [2, 3]
  >>> sc.parallelize([2, 3, 4, 5, 6]).take(10)
  [2, 3, 4, 5, 6]
  >>> sc.parallelize(range(100), 100).filter(lambda x: x > 90).take(3)
  [91, 92, 93]
  ```

- count

  返回RDD中元素的个数

  ```
  >>> sc.parallelize([2, 3, 4]).count()
  3
  ```

### 2.4 Spark RDD两类算子执行示意

![s5](./img/s5.png)

![s6](./img/s6.png)