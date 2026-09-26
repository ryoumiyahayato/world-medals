import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const root = process.cwd();
const catalogue = JSON.parse(await fs.readFile(path.join(root,'data','catalogue.json'),'utf8'));
const manifest = JSON.parse(await fs.readFile(path.join(root,'image_manifest.json'),'utf8'));
const images = new Map(manifest.map(x=>[x.key,x]));
const outDir = path.join(root,'outputs','ottoman-20260925');
await fs.mkdir(outDir,{recursive:true});

const wb=Workbook.create();
const sh=wb.worksheets.add('奥斯曼帝国');
sh.showGridLines=false;
sh.freezePanes.freezeRows(1);
sh.getRange('A1:C1').values=[['名称＋日期','等级／版别','完整图片']];
sh.getRange('A1:C1').format={fill:'#253638',font:{name:'Arial',size:12,bold:true,color:'#FFFFFF'},verticalAlignment:'center'};
sh.getRange('A1:C1').format.rowHeightPx=38;
sh.getRange('A:A').format.columnWidthPx=280;
sh.getRange('B:B').format.columnWidthPx=230;
sh.getRange('C:C').format.columnWidthPx=640;

for(let i=0;i<catalogue.records.length;i++){
  const r=catalogue.records[i], excelRow=i+2, row0=i+1;
  const name=[r.name,r.original,r.date].join('\n');
  let variant=r.variant;
  if(r.views.length===2) variant+='\n左：正面　右：背面';
  sh.getRange(`A${excelRow}:B${excelRow}`).values=[[name,variant]];
  const range=sh.getRange(`A${excelRow}:C${excelRow}`);
  range.format.rowHeightPx=300;
  range.format.font={name:'Arial',size:12,color:'#233336'};
  range.format.verticalAlignment='center';
  range.format.wrapText=true;
  range.format.fill=i%2===0?'#FFFFFF':'#F6F8F7';
  range.format.borders={bottom:{style:'thin',color:'#D8DEDC'}};
  const boxWidth=r.views.length===2?295:610;
  const boxHeight=270;
  for(let j=0;j<r.views.length;j++){
    const im=images.get(r.views[j].key);
    if(!im) throw new Error('Missing source image '+r.views[j].key);
    const file=path.join(root,'assets','embeds',path.parse(im.path).name+'.jpg');
    const bytes=await fs.readFile(file);
    const ratio=Math.min(boxWidth/im.width,boxHeight/im.height);
    const w=Math.round(im.width*ratio),h=Math.round(im.height*ratio);
    const boxLeft=r.views.length===2?10+j*315:10;
    const x=boxLeft+Math.round((boxWidth-w)/2),y=15+Math.round((boxHeight-h)/2);
    sh.images.add({dataUrl:'data:image/jpeg;base64,'+bytes.toString('base64'),
      anchor:{from:{row:row0,col:2,rowOffsetPx:y,colOffsetPx:x},extent:{widthPx:w,heightPx:h}}});
  }
}
wb.recalculate();
const check=await wb.inspect({kind:'region',sheetId:sh.sheetId,range:`A1:C${catalogue.records.length+1}`,maxChars:3000});
console.log(check.ndjson);
const preview=await wb.render({sheetName:'奥斯曼帝国',range:'A1:C4',scale:1,format:'png'});
await fs.writeFile(path.join(outDir,'preview.png'),new Uint8Array(await preview.arrayBuffer()));
const xlsx=await SpreadsheetFile.exportXlsx(wb);
const outfile=path.join(outDir,'ottoman_catalogue_2026-09-25.xlsx');
await xlsx.save(outfile);
const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(outfile));
const reopenedCheck=await reopened.inspect({kind:'region',sheetId:'奥斯曼帝国',range:'A1:C4',maxChars:1500});
console.log('REOPENED',reopenedCheck.ndjson);
console.log('OUTPUT',outfile);
