import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from aiohttp import web
from bench.client import measure
from bench.hardware import npu_memory_mb


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_fake_stream_and_metrics(self):
        async def tokenize(req):
            return web.json_response({'tokens':list(range(5500))})
        async def health(req):
            return web.Response(text='ok')
        async def metrics(req):
            return web.Response(text='vllm:num_requests_running 3\nvllm:num_requests_waiting 1\n')
        async def completion(req):
            body=await req.json()
            n=body['max_tokens']
            assert n==body['min_tokens']
            assert body['ignore_eos']
            assert body['return_token_ids']
            response=web.StreamResponse(status=200,headers={'Content-Type':'text/event-stream'})
            await response.prepare(req)
            import json
            for chunk in [list(range(i,min(i+3,n))) for i in range(0,n,3)]:
                await response.write(('data: '+json.dumps({'choices':[{'index':0,'token_ids':chunk}]})+'\n\n').encode())
                await asyncio.sleep(.001)
            await response.write(('data: '+json.dumps({'choices':[{'index':0,'token_ids':[], 'finish_reason':'length'}]})+'\n\n').encode())
            await response.write(b'data: [DONE]\n\n')
            return response
        app=web.Application()
        app.router.add_post('/tokenize',tokenize)
        app.router.add_post('/v1/completions',completion)
        app.router.add_get('/metrics',metrics)
        app.router.add_get('/health',health)
        runner=web.AppRunner(app)
        await runner.setup()
        site=web.TCPSite(runner,'127.0.0.1',0)
        await site.start()
        url=f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}'
        try:
            with TemporaryDirectory() as dirname:
                out=Path(dirname)
                result=await measure(url,'Qwen/Test',out,prompt_tokens=32,output_tokens=32,
                         concurrency=2,duration_s=.3,drain_s=.2,request_timeout_s=3,
                         warmup_requests=1,warmup_output_tokens=8,metrics_interval_s=.05,
                         should_stop=lambda:False)
                self.assertGreater(result['completed_requests'],0)
                self.assertGreater(result['delivered_tokens_per_s'],0)
                self.assertIn('token_id',(out/'token_events.csv').read_text())
                self.assertIn('num_requests_waiting',(out/'metrics.csv').read_text())
                self.assertIn('measurement_start',(out/'phases.csv').read_text())
        finally:
            await runner.cleanup()

    def test_npu_smi_parser(self):
        self.assertEqual(npu_memory_mb('Memory-Usage(MB) | 1024 / 65536'),(1024,65536))
        # Ascend 26.x overview table reports absolute HBM used/total on the chip row.
        table = ('| 0     910B3               | OK            | 100.0                35                      0    / 0                |\n'
                 '| 0                         | 0000:C1:00.0  | 0                    0    / 0                3447 / 65536            |')
        self.assertEqual(npu_memory_mb(table), (3447, 65536))
        usages = ('HBM Capacity(MB)               : 65536\n'
                  'HBM Usage Rate(%)              : 5\n')
        self.assertEqual(npu_memory_mb(usages), (3277, 65536))


if __name__=='__main__':
    unittest.main()
