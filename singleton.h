#include<pthread.h>
class Singleton{
    private:
        static Singleton * Instance;
        Singleton();
        Singleton(const Singleton &);
        Singleton & operator= (const Singleton &);
    public:
        static Singleton * getInstance();
};
Singleton * Singleton::Instance = new Singleton();
Singleton * Singleton::getInstance(){
    if (Instance==NULL)
    {
        lock();
        if(Instance==NULL)
        {
            Instance = new Singleton();
        }
        unlock();
    }
    return Instance;
}

class MutexLock{
    private:
        pthread_mutex_t _mutex;
        pid_t _holder;
    public:
        MutexLock():_holder(0){pthread_mutex_init(&_mutex,NULL);}
        ~MutexLock()
        {
            assert(_holder==0);
            pthread_mutex_destroy(&_mutex);
        }
        
        
};