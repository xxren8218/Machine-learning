## MapReduce实战

### 3.3.1 利用MRJob编写和运行MapReduce代码

**mrjob 简介**

- 提出背景
  - 若要写MapReduce，一般也不会用hadoop streaming,它没有任何封装，是自己写脚本，通过指令上传。
  - 实际上有很多步骤有优化的余地。——出现了MRJob的库
- 使用python开发在Hadoop上运行的程序, mrjob是最简单的方式
- mrjob程序可以在本地测试运行也可以部署到Hadoop集群上运行
- 如果不想成为hadoop专家, 但是需要利用Hadoop写MapReduce代码,mrJob是很好的选择
- 优点：
  - 如果涉及多个map和多个reduce，或上个MR的输出作为下一个MR的输入的话。若用hadoop-streaming，需要写多个脚本。而MRJob可以通过一个类对其进行解决。——MRStep。——应用：TOPN统计

**mrjob 安装**

- 使用pip安装
  - pip install mrjob

**mrjob实现WordCount**

```python
from mrjob.job import MRJob

class MRWordFrequencyCount(MRJob):

    def mapper(self, _, line):
        # 得到三个生成器，需next
        yield "chars", len(line)
        yield "words", len(line.split())
        yield "lines", 1
        
	# key 相同的会走到同一个reducer中
    def reducer(self, key, values):
        yield key, sum(values)


if __name__ == '__main__':
    """
    调用run以后，他会自己调用mapper,和reducer方法。
    """
    MRWordFrequencyCount.run() 
```

- 每个单词词频的统计。

```python
from mrjob.job import MRJob
 
class MRWordCount(MRJob):
 
    # 每一行从line中输入
    def mapper(self, key, line):
        for word in line.split():
            yield word,1
 
    # word相同的 会走到同一个reduce
    def reducer(self, word, counts):
        yield word, sum(counts)
 
if __name__ == '__main__':
    MRWordCount.run()
```

**运行WordCount代码**

打开命令行, 找到一篇文本文档, 敲如下命令:

```shell
python mr_word_count.py my_file.txt
```

### 3.3.2 运行MRJOB的不同方式

1、内嵌(-r inline)方式

特点是调试方便，启动单一进程模拟任务执行状态和结果，默认(-r inline)可以省略，输出文件使用 > output-file 或-o output-file，比如下面两种运行方式是等价的

python word_count.py -r inline input.txt > output.txt
python word_count.py input.txt > output.txt

2、本地(-r local)方式

用于本地模拟Hadoop调试，与内嵌(inline)方式的区别是启动了多进程执行每一个任务。如：

python word_count.py -r local input.txt > output1.txt

3、Hadoop(-r hadoop)方式

用于hadoop环境，支持Hadoop运行调度控制参数，如：

1)指定Hadoop任务调度优先级(VERY_HIGH|HIGH),如：--jobconf mapreduce.job.priority=VERY_HIGH。

2)Map及Reduce任务个数限制，如：--jobconf mapreduce.map.tasks=2  --jobconf mapreduce.reduce.tasks=5

**python word_count.py -r hadoop hdfs:///test.txt -o  hdfs:///output **

-  要求输出的hadoop不能有内容——删掉output。

**遇到的坑——code127错误**

在后面加 -python-bin /miniconda2/envs/py365/bin/python就行。因为在虚拟机运行为py3.x，而本机环境为2.x！

![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day03_Hadoop\img\图4.PNG)

### 3.3.3 mrjob 实现 topN统计（实验）

- 上个MR的输出作为下一个MR的输入的话。MRJob.MRStep

统计数据中出现次数最多的前n个数据

```python
import sys
from mrjob.job import MRJob,MRStep
import heapq

class TopNWords(MRJob):
    def mapper(self, _, line):
        if line.strip() != "":
            for word in line.strip().split():
                yield word,1

    # 介于mapper和reducer之间，用于临时的将mapper输出的数据进行统计
    def combiner(self, word, counts):
        yield word,sum(counts)

    def reducer_sum(self, word, counts):
        yield None,(sum(counts),word) 
        # key为None，只有value有值。
		# 调换位置原因——后面的取最大的N个值是按key进行取值的。
        
    # 利用heapq将数据进行排序，将最大的2个取出
    def top_n_reducer(self,_,word_cnts):
        for cnt,word in heapq.nlargest(2,word_cnts):
            yield word,cnt # 再调换一次。
    
	# 实现steps方法用于指定自定义的mapper，comnbiner和reducer方法
    def steps(self):
        # 这里有两个MR。不过第二个没有mapper
        return [
            MRStep(mapper=self.mapper,
                   combiner=self.combiner,
                   reducer=self.reducer_sum),
            MRStep(reducer=self.top_n_reducer)
        ]

def main():
    TopNWords.run()

if __name__=='__main__':
    main()
```

- 本地运行实例：

![](D:\阶段6-人工智能项目\1-推荐系统基础\1-推荐系统基础课件\day03_Hadoop\img\图5.PNG)



### 3.4 MRJOB 文件合并

**需求描述**

- 两个文件合并 类似于数据库中的两张表合并

```shell
uid uname
01 user1 
02 user2
03 user3
uid orderid order_price
01   01     80
01   02     90
02   03    82
02   04    95
```



**mrjob 实现**

实现对两个数据表进行join操作，显示效果为每个用户的所有订单信息

```
"01:user1"	"01:80,02:90"
"02:user2"	"03:82,04:95"
```

```python
from mrjob.job import MRJob
import os
import sys
class UserOrderJoin(MRJob):
    SORT_VALUES = True
    # 二次排序参数：http://mrjob.readthedocs.io/en/latest/job.html
    def mapper(self, _, line):
        fields = line.strip().split('\t') # 用制表符进行拆分
        if len(fields) == 2:
            # user data
            source = 'A'
            user_id = fields[0]
            user_name = fields[1]
            yield  user_id,[source,user_name] # 01 [A,user1]
        elif len(fields) == 3:
            # order data
            source ='B'
            user_id = fields[0]
            order_id = fields[1]
            price = fields[2]
            yield user_id,[source,order_id,price] #01 ['B',01,80]['B',02,90]
        else :
            pass

    def reducer(self,user_id,values):
        '''
        每个用户的订单列表
        "01:user1"	"01:80,02:90"
        "02:user2"	"03:82,04:95"

        :param user_id:
        :param values:[A,user1]  ['B',01,80]
        :return:
        '''
        values = [v for v in values]  # 加了 "A"""B"以后保证先过来的是两个元素值。
        							  # 首行SORT_VALUES = True
        if len(values)>1 :
            user_name = values[0][1]
            order_info = [':'.join([v[1],v[2]]) for v in values[1:]] #[01:80,02:90]
            yield ':'.join([user_id,user_name]),','.join(order_info)




def main():
    UserOrderJoin.run()

if __name__ == '__main__':
    main()
```

实现对两个数据表进行join操作，显示效果为每个用户所下订单的订单总量和累计消费金额

```
"01:user1"	[2, 170]
"02:user2"	[2, 177]
```

```python
from mrjob.job import MRJob
import os
import sys
class UserOrderJoin(MRJob):
    # 二次排序参数：http://mrjob.readthedocs.io/en/latest/job.html
    SORT_VALUES = True

    def mapper(self, _, line):
        fields = line.strip().split('\t')
        if len(fields) == 2:
            # user data
            source = 'A' 
            user_id = fields[0]
            user_name = fields[1]
            yield  user_id,[source,user_name]
        elif len(fields) == 3:
            # order data
            source ='B'
            user_id = fields[0]
            order_id = fields[1]
            price = fields[2]
            yield user_id,[source,order_id,price]
        else :
            pass



    def reducer(self,user_id,values):
        '''
        统计每个用户的订单数量和累计消费金额
        :param user_id:
        :param values:
        :return:
        '''
        values = [v for v in values]
        user_name = None
        order_cnt = 0
        order_sum = 0
        if len(values)>1:
            for v in values:
                if len(v) ==  2 :
                    user_name = v[1]
                elif len(v) == 3:
                    order_cnt += 1
                    order_sum += int(v[2])
            yield ":".join([user_id,user_name]),(order_cnt,order_sum)



def main():
    UserOrderJoin().run()

if __name__ == '__main__':
    main()	
```





