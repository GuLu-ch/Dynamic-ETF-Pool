# ETF专题
## ETF基础信息
- 接口：etf_basic
- 描述：获取国内ETF基础信息，包括了QDII。数据来源与沪深交易所公开披露信息。
- 限量：单次请求最大放回5000条数据（当前ETF总数未超过2000）
- 权限：用户积8000积分可调取，具体请参阅积分获取办法

### 输入参数
名称	类型	必选	描述
ts_code	str	N	ETF代码（带.SZ/.SH后缀的6位数字，如：159526.SZ）
index_code	str	N	跟踪指数代码
list_date	str	N	上市日期（格式：YYYYMMDD）
list_status	str	N	上市状态（L上市 D退市 P待上市）
exchange	str	N	交易所（SH上交所 SZ深交所）
mgr	str	N	管理人（简称，e.g.华夏基金)

### 输出参数
名称	类型	默认显示	描述
ts_code	str	Y	基金交易代码
csname	str	Y	ETF中文简称
extname	str	Y	ETF扩位简称(对应交易所简称)
cname	str	Y	基金中文全称
index_code	str	Y	ETF基准指数代码
index_name	str	Y	ETF基准指数中文全称
setup_date	str	Y	设立日期（格式：YYYYMMDD）
list_date	str	Y	上市日期（格式：YYYYMMDD）
list_status	str	Y	存续状态（L上市 D退市 P待上市）
exchange	str	Y	交易所（上交所SH 深交所SZ）
mgr_name	str	Y	基金管理人简称
custod_name	str	Y	基金托管人名称
mgt_fee	float	Y	基金管理人收取的费用
etf_type	str	Y	基金投资通道类型（境内、QDII）

### 接口示例
#获取当前所有上市的ETF列表
df = pro.etf_basic(list_status='L', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')


#获取“嘉实基金”所有上市的ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取“嘉实基金”在深交所上市的所有ETF列表
df = pro.etf_basic(mgr='嘉实基金'， list_status='L', exchange='SZ', fields='ts_code,extname,index_code,index_name,exchange,etf_type')


#获取以沪深300指数为跟踪指数的所有上市的ETF列表
df = pro.etf_basic(index_code='000300.SH', fields='ts_code,extname,index_code,index_name,exchange,mgr_name')


### 数据示例
ts_code       extname    index_code    index_name exchange   mgr_name
0   159238.SZ      300ETF增强  000300.SH    沪深300指数       SZ   景顺长城基金
1   159300.SZ        300ETF  000300.SH    沪深300指数       SZ     富国基金
2   159330.SZ    沪深300ETF基金  000300.SH    沪深300指数       SZ   西藏东财基金
3   159393.SZ    沪深300指数ETF  000300.SH    沪深300指数       SZ     万家基金
4   159673.SZ    沪深300ETF鹏华  000300.SH    沪深300指数       SZ     鹏华基金
5   159919.SZ      沪深300ETF  000300.SH    沪深300指数       SZ     嘉实基金
6   159925.SZ    沪深300ETF南方  000300.SH    沪深300指数       SZ     南方基金
7   159927.SZ     鹏华沪深300指数  000300.SH    沪深300指数       SZ     鹏华基金
8   510300.SH      沪深300ETF  000300.SH    沪深300指数       SH   华泰柏瑞基金
9   510310.SH   沪深300ETF易方达  000300.SH    沪深300指数       SH    易方达基金


## ETF基准指数列表
- 接口：etf_index
- 描述：获取ETF基准指数列表信息
- 限量：单次请求最大返回5000行数据（当前未超过2000个）
- 权限：用户积累8000积分可调取，具体请参阅积分获取办法

### 输入参数
名称	类型	必选	描述
ts_code	str	N	指数代码
pub_date	str	N	发布日期（格式：YYYYMMDD）
base_date	str	N	指数基期（格式：YYYYMMDD）

### 输出参数
名称	类型	默认显示	描述
ts_code	str	Y	指数代码
indx_name	str	Y	指数全称
indx_csname	str	Y	指数简称
pub_party_name	str	Y	指数发布机构
pub_date	str	Y	指数发布日期
base_date	str	Y	指数基日
bp	float	Y	指数基点(点)
adj_circle	str	Y	指数成份证券调整周期

### 接口示例
#获取当前ETF跟踪的基准指数列表
df = pro.etf_index(fields='ts_code,indx_name,pub_date,bp')

### 数据示例
ts_code        indx_name         pub_date           bp
0        000068.SH         上证自然资源指数  20100528  1000.000000
1        000001.SH           上证综合指数  19910715   100.000000
2        000989.SH       中证全指可选消费指数  20110802  1000.000000
3       000990.CSI       中证全指主要消费指数  20110802  1000.000000


## ETF实时分钟
- 接口：rt_etf_min
- 描述：获取ETF实时分钟数据，包括1~60min
- 限量：单次最大1000行数据，可以通过ETF代码提取数据，支持逗号分隔的多个代码同时提取
- 权限：正式权限请参阅 权限说明
- 注：支持股票当日开盘以来的所有ETF历史分钟数据提取，接口名：rt_etf_min_daily（仅支持一个个代码提取，不同同时提取多个），可以在线开通权限。
### 输入参数
名称	类型	必选	描述
freq	str	Y	1MIN,5MIN,15MIN,30MIN,60MIN （大写）
ts_code	str	Y	支持单个和多个：589960.SH 或者 589960.SH,159100.SZ

### freq参数说明
freq	说明
1MIN	1分钟
5MIN	5分钟
15MIN	15分钟
30MIN	30分钟
60MIN	60分钟

### 输出参数

名称	类型	默认显示	描述
ts_code	str	Y	股票代码
time	None	Y	交易时间
open	float	Y	开盘价
close	float	Y	收盘价
high	float	Y	最高价
low	float	Y	最低价
vol	float	Y	成交量(股）
amount	float	Y	成交额（元）


### 接口用法
pro = ts.pro_api()

#获取科创新能源ETF易方达589960.SH的实时分钟数据
df = pro.rt_etf_min(ts_code='589960.SH', freq='1MIN')



## ETF实时分钟-日累计
- 接口：rt_etf_min_daily
- 描述：获取ETF实时分钟数据日累计，包括1~60min
- 限量：单次最大1000行数据，支持股票当日开盘以来的所有ETF历史分钟数据提取（仅支持一个个代码提取，不同同时提取多个）
- 权限：正式权限请参阅 权限说明



### 输入参数
名称	类型	必选	描述
freq	str	Y	1MIN,5MIN,15MIN,30MIN,60MIN （大写）
ts_code	str	Y	只支持单个


### freq参数说明
freq	说明
1MIN	1分钟
5MIN	5分钟
15MIN	15分钟
30MIN	30分钟
60MIN	60分钟


### 输出参数
名称	类型	默认显示	描述
ts_code	str	Y	股票代码
time	None	Y	交易时间
open	float	Y	开盘价
close	float	Y	收盘价
high	float	Y	最高价
low	float	Y	最低价
vol	float	Y	成交量(股）
amount	float	Y	成交额（元）
### 代码示例

    # 导入sdk包
    import tushare as ts
    # 配置凭据，如果已全局配置了，可以忽略。
    ts.set_token('<--your-token-->')
    # 获取接口实例
    pro = ts.pro_api()
    # 获取科创芯片设计ETF（588780.SH）当日1分钟实时行情
    df = pro.rt_etf_min_daily(ts_code='588780.SH',freq='1MIN')


### 数据结果
code  freq                 time   open  close   high    low         vol      amount
0   588780.SH  1MIN  2026-06-10 09:30:00  1.024  1.024  1.024  1.024    729200.0    746701.0
1   588780.SH  1MIN  2026-06-10 09:31:00  1.024  1.038  1.038  1.024   3068800.0   3169337.0
2   588780.SH  1MIN  2026-06-10 09:32:00  1.038  1.052  1.052  1.038   4226200.0   4415521.0


## ETF历史分钟行情

- 接口：etf_mins
- 描述：获取ETF分钟数据，支持1min/5min/15min/30min/60min行情，提供Python SDK和 http Restful API两种方式
- 限量：单次最大8000行数据，可以通过股票代码和时间循环获取，本接口可以提供超过10年ETF历史分钟数据
- 权限：正式权限请参阅 权限说明



### 输入参数
名称	类型	必选	描述
ts_code	str	Y	ETF代码，e.g. 159001.SZ
freq	str	Y	分钟频度（1min/5min/15min/30min/60min）
start_date	datetime	N	开始日期 格式：2025-06-01 09:00:00
end_date	datetime	N	结束时间 格式：2025-06-20 19:00:00


### freq参数说明
freq	说明
1min	1分钟
5min	5分钟
15min	15分钟
30min	30分钟
60min	60分钟


### 输出参数
名称	类型	默认显示	描述
ts_code	str	Y	ETF代码
trade_time	str	Y	交易时间
open	float	Y	开盘价
close	float	Y	收盘价
high	float	Y	最高价
low	float	Y	最低价
vol	int	Y	成交量（股）
amount	float	Y	成交金额（元）


### 接口用法
    pro = ts.pro_api()

    #获取沪深300ETF华夏510330.SH的历史分钟数据
    df = pro.etf_mins(ts_code='510330.SH', freq='1min', start_date='2025-06-20 09:00:00', end_date='2025-06-20 19:00:00')


### 数据样例
ts_code           trade_time  close   open   high    low        vol      amount
0    510330.SH  2025-06-20 15:00:00  3.991  3.991  3.992  3.990   800600.0   3194805.0
1    510330.SH  2025-06-20 14:59:00  3.991  3.990  3.991  3.989   182500.0    728177.0
2    510330.SH  2025-06-20 14:58:00  3.990  3.992  3.992  3.990   113700.0    453763.0




## ETF实时日线
- 接口：rt_etf_k
- 描述：获取ETF实时日k线行情，支持按ETF代码或代码通配符一次性提取全部ETF实时日k线行情
- 积分：本接口是单独开权限的数据，单独申请权限请参考权限列表


### 输入参数

名称	类型	必选	描述
ts_code	str	Y	支持通配符方式，e.g. 5*.SH、15*.SZ、159101.SZ
topic	str	Y	分类参数，取上海ETF时，需要输入'HQ_FND_TICK'，参考下面例子


注：ts_code代码一定要带.SH/.SZ/.BJ后缀



### 输出参数

名称	类型	默认显示	描述
ts_code	str	Y	ETF代码
name	None	Y	ETF名称
pre_close	float	Y	昨收价（元）
high	float	Y	最高价（元）
open	float	Y	开盘价（元）
low	float	Y	最低价（元）
close	float	Y	收盘价（最新价）
vol	int	Y	成交量（股）
amount	int	Y	成交金额（元）
num	int	Y	开盘以来成交笔数
ask_volume1	int	N	委托卖盘（股）
bid_volume1	int	N	委托买盘（股）
trade_time	str	N	交易时间


### 接口示例

    #获取今日所有深市ETF实时日线和成交笔数
    df = pro.rt_etf_k(ts_code='1*.SZ')

    #获取今日沪市所有ETF实时日线和成交笔数
    df = pro.rt_etf_k(ts_code='5*.SH', topic='HQ_FND_TICK')


### 数据示例

ts_code      name      pre_close     high     open     low    close        vol     amount    num
0    520860.SH      港股通科      1.024    1.054    1.048   1.041    1.048   15071600   15780985    307
1    515320.SH    电子50        1.173    1.211    1.184   1.184    1.206    1830600    2191339     98
2    511600.SH    货币ETF     100.008  100.003  100.002  99.999  100.000      12022    1202204     28
3    501075.SH      科创主题      2.350    2.400    2.357   2.357    2.400       4200      10040     11



## ETF日线行情
- 接口：fund_daily
- 描述：获取ETF行情每日收盘后成交数据，历史超过10年
- 限量：单次最大5000行记录，可以根据ETF代码和日期循环获取历史，总量不限制
- 积分：需要至少5000积分才可以调取，8000积分频次更高，具体请参阅积分获取办法





### 输入参数

名称	类型	必选	描述
ts_code	str	N	基金代码
trade_date	str	N	交易日期(YYYYMMDD格式，下同)
start_date	str	N	开始日期
end_date	str	N	结束日期




### 输出参数

名称	类型	默认显示	描述
ts_code	str	Y	TS代码
trade_date	str	Y	交易日期
open	float	Y	开盘价(元)
high	float	Y	最高价(元)
low	float	Y	最低价(元)
close	float	Y	收盘价(元)
pre_close	float	Y	昨收盘价(元)
change	float	Y	涨跌额(元)
pct_chg	float	Y	涨跌幅(%)
vol	float	Y	成交量(手)
amount	float	Y	成交额(千元)




### 接口示例

    pro = ts.pro_api()

    #获取”沪深300ETF华夏”ETF2025年以来的行情，并通过fields参数指定输出了部分字段
    df = pro.fund_daily(ts_code='510330.SH', start_date='20250101', end_date='20250618', fields='trade_date,open,high,low,close,vol,amount')




### 数据示例

trade_date   open   high    low  close         vol       amount
0     20250618  4.008  4.024  3.996  4.017   382896.00   153574.446
1     20250617  4.015  4.022  4.000  4.014   440272.04   176617.125
2     20250616  4.000  4.018  3.996  4.015   423526.00   169788.251
3     20250613  4.023  4.028  3.992  4.004  1216787.53   487632.318


## 基金复权因子
- 接口：fund_adj
- 描述：获取基金复权因子，用于计算基金复权行情
- 限量：单次最大提取2000行记录，可循环提取，数据总量不限制
- 积分：用户积600积分可调取，超过5000积分以上频次相对较高。具体请参阅积分获取办法





### 输入参数

名称	类型	必选	描述
ts_code	str	N	TS基金代码（支持多只基金输入）
trade_date	str	N	交易日期（格式：yyyymmdd，下同）
start_date	str	N	开始日期
end_date	str	N	结束日期
offset	str	N	开始行数
limit	str	N	最大行数




### 输出参数

名称	类型	默认显示	描述
ts_code	str	Y	ts基金代码
trade_date	str	Y	交易日期
adj_factor	float	Y	复权因子
### 接口使用

    pro = ts.pro_api()

    df = pro.fund_adj(ts_code='513100.SH', start_date='20190101', end_date='20190926')

### 数据示例

ts_code    trade_date  adj_factor
0    513100.SH   20190926         1.0
1    513100.SH   20190925         1.0
2    513100.SH   20190924         1.0
3    513100.SH   20190923         1.0



## ETF份额规模
- 接口：etf_share_size
- 描述：获取沪深ETF每日份额和规模数据，能体现规模份额的变化，掌握ETF资金动向，同时提供每日净值和收盘价；数据指标是分批入库，交易所于次日早8点30左右更新上一交易日的数据；另外，涉及海外的ETF数据更新会晚一些属于正常情况。
- 限量：单次最大5000条，可根据代码或日期循环提取
- 积分：需要8000积分可以调取，具体请参阅积分获取办法



### 输入参数
名称	类型	必选	描述
ts_code	str	N	基金代码 （可从ETF基础信息接口提取）
trade_date	str	N	交易日期（YYYYMMDD格式，下同）
start_date	str	N	开始日期
end_date	str	N	结束日期
exchange	str	N	交易所（SSE上交所 SZSE深交所）


### 输出参数
名称	类型	默认显示	描述
trade_date	str	Y	交易日期
ts_code	str	Y	ETF代码
etf_name	str	Y	基金名称
total_share	float	Y	总份额（万份）
total_size	float	Y	总规模（万元）
nav	float	N	基金份额净值(元)
close	float	N	收盘价（元）
exchange	str	Y	交易所（SSE上交所 SZSE深交所 BSE北交所）
### 代码示例
    #获取”沪深300ETF华夏”ETF2025年以来每个交易日的份额和规模情况
    df = pro.etf_share_size(ts_code='510330.SH', start_date='20250101', end_date='20251224')

    #获取2025年12月24日上交所的所有ETF份额和规模情况
    df = pro.etf_share_size(trade_date='20251224', exchange='SSE')
### 数据结果
trade_date    ts_code       etf_name  total_share    total_size exchange
0     20251224  510330.SH  沪深300ETF华夏   4741854.98  2.287898e+07      SSE
1     20251222  510330.SH  沪深300ETF华夏   4746894.98  2.279127e+07      SSE
2     20251219  510330.SH  沪深300ETF华夏   4756974.98  2.262512e+07      SSE
3     20251218  510330.SH  沪深300ETF华夏   4757514.98  2.253778e+07      SSE
4     20251217  510330.SH  沪深300ETF华夏   4756884.98  2.266418e+07      SSE


## ETF每日持仓组合(沪市）
- 接口：etf_sh_cons
- 描述：获取上交所场内所有ETF每日盘前披露的的一篮子组合信息,包括成分股票数量、申赎现金折溢价比例等数据
- 限量：单次最大3000条，可根据代码或日期循环提取
- 积分：需要8000积分可以调取，具体请参阅积分获取办法
-
### 输入参数
名称	类型	必选	描述
ts_code	str	N	板块代码
trade_date	str	N	交易日期(YYYYMMDD)
con_code	str	N	成分股票代码
start_date	str	N	开始日期(YYYYMMDD)
end_date	str	N	结束日期(YYYYMMDD)
### 输出参数
名称	类型	默认显示	描述
trade_date	str	Y	交易日期
ts_code	str	Y	ETF代码
con_code	str	Y	成分代码
con_name	str	Y	成分名称
qty	int	Y	股票数量(股)
sub_flag	str	Y	现金替代标志：允许/必须
cpr	float	Y	申购现金替代溢价比率（%）
rdr	float	Y	赎回现金替代折价比率（%）
sca	float	Y	替代金额(单位：人民币元)
exchange	str	Y	交易所代码HK港交所 SH上交所 SZ深交所 OTH其他

### 代码示例
    # 获取接口实例
    pro = ts.pro_api()

    # 获取517030易方达中证沪港深300ETF在2026年6月15日的持仓组合信息
    df = pro.etf_sh_cons(trade_date='20260615', ts_code='517030.SH')
    print(df)

### 数据结果
trade_date    ts_code   con_code con_name   qty sub_flag cpr rdr        sca exchange
0     20260615  517030.SH  000001.SZ     平安银行  1100       允许  15  60  12364.000       SZ
1     20260615  517030.SH   00001.HK       长和     0       必须   -   -      0.000       HK
2     20260615  517030.SH   00002.HK     中电控股     0       必须   -   -      0.000       HK





## ETF每日持仓组合(深市）

- 接口：etf_sz_cons
- 描述：获取深交所场内所有ETF每日盘前披露的一篮子组合信息,包括成分股票数量、申赎现金折溢价比例等数据
- 限量：单次最大3000条，可根据代码或日期循环提取
- 积分：需要8000积分可以调取，具体请参阅积分获取办法

### 输入参数
名称	类型	必选	描述
ts_code	str	N	板块代码
trade_date	str	N	交易日期(YYYYMMDD)
con_code	str	N	成分股票代码
start_date	str	N	开始日期(YYYYMMDD)
end_date	str	N	结束日期(YYYYMMDD)
### 输出参数
名称	类型	默认显示	描述
trade_date	str	Y	交易日期
ts_code	str	Y	ETF代码
con_code	str	Y	成分代码
con_name	str	Y	成分名称
qty	int	Y	股票数量(股)
sub_flag	str	Y	现金替代标志
cpr	float	Y	申购现金替代保证金率（%）
rdr	float	Y	赎回现金替代保证金率（%）
sub_cc	float	Y	申购替代金额(单位：人民币元)
red_cc	float	Y	赎回替代金额(单位：人民币元)
exchange	str	Y	交易所代码HK港交所 SH上交所 SZ深交所 OTH其他
### 代码示例
    # 获取接口实例
    pro = ts.pro_api()

    # 拉取159051.SZ易方达中证全指医疗器械ETF在2026年6月25日的持仓组合数据
    df = pro.etf_sz_cons(ts_code='159051.SZ', trade_date='20260625')
    print(df)
### 数据结果
trade_date    ts_code   con_code con_name   qty sub_flag    cpr   rdr       sub_cc       red_cc exchange
0   20260625  159051.SZ  159900.SZ     申赎现金     0       必须   0.00  0.00  512407.5000  141173.9000       SZ
1   20260625  159051.SZ  000710.SZ     贝瑞基因   400       允许  34.00  0.00       0.0000       0.0000       SZ
2   20260625  159051.SZ  002022.SZ     科华生物   800       允许  34.00  0.00       0.0000       0.0000       SZ



## ETF实时参考

- 接口：rt_etf_sz_iopv
- 描述：ETF实时净值和申购赎回数据参考，目前只提供深市
- 限量：单次最大5000条，完全覆盖当前总量
- 权限：本接口为单独开权限的接口，跟积分多个无关。正式权限请参阅 权限说明

### 输入参数
名称	类型	必选	描述
ts_code	str	N	ETF代码（默认为空，即一次全市场。支持单个和多个ETF过滤提取）
### 输出参数
名称	类型	默认显示	描述
trade_time	datetime	Y	交易时间
ts_code	str	Y	ETF代码
vol	float	Y	成交量（份）
num	int	Y	成交笔数
amount	float	Y	成交金额（元）
price	float	Y	最新价（元）
iopv	float	Y	最近参考净值
pre_iopv	float	Y	前一日参考净值
buy_num	int	Y	申购笔数
buy_vol	float	Y	申购买量(份)
sell_num	int	Y	赎回笔数
sell_vol	float	Y	赎回买量（份）
### 代码示例
    # 导入sdk包
    import tushare as ts

    # 配置凭据，如果已全局配置了，可以忽略。
    ts.set_token('<--your-token-->')

    # 获取接口实例
    pro = ts.pro_api()

    # 示例： 获取单个ETF（159103.SZ）的最新参考
    df = pro.rt_etf_sz_iopv(ts_code="159103.SZ")
    print(df)

    # 示例： 获取两个ETF的最新参考（159103.SZ,159105.SZ）
    df = pro.rt_etf_sz_iopv(ts_code="159103.SZ,159105.SZ")
    print(df)

    # 示例：获取深市ETF全部实时参考指标
    df = pro.rt_etf_sz_iopv()

    #示例：获取深市ETF指定指标的实时参考
    df = pro.rt_etf_sz_iopv(fields='trade_time,ts_code,iopv,buy_num,buy_vol,sell_num,sell_vol')
    print(df)
### 数据结果
trade_time    ts_code    iopv  buy_num   buy_vol  sell_num  sell_vol
0    2026-03-20 10:27:27  161039.SZ  0.0000        0    0.0000         0    0.0000
1    2026-03-20 10:28:45  159003.SZ  0.0000        7    1.1101        18    3.3692
2    2026-03-20 10:28:48  159005.SZ  0.0000       26    5.3240         4    0.5903
3    2026-03-20 10:29:03  159102.SZ  0.7776        0    0.0000         0    0.0000


### 指数公告

- 接口：idx_anns
- 描述：获取指数公司披露的相关公告信息，包括中证指数、国证指数、恒生指数和华证指数的及时与历史公告信息，跟踪指数最新信息和发展方向。
- 限量：单次最大返回1000条数据，可根据日期循环提取
- 积分：需要6000积分可以调取，具体请参阅积分获取办法

### 输入参数
名称	类型	必选	描述
ann_date	str	N	公告日期（YYYYMMDD格式，下同）
start_date	str	N	公告开始日期
end_date	str	N	公告结束日期
src	str	N	信息来源（中证指数、国证指数、恒生指数、华证指数）
### 输出参数
名称	类型	默认显示	描述
ann_date	str	Y	公告日期
title	str	Y	标题
url	str	Y	链接
source	str	Y	来源
type	str	Y	类型(指数发布、指数修订、指数更名、其他）
### 代码示例
    # 拉取接口(idx_anns)数据
    # 示例：获取2026年4月16日指数公司发布的指数公告
    df = pro.idx_anns(ann_date='20260416')

    #示例：获取中证指数公司发布的指数公告
    df = pro.idx_anns(src='中证指数')

    #示例：获取国证指数公司2026年1月以来发布的指数公告，并指定输出字段
    df = pro.idx_anns(src='国证指数', start_date='20260101', fields='ann_date,title,type')
### 数据结果
ann_date                           title                                                url source   type
0  20260420                 关于发布华证HALO指数的公告  https://www.chindices.com/news_detail.html?id=777   华证指数
1  20260417              恒生中国高股息率指数年度指数检讨结果  https://www.hsi.com.hk/static/uploads/contents...   恒生指数     其他
2  20260416                  关于调整三板指数样本股的公告  https://www.csindex.com.cn/#/about/newsDetail?...   中证指数   指数调样
