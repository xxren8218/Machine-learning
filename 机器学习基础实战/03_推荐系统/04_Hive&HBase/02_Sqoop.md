## Sqoop

### 1 Sqoop概述

- 什么是Sqoop

  - Sqoop 是一款进行数据传输的工具, 可在hadoop 的 hdfs 和关系型数据库之间传输数据
  - 可以使用Sqoop把数据从MySQL 或 Oracle导入到hdfs中, 也可以把数据从hdfs导入到MySQL或Oracle中
  - Sqoop可自动执行数据传输的大部分过程, 使用MapReduce导入和导出数据，提供并行操作和容错

- 为什么要使用sqoop?

  - 快速实现Hadoop(HDFS/hive/hbase)与mysql/Oracle等关系型数据库之间的数据传递
  - Sqoop提供多种数据传输方式

- Sqoop原理

  ![](/img/sqoop.png)

### 2 Sqoop安装

- 下载安装包[url](http://archive.cloudera.com/cdh5/cdh/5/sqoop-1.4.6-cdh5.7.0.tar.gz) 

- 解压到centos中

  ```
  tar -zxvf /home/hadoop/software/sqoop-1.4.6-cdh5.7.0.tar.gz  -C ~/app/
  ```

- 配置环境变量

  ```shell
  vi ~/.bash_profile
  export SQOOP_HOME=/home/hadoop/app/sqoop-1.4.6-cdh5.7.0
  export PATH=$SQOOP_HOME/bin:$PATH
  ```

- 激活环境变量

  ```
  source ~/.bash_profile
  ```

- 到 $SQOOP_HOME/conf 目录下 配置sqoop_env.sh

  ```shell
  cp sqoop-env-template.sh sqoop-env.sh
  vi sqoop-env.sh
  #在sqoop_env.sh中
  export HADOOP_COMMON_HOME=/home/hadoop/app/hadoop-2.6.0-cdh5.7.0/
  export HADOOP_MAPRED_HOME=/home/hadoop/app/hadoop-2.6.0-cdh5.7.0/
  export HIVE_HOME=/home/hadoop/app/hive-1.1.0-cdh5.7.0/
  ```

- 拷贝 mysql驱动到$SQOOP_HOME/lib目录下

  ```shell
  cp /home/hadoop/app/hive-1.1.0-cdh5.7.0/lib/mysql-connector-java-5.1.47.jar /home/hadoop/app/sqoop-1.4.6-cdh5.7.0/lib/
  ```

- 测试sqoop环境

  ```shell
  sqoop-version
  ```

  看到如下输出 说明sqoop安装成功

  ```shell
  Sqoop 1.4.6-cdh5.7.0
  git commit id
  Compiled by jenkins on ******
  ```
  
- 然后进入到MySQL的Docker环境中

  ```bash
  docker exec -ti mysql bash
  ```

  

### 3 使用Sqoop导入数据到hdfs中

- 准备mysql数据

  建表语句

  ```sql
  CREATE table u(id int PRIMARY KEY AUTO_INCREMENT,fname varchar(20),lname varchar(20));
  ```

  插入数据

  ```sql
  insert into u3 (fname, lname) values('George','washington');
  insert into u3 (fname, lname) values('George','bush');
  insert into u3 (fname, lname) values('Bill','clinton');
  insert into u3 (fname, lname) values('Bill','gates');
  ```

- Sqoop导入命令介绍

  - 命令语法: sqoop import (控制参数) (导入参数)
  - 命令元素: 导入操作, 数据源, 访问方式, 导入控制, 目标地址 
  - 命令理解: 数据从哪里来, 有什么控制, 到哪里去

  ```shell
  sqoop import --connect jdbc:mysql://127.0.0.1:3306/test --username root --password root\!123A --table u -m 1 
  # -m 表示用几个MR任务执行，前提是文件小于128M，否则拆成多个block
  ```

  - 添加--target-dir 指定hdfs上数据存放的目录

  ``` shell
  sqoop import --connect jdbc:mysql://localhost:3306/test --username root --password root!123A --table u --target-dir /tmp/u1 -m 1
  ```

- 导入可能出现的问题 

![error](/img/error.png)

​	解决 上传java-json.jar到$SQOOP_HOME/lib目录下



- 默认数据上传到hdfs中如下路径

  ```
  /user/当前linux用户名/mysql表名/
  ```

- 通过hive 建立外表导入数据到hive

  ```sql
  CREATE EXTERNAL TABLE u4(
      id INT,
      fname STRING,
      lname STRING
  )
  ROW FORMAT delimited fields terminated by ',' 
  LOCATION '/user/hadoop/u/';
  ```

- 也可能出现断开连接的情况

  ```shell
  hive --service metastore&  # 加上&表示在后台跑。
  ```

  