import unittest
from pathlib import Path
import pickle

from py_restart import multi_count, enable_counter, simple_counter


class SaveLoadContent():
    """
    何かしらをpickleで保存する
    """
    def __init__(self, content):
        self.content = content
        
    def save(self, save_path):
        with open(save_path, "wb") as f:
            pickle.dump(self.content, f)
            
    def load(self, load_path):
        with open(load_path, "rb") as f:
            self.content = pickle.load(f)


class TestRestart(unittest.TestCase):
    def setUp(self):
        test_path = Path("test")
        tmp_list = list(test_path.glob("*.tmp"))
        for tmp_path in tmp_list:
            tmp_path.unlink()
            
    def tearDown(self):
        test_path = Path("test")
        tmp_list = list(test_path.glob("*.tmp"))
        self.assertEqual(len(tmp_list), 0)
        pickle_list = list(test_path.glob("*.pickle"))
        self.assertEqual(len(pickle_list), 0)
        
    def test_enable_counter(self):
        # 通常の利用
        tempfile_path = Path("test/temp1.tmp")
        iter_counter = 0
        try:
            with enable_counter(tempfile_path) as counter:
                for i in counter(range(10)):
                    if iter_counter >= 5:
                        raise Exception("stop iteration")
                    iter_counter+= 1
        except:
            pass
        
        with enable_counter(tempfile_path) as counter:
            for i in counter(range(10)):
                iter_counter += 1
                
        self.assertEqual(iter_counter, 10)
        
        # 何もしない
        tempfile_path = Path("test/temp2.tmp")
        iter_counter = 0
        try:
            with enable_counter(tempfile_path, use_tempfile=False) as counter:
                for i in counter(range(10)):
                    if iter_counter >= 5:
                        raise Exception("stop iteration")
                    iter_counter+= 1
        except:
            pass
        with enable_counter(tempfile_path, use_tempfile=False) as counter:
            for i in counter(range(10)):
                iter_counter += 1
                
        self.assertEqual(iter_counter, 15)
        
        
        
    def test_simple_counter(self):
        # 通常の利用
        tempfile_path = Path("test/temp1.tmp")
        
        iter_counter = 0
        try:
            for i in simple_counter(tempfile_path, range(10)):
                if iter_counter >= 5:
                    raise Exception("stop iteration")
                iter_counter+= 1
        except:
            pass
        
        for i in simple_counter(tempfile_path,range(10)):
            iter_counter += 1
                
        self.assertEqual(iter_counter, 10)
        
        # 何もしない
        tempfile_path = Path("test/temp2.tmp")
        
        iter_counter = 0
        try:
            for i in simple_counter(tempfile_path, range(10), use_tempfile=False):
                if iter_counter >= 5:
                    raise Exception("stop iteration")
                iter_counter+= 1
        except:
            pass
        
        for i in simple_counter(tempfile_path,range(10), use_tempfile=False):
            iter_counter += 1
                
        self.assertEqual(iter_counter, 15)       
        
        # save_spanを変更
        tempfile_path = Path("test/temp3.tmp")
        
        iter_counter = 0
        try:
            for i in simple_counter(tempfile_path, range(10), save_span=4): 
                if iter_counter >= 5:
                    raise Exception("stop iteration")
                iter_counter+= 1
        except:
            pass
        
        for i in simple_counter(tempfile_path,range(10), save_span=4):
            iter_counter += 1
                
        self.assertEqual(iter_counter, 11)
    
    def test_multi_count(self):
        tempfile_path1 = Path("test/tempfile1.tmp")
        tempfile_path2 = Path("test/tempfile2.tmp")
        
        iter_counter1 = 0
        iter_counter2 = 0
        
        try:
            with multi_count():
                with enable_counter(tempfile_path1) as counter:
                    for i in counter(range(10)):
                        iter_counter1 += 1
                        
                for i in simple_counter(tempfile_path2, range(10)):
                    if iter_counter2 >= 5:
                        raise Exception("stoi iteration")
                    iter_counter2 += 1
        except:
            pass
        with multi_count():
            with enable_counter(tempfile_path1) as counter:
                for i in counter(range(10)):
                    iter_counter1 += 1

            for i in simple_counter(tempfile_path2, range(10)):
                iter_counter2 += 1
        
        
        self.assertEqual(iter_counter1, 10)
        self.assertEqual(iter_counter2, 10)
        
    def test_save_load_object(self):
        tempfile_path = Path("test/tempfile1.tmp")
        save_object = {"sum":0}
        save_object_path = Path("test/temp_sum.pickle")
        
        try:
            with enable_counter(tempfile_path) as counter:
                save_object = counter.save_load_object(save_object, save_object_path)
                for i in counter(range(10)):
                    if i >= 5:
                        raise Exception("stop iteration")
                    save_object["sum"] += i  
                    counter.object = save_object
        except:
            pass
        
        load_object = {"sum":100}
        with enable_counter(tempfile_path) as counter:
            load_object = counter.save_load_object(load_object, save_object_path)
            for i in counter(range(10)):
                load_object["sum"] += i
                
        self.assertEqual(load_object["sum"], 45)
        
    def test_save_load_func(self):
        tempfile_path = Path("test/tempfile1.tmp")
        save_content = SaveLoadContent([0,0,0,0,0])
        save_object_path = Path("test/temp_content.pickle")
        
        try:
            with enable_counter(tempfile_path) as counter:
                counter.save_load_funcs(save_funcs=[save_content.save],
                                        load_funcs=[save_content.load],
                                        func_paths=[save_object_path]
                                       )
                for i in counter(range(10)):
                    if i>= 5:
                        raise Exception("stop iteration")

                    save_content.content = [item+i for item in save_content.content]
        except:
            pass
        load_content = SaveLoadContent([0,0,0,0,0])
        
        with enable_counter(tempfile_path) as counter:
            counter.save_load_funcs(save_funcs=[load_content.save],
                                    load_funcs=[load_content.load],
                                    func_paths=[save_object_path]
                                   )
            for i in counter(range(10)):
                load_content.content = [item+i for item in load_content.content]  
            
        self.assertTrue(all([item==45 for item in load_content.content]))

if __name__ == "__main__":
    unittest.main()