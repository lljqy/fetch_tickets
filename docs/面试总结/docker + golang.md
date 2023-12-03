golang中常见的数据结构
bool, byte, rune
int, int8, int16, int32, int64
float32, float64
complex64, complex128
string
数组，切片，map，函数和方法，接口，结构体

切片的底层原理
type slice struct {
 array unsafe.Pointer # 指向底层数组的指针
 len   int # 切片的长度，也就是说当前切片中的元素个数
 cap   int # 切片的容量，也就是说切片最大能够存储多少个元素
}
切片实际上是指向底层数组的一段片段，切片的长度可变，能够动态扩容，开发过程中比数组好用很多
扩容的规则：
    1. 当切片的容量小于256时，newCap = oldCap * 2
    2. 当切片容量大于256时，newCap = oldCap + (oldCap + 3 * 256) / 4

map的底层原理

channel的底层原理