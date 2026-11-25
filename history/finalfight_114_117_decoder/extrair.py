import numpy as np, csv, sys, hashlib, json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw
z=ZipFile(sys.argv[1]); out=Path(sys.argv[2]);out.mkdir(exist_ok=True,parents=True)
assert z.testzip() is None
names=['ff-5m.7a','ff-7m.9a','ff-1m.3a','ff-3m.5a']
a=np.stack([np.frombuffer(z.read(n),np.uint8).reshape(-1,2) for n in names]).transpose(1,0,2).reshape(-1,4)
# MAME plane offsets 24,16,8,0; first plane is most significant.
p=(np.unpackbits(a,axis=1).reshape(-1,4,8)*(1<<np.arange(4))[None,:,None]).sum(axis=1).astype(np.uint8)
# Verify independent scalar decoding for selected groups.
for i in [0,1,100,12345,len(a)-1]:
 assert list(p[i])==[sum(((int(a[i,k])>>(7-x))&1)<<k for k in range(4)) for x in range(8)]
raw=p.reshape(-1,16,16)
def sheet(tiles,start,size,name):
 for j in range(0,len(tiles),256):
  cell=size+12; im=Image.new('L',(16*cell,16*cell),32);d=ImageDraw.Draw(im)
  for k,t in enumerate(tiles[j:j+256]):
   x=k%16*cell;y=k//16*cell;im.paste(Image.fromarray(t*17),(x,y));d.text((x,y+size),f'{start+j+k:04X}',fill=255)
  im.save(out/f'{name}_{start+j:04X}.png')
# PAL normalized addresses use 8x8 half-row pairs (64 bytes per unit); 16x16 code shifted by 1, 32x32 by 3.
bg=raw[0x3000:0x4000]; bg3=p.reshape(-1,32,32)[0x980:0xc00]
sheet(bg,0x3000,16,'scroll2');sheet(bg3,0x980,32,'scroll3')
# SNES conversion: bijection CPS pen 15 -> 0, other pens +1. No palette reduction.
tiles=bg.reshape(-1,2,8,2,8).transpose(0,1,3,2,4).reshape(-1,8,8); t=(tiles+1)%16
planes=np.packbits(((t[:,None,:,:]>>np.arange(4)[None,:,None,None])&1).astype(np.uint8),axis=3).squeeze(3)
enc=planes.reshape(-1,2,2,8).transpose(0,1,3,2).reshape(-1,32)
dec=np.unpackbits(enc.reshape(-1,2,8,2).transpose(0,1,3,2).reshape(-1,4,8,1),axis=3)
assert np.array_equal((dec*(1<<np.arange(4))[None,:,None,None]).sum(axis=1),t)
unique,idx=np.unique(enc,axis=0,return_inverse=True)
with open(out/'scroll2_indice.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['cps_code_hex','snes_tl','snes_tr','snes_bl','snes_br']);w.writerows([[f'{0x3000+i:04X}',*map(int,row)] for i,row in enumerate(idx.reshape(-1,4))])
# no bulk ROM-derived binaries distributed: regenerate locally from owned ROM
print(json.dumps({'scroll2_16x16':len(bg),'scroll3_32x32':len(bg3),'snes_8x8':len(t),'unique_8x8':len(unique),'unique_bytes':unique.nbytes,'roundtrip':True}))
