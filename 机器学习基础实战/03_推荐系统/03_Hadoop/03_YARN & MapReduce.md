# YARN&MapReduce

掌握目标：

- 了解YARN概念和产生背景
- 了解MapReduce概念
- 说出YARN执行流程
- 说出MapReduce原理
- 独立完成Mrjob实现wordcount
- 完成提交作业到YARN上执行



## 资源调度框架 YARN

### 3.1.1 什么是YARN

- Yet Another Resource Negotiator, 另一种资源协调者
- 通用资源管理系统
- 为上层应用提供统一的资源管理和调度，为集群在利用率、资源统一管理和数据共享等方面带来了巨大好处

### 3.1.2 YARN产生背景 

- 通用资源管理系统

  - Hadoop数据分布式存储（数据分块，冗余存储）
  - 当多个MapReduce任务要用到相同的hdfs数据， 需要进行资源调度管理
  - Hadoop1.x时并没有YARN，MapReduce 既负责进行计算作业又处理服务器集群资源调度管理

- 服务器集群资源调度管理和MapReduce执行过程耦合在一起带来的问题

  - Hadoop早期, 技术只有Hadoop, 这个问题不明显

  - 随着大数据技术的发展，Spark Storm ... 计算框架都要用到服务器集群资源 

  - 如果没有通用资源管理系统，只能为多个集群分别提供数据

    -  资源利用率低 运维成本高

    ![](/img/image-yarn2.png)

  - Yarn (Yet Another Resource Negotiator) 另一种资源调度器

    - Mesos 大数据资源管理产品

- 不同计算框架可以共享同一个HDFS集群上的数据，享受整体的资源调度

  ![](/img/hadoop-yarn3.png)

### 3.1.3 YARN的架构和执行流程

- ResourceManager: RM 资源管理器
  ​	整个集群同一时间提供服务的RM只有一个，负责集群资源的统一管理和调度
  ​	处理客户端的请求： submit, kill
  ​	监控我们的NM，一旦某个NM挂了，那么该NM上运行的任务需要告诉我们的AM来如何进行处理
- NodeManager: NM 节点管理器
  ​	整个集群中有多个，负责自己本身节点资源管理和使用
  ​	定时向RM汇报本节点的资源使用情况
  ​	接收并处理来自RM的各种命令：启动Container
  ​	处理来自AM的命令
- ApplicationMaster: AM
  ​	每个应用程序对应一个：MR、Spark，负责应用程序的管理
  ​	为应用程序向RM申请资源（core、memory），分配给内部task
  ​	需要与NM通信：启动/停止task，task是运行在container里面，AM也是运行在container里面
- Container 容器: 封装了CPU、Memory等资源的一个容器,是一个任务运行环境的抽象
- Client: 提交作业 查询作业的运行进度,杀死作业

![](/img/yarn4.png)



1，Client提交作业请求

2，ResourceManager 进程和 NodeManager 进程通信，根据集群资源，为用户程序分配第一个Container(容器)，并将 ApplicationMaster 分发到这个容器上面

3，在启动的Container中创建ApplicationMaster

4，ApplicationMaster启动后向ResourceManager注册进程,申请资源

5，ApplicationMaster申请到资源后，向对应的NodeManager申请启动Container,将要执行的程序分发到NodeManager上

6，Container启动后，执行对应的任务

7，Tast执行完毕之后，向ApplicationMaster返回结果

8，ApplicationMaster向ResourceManager汇报任务结束。 请求kill

### 3.1.5 YARN环境搭建

1）mapred-site.xml

```
<property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
</property>
```

2）yarn-site.xml

```
<property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
</property>
```

3) 启动YARN相关的进程
sbin/start-yarn.sh

4）验证
​	jps
​		ResourceManager
​		NodeManager
​	http://192,168.19.137:8088

5）停止YARN相关的进程
​	sbin/stop-yarn.sh



## 分布式处理框架 MapReduce

### 3.2.1 什么是MapReduce

- 源于Google的MapReduce论文(2004年12月)
- Hadoop的MapReduce是Google论文的开源实现
- MapReduce优点: 海量数据离线处理&易开发
- MapReduce缺点: 不能实时流式计算

### 3.2.2 MapReduce编程模型

- MapReduce分而治之的思想

  - 数钱实例：一堆钞票，各种面值分别是多少
    - 单点策略
      - 一个人数所有的钞票，数出各种面值有多少张
    - 分治策略
      - 每个人分得一堆钞票，数出各种面值有多少张
      - 汇总，每个人负责统计一种面值
    - 解决数据可以切割进行计算的应用

- MapReduce编程分Map和Reduce阶段——还是过于简单了（相比于Spark,不能进行求平均操作，得自己写。）

  - 将作业拆分成Map阶段和Reduce阶段
  - Map阶段 Map Tasks 分：把复杂的问题分解为若干"简单的任务"
  - Reduce阶段: Reduce Tasks 合：reduce

- MapReduce编程执行步骤

  - 准备MapReduce的输入数据
  - 准备Mapper数据，进行Mapper操作
  - Shuffle
  - Reduce处理
  - 结果输出

- **编程模型**

- 借鉴函数式编程方式

- 用户只需要实现两个函数接口：

  - Map(in_key,in_value)

    --->(out_key,intermediate_value) list

  - Reduce(out_key,intermediate_value) list

    --->out_value list

- Word Count 词频统计案例

  ![](D:/阶段6-人工智能项目/1-推荐系统基础/1-推荐系统基础课件/day03_Hadoop/img/image-mapreduce.png)

### 3.2.3 Hadoop Streaming 实现wordcount （实验 了解）

- 提供了python的API，写完以后翻译成java去执行的。——此处用了虚拟环境（source activate py365）

  - Mapper

  ```python
  import sys
  
  # 输入为标准输入stdin
  for line in sys.stdin:
      # 删除开头和结尾的空行
      line = line.strip()
      # 以默认空格分隔单词到words列表
      words = line.split()
      for word in words:
          # 输出所有单词，格式为“单词 1”以便作为Reduce的输入
          print("%s %s"%(word,1))
  ```

  - Reducer

  ```python
  import sys
  
  current_word = None
  current_count = 0
  word = None
  
  # 获取标准输入，即mapper.py的标准输出
  for line in sys.stdin:
      # 删除开头和结尾的空行
      line = line.strip()
  
      # 解析mapper.py输出作为程序的输入，以tab作为分隔符
      word, count = line.split()
  
      # 转换count从字符型到整型
      try:
          count = int(count)
      except ValueError:
          # count非数字时，忽略此行
          continue
  
      # 要求mapper.py的输出做排序（sort）操作，以便对连续的word做判断
      if current_word == word:
          current_count += count
      else :
          # 出现了一个新词
          # 输出当前word统计结果到标准输出
          if current_word :
              print('%s\t%s' % (current_word, current_count))
          # 开始对新词的统计
          current_count = count
          current_word = word
  
  # 输出最后一个word统计
  if current_word == word:
      print("%s\t%s"% (current_word, current_count))
  ```

  

  - 本地实现

  ​     `cat xxx.txt`|`python3 map.py`|`sort|python3 red.py`

  得到最终的输出

  **注：hadoop-streaming会主动将map的输出数据进行字典排序**

  

- 通过Hadoop Streaming 提交作业到Hadoop集群

  ```shell
  STREAM_JAR_PATH="/root/bigdata/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.9.1.jar"    # hadoop streaming jar包所在位置
  INPUT_FILE_PATH_1="/The_Man_of_Property.txt"  #要进行词频统计的文档在hdfs中的路径
  OUTPUT_PATH="/output"                         #MR作业后结果的存放路径
  
  hadoop fs -rm -r -skipTrash $OUTPUT_PATH    #输出路径如果之前存在 先删掉否则会报错
  
  hadoop jar $STREAM_JAR_PATH \   
  		-input $INPUT_FILE_PATH_1 \ # 指定输入文件位置
  		-output $OUTPUT_PATH \      #指定输出结果位置
  		-mapper "python map.py" \   #指定mapper执行的程序
  		-reducer "python red.py" \  #指定reduce阶段执行的程序
  		-file ./map.py \            #通过-file 把python源文件分发到集群的每一台机器上  
  		-file ./red.py
  ```

- 到Hadoop集群查看运行结果

  ![](/img/mr_result.png)

  ### 文档说明

- 对于java而言，.java编译->.class文件（多个打包）->.jar-> 在JVM虚拟机上运行。对于JVM而言，.jar是其可执行文件。相当于windows的.exe。

- 通过hadoop-streaming-2.9.1.ja可执行文件将python的可执行文件翻译成java。

![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day03_Hadoop\img\图1.PNG)

结果如图

![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day03_Hadoop\img\图2.PNG)



## 注意！

得开启YARN才可以

也可以去YARN去看：端口号8088

![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day03_Hadoop\img\图3.PNG)