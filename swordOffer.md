# 2.面试需要的基础知识
面试题1：
CMyString & operator = (const CMyString &str)
{
    if(this == &str)
        return *this;
    delete []m_pData;//考虑此步骤的异常安全性
    m_pData = NULL;
    m_pData = new char[strlen(str.m_pData)+1];
    strcpy(m_pData,str.m_pData);

    return *this;
}
