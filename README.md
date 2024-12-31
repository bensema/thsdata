# thsdata


# Installation
```bash
pip install --upgrade thsdata
```

# Usage
```python
import sys
import pandas as pd
from thsdata import ZhuThsQuote
from thsdata.constants import *


quote = ZhuThsQuote()

login_reply = quote.connect()
if login_reply.err_code != 0:
    print(f"登录错误:{login_reply.err_code}, 信息:{login_reply.err_message}")
    sys.exit(0)
else:
    print("Connected successfully")


reply = quote.security_bars("USHA600519",20031201,20241231,FuquanNo, KlineDay)

if reply.err_code != 0:
    print(f"查询错误:{reply.err_code}, 信息:{reply.err_message}")
    sys.exit(0)


df = pd.DataFrame(reply.data)

print(df)

quote.disconnect()
```
result:
```
Connected successfully
           time    close   volume      turnover     open     high      low
0    2003-12-01    23.01   876473  2.019143e+07    23.30    23.30    22.85
1    2003-12-02    23.18   694387  1.607632e+07    23.19    23.26    23.00
2    2003-12-03    23.52  1357229  3.179035e+07    23.25    23.80    23.18
3    2003-12-04    23.42   816032  1.915335e+07    23.56    23.68    23.31
4    2003-12-05    23.87  2033561  4.801934e+07    23.40    23.90    23.31
...         ...      ...      ...           ...      ...      ...      ...
5049 2024-12-25  1530.00  1712339  2.621062e+09  1538.80  1538.80  1526.10
5050 2024-12-26  1527.79  1828651  2.798840e+09  1534.00  1538.78  1523.00
5051 2024-12-27  1528.97  2075932  3.170191e+09  1528.90  1536.00  1519.50
5052 2024-12-30  1525.00  2512982  3.849543e+09  1533.97  1543.96  1525.00
5053 2024-12-31  1524.00  3935445  6.033540e+09  1525.40  1545.00  1522.01

[5054 rows x 7 columns]
```