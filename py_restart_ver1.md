# イテレーション時に進捗を保存
イテレーションが何らかの例外によって途中で終了した場合，その進捗状況を一時ファイルに保存し，再度実行時にそこから開始できる．

### 使い方

```python
from pathlib import Path
from py_restart import enable_counter, multi_count
```

#### 一つの場合 
以下のように，`enable_counter`をwith文に添えた返り値でイテレーターをラップする．
この例では，`i`が4のときにKeybord interruptを行った後，もう一度実行した結果である．

```python
tempfile_path = Path("temp.tmp")

with enable_counter(tempfile_path) as counter:
    for i in counter(range(10)):
        print(i)
        time.sleep(3)
```

    4
    5
    6
    7
    8
    9
    

### 二つ以上の場合 
`enable_counter`のみでは，一つのfor文が終了したときに一時ファイルが削除されてしまうため二つ以上for文が連続する場合に進捗を保存できない．`multi_count`を利用すればそのインデントブロック内のすべての`enable_counter`でラップしたイテレーションが終了するまで一時ファイルを残すことができる．以下の例では，一つ目のfor文が終了したのちに`i`が2の時点でKeybord interruptを行い，再度実行した結果である．

```python
tempfile_path1 = Path("temp1.tmp")
tempfile_path2 = Path("temp2.tmp")

with multi_count():
    with enable_counter(tempfile_path1) as counter:
        for i in counter(range(10)):
            print("1:",i)
            time.sleep(3)
            
    print("1 is finished")
    with enable_counter(tempfile_path2) as counter:
        for i in counter(range(5)):
            print("2:",i)
            time.sleep(3)
```

    1 is finished
    2: 2
    2: 3
    2: 4
    

### 再帰的に使う場合 


```python
tempfile_path3 = Path("temp3.tmp")
tempfile_path4 = Path("temp4.tmp")

with enable_counter(tempfile_path3) as outer_counter:
    for i in outer_counter(range(5)):
        print("outer:",i)
        with enable_counter(tempfile_path4) as inner_conter:
            for j in inner_conter(range(5)):
                print("\tinner:",j)
                time.sleep(3)
```

    outer: 2
    	inner: 3
    	inner: 4
    outer: 3
    	inner: 0
    	inner: 1
    	inner: 2
    	inner: 3
    	inner: 4
    outer: 4
    	inner: 0
    	inner: 1
    	inner: 2
    	inner: 3
    	inner: 4
    

###  エラーとなる処理


```python
with enable_counter(tempfile_path) as counter:
    with multi_count():
        pass
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-163-f5a499529421> in <module>
          1 with enable_counter(tempfile_path) as counter:
    ----> 2     with multi_count():
          3         pass
    

    <ipython-input-153-80c9ab78e5ba> in __enter__(self)
         10             raise Exception("MultiCount has already opend. cannot open another MultiCount")
         11         if config.is_enable:
    ---> 12             raise Exception("Counter has already opened. please close Counter")
         13 
         14         config.parent = self.parent_restart
    

    Exception: Counter has already opened. please close Counter



```python
with multi_count():
    with multi_count():
        pass
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-164-3b3e455f2f62> in <module>
          1 with multi_count():
    ----> 2     with multi_count():
          3         pass
    

    <ipython-input-153-80c9ab78e5ba> in __enter__(self)
          8     def __enter__(self):
          9         if config.parent is not None:
    ---> 10             raise Exception("MultiCount has already opend. cannot open another MultiCount")
         11         if config.is_enable:
         12             raise Exception("Counter has already opened. please close Counter")
    

    Exception: MultiCount has already opend. cannot open another MultiCount

