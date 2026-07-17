
1. 安装对应库（库里其实也是导入tushare，修改了地址）
pip install tnskhdata

2. 把import tushare as ts修改为
import tnskhdata as ts

import tnskhdata as ts
pro = ts.pro_api('Tushare_apikey')


Tushare官方文档：https://tushare.pro/document/2
