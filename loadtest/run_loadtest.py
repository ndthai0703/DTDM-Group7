"""Chỉ chạy khi xác nhận URL, chi phí và throttling."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--host',required=True,help='https://.../stage nếu API dùng stage');p.add_argument('--confirm-aws',action='store_true',help='Xác nhận nhóm đồng ý kiểm thử tải AWS');p.add_argument('--seconds',type=int,default=120);a=p.parse_args()
if not a.confirm_aws:sys.exit('Cần thêm --confirm-aws sau khi đồng ý chạy tải thật.')
for n,rate in [(10,2),(50,5),(100,10)]:
 print('Starting',n,'users');sys.stdout.flush()
 subprocess.run([sys.executable,'-m','locust','-f',str(Path(__file__).with_name('locustfile.py')),'--headless','--host',a.host,'--users',str(n),'--spawn-rate',str(rate),'--run-time',f'{a.seconds}s','--csv',str(Path(__file__).parent/'results'/f'aws_{n}')],check=True)
