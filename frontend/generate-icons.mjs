import zlib from 'zlib';
import fs from 'fs';

// CRC32
const crcTable = new Uint32Array(256);
for (let i = 0; i < 256; i++) {
  let c = i;
  for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
  crcTable[i] = c;
}
function crc32(buf) {
  let crc = 0xFFFFFFFF;
  for (const b of buf) crc = crcTable[(crc ^ b) & 0xFF] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function u32(n) { return Buffer.from([(n>>>24)&0xFF,(n>>>16)&0xFF,(n>>>8)&0xFF,n&0xFF]); }
function pngChunk(type, data) {
  const t = Buffer.from(type);
  const crc = u32(crc32(Buffer.concat([t, data])));
  return Buffer.concat([u32(data.length), t, data, crc]);
}

function sign(p1x,p1y,p2x,p2y,p3x,p3y) {
  return (p1x-p3x)*(p2y-p3y) - (p2x-p3x)*(p1y-p3y);
}
function inTriangle(px,py,ax,ay,bx,by,cx,cy) {
  const d1=sign(px,py,ax,ay,bx,by), d2=sign(px,py,bx,by,cx,cy), d3=sign(px,py,cx,cy,ax,ay);
  return !((d1<0||d2<0||d3<0) && (d1>0||d2>0||d3>0));
}

function makePNG(size) {
  const p = size / 64;
  const px = new Uint8Array(size * size * 4);

  function set(x, y, r, g, b, a=255) {
    if (x<0||x>=size||y<0||y>=size) return;
    const i=(y*size+x)*4; px[i]=r; px[i+1]=g; px[i+2]=b; px[i+3]=a;
  }

  // Background #111111 with rounded corners (radius = 12/64 * size)
  const radius = Math.round(12 * p);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      // Corner check
      let inCorner = false;
      const corners = [[radius,radius],[size-radius-1,radius],[radius,size-radius-1],[size-radius-1,size-radius-1]];
      for (const [cx,cy] of corners) {
        const dx=x-cx, dy=y-cy;
        if (Math.abs(x-cx)<=radius && Math.abs(y-cy)<=radius) {
          if (dx*dx+dy*dy > radius*radius) { inCorner=true; break; }
        }
      }
      if (!inCorner) set(x, y, 0x11, 0x11, 0x11);
    }
  }

  // Scale SVG coords (viewBox 0 0 64 64) to canvas
  const s = (v) => Math.round(v * p);

  // Orange top triangle: 16,10 → 48,10 → 32,32
  const [t1ax,t1ay,t1bx,t1by,t1cx,t1cy] = [s(16),s(10),s(48),s(10),s(32),s(32)];
  // Orange bottom triangle: 16,54 → 48,54 → 32,32
  const [t2ax,t2ay,t2bx,t2by,t2cx,t2cy] = [s(16),s(54),s(48),s(54),s(32),s(32)];

  const yMin1=Math.min(t1ay,t1by,t1cy), yMax1=Math.max(t1ay,t1by,t1cy);
  const yMin2=Math.min(t2ay,t2by,t2cy), yMax2=Math.max(t2ay,t2by,t2cy);
  const xMin1=Math.min(t1ax,t1bx,t1cx), xMax1=Math.max(t1ax,t1bx,t1cx);
  const xMin2=Math.min(t2ax,t2bx,t2cx), xMax2=Math.max(t2ax,t2bx,t2cx);

  for (let y=yMin1; y<=yMax1; y++)
    for (let x=xMin1; x<=xMax1; x++)
      if (inTriangle(x,y,t1ax,t1ay,t1bx,t1by,t1cx,t1cy)) set(x,y,0xFF,0x6B,0x35);

  for (let y=yMin2; y<=yMax2; y++)
    for (let x=xMin2; x<=xMax2; x++)
      if (inTriangle(x,y,t2ax,t2ay,t2bx,t2by,t2cx,t2cy)) set(x,y,0xFF,0x6B,0x35);

  // White bars: x=14,y=8,w=36,h=5 and x=14,y=51,w=36,h=5
  for (let y=s(8); y<s(8)+s(5); y++) for (let x=s(14); x<s(14)+s(36); x++) set(x,y,0xFF,0xFF,0xFF);
  for (let y=s(51); y<s(51)+s(5); y++) for (let x=s(14); x<s(14)+s(36); x++) set(x,y,0xFF,0xFF,0xFF);

  // Yellow dot at 32,38 r=3
  const dr=s(3), dcx=s(32), dcy=s(38);
  for (let dy=-dr; dy<=dr; dy++)
    for (let dx=-dr; dx<=dr; dx++)
      if (dx*dx+dy*dy<=dr*dr) set(dcx+dx,dcy+dy,0xFF,0xCC,0x00);

  // Build PNG
  const ihdr = pngChunk('IHDR', Buffer.concat([u32(size),u32(size),Buffer.from([8,6,0,0,0])]));
  const rows = [];
  for (let y=0; y<size; y++) {
    rows.push(Buffer.from([0]));
    rows.push(Buffer.from(px.slice(y*size*4, (y+1)*size*4)));
  }
  const idat = pngChunk('IDAT', zlib.deflateSync(Buffer.concat(rows), {level:6}));
  const iend = pngChunk('IEND', Buffer.alloc(0));
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]), ihdr, idat, iend]);
}

for (const size of [192, 512]) {
  fs.writeFileSync(`static/icon-${size}.png`, makePNG(size));
  console.log(`✓ static/icon-${size}.png`);
}
