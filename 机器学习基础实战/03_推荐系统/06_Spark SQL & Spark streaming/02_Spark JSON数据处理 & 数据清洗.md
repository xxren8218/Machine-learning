# 1、JSON数据的处理

## 1.1 介绍 

**JSON数据**

- 网页和后端数据交互所用我的格式。
- 在Spark中能自动化的把结构加载进来，并且能推断数据类型。（CSV将所有都处理成 String）

- `Spark SQL can automatically infer the schema of a JSON dataset and load it as a DataFrame`

  Spark SQL能够自动将JSON数据集以结构化的形式加载为一个DataFrame

- This conversion can be done using SparkSession.read.json on a JSON file

  读取一个JSON文件可以用SparkSession.read.json方法

**从JSON到DataFrame**

- 指定DataFrame的schema

  1，通过反射自动推断，适合静态数据

  2，程序指定，适合程序运行中动态生成的数据

**加载json数据**

```python
# 使用内部的schema
jsonDF = spark.read.json("xxx.json")
jsonDF = spark.read.format('json').load('xxx.json')

# 指定schema
jsonDF = spark.read.schema(jsonSchema).json('xxx.json')
```

**嵌套结构的JSON**

- 重要的方法

  1，get_json_object

  2，get_json

  3，explode

## 1.2 实践

### 1.2.1 静态json数据的读取和操作

**无嵌套结构的json数据**

```python
from pyspark.sql import SparkSession
spark =  SparkSession.builder.appName('json_demo').getOrCreate()
sc = spark.sparkContext

# ==========================================
#                无嵌套结构的json
# ==========================================
jsonString = [
"""{ "id" : "01001", "city" : "AGAWAM",  "pop" : 15338, "state" : "MA" }""",
"""{ "id" : "01002", "city" : "CUSHMAN", "pop" : 36963, "state" : "MA" }"""
]
```

**从json字符串数组得到DataFrame**

```python
# 从json字符串数组得到rdd有两种方法
# 1. 转换为rdd，再从rdd到DataFrame
# 2. 直接利用spark.createDataFrame()，见后面例子

jsonRDD = sc.parallelize(jsonString)   # stringJSONRDD
jsonDF =  spark.read.json(jsonRDD)  # convert RDD into DataFrame
jsonDF.printSchema()
jsonDF.show()
```

**直接从文件生成DataFrame**

```python
# -- 直接从文件生成DataFrame
# 只有被压缩后的json文件内容，才能被spark-sql正确读取，否则格式化后的数据读取会出现问题
jsonDF = spark.read.json("xxx.json")
# or
# jsonDF = spark.read.format('json').load('xxx.json')

jsonDF.printSchema()
jsonDF.show(truncate=False) # truncate=False 数据较长的时候不会...进行省略。默认会以...替换行内过长的数据

jsonDF.filter(jsonDF.pop>4000).show(10)

# 依照已有的DataFrame，创建一个临时的表(相当于mysql数据库中的一个表)，这样就可以用纯sql语句进行数据操作
jsonDF.createOrReplaceTempView("tmp_table")

resultDF = spark.sql("select * from tmp_table where pop>4000")
resultDF.show(10)
```

### 1.2.1 动态json数据的读取和操作

**指定DataFrame的Schema**

上面的例子为通过反射自动推断schema，适合静态数据

下面我们来讲解如何进行程序指定schema

**没有嵌套结构的json**

```python
jsonString = [
"""{ "id" : "01001", "city" : "AGAWAM",  "pop" : 15338, "state" : "MA" }""",
"""{ "id" : "01002", "city" : "CUSHMAN", "pop" : 36963, "state" : "MA" }"""
]

jsonRDD = sc.parallelize(jsonString)

from pyspark.sql.types import *

# 定义结构类型
# StructType：schema的整体结构，表示JSON的对象结构
# XXXStype:指的是某一列的数据类型
jsonSchema = StructType() \
  .add("id", StringType(),True) \
  .add("city", StringType()) \
  .add("pop" , LongType()) \
  .add("state",StringType())

jsonSchema = StructType() \
  .add("id", LongType(),True) \
  .add("city", StringType()) \
  .add("pop" , DoubleType()) \
  .add("state",StringType())

reader = spark.read.schema(jsonSchema)

jsonDF = reader.json(jsonRDD)
jsonDF.printSchema()
jsonDF.show()
```

**带有嵌套结构的json**

```python
from pyspark.sql.types import *
jsonSchema = StructType([
    StructField("id", StringType(), True),
    StructField("city", StringType(), True),
    StructField("loc" , ArrayType(DoubleType())),
    StructField("pop", LongType(), True),
    StructField("state", StringType(), True)
])

reader = spark.read.schema(jsonSchema)
jsonDF = reader.json('data/nest.json')
jsonDF.printSchema()
jsonDF.show(2)
jsonDF.filter(jsonDF.pop>4000).show(10)
```

#2、数据清洗

- 处理重复数据
- 处理缺失情况
- 处理异常值

前面我们处理的数据实际上都是已经被处理好的规整数据，但是在大数据整个生产过程中，需要先对数据进行数据清洗，将杂乱无章的数据整理为符合后面处理要求的规整数据。

##2.1 数据去重

```python
'''
1.删除重复数据

groupby().count()：可以看到数据的重复情况
'''
df = spark.createDataFrame([
  (1, 144.5, 5.9, 33, 'M'),
  (2, 167.2, 5.4, 45, 'M'),
  (3, 124.1, 5.2, 23, 'F'),
  (4, 144.5, 5.9, 33, 'M'),
  (5, 133.2, 5.7, 54, 'F'),
  (3, 124.1, 5.2, 23, 'F'),
  (5, 129.2, 5.3, 42, 'M'),
], ['id', 'weight', 'height', 'age', 'gender'])

# 查看重复记录
# 无意义重复数据去重：数据中行与行完全重复
# 1.首先删除完全一样的记录
df2 = df.dropDuplicates()

# 有意义去重：删除除去无意义字段之外的完全重复的行数据
# 2.其次，关键字段值完全一模一样的记录（在这个例子中，是指除了id之外的列一模一样）

# 删除某些字段值完全一样的重复记录，subset参数定义这些字段
df3 = df2.dropDuplicates(subset = [c for c in df2.columns if c!='id'])

# 3.有意义的重复记录去重之后，再看某个无意义字段的值是否有重复（在这个例子中，是看id是否重复）
# 查看某一列是否有重复值
import pyspark.sql.functions as fn
df3.agg(fn.count('id').alias('id_count'),fn.countDistinct('id').alias('distinct_id_count')).collect()

# 4.对于id这种无意义的列重复，添加另外一列自增id——不连续。
df3.withColumn('new_id',fn.monotonically_increasing_id()).show()
```

### 2.2 缺失值处理

```python
'''
2.处理缺失值
2.1 对缺失值进行删除操作(行，列)
2.2 对缺失值进行填充操作(列的均值)
2.3 对缺失值对应的行或列进行标记
'''
df_miss = spark.createDataFrame([
(1, 143.5, 5.6, 28,'M', 100000),
(2, 167.2, 5.4, 45,'M', None),
(3, None , 5.2, None, None, None),
(4, 144.5, 5.9, 33, 'M', None),
(5, 133.2, 5.7, 54, 'F', None),
(6, 124.1, 5.2, None, 'F', None),
(7, 129.2, 5.3, 42, 'M', 76000),],
 ['id', 'weight', 'height', 'age', 'gender', 'income'])

# 1.计算每条记录的缺失值情况
# 将DataFrame转换成RDD，这样写自定义函数方便些。

# 从行的角度统计缺失情况.
df_miss.rdd.map(lambda row:(row['id'], sum([c==None for c in row]))).collect()
[(1, 0), (2, 1), (3, 4), (4, 1), (5, 1), (6, 2), (7, 0)]

# 2.计算各列的缺失情况百分比
df_miss.agg(*[(1 - (fn.count(c) / fn.count('*'))).alias(c + '_missing') for c in df_miss.columns]).show()

# 3、删除缺失值过于严重的列
# 其实是先建一个DF，不要缺失值的列
df_miss_no_income = df_miss.select([
c for c in df_miss.columns if c != 'income'
])

# 4、按照缺失值删除行（threshold是根据一行记录中，缺失字段的百分比的定义）
df_miss_no_income.dropna(thresh=3).show()

# 5、填充缺失值，可以用fillna来填充缺失值，
# 对于bool类型、或者分类类型，可以为缺失值单独设置一个类型，missing
# 对于数值类型，可以用均值或者中位数等填充

# fillna可以接收两种类型的参数：
# 一个数字、字符串，这时整个DataSet中所有的缺失值都会被填充为相同的值。
# 也可以接收一个字典｛列名：值｝这样

# 先计算均值，并组织成一个字典(除去性别这一列。)
means = df_miss_no_income.agg( *[fn.mean(c).alias(c) for c in df_miss_no_income.columns if c != 'gender']).toPandas().to_dict('records')[0]

# 然后添加其它的列——非数值型
means['gender'] = 'missing'

df_miss_no_income.fillna(means).show()
```

###2.3 异常值处理——年龄等。

```python
'''
3、异常值处理
异常值：不属于正常的值 包含：缺失值，超过正常范围内的较大值或较小值
分位数去极值
中位数绝对偏差去极值
正态分布去极值
上述三种操作的核心都是：通过原始数据设定一个正常的范围，超过此范围的就是一个异常值
'''
df_outliers = spark.createDataFrame([
(1, 143.5, 5.3, 28),
(2, 154.2, 5.5, 45),
(3, 342.3, 5.1, 99),
(4, 144.5, 5.5, 33),
(5, 133.2, 5.4, 54),
(6, 124.1, 5.1, 21),
(7, 129.2, 5.3, 42),
], ['id', 'weight', 'height', 'age'])
# 设定范围 超出这个范围的 用边界值替换

# approxQuantile方法接收三个参数：参数1，列名；参数2：想要计算的分位点，可以是一个点，也可以是一个列表（0和1之间的小数），第三个参数是能容忍的误差，如果是0，代表百分百精确计算。

cols = ['weight', 'height', 'age']

bounds = {}
for col in cols:
    quantiles = df_outliers.approxQuantile(col, [0.25, 0.75], 0.05)
    IQR = quantiles[1] - quantiles[0]
    bounds[col] = [
        quantiles[0] - 1.5 * IQR,
        quantiles[1] + 1.5 * IQR
        ]

>>> bounds
{'age': [-11.0, 93.0], 'height': [4.499999999999999, 6.1000000000000005], 'weight': [91.69999999999999, 191.7]}

# 为异常值字段打标志
outliers = df_outliers.select(*['id'] + [( (df_outliers[c] < bounds[c][0]) | (df_outliers[c] > bounds[c][1]) ).alias(c + '_o') for c in cols ])
outliers.show()
#
# +---+--------+--------+-----+
# | id|weight_o|height_o|age_o|
# +---+--------+--------+-----+
# |  1|   false|   false|false|
# |  2|   false|   false|false|
# |  3|    true|   false| true|
# |  4|   false|   false|false|
# |  5|   false|   false|false|
# |  6|   false|   false|false|
# |  7|   false|   false|false|
# +---+--------+--------+-----+

# 再回头看看这些异常值的值，重新和原始数据关联

df_outliers = df_outliers.join(outliers, on='id')
df_outliers.filter('weight_o').select('id', 'weight').show()
# +---+------+
# | id|weight|
# +---+------+
# |  3| 342.3|
# +---+------+

df_outliers.filter('age_o').select('id', 'age').show()
# +---+---+
# | id|age|
# +---+---+
# |  3| 99|
# +---+---+
```

