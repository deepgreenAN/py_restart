# イテレーション時に進捗を保存
イテレーションが何らかの例外によって途中で終了した場合，その進捗状況を一時ファイルに保存し，再度実行時にそこから開始できる．

### 使い方

```python
from pathlib import Path
from py_restart import enable_counter, multi_count, simple_counter
```

#### 一つの場合 

以下のように，`enable_counter`をwith文に添えた返り値でイテレーターをラップする．イテレーション内でエラーが生じた場合に，一時ファイルを保存し，次回はエラーが起きたイテレーションから再開できる．
この例では，iが4のときにKeybordInterruptを行った後，もう一度実行した結果である．


```python
tempfile_path = Path("temp1.tmp")

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
    

#### 一つの場合(毎回保存する場合) 

with文を利用したくない場合，`simple_couonter`が利用できる．`simple_counter`は直接ジェネレータを出力するが，毎回一時ファイルを更新し，保存する．


```python
tempfile_path = Path("temp2.tmp")

for i in simple_counter(tempfile_path, range(10)):
    print(i)
    time.sleep(3)
```

    4
    5
    6
    7
    8
    9
    

#### 二つ以上の場合 

`enable_counter`あるいは`simple_counter`のみでは，一つのfor文が終了したときに一時ファイルが削除されてしまうため二つ以上for文が連続する場合に進捗を保存できない．`multi_count{を利用すればそのインデントブロック内のすべてのでラップしたイテレーションが終了するまで一時ファイルを残すことができる．以下の例では，一つ目のfor文が終了したのちにiが2の時点でKeybordInterruptを行い，再度実行した結果である


```python
tempfile_path1 = Path("temp3.tmp")
tempfile_path2 = Path("temp4.tmp")

with multi_count():
    with enable_counter(tempfile_path1) as counter:
        for i in counter(range(10)):
            print("1:",i)
            time.sleep(3)
            
    print("1 is finished")
    for i in simple_counter(tempfile_path2, range(5)):
            print("2:",i)
            time.sleep(3)
```

    1 is finished
    2: 2
    2: 3
    2: 4
    

### 再帰的に使う場合 

以下の例では，iが1,jが2の時にKeybordInterruptを行ったのち，再度実行したものである．


```python
tempfile_path3 = Path("temp5.tmp")
tempfile_path4 = Path("temp6.tmp")

with enable_counter(tempfile_path3) as outer_counter:
    for i in outer_counter(range(5)):
        print("outer:",i)
        for j in simple_counter(tempfile_path4 ,range(5)):
                print("\tinner:",j)
                time.sleep(3)
```

    outer: 1
    	inner: 2
    	inner: 3
    	inner: 4
    outer: 2
    	inner: 0
    	inner: 1
    	inner: 2
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

以下のように，`multi_count`は再帰的に利用できない


```python
with multi_count():
    with multi_count():
        pass
```


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-85-3b3e455f2f62> in <module>
          1 with multi_count():
    ----> 2     with multi_count():
          3         pass
    

    <ipython-input-77-06c8301f69c3> in __enter__(self)
          8     def __enter__(self):
          9         if config.parent is not None:
    ---> 10             raise Exception("MultiCount has already opend. cannot open another MultiCount")
         11 
         12         config.parent = self.parent_restart
    

    Exception: MultiCount has already opend. cannot open another MultiCount

