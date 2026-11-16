"""Download one pinned IBM public sample; no credentials or user data transmitted."""
from pathlib import Path
import hashlib
import urllib.request
URL='https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/d5371f5d83a446ad5673cbcca3b814b926491f8a/data/Telco-Customer-Churn.csv'
SHA256='16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91'
if __name__=='__main__':
    raw=urllib.request.urlopen(URL,timeout=60).read()
    if hashlib.sha256(raw).hexdigest()!=SHA256:raise ValueError('Dataset checksum mismatch; inspect source before use.')
    p=Path('data/Telco-Customer-Churn.csv');p.parent.mkdir(exist_ok=True);p.write_bytes(raw)
    print(f'Verified {len(raw):,} bytes: {p}')
