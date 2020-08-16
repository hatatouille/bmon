# bmon

https://sites.google.com/a/chromium.org/chromedriver/home
ここから最新のchromedriverを落とす

python3.6以上推奨
`$ pip install selenium`

`$ mv ~/Downloads/chromedriver_mac64.zip`

`$ unzip chromedriver_mac64.zip`

`$ ll chromedriver
-rwxr-xr-x@ 1 <username>  staff    15M  5 28 09:56 chromedriver`


### 時間的に直近の予約をとにかくしたい場合
`python3 bmon.py`

### 指定したURLの予約をしたい場合（満員の場合予約できるまでループ）
`python3 bmon.py 'https://www.b-monster.jp/reserve/punchbag?lesson_id=120664&studio_code=0003'`
