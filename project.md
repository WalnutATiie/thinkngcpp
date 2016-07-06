#项目知识总结
## 1. 暗网搜索引擎与舆情监测
## 1.1 Elasticsearch检索集群
将爬下来的网页去标签之后存入Elasticsearch，英文索引使用standard分析器，中文索引使用ik分析器，其他使用默认分析器。  
去标签工具pattern.web，plaintext部分，支持定制去除的标签部分。在elasticsearch中存储的字段：content,title,domain_name,url_MD5,create_time,language,url,content_simhash  
去重采用Url_MD5作为唯一标识，simhash用于内容去重。  
基于查询接口的检索，对于其他语言采用term查询进行完全匹配，对于存在分析器的中英文，采用基于lucene的match_query的查询，并将模糊匹配设置为2-gram，英文为3-gram  
lucene查询接口待展开  
查询响应时间优化，受限制与机器性能，使用match_phrase的查询耗时很长，size所影响，分页面取  
设计可支持布尔查询  
### 1.2 排名优化
查询相关度：VSM文档、query表示法，计算向量夹角余弦相似度、Okapi计算方法(短查询检索比余弦相似度更有效) 
Elasticsearch中是基于lucene的计算方法，自带效果已经很好，rank值  
返回的结果每一条都有一个评分，对该评分加权    
链接关系：域名级别的pagerank，包括非onion网站外链的链入，离线计算(数量万的数量级)，NetworkX  
离线算出pagerank值归一化(每天计算一次)，作为参数相乘，调参    
用户反馈：权值归一化，作为参数相乘，调参  
网页质量：网页长度  
最后根据simhash去除相似页面  
### 1.3 基于NB的网页分类器
这里主要还是借助了信息检索领域中的文本分类的方法。基于词袋模型。基于词袋模型的文本分类的重要前提是认为：文档的内容与其中所包含的词有着必然的联系。  
VSM模型是文本分类问题的文档表示模型。  
VSM模型是在词袋模型的基础之上的模型，完全忽略了除了词信息以外的所有部分，这使得其所能表达的信息量存在上限。  
相比较于分类算法，对特征的选择会更影响分类的效果。  
词向量表示：Word2Vec TF/IDF 作为权重  
文本分类问题的另一个特性：向量稀疏性  
去停用词，词根还原。使用NLTK  
朴素贝叶斯算法  
特征词提取（降维）特征选择：TF-IDF阈值  
分词：jieba分词（python）
分类效果一般  
拓展：超文本分类 网站特征  
文本分类库：TextGrocery
贝叶斯分类的推导
### 1.4 关键词生成方案  

### 1.5 工程问题
去标签pattern.web存到ES，网页存到hdfs做离线分析，后续ES读写分离，编写ES插件从kafka里pull数据  
HDFS块存储，使用json，dump序列化之后放入redis，HDFS端读redis，组成arraylist，达到64MB后，再序列化写入hdfs文件块  
高亮：自带b标签  
摘要截取：高亮关键词前30字节后70字节  
搜索：普通搜索  
spark与NetworkX图计算
## 2. 暗网爬虫
### 2.1 元搜索引擎采集
使用的搜索引擎360、有道、bing、duckduckgo、disconnect、google、yahoo  
元搜索引擎searx 
元搜索代理资源获取，网络免费代理，zmap扫描常用代理端口的代理，Tor代理 
透明代理，普通匿名代理，高匿代理 代理验证，ip地理位置，可访问站点  
代理优先级计算公式  
模拟登陆 抓包获取提交字段 模拟表单提交 获取cookie python中cookieJar对象 封装requests库或者urllib2  
对于获取到的结果以页面url作为唯一标识使用投票排序，不同搜索引擎的结果有不同的权重    
实时性优化采用延迟加载技术  
借助于元搜索引擎的onion地址采集技术，循环搜索直到新地址不再出现为止  
gevent协程的并发数据采集框架gtaskpool(zhangwentao的ppt，待总结)  
在线验证gtaskpool，urllib2，http、https、socks代理  
说是协程池，因为协程的创建和删除并不需要资源消耗，完全是代码级别的切换，所以协程池就是限制了协程的数目  
### 2.2 分布式爬虫框架
框架功能：
- 支持爬取任务提交；  
- 爬虫机器scrapy横向热扩展；  
- 单个页面的优先级设置；  
- 基于twisted的并发爬取与pipeline操作；   
- 基于kafka的爬虫任务控制（下发、暂停、取消、爬取信息，主要从redis里遍历统计得到）

任务设置粒度有：appid,crawlid,spiderid 字段有起始url，任务优先级，allow_domains，是否使用代理，代理类型，是否使用随机ua，ua类型，是否使用cookie，cookie字段，allow_regex
deny_domain、最大深度、当前任务状态（1:可执行，0:暂停）、超时时间。  
kafka topics：
- demo.incoming_urls
- demo.crawled_firehose
- demo.outbound_firehose
- demo.$(appid)_firehose
redis keys:
- zset: link:queue
- set: dupfilter:crawlid (2min超时删除)

架构图  
64GB主从redis服务，url状态爆炸很容易link:queue就满了。  
暂时的解决方案：当超过redis占用内存超过75%时，随机移除一些value值，放入elasticsearch集群中进行暂存，等memory负载低于20%，再往redis里放。
现在的状态：一直在往外挪，没有往里面回写。  
爬取优先级：可自主设定，默认每一层页面优先级减10。  
scrapy架构图
### 2.3 爬虫优化  
代理资源调度算法  
ua分类233个（客户端分类，浏览器分类，操作系统分类），轮询算法  
网页去标签后，计算simhash值：
- 将simhash存入Elasticsearch中（term）为何不用mysql，大量新增，不适合建立索引
- BF的方法，最终被抛弃，占内存，速度也没见得有多快

url归一化：web数据挖掘相应章节  
爬虫聚类逃逸算法：
有些url实际上是一样的页面，但是由于url动态生成导致url不一样，爬虫往深了爬，就会一直陷入到这种循环里面  
解决方法：
- 限制爬取层数
- 使用清华大学的一片论文中提到的动态url聚类算法，聚成一类的url中，如果有超过90%的页面都是相似的，那么讲该类的url标注为重复。

在实际工程中采用了以上两者相结合的方法。  
登录页面的自动识别：根据标签识别，使用机器学习库的方法识别。  
post字段，从静态页面中提取，模拟登录之后提取。  
获取cookieJar
支持http、socks代理  
参考autologin源码 
任务下发，站点重要性评估公式，定时任务。  
增量爬取（网页重访）：泊松分布模型 web知识挖掘对应章节 待展开 
Rabbitmq消息传输系统：项目需求，数据分片（每个消息小于1400），json自带序列化方法。  
分布式发送消息，单机接收消息，吞吐量问题。
解决方式：ES连接池、多线程、Rabbitmq异步消费者，RPC模式的断线重连。  
协程不能用，因为ES提供的接口是同步阻塞的接口。  
SpringMVC 简要了解一下，能讲出来大概就行。  







