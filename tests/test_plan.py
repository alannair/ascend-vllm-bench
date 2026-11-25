import unittest
from bench.plan import config, make_plan, tp_for
from bench.runtime import docker_command
from pathlib import Path


class PlanTests(unittest.TestCase):
    def test_47_models_and_940_runs(self):
        cfg=config()
        self.assertEqual(len(cfg['models']),47)
        plan=make_plan(cfg)
        self.assertEqual(len(plan['runs']),940)
        self.assertEqual(len(set((r['model'],r['config_id']) for r in plan['runs'])),940)
        self.assertEqual(sum(r['study']=='decode' for r in plan['runs']),47*8)
        self.assertEqual(sum(r['study']=='prefill' for r in plan['runs']),47*12)
        self.assertEqual(set(r['prompt_tokens'] for r in plan['runs'] if r['study']=='decode'),{32})
        self.assertEqual(set(r['output_tokens'] for r in plan['runs'] if r['study']=='decode'),{512})
        self.assertEqual(set(r['prompt_tokens'] for r in plan['runs'] if r['study']=='prefill'),{256,1024,4096})
        self.assertEqual(set(r['output_tokens'] for r in plan['runs'] if r['study']=='prefill'),{32})

    def test_exact_matching(self):
        cfg=config()
        plan=make_plan(cfg,['Qwen/Qwen3-4B'])
        self.assertEqual(len(plan['runs']),20)
        self.assertEqual(plan['models'],['Qwen/Qwen3-4B'])
        self.assertEqual(tp_for('Qwen/Qwen3-32B',cfg),2)
        self.assertEqual(tp_for('Qwen/Qwen3-30B-A3B',cfg),2)
        self.assertEqual(tp_for('Qwen/QwQ-32B-AWQ',cfg),1)

    def test_device_isolation(self):
        cfg=config()
        entry=make_plan(cfg,['Qwen/Qwen3-32B'],max_runs=1)['runs'][0]
        cmd=docker_command(cfg,entry,Path('/data2/alan/logs'),Path('/data2/alan/data'),'test')
        arg=' '.join(cmd)
        self.assertIn('/dev/davinci0',arg)
        self.assertIn('/dev/davinci1',arg)
        self.assertNotIn('/dev/davinci4',arg)
        self.assertIn('--privileged',arg)
        self.assertIn('--tensor-parallel-size 2',arg)
        self.assertIn('HF_TOKEN',arg)
        self.assertIn('HUGGING_FACE_HUB_TOKEN',arg)
        self.assertNotIn('secret',arg)
        # Quantized model IDs must not force bf16 (breaks AWQ/FP8 load paths).
        awq=make_plan(cfg,['AMead10/Llama-3.2-1B-Instruct-AWQ'],max_runs=1)['runs'][0]
        awq_cmd=' '.join(docker_command(cfg,awq,Path('/data2/alan/logs'),Path('/data2/alan/data'),'awq'))
        self.assertIn('--dtype auto',awq_cmd)
        self.assertNotIn('--dtype bfloat16',awq_cmd)
        with self.assertRaises(ValueError):
            make_plan({**cfg,'devices':[0,1,2,4]})


if __name__=='__main__':
    unittest.main()
