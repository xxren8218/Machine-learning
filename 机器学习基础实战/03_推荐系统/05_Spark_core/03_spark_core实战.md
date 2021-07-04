## spark-core 实战案例

掌握目标：

- 独立实现Spark RDD的word count案例
- 独立实现spark RDD的PV UV统计案例
- 独立实现spark standalone模式的启动
- 说出广播变量的概念



对于数据在shell里面写，没有交互，对于数据分析而言不好，将其用PyCharm编写可进行交互，便于分析。

- 即在PyCharm上编写，然后数据同步到Centos上面运行，运行结束后，还在PyCharm上面显示。



### 1.0 Pycharm编写spark代码环境配置

准备pycharm环境

- 1.PyCharm的配置
  
  - file->new-project->pure Python->exiting interpreter->add remote->SSH Crederitals->填写Host(192.168.19.137)->Username(root)->密码->选择python的解释器路径为(/miniconda2/envs/py365/bin/python)->Remote project location(/root/bigdata/code)
  
- 代码如下：

  ```python
  from pyspark import SparkContext
  
  # 第一个是链接用的哪种环境，若几个集群的话，传递的应该是master节点的RL地址
  sc = SparkContext('local[2]','wordcount')
  
  rdd1 = sc.textFile("file:///root/code/test.txt").\
      flatMap(lambda x: x.split()).map(lambda x: (x, 1)).\
      reduceByKey(lambda a,b: a+b)
  
  print(rdd1.collect())
  ```

  运行出现了错误：

  ![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day05_Spark_core\img\1.PNG)



解决方法：

- 在centos上面查找JAVA_HOME所在位置(vi ~/.bash_profile)，添加到环境变量中：

- ```python
  ####################################
  import os
  
  JAVA_HOME = '/root/bigdata/jdk'
  os.environ['JAVA_HOME'] = JAVA_HOME
  ####################################
  
  from pyspark import SparkContext
  
  # 第一个master的位置，第二个是spark作业的名字。
  sc = SparkContext('local[2]','wordcount') # 第一个是链接用的哪种环境，若几个集群的话，传递的应该是master节点的RL地址
  
  rdd1 = sc.textFile("file:///root/code/test.txt").\
      flatMap(lambda x: x.split()).map(lambda x: (x, 1)).\
      reduceByKey(lambda a,b: a+b)
  
  print(rdd1.collect())
  ```

  还会出现python的版本不一致的问题，再添加python的环境。以及pyspark的版本问题。

  ```python
  ####################################
  import os
  JAVA_HOME = '/root/bigdata/jdk'
  PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
  os.environ['JAVA_HOME'] = JAVA_HOME
  os.environ['PYSPARK_PYTHON'] = PYSPARK_PYTHON
  os.environ['PYSPARK_DRIVER_PYTHON'] = PYSPARK_PYTHON
  ####################################
  
  from pyspark import SparkContext
  
  sc = SparkContext('local[2]','wordcount')
  rdd1 = sc.textFile("file:///root/code/test.txt").\
      flatMap(lambda x: x.split()).map(lambda x: (x,1)).\
      reduceByKey(lambda a,b: a+b)
  
  print(rdd1.collect())
  ```


### 1.1利用PyCharm编写spark wordcount程序

- 代码

```python
import os
JAVA_HOME = '/root/bigdata/jdk'
PYSPARK_PYTHON = "/miniconda2/envs/py365/bin/python"
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["PYSPARK_PYTHON"] = PYSPARK_PYTHON
os.environ["PYSPARK_DRIVER_PYTHON"] = PYSPARK_PYTHON

from pyspark import SparkContext
if __name__ == '__main__':
    # 创建spark context
    sc = SparkContext('local[2]','wordcount')
    # 通过spark context 获取rdd
    rdd1 = sc.textFile('file:///root/tmp/test.txt')
    rdd2 = rdd1.flatMap(lambda line:line.split())
    rdd3 = rdd2.map(lambda x:(x,1))
    rdd4 = rdd3.reduceByKey(lambda x,y:x+y)
    print(rdd4.collect())
```

### 1.2 通过spark实现点击流日志分析

在新闻类网站中，经常要衡量一条网络新闻的页面访问量，最常见的就是uv和pv，如果在所有新闻中找到访问最多的前几条新闻，topN是最常见的指标。

- 数据示例

```shell
# 每条数据代表一次访问记录 包含了ip 访问时间 访问的请求方式 访问的地址...信息
194.237.142.21 - - [18/Sep/2013:06:49:18 +0000] "GET /wp-content/uploads/2013/07/rstudio-git3.png HTTP/1.1" 304 0 "-" "Mozilla/4.0 (compatible;)"
183.49.46.228 - - [18/Sep/2013:06:49:23 +0000] "-" 400 0 "-" "-"
163.177.71.12 - - [18/Sep/2013:06:49:33 +0000] "HEAD / HTTP/1.1" 200 20 "-" "DNSPod-Monitor/1.0"
163.177.71.12 - - [18/Sep/2013:06:49:36 +0000] "HEAD / HTTP/1.1" 200 20 "-" "DNSPod-Monitor/1.0"
101.226.68.137 - - [18/Sep/2013:06:49:42 +0000] "HEAD / HTTP/1.1" 200 20 "-" "DNSPod-Monitor/1.0"
101.226.68.137 - - [18/Sep/2013:06:49:45 +0000] "HEAD / HTTP/1.1" 200 20 "-" "DNSPod-Monitor/1.0"
60.208.6.156 - - [18/Sep/2013:06:49:48 +0000] "GET /wp-content/uploads/2013/07/rcassandra.png HTTP/1.0" 200 185524 "http://cos.name/category/software/packages/" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36"
222.68.172.190 - - [18/Sep/2013:06:49:57 +0000] "GET /images/my.jpg HTTP/1.1" 200 19939 "http://www.angularjs.cn/A00n" "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36"
222.68.172.190 - - [18/Sep/2013:06:50:08 +0000] "-" 400 0 "-" "-"
```

- 访问的pv

  pv：网站的总访问量

  ```python
  from pyspark.sql import SparkSession
  
  spark = SparkSession.builder.appName("pv").getOrCreate()
  sc = spark.sparkContext
  rdd1 = sc.textFile("file:///root/bigdata/data/access.log")
  # 把每一行数据记为("pv",1)
  rdd2 = rdd1.map(lambda x:("pv",1)).reduceByKey(lambda a,b:a+b)
  rdd2.collect()
  sc.stop()
  ```

- 访问的uv

  uv：网站的独立用户访问量

  ```python
  from pyspark.sql import SparkSession
  
  spark = SparkSession.builder.appName("pv").getOrCreate()
  sc = spark.sparkContext
  rdd1 = sc.textFile("file:///root/bigdata/data/access.log")
  # 对每一行按照空格拆分，将ip地址取出
  rdd2 = rdd1.map(lambda x:x.split(" ")).map(lambda x:x[0])
  # 把每个ur记为1
  rdd3 = rdd2.distinct().map(lambda x:("uv",1))
  rdd4 = rdd3.reduceByKey(lambda a,b:a+b)
  rdd4.saveAsTextFile("hdfs:///uv/result")
  sc.stop()
  ```

- 访问的topN

  ```python
  from pyspark.sql import SparkSession
  
  spark = SparkSession.builder.appName("topN").getOrCreate()
  sc = spark.sparkContext
  rdd1 = sc.textFile("file:///root/bigdata/data/access.log")
  # 对每一行按照空格拆分，将url数据取出，把每个url记为1
  rdd2 = rdd1.map(lambda x:x.split(" ")).filter(lambda x:len(x)>10).map(lambda x:(x[10],1))
  # 对数据进行累加，按照url出现次数的降序排列
  rdd3 = rdd2.reduceByKey(lambda a,b:a+b).sortBy(lambda x:x[1],ascending=False)
  # 取出序列数据中的前n个
  rdd4 = rdd3.take(5)
  rdd4.collect()
  sc.stop()
  ```

###注意：

这里不懂的可以去上篇看数据的具体格式！



### 2. 通过spark实现ip地址查询

**需求**

在互联网中，我们经常会见到城市热点图这样的报表数据，例如在百度统计中，会统计今年的热门旅游城市、热门报考学校等，会将这样的信息显示在热点图中。

因此，我们需要通过日志信息（运行商或者网站自己生成）和城市ip段信息来判断用户的ip段，统计热点经纬度。

**ip日志信息**

在ip日志信息中，我们只需要关心ip这一个维度就可以了，其他的不做介绍

**思路**

1、 加载城市ip段信息，获取ip起始数字和结束数字，经度，纬度

2、 加载日志数据，获取ip信息，然后转换为数字，和ip段比较

3、 比较的时候采用二分法查找，找到对应的经度和纬度

4，对相同的经度和纬度做累计求和

5， 取出最终的topN的经纬度



**启动Spark集群**

- 进入到$SPARK_HOME/sbin目录

  - 启动Master	

  ```shell
  ./start-master.sh -h 192.168.19.137
  ```

  - 启动Slave

  ```shell
       ./start-slave.sh spark://192.168.19.137:7077
  ```

  - jps查看进程

  ```shell
  27073 Master
  27151 Worker
  ```

  - 关闭防火墙

  ```shell
  systemctl stop firewalld
  ```

  - 通过SPARK WEB UI查看Spark集群及Spark
    - http://192.168.199.188:8080/  监控Spark集群
    - http://192.168.199.188:4040/  监控Spark Job

- 代码

  ```python
  from pyspark.sql import SparkSession
  # 255.255.255.255 0~255 256个数  2^8 是8位2进制数  ——>转化成32位的二进制数
  #将ip转换为特殊的数字形式  223.243.0.0|223.243.191.255|  255 2^8
  #‭11011111‬
  #00000000
  #1101111100000000
  #‭        11110011‬
  #11011111111100110000000000000000
  def ip_transform(ip):     
      ips = ip.split(".") # [223,243,0,0] 32位二进制数
      ip_num = 0
      for i in ips:
          ip_num = int(i) | ip_num << 8
      return ip_num
  
  # 二分法查找ip对应的行的索引
  def binary_search(ip_num, broadcast_value):
      start = 0
      end = len(broadcast_value) - 1
      while (start <= end):
          mid = int((start + end) / 2)
          if ip_num >= int(broadcast_value[mid][0]) and ip_num <= int(broadcast_value[mid][1]):
              return mid
          if ip_num < int(broadcast_value[mid][0]):
              end = mid
          if ip_num > int(broadcast_value[mid][1]):
              start = mid
  
  def main():
      spark = SparkSession.builder.appName("test").getOrCreate()
      sc = spark.sparkContext
      city_id_rdd = sc.textFile("file:///home/hadoop/app/tmp/data/ip.txt").map(lambda x:x.split("|")).map(lambda x: (x[2], x[3], x[13], x[14]))
      # 创建一个广播变量
      city_broadcast = sc.broadcast(city_id_rdd.collect())
      dest_data = sc.textFile("file:///home/hadoop/app/tmp/data/20090121000132.394251.http.format").map(
          lambda x: x.split("|")[1])
      # 根据取出对应的位置信息
      def get_pos(x):
          # 从广播变量中获取ip地址库
          city_broadcast_value = city_broadcast.value
          # 根据单个ip获取对应经纬度信息
          def get_result(ip):
              ip_num = ip_transform(ip)
              index = binary_search(ip_num, city_broadcast_value)
              # ((纬度,精度),1)
              return ((city_broadcast_value[index][2], city_broadcast_value[index][3]), 1)
  
          x = map(tuple,[get_result(ip) for ip in x])
          return x
  
      dest_rdd = dest_data.mapPartitions(lambda x: get_pos(x)) # ((纬度,精度),1)
      result_rdd = dest_rdd.reduceByKey(lambda a, b: a + b).sortBy(lambda x:x[1],ascending=False)
      print(result_rdd.collect())
      sc.stop()
  
  if __name__ == '__main__':
      main()
  ```

- **广播变量的使用**

  - 要统计Ip所对应的经纬度, 每一条数据都会去查询ip表
  - 每一个task 都需要这一个ip表, 默认情况下, 所有task都会去复制ip表
  - 实际上 每一个Worker上会有多个task, 数据也是只需要进行查询操作的, 所以这份数据可以共享,没必要每个task复制一份
  - 可以通过广播变量, 通知当前worker上所有的task, 来共享这个数据,避免数据的多次复制,可以大大降低内存的开销
  - sparkContext.broadcast(要共享的数据)
  
- **mapPartitions** 

  - transformation操作 
  - 类似map 但是map是一条一条传给里面函数的 mapPartitions 数据是一部分一部分传给函数的
  - 应用场景 数据处理的时候 需要连接其它资源 如果一条一条处理 会处理一条连一次， 一份一份处理可以很多条数据连一次其它资源 可以提高效率

- **二分法查找**

- ip_transform 把223.243.0.0 转换成10进制的数字——位运算。 