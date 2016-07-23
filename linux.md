# Linux高性能服务器编程 
## 1. tcpip协议详解
## 9. IO复用
非阻塞connect()实现  
步骤1： 设置非阻塞，启动连接  
实现非阻塞 connect ，首先把 sockfd 设置成非阻塞的。这样调用
connect 可以立刻返回，根据返回值和 errno 处理三种情况：  
(1) 如果返回 0，表示 connect 成功。  
(2) 如果返回值小于 0， errno 为 EINPROGRESS,  表示连接
      建立已经启动但是尚未完成。这是期望的结果，不是真正的错误。  
(3) 如果返回值小于0，errno 不是 EINPROGRESS，则连接出错了。  
 
步骤2：判断可读和可写  
然后把 sockfd 加入 select 的读写监听集合，通过 select 判断 sockfd
是否可写，处理三种情况：  
(1) 如果连接建立好了，对方没有数据到达，那么 sockfd 是可写的  
(2) 如果在 select 之前，连接就建立好了，而且对方的数据已到达，那么 sockfd 是可读和可写的。  
(3) 如果连接发生错误，sockfd 也是可读和可写的。  
判断 connect 是否成功，就得区别 (2) 和 (3)，这两种情况下 sockfd 都是可读和可写的，区分的方法是，调用 getsockopt 检查是否出错。  
 
步骤3：使用 getsockopt 函数检查错误  
getsockopt(sockfd, SOL\_SOCKET, SO\_ERROR, &error, &len)  
在 sockfd 都是可读和可写的情况下，我们使用 getsockopt 来检查连接
是否出错。但这里有一个可移植性的问题。  
如果发生错误，getsockopt 源自 Berkeley 的实现将在变量 error 中
返回错误，getsockopt 本身返回0；然而 Solaris 却让 getsockopt 返回 -1，
并把错误保存在 errno 变量中。所以在判断是否有错误的时候，要处理
这两种情况。