# Linux高性能服务器编程 
## 1. tcpip协议族
数据链路层：ARP、RARP（询问网络管理设备自己的ip地址）  
网络层：ICMP：差错报文、查询报文；IP  
传输层：TCP、UDP  
应用层：ping、telent、OSPF、DNS  
数据链路层封装的数据被称为帧，使用6字节的目标物理地址和源物理地址，使用CRC校验包头和数据，MTU为1500字节。
数据包校验大都采用CRC校验。  
## 2.IP协议详解
IP为上层协议提供无状态、无连接、不可靠的服务。    
IP分片：当IP数据报的长度超过MTU，将会被分片传输。分片可能发生在任何一个传输中间节点上，只有到目标机器以后才会重新组装。  
MF标识 DF标识   
路由更新算法：RIP、OSPF、BGP   
## 3.TCP协议详解  
TCP相对于UDP协议的特点是面向连接、字节流、可靠传输。TCP连接是全双工的。  
由于内核的发送缓冲区与接收缓冲区的存在，TCP模块发送出的TCP报文段的个数和应用程序执行的写操作的次数之间没有固定的数量关系。接收模块同上。  
TCP头部至少为20byte，包括2byte的源端口与目的端口号，4byte的seq和ack，标志位，2byte的窗口大小，2byte的CRC校验，2byte的紧急指针。  
三次握手、四次挥手  
超时重连报文段的seq是一样的，间隔时间分别为1s、2s、4s……5次重连失败以后放弃连接并通知应用程序。    
TIME_WAIT状态是客户端等待两个报文段最大生存时间（2MSL），以确保两个方向上的所有报文段都已经失效，才完全关闭。
## 5.Linux网络编程基础API
网络字节序转主机字节序函数：htons,htonl,ntohs,ntohl  
通用socket地址：socket网络编程中表示socket地址的是结构体sockaddr。定义如下：  
struct sockaddr  
{  
      sa\_family\_t sa\_family;  
      char sa_data[14];   
}    
TCP/IP协议族有sockaddr\_in和sockaddr\_in6两个专用socket地址结构体。  
struct sockaddr\_in  
{  
      sa\_family\_t sin\_family;  
      u\_int16\_t sin\_port;  
      struct in\_addr sin\_addr;  
}    
struct in\_addr  
{  
      u\_int32\_t s_addr;  
}  
IP地址转换函数：inet\_pton,inet\_ntop;    
创建socket：int socket(int domain,int type,int protocol);非阻塞SOCK\_NONBLOCK;    
绑定socket：int bind(int sockfd,const struct sockaddr* my\_addr, socklen\_t addrlen);  
监听socket：int listen(int sockfd,int backlog);  
接收连接：int accpet(int sockfd,struct sockaddr * addr, socklen\_t *addrlen);  
发起连接：int connect(int sockfd,const struct sockaddr *serv\_addr, socklen\_t addrlen);  
关闭连接：int close(int fd);基于引用计数；直接关闭连接：int shutdown(int fd);  
数据读写：ssize\_t recv(int sockfd, void *buf, size\_t len, int flags);ssize_t send(…);  
UDP数据读写：ssize\_t recvfrom sendto;  
通用数据读写函数：ssize\_t recvmsg sendmsg;  
地址信息函数：int getsockname(本机端) getpeername(远端);  
socket选项：int getsockopt setsockopt;  
TIME\_WAIT：状态重用SO\_REUSEADDR;  
## 6.高级IO函数
未名管道: int pipe(int fd[2]);  


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