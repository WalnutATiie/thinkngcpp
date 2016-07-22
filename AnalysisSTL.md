# STL源码剖析
## 1.空间配置器
简单的泛型空间配置器：allocate,construct,deallocate,destruct  
具备sub-allocation的SGI空间配置器  
std::allocator  
std:alloc  
利用placement new 定义全局construct()和destory()
destory()的两个版本，第一个版本接收一个指针，准备将该指针所指之物析构掉，直接调用该对象的析构函数即可；  
第二个版本接受begin和end两个迭代器，将迭代器范围之内的所有对象析构掉。在这之前判别析构对象是否是内置类型，否则才进行析构。  
空间的配置和释放：SGI设计的时候考虑到一下问题：  
- 向system heap要求空间
- 考虑多线程的状态  
- 考虑内存不足的应变措施  
- 考虑内存碎片问题  

SGI STL设计空间配置的时候设计了两级配置器。  
> SGI STL第一级配置器  
1.allocate()直接使用malloc(),deallocate()直接使用free().  
2.模拟C++的set_new_handler()以处理内存不足的情况。  

> SGI STL第二级配置器  
1.维护16个自由链表，负责16种小型区块的次配置能力。内存池以malloc()配置而得。如果内存不足，转调用至第一级配置器。  
2.如果需求区块大于128bytes，就转调用第一级配置器。  

第二级配置器中16个free-lists，各自分别管理8、16、24byte……的小额区块。  
第二级配置器中拥有配置器的标准接口函数allocate()。此函数首先判断区块的大小，大于128byte就调用一级配置器，小于就检查对应的free list。  
如果free list中有可用的区块，就直接拿来使用，如果没有可用的区块，就讲区块大小上调至8倍数边界，然后调用refill()，准备为free list重新填充空间。  
deallocate()中首先判断是否小于128byte，否则找到对应的free list区块，进行回收。  

第二级配置器中[内存池](http://qqsunkist.iteye.com/blog/1504895)的实现 
STL定义有五个全局函数，作用于未初始化空间上。construct(),destruct(),uninitialized\_copy(),uninitialized\_fill(),uninitialized\_fill\_n()。  
## 2.迭代器与traits编程技法
STL的中心设计思想是：将数据容器和算法分开，彼此独立设计，再使用迭代器将二者撮合在一起。  
迭代器是一种智能指针。auto_ptr的例子。  
迭代器相应型别的实现：函数模板的参数推导机制。  
迭代器相应型别：value type,difference type,reference type,pointer type,iterator type  
## 3.序列式容器
C++ array;STL vector,deque,list,stack,priority-queue,queue  
vector与vector迭代器定义  
capacity扩充为原来的两倍
deque和vector的区别：  
deque允许常数时间内对头部进行元素的插入和删除；deque没有capacity的概念，因为它是动态地以分段连续空间组合而成，随时可以增加一段新的空间并连接起来，因此deque没有reserve功能；deque虽然也提供随机访问，但是它的迭代器不是普通的指针，其复杂度和vector没有可比性。除非必要，应尽可能选择vector而非deque。如果要对deque进行排序操作，为了提高效率，可以复制到一个vector容器中进行排序。  
deque由一段一段的连续空间构成，可以在头端尾端串接新申请的连续空间，并通过map的映射设计，封装出可以随机存取的接口。  
stack、queue都是基于deque而实现的，stack、queue被称作container adapter，二者没有迭代器。  
priority queue的实现是用max-heap来实现的，没有迭代器。  
push\_heap建堆，pop\_heap弹出并调整堆。  
slist不是STL标准里面的，SGI STL将其包含在内