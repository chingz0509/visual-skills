"""Behavior tests for preservation, replay, formal copy, and the bounded repair workflow."""
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=load('collage',ROOT/'skills/visual-skills/scripts/collage.py')
r=load('replay',ROOT/'skills/visual-skills/scripts/replay.py')

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.input=self.root/'input.png';im=Image.new('RGB',(360,240),'#376a61');d=ImageDraw.Draw(im)
  for x,color in [(0,'red'),(330,'blue')]:d.rectangle((x,0,x+29,239),fill=color)
  im.save(self.input)
  self.plan={'category':'group','title':['一起'],'subtitle':'保留每个人','palette':'archive','layout':'editorial','photo_mode':'whole','tone':'color','seed':4,'design_reason':'test','formal_copy':['一起','保留每个人']}
  self.planfile=self.root/'plan.json';c.write_json(self.planfile,self.plan)
  self.run=self.root/'run'
  self.env=patch.dict(os.environ,{'VISUAL_SKILLS_VISION':''});self.env.start()
 def tearDown(self):self.env.stop();self.temp.cleanup()
 def render(self):
  with contextlib.redirect_stdout(io.StringIO()):c.render(argparse.Namespace(input=str(self.input),plan=str(self.planfile),output=str(self.run)))
 def review(self,passed):
  data={key:passed for key in c.REVIEW_KEYS};data.update(notes='Synthetic workflow test, not a visual verdict on benchmark photos.',reviewer='unit test')
  f=self.root/'review.json';c.write_json(f,data)
  with contextlib.redirect_stdout(io.StringIO()):c.review(argparse.Namespace(run=str(self.run),review=str(f)))
 def repair(self):
  with contextlib.redirect_stdout(io.StringIO()):c.repair(argparse.Namespace(run=str(self.run),plan=str(self.planfile)))
 def test_original_pixels_and_both_edges_survive_preparation(self):
  dest=self.root/'prep';dest.mkdir();photo,_,same=c.prepare_photo(self.input,dest,self.plan)
  self.assertTrue(same);self.assertEqual(photo.convert('RGB').tobytes(),Image.open(self.input).tobytes())
  self.assertEqual(photo.getpixel((0,0)),(255,0,0,255));self.assertEqual(photo.getpixel((359,239)),(0,0,255,255))
 def test_replay_is_identical_and_tampering_is_rejected(self):
  self.render();bundle=self.run/'attempt-0'
  with contextlib.redirect_stdout(io.StringIO()):self.assertTrue(r.replay(bundle,self.root/'replay.png'))
  record=c.read_json(bundle/'record.json');layer=bundle/record['layers'][0]['file'];layer.write_bytes(b'tampered')
  with self.assertRaisesRegex(ValueError,'hash mismatch'):r.replay(bundle,self.root/'bad.png')
 def test_three_attempt_limit_and_forced_whole_photo_fallback(self):
  self.render();self.review(False);self.repair();self.review(False);self.repair()
  plan=c.read_json(self.run/'attempt-2/plan.json');self.assertEqual(plan['layout'],'simple');self.assertEqual(plan['photo_mode'],'whole')
  self.review(False);state=c.read_json(self.run/'state.json');self.assertEqual(state['status'],'failed');self.assertEqual(len(state['attempts']),3)
  with self.assertRaises(ValueError):self.repair()
  self.assertFalse((self.run/'final.png').exists())
 def test_simple_pass_is_not_reported_as_complex(self):
  self.render();self.review(False);self.repair();self.review(False);self.repair();self.review(True)
  self.assertEqual(c.read_json(self.run/'state.json')['status'],'simple_pass')
 def test_source_tampering_and_missing_formal_copy_stop_render(self):
  with self.assertRaisesRegex(ValueError,'Formal copy'):c.validate_plan(dict(self.plan,title=['不同']))
  self.render();self.review(False);(self.run/'original.png').write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'Original photo changed'):self.repair()
 def test_groups_cannot_be_segmented_and_old_runs_are_not_overwritten(self):
  with self.assertRaisesRegex(ValueError,'must stay whole'):c.validate_plan(dict(self.plan,photo_mode='cutout'))
  self.render()
  with self.assertRaisesRegex(ValueError,'new or empty'):self.render()

 def creative_inputs(self):
  self.plan.update(subject_policy='creative',layout='freeform',allowed_changes=['印刷质感和背景'],keep_features=['所有人及相对关系'])
  c.write_json(self.planfile,self.plan)
  artwork=self.root/'art.png';Image.new('RGB',(1200,1600),'#d4be88').save(artwork)
  provenance=self.root/'generation.json';c.write_json(provenance,{'model':'synthetic fixture, not a real generation',
   'permission':'user_selected_creative','prompt':'Synthetic workflow test only','parameters':{'size':'1200x1600'}})
  return artwork,provenance
 def test_creative_route_discloses_redraw_and_requires_subject_review(self):
  artwork,meta=self.creative_inputs()
  with contextlib.redirect_stdout(io.StringIO()):c.render(argparse.Namespace(input=str(self.input),plan=str(self.planfile),output=str(self.run),artwork=str(artwork),provenance=str(meta)))
  bundle=self.run/'attempt-0';record=c.read_json(bundle/'record.json');checks=c.read_json(bundle/'checks.json')
  self.assertFalse(record['editable_internal_layers'])
  self.assertNotIn('source_not_regenerated',{x['name'] for x in checks['checks']})
  self.assertEqual((bundle/'source-original.png').read_bytes(),self.input.read_bytes())
  with self.assertRaisesRegex(ValueError,'Creative review'):self.review(True)
  data={key:True for key in c.REVIEW_KEYS+['identity_recognizable','no_subject_artifacts','changes_within_permission']}
  data.update(notes='Synthetic workflow fixture, no aesthetic verdict.',reviewer='unit test')
  f=self.root/'complete-review.json';c.write_json(f,data)
  with contextlib.redirect_stdout(io.StringIO()):c.review(argparse.Namespace(run=str(self.run),review=str(f)))
  self.assertEqual(c.read_json(self.run/'state.json')['status'],'complex_pass')
  with contextlib.redirect_stdout(io.StringIO()):self.assertTrue(r.replay(bundle,self.root/'creative-replay.png'))
 def test_creative_art_cannot_enter_preserve_mode_or_stretch_to_fit(self):
  artwork,meta=self.creative_inputs()
  with self.assertRaisesRegex(ValueError,'cannot import generated'):c.make_bundle(self.input,dict(self.plan,subject_policy='preserve',layout='editorial'),self.root/'blocked',artwork,meta)
  Image.new('RGB',(1024,1024),'white').save(artwork)
  with self.assertRaisesRegex(ValueError,'never stretch'):c.make_bundle(self.input,self.plan,self.root/'square',artwork,meta)
  self.assertFalse((self.root/'square/final.png').exists())
 def test_creative_final_fallback_returns_to_original_pixels(self):
  artwork,meta=self.creative_inputs()
  with contextlib.redirect_stdout(io.StringIO()):c.render(argparse.Namespace(input=str(self.input),plan=str(self.planfile),output=str(self.run),artwork=str(artwork),provenance=str(meta)))
  rejection={key:False for key in c.REVIEW_KEYS+['identity_recognizable','no_subject_artifacts','changes_within_permission']}
  rejection.update(notes='Reject synthetic fixture for testing fallback.',reviewer='unit test')
  f=self.root/'reject.json';c.write_json(f,rejection)
  for _ in range(2):
   with contextlib.redirect_stdout(io.StringIO()):
    c.review(argparse.Namespace(run=str(self.run),review=str(f)))
    c.repair(argparse.Namespace(run=str(self.run),plan=str(self.planfile),artwork=str(artwork),provenance=str(meta)))
  bundle=self.run/'attempt-2';plan=c.read_json(bundle/'plan.json')
  self.assertEqual((plan['layout'],plan['subject_policy']),('simple','preserve'))
  self.assertEqual(Image.open(bundle/'photo-prepared.png').convert('RGB').tobytes(),Image.open(self.input).tobytes())
  self.assertFalse((bundle/'generated-artwork.png').exists())
  self.review(True);self.assertEqual(c.read_json(self.run/'state.json')['status'],'simple_pass')
 def test_new_layouts_keep_whole_photos_inside_canvas(self):
  for layout in ['cover','split','window']:
   with self.subTest(layout=layout):
    plan=dict(self.plan,layout=layout,palette='cobalt')
    bundle=self.root/layout;c.make_bundle(self.input,plan,bundle)
    self.assertTrue(c.read_json(bundle/'checks.json')['all_hard_checks_pass'])
    photo=c.read_json(bundle/'record.json')['photo_boxes'];self.assertEqual(len(photo),1)
    x,y,right,bottom=photo[0];self.assertTrue(0<=x<right<=1200 and 0<=y<bottom<=1600)

if __name__=='__main__':unittest.main()
