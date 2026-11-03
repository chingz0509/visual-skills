"""The first Agent-authored plans, based on visual inspection of the frozen inputs."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
settings=[
('person-easy',['把今天','贴成喜欢的样子'],'做自己的封面人物','lilac','cutout','cutout','mono','A LITTLE / DAYDREAM','干净背景的人像适合保留原面容、黑白剪贴；紫色与橙色纸层呼应编辑式拼贴。'),
('person-hard',['笑容','自带光芒'],'把平常的瞬间认真收藏','lagoon','cutout','cutout','color','GOOD / LITTLE DAYS','散发与花纹衣物是抠图难点；先检查原像素剪贴，底部保留衣物和姿态。'),
('group-easy',['一起','就在这一刻'],'每个人都在画面里','archive','editorial','whole','mono','BETTER / TOGETHER','七人原合照作为整体保留，宽幅照片配纸层与大字；原本出框边缘不进一步裁切。'),
('group-hard',['有你们','才叫日常'],'把相聚的片刻留下来','lilac','editorial','whole','color','IN GOOD / COMPANY','保留前景背影、桌面和人物关系，整图嵌入；橙紫纸层形成纵向海报层次。'),
('product-easy',['把光','留在手里'],'每一帧都值得珍藏','archive','cutout','cutout','color','KEEP / LOOKING','相机和镜头作为完整产品保留，白背景适合抠图，橙色纸块与黄纸条提供节奏。'),
('product-hard',['慢一点','感受时间'],'让时间有自己的节奏','lilac','cutout','cutout','color','TAKE / YOUR TIME','复杂背景中的反光表链与细字是硬例，需重点核对表链与盘面，失败后整图修复。'),
('pet-easy',['今天','负责可爱'],'把小小的快乐贴起来','lagoon','cutout','cutout','color','LITTLE / HAPPY THINGS','猫咪脸与耳朵完整保留，细毛和胡须需要单独核对；蓝绿底与黄纸条。'),
('pet-hard',['快乐','成双出现'],'一起晒太阳吧','archive','cutout','cutout','color','DOUBLE / THE JOY','两只幼犬都保留，草地花朵可能干扰分割；检查脚部与两只狗之间的关系。'),
('landscape-easy',['把远方','寄给自己'],'山湖之间，留一点空白','archive','landscape','whole','color','A PLACE / TO REMEMBER','横向湖山完整放入纵版；用纸张、网格和标题构成层次，不重组山湖。'),
('landscape-hard',['走进','安静的深处'],'让脚步慢下来','forest','landscape','whole','color','INTO / THE QUIET','深色竖幅密林完整保留，以暖纸底和黄色点缀提供对比，避免加重黑位。')]
for i,(key,title,subtitle,palette,layout,mode,tone,motif,reason) in enumerate(settings):
 plan={'schema_version':1,'category':key.split('-')[0],'title':title,'subtitle':subtitle,'palette':palette,'layout':layout,'photo_mode':mode,'tone':tone,'seed':103+i,'design_reason':reason,'motif':motif,'eyebrow':'PAPER / MOMENTS','edition':'A MOMENT, KEPT','formal_copy':[]}
 (root/'benchmark/plans'/(key+'.json')).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
