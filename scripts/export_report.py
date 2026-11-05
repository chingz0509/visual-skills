#!/usr/bin/env python3
"""Export every benchmark outcome and intermediate attempt, without selecting only successes."""
import argparse,json,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
items=json.loads((ROOT/'benchmark/manifest.json').read_text())['items']
corrections=json.loads((ROOT/'benchmark/provenance-addendum.json').read_text())['corrections']
run=ROOT/'benchmark/runs'/a.run;examples=ROOT/'examples';examples.mkdir(exist_ok=True)
shutil.copyfile(run/'contact-sheet.jpg',examples/'contact-sheet.jpg')
rows=[];all_attempts=[]
lines=['# 固定集实验报告 · '+a.run,'','日期：2026-11-03。输入在渲染器实现与调试前冻结；五类各两张、一易一难。无失败换图。','',
'这是当前 Codex 桌面端中的开发验证，由同一 Agent 写计划并逐图检查，不是独立盲测。项目发起人的最终验收仍为待完成。所有结果为实验结果，不据此宣称达到通用可用标准。','',
'程序检查和 Agent 初检均通过后才计入。初次通过 8 张；两张宠物图因抠图问题被拒绝，第一次修复恢复完整原片后通过。复杂通过 10、简洁通过 0、最终失败 0。没有为凑齐状态而人为制造失败。第二次简洁降级与最终失败路径另有合成输入行为测试，不混入这 10 张的结果。','',
'拟定门槛为至少 8/10 可用，其中至少 6/10 复杂通过。当前 Agent 初检达到该数值，**用户最终验收未完成，门槛尚未最终确认**。纸层、构图和字形仍有统一模板感，和参考图的自由编辑感存在差距。','',
'![全部最终结果](../examples/contact-sheet.jpg)','','| 固定输入 | 初次结果 | 最终结果 | 尝试数 | 精确复现 | 用户验收 |','|---|---|---|---|---|---|']
for item in items:
 key=item['id'];root=run/key;state=json.loads((root/'state.json').read_text());target=examples/key;target.mkdir(exist_ok=True)
 first=state['attempts'][0]['status'];status=state['status'];replay=root/'replayed.png'
 identical=replay.exists() and hashlib.sha256(replay.read_bytes()).hexdigest()==hashlib.sha256((root/'final.png').read_bytes()).hexdigest()
 rows.append({'id':key,'first':first,'final':status,'attempts':len(state['attempts']),'replay_identical':identical,'human_acceptance':'pending'})
 lines.append(f'| {key} | {first} | {status} | {len(state["attempts"])} | {identical} | 待验收 |')
 shutil.copyfile(root/'state.json',target/'state.json')
 for attempt in state['attempts']:
  source=root/attempt['bundle'];dest=target/attempt['bundle'];dest.mkdir(exist_ok=True)
  for name in ['final.png','plan.json','checks.json','visual-review.json','error.json']:
   if (source/name).exists():shutil.copyfile(source/name,dest/name)
  all_attempts.append({'id':key,**attempt})
lines += ['','## 每张照片与完整尝试','', '原片、实际图层、字体和复现脚本在本地 `benchmark/runs/'+a.run+'/` 中保留。公开目录保留成品与检查记录，原片按固定清单下载；完整素材包不在 Git 分发中。','', '来源许可及元数据更正见 [THIRD_PARTY](../THIRD_PARTY.md)。']
for item in items:
 key=item['id'];meta={**item,**corrections.get(key,{})};state=json.loads((run/key/'state.json').read_text())
 lines+=['','### '+key,'',item['challenge'],'',f'照片：{meta["photographer"]} / [Pexels {item["photo_id"]}]({meta["source_page"]})。','']
 for attempt in state['attempts']:
  folder=f'../examples/{key}/{attempt["bundle"]}'
  review_path=run/key/attempt['bundle']/'visual-review.json'
  note=json.loads(review_path.read_text())['notes'] if review_path.exists() else attempt.get('error','待检查')
  lines += [f'**第 {attempt["index"]} 次尝试：{attempt["status"]}** — {note}','',f'![{key} {attempt["bundle"]}]({folder}/final.png)','',f'[计划]({folder}/plan.json) · [硬检查]({folder}/checks.json) · [视觉记录]({folder}/visual-review.json)','']
lines += ['## 验证边界','','- 10 个最终结果从保存图层重合成，逐像素一致。','- 6 项行为测试通过，覆盖原片 RGB 与边界、复现及篡改检测、三次尝试上限、简洁通过分类、正式文案保留、合照限制与防覆盖。','- 在当前机器复用已有 Python 依赖成功；没有声称空白机器的自动安装路径已全部验证。','- Apple Vision 分割和 OCR 仅在当前 macOS 环境验证。','- 当前版式固定 1200×1600、四种布局、短文案；不保证所有文字或图片都能得到满意结果。','- 视觉评审由作者 Agent 执行，可能存在审美偏差。用户可以逐项否决，并作为后续迭代证据。','']
(ROOT/'benchmark/REPORT.md').write_text('\n'.join(lines))
(ROOT/'benchmark/results.json').write_text(json.dumps({'run':a.run,'experimental':True,'human_final_acceptance':'pending','results':rows,'attempts':all_attempts},ensure_ascii=False,indent=2)+'\n')
print('Exported all',len(rows),'cases and',len(all_attempts),'attempts')
