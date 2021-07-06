# 掌握目标

- 说出Spark Sql的相关概念
- 说出DataFrame与RDD的联系
- 独立实现Spark Sql对JSON数据的处理
- 独立实现Spark Sql进行数据清洗

## 1、Spark SQL 概述

**Spark SQL概念**

* Spark SQL is Apache Spark's module for working with structured data.
  * 它是spark中用于处理结构化数据的一个模块

**Spark SQL历史**

- Hive是目前大数据领域，事实上的数据仓库标准。

![s9](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s9.png)

- Shark：shark底层使用spark的基于内存的计算模型，从而让性能比Hive提升了数倍到上百倍。
- 底层很多东西还是依赖于Hive，修改了内存管理、物理计划、执行三个模块
- 2014年6月1日的时候，Spark宣布了不再开发Shark，全面转向Spark SQL的开发

**Spark SQL优势**

- Write Less Code

![s10](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s10.png)

* Performance

![s11](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s11.png)

python操作RDD，转换为可执行代码，运行在java虚拟机，涉及两个不同语言引擎之间的切换，进行进程间		通信很耗费性能。

DataFrame

- 是RDD为基础的分布式数据集，类似于传统关系型数据库的二维表，dataframe记录了对应列的名称和类型
- dataFrame引入schema和off-heap(使用操作系统层面上的内存)
  - 1、解决了RDD的缺点
  - 序列化和反序列化开销大
  - 频繁的创建和销毁对象造成大量的GC
  - 2、丢失了RDD的优点
  - RDD编译时进行类型检查
  - RDD具有面向对象编程的特性



用scala/python编写的RDD比Spark SQL编写转换的RDD慢，涉及到执行计划

- CatalystOptimizer：Catalyst优化器
- ProjectTungsten：钨丝计划，为了提高RDD的效率而制定的计划
- Code gen：代码生成器

![s12](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s12.png)

直接编写RDD也可以自实现优化代码，但是远不及SparkSQL前面的优化操作后转换的RDD效率高，快1倍左右

优化引擎：类似mysql等关系型数据库基于成本的优化器

首先执行逻辑执行计划，然后转换为物理执行计划(选择成本最小的)，通过Code Generation最终生成为RDD

* Language-independent API

  用任何语言编写生成的RDD都一样，而使用spark-core编写的RDD，不同的语言生成不同的RDD

- Schema

  结构化数据，可以直接看出数据的详情

  在RDD中无法看出，解释性不强，无法告诉引擎信息，没法详细优化。

**为什么要学习sparksql **

sparksql特性

  *  1、易整合
  *  2、统一的数据源访问
  *  3、兼容hive
  *  4、提供了标准的数据库连接（jdbc/odbc）

# 2、DataFrame

## 2.1 介绍

在Spark语义中，DataFrame是一个分布式的**行集合**，可以想象为一个关系型数据库的表，或者一个带有列名的Excel表格。它和RDD一样，有这样一些特点：

- Immuatable：一旦RDD、DataFrame被创建，就不能更改，只能通过transformation生成新的RDD、DataFrame
- Lazy Evaluations：只有action才会触发Transformation的执行
- Distributed：DataFrame和RDD一样都是分布式的
- dataframe和dataset（没有python版本,没法做类型校验。python是若类型语言）统一，dataframe只是dataset[ROW]的类型别名。由于Python是弱类型语言，只能使用DataFrame

**DataFrame vs RDD**

- RDD：分布式的对象的集合，Spark并不知道对象的详细模式信息
- DataFrame：分布式的Row对象的集合，其提供了由列组成的详细模式信息，使得Spark SQL可以进行某些形式的执行优化。
- DataFrame和普通的RDD的逻辑框架区别如下所示：

![s13](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s13.png)

- 左侧的RDD Spark框架本身不了解 Person类的内部结构。

- 右侧的DataFrame提供了详细的结构信息（schema——每列的名称，类型）
- DataFrame还配套了新的操作数据的方法，DataFrame API（如df.select())和SQL(select id, name from xx_table where ...)。
- DataFrame还引入了off-heap,意味着JVM堆以外的内存, 这些内存直接受操作系统管理（而不是JVM）。

- RDD是分布式的Java对象的集合。DataFrame是分布式的Row对象的集合。DataFrame除了提供了比RDD更丰富的算子以外，更重要的特点是提升执行效率、减少数据读取以及执行计划的优化。
- DataFrame的抽象后，我们处理数据更加简单了，甚至可以用SQL来处理数据了
- 通过DataFrame API或SQL处理数据，会自动经过Spark 优化器（Catalyst）的优化，即使你写的程序或SQL不仅高效，也可以运行的很快。
- **DataFrame相当于是一个带着schema的RDD**

**Pandas DataFrame vs Spark DataFrame**

- Cluster Parallel：集群并行执行
- Lazy Evaluations: 只有action才会触发Transformation的执行
- Immutable：不可更改
- Pandas rich API：比Spark SQL api丰富

## 2.2 创建DataFrame

0.创建之前必须有一个SparkSession.

1，创建dataFrame的步骤

​	调用方法例如：spark.read.xxx方法

2，其他方式创建dataframe

- createDataFrame：pandas dataframe、list、RDD

- 数据源：RDD、csv、json、parquet、orc、jdbc

  ```python
  jsonDF = spark.read.json("xxx.json")
  
  jsonDF = spark.read.format('json').load('xxx.json')
  
  parquetDF = spark.read.parquet("xxx.parquet")
  
  jdbcDF = spark.read.format("jdbc").option("url","jdbc:mysql://localhost:3306/db_name").option("dbtable","table_name").option("user","xxx").option("password","xxx").load()
  ```

- Transformation:延迟性操作

- action：立即操作

  ![s14](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day06_Spark_sql&Spark_streaming/pics/s14.png)

## 2.3 DataFrame API实现

**基于RDD创建**

```python
from pyspark.sql import SparkSession
from pyspark.sql import Row

# 创建DatFrame需要有 Spark Session
# 创建RDD需要有SparkContext

spark = SparkSession.builder.appName('test').getOrCreate()
sc = spark.sparkContext
# spark.conf.set("spark.sql.shuffle.partitions", 6)
# ================直接创建==========================
l = [('Ankit',25),('Jalfaizy',22),('saurabh',20),('Bala',26)]
rdd = sc.parallelize(l)
# 为数据添加列名
people = rdd.map(lambda x: Row(name=x[0], age=int(x[1])))
# 通过SparkSession来创建DataFrame
schemaPeople = spark.createDataFrame(people)
```

**从csv中读取数据**

```python
# ==================从csv读取======================
# 加载csv类型的数据并转换为DataFrame,默认是从hadoop的/user/root//下查找，目前我们用户是root
df = spark.read.format("csv"). \
    option("header", "true") \   # header True,把最前面的展示出来。
    .load("iris.csv")
# 显示数据结构
df.printSchema()
# 显示前10条数据
df.show(10)
# 统计总量
df.count()
# 列名
df.columns
```

**增加一列**

```python
# ===============增加一列(或者替换) withColumn===========
# 定义一个新的列，数据为其他某列数据的两倍
# 如果操作的是原有列，可以替换原有列的数据
df.withColumn('newWidth',df.SepalWidth * 2).show()
```

**删除一列**

```python
# ==========删除一列  drop=========================
# 删除一列
df.drop('newWidth').show()
```

**统计信息**

```python
# ================ 统计信息 describe================
df.describe().show()
# 计算某一列的描述信息
df.describe('newWidth').show()   
```

**提取部分列**

```python
# ===============提取部分列 select==============
df.select('SepalLength','SepalWidth').show()
```

**基本统计功能**

```python
# ==================基本统计功能 distinct count=====
df.select('cls').distinct().count()
```

**分组统计**

```python
# 分组统计 groupby(colname).agg({'col':'fun','col2':'fun2'})
df.groupby('cls').agg({'SepalWidth':'mean','SepalLength':'max'}).show()

# avg(), count(), countDistinct(), first(), kurtosis(),
# max(), mean(), min(), skewness(), stddev(), stddev_pop(),
# stddev_samp(), sum(), sumDistinct(), var_pop(), var_samp() and variance()
```

**自定义的汇总方法**

```python
# 自定义的汇总方法
import pyspark.sql.functions as fn
# 调用函数并起一个别名
df.agg(fn.count('SepalWidth').alias('width_count'),fn.countDistinct('cls').alias('distinct_cls_count')).show()
```

**拆分数据集**

```python
# ====================数据集拆成两部分 randomSplit ===========
# 设置数据比例将数据划分为两部分
trainDF, testDF = df.randomSplit([0.6, 0.4])
```

**采样数据**

```python
# ================采样数据 sample===========
# withReplacement：是否有放回的采样
# fraction：采样比例
# seed：随机种子
sdf = df.sample(False,0.2,100)
```

**查看两个数据集在类别上的差异**

```python
# 查看两个数据集在类别上的差异 subtract，确保训练数据集覆盖了所有分类
diff_in_train_test = testDF.select('cls').subtract(trainDF.select('cls'))
diff_in_train_test.distinct().count()
```

**交叉表**

```python
# ================交叉表 crosstab=============
df.crosstab('cls','SepalLength').show()
```

**udf**

udf：自定义函数

```python
# ================== 综合案例 + udf================
# 测试数据集中有些类别在训练集中是不存在的，找到这些数据集做后续处理
trainDF,testDF = df.randomSplit([0.99,0.01])

diff_in_train_test = trainDF.select('cls').subtract(testDF.select('cls')).distinct().show()

# 首先找到这些类，整理到一个列表
not_exist_cls = trainDF.select('cls').subtract(testDF.select('cls')).distinct().rdd.map(lambda x :x[0]).collect()

# 定义一个方法，用于检测
def should_remove(x):
    if x in not_exist_cls:
        return -1
    else :
        return x

# 创建udf，udf函数需要两个参数：
# Function
# Return type (in my case StringType())

# 在RDD中可以直接定义函数，交给rdd的transformatioins方法进行执行
# 在DataFrame中 需要通过udf将自定义函数封装成udf函数，创建一个UDF对象，只有UDF对象 才可以DataFrame进行调用执行

from pyspark.sql.types import StringType
from pyspark.sql.functions import udf

# 先封装成UDF函数。
check = udf(should_remove,StringType())

resultDF = trainDF.withColumn('New_cls',check(trainDF['cls'])).filter('New_cls <> -1')

resultDF.show()
```

