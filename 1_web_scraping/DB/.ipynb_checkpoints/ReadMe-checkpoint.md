# 檔案結構

* `DB`資料夾下將有三類檔案

    * `0_original_preserved` ： 為保留第一次爬蟲時的最原初dictionary
    
    * `各職業名稱資料夾內的npy檔` ： 為每一次爬蟲更新資料時留下的tmp檔，會加上`sys.time`作為註記，以免覆蓋其他檔案
    
    * `DB`資料夾下的`.npy`檔 ： 為更新後保持最新的dictionary檔
    
        1. load 自己
        2. 用`self_dict.update(new_dict)`來更新
        3. `np.save()`儲存自己
        
* 路徑："/home/ubuntu/Python_Codes/HS/DB"