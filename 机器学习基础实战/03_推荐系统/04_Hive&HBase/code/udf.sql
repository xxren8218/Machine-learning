hadoop fs -mkdir /user/hive/lib

hadoop fs -put hive-contrib-2.0.1.jar /user/hive/lib/

hive> add jar hdfs:///user/hive/lib/hive-contrib-2.0.1.jar;

hive> CREATE TEMPORARY FUNCTION row_sequence as 'org.apache.hadoop.hive.contrib.udf.UDFRowSequence'

Select row_sequence(),* from test;


CREATE  FUNCTION test.row_sequence as 'org.apache.hadoop.hive.contrib.udf.UDFRowSequence' using jar 'hdfs:///user/hive/lib/hive-contrib-2.0.1.jar'






===================================== python udf ===============================================
https://acadgild.com/blog/hive-udf-in-python/


CREATE table u(
fname STRING,
lname STRING);

insert into table  u values('asdf','asdf');
insert into table  u values('asdf2','asdf');
insert into table  u values('asdf3','asdf');
insert into table  u values('asdf4','asdf');

hadoop fs -put udf.py /user/hive/lib/

ADD FILE hdfs:///user/hive/lib/udf.py;


-- python 版本带来的问题

SELECT TRANSFORM(fname, lname) USING 'udf.py' AS (fname, l_name) FROM u;

SELECT TRANSFORM(fname, lname) USING 'python2.6 udf.py' AS (fname, l_name) FROM u;

====================================== python udaf ==============================================
https://www.inovex.de/blog/hive-udfs-and-udafs-with-python/

TRANSFORM,and UDF and UDAF
it is possible to plug in your own custom mappers and reducers
 A UDF is basically only a transformation done by a mapper meaning that each row should be mapped to exactly one row. A UDAF on the other hand allows us to transform a group of rows into one or more rows, meaning that we can reduce the number of input rows to a single output row by some custom aggregation.
UDF：就是做一个mapper，对每一条输入数据，映射为一条输出数据。
UDAF:就是一个reducer，把一组输入数据映射为一条输出数据。

一个脚本至于是做mapper还是做reducer，又或者是做udf还是做udaf，取决于我们把它放在什么要的hive操作符中。放在select中的基本就是udf，放在distribute by和cluster by中的就是reducer。


We can control if the script is run in a mapper or reducer step by the way we formulate our HiveQL query.
The statements DISTRIBUTE BY and CLUSTER BY allow us to indicate that we want to actually perform an aggregation.

User-Defined Functions (UDFs) for transformations and even aggregations which are therefore called User-Defined Aggregation Functions (UDAFs)




USE test;
CREATE TABLE foo (id INT, vtype STRING, price FLOAT);
INSERT INTO TABLE foo VALUES (1, "car", 1000.);
INSERT INTO TABLE foo VALUES (2, "car", 42.);
INSERT INTO TABLE foo VALUES (3, "car", 10000.);
INSERT INTO TABLE foo VALUES (4, "car", 69.);
INSERT INTO TABLE foo VALUES (5, "bike", 1426.);
INSERT INTO TABLE foo VALUES (6, "bike", 32.);
INSERT INTO TABLE foo VALUES (7, "bike", 1234.);
INSERT INTO TABLE foo VALUES (8, "bike", null);




----------------- udaf ------------------------------
pip install virtualenv
virtualenv --no-site-packages -p /usr/local/Python-2.7.11/bin/python penv27

-p：指定使用的pytohn版本号

source venv/bin/activate

pip install pandas

cd venv
tar zcvfh ../penv27.tar ./
“-h”的参数:它会把符号链接文件视作普通文件或目录，从而打包的是源文件

hadoop fs -put penv27.tar /user/hive/lib/
hadoop fs -ls /user/hive/lib
hadoop fs -put udaf.py /user/hive/lib/
hadoop fs -put udaf.sh /user/hive/lib



DELETE ARCHIVE hdfs:///user/hive/lib/penv27.tar;
ADD ARCHIVE hdfs:///user/hive/lib/penv27.tar;
DELETE FILE hdfs:///user/hive/lib/udaf.py;
ADD FILE hdfs:///user/hive/lib/udaf.py;
DELETE FILE hdfs:///user/hive/lib/udaf.sh;
ADD FILE hdfs:///user/hive/lib/udaf.sh;

USE test;
SELECT TRANSFORM(id, vtype, price) USING 'udaf.sh' AS (vtype STRING, mean FLOAT, var FLOAT)
  FROM (SELECT * FROM foo CLUSTER BY vtype) AS TEMP_TABLE;





set -e
这句语句告诉bash如果任何语句的执行结果不是true则应该退出。这样的好处是防止错误像滚雪球般变大导致一个致命的错误，而这些错误本应该在之前就被处理掉。
(>&2 echo "Begin of script")
 命令组。括号中的命令将会新开一个子shell顺序执行，