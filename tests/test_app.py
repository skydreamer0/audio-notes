import asyncio
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

import httpx
from app import main as m


def wav():
    data = io.BytesIO()
    with wave.open(data, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(16000)
        f.writeframes(b'\0\0' * 16000)
    return data.getvalue()


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=m.app), base_url='http://localhost',
                                       headers={'x-audio-token': m.TOKEN})
    async def asyncTearDown(self):
        for j in list(m.JOBS.values()):
            await m.stop(j)
        m.JOBS.clear()
        await self.client.aclose()
    async def finish(self, id):
        j=m.JOBS[id]
        if j.task:
            await asyncio.wait_for(j.task, 10)
        return j
    async def submit(self, data, **kwargs):
        return await self.client.post('/api/jobs', content=data, **kwargs)
    async def test_ui_and_health(self):
        r=await self.client.get('/')
        self.assertEqual(r.status_code,200);self.assertIn('Audio Notes', r.text)
        self.assertIn(m.TOKEN,r.text)
        self.assertIn("frame-ancestors 'none'",r.headers['content-security-policy'])
        h=(await self.client.get('/api/health')).json()
        self.assertTrue(h['media_ready'])
    async def test_csrf_token(self):
        r=await self.client.get('/api/health',headers={'x-audio-token':'wrong'})
        self.assertEqual(r.status_code,403)
    async def test_origin_and_host(self):
        r=await self.client.post('/api/jobs',content=wav(),headers={'origin':'https://evil.test'})
        self.assertEqual(r.status_code,403)
        r=await self.client.get('/',headers={'host':'evil.test'})
        self.assertEqual(r.status_code,400)
    async def test_empty(self):
        r=await self.submit(b'');self.assertEqual(r.status_code,400);self.assertEqual(m.JOBS,{})
    async def test_size_limit(self):
        with patch.object(m,'LIMIT',8):
            r=await self.submit(b'123456789')
        self.assertEqual(r.status_code,413);self.assertEqual(m.JOBS,{})
    async def test_mime_and_extension_not_trusted(self):
        r=await self.submit(b'not audio',headers={'content-type':'audio/wav','x-filename':'../../fake.wav'})
        j=await self.finish(r.json()['id'])
        self.assertEqual(j.status,'failed');self.assertFalse(j.directory.exists())
        self.assertEqual(j.segments,[])
    async def test_real_ffmpeg_missing_engine(self):
        with patch.object(m,'ready',return_value=False):
            r=await self.submit(wav(),headers={'x-filename':'../../outside.wav'})
            j=await self.finish(r.json()['id'])
        self.assertEqual(j.status,'failed');self.assertIn('未就緒',j.error)
        self.assertEqual(j.segments,[]);self.assertFalse(j.directory.exists())
    async def test_pipeline_contract_with_explicit_stub(self):
        actual=m.command
        async def command(j,*args,**kw):
            if args[0]==m.sys.executable:
                Path(args[-1]).write_text(json.dumps([{'id':1,'start':0.1,'end':0.9,'text':'TEST STUB ONLY'}]))
                return b''
            return await actual(j,*args,**kw)
        with patch.object(m,'ready',return_value=True),patch.object(m,'command',side_effect=command):
            r=await self.submit(wav());j=await self.finish(r.json()['id'])
        self.assertEqual(j.status,'completed');self.assertFalse(j.directory.exists())
        for kind in ['txt','md','srt']:
            response=await self.client.get(f'/api/jobs/{j.id}/export/{kind}')
            self.assertEqual(response.status_code,200);self.assertIn('TEST STUB ONLY',response.text)
        self.assertEqual((await self.client.get(f'/api/jobs/{j.id}/export/html')).status_code,400)
        response=await self.client.post(f'/api/jobs/{j.id}/summary',json={'consent':False})
        self.assertEqual(response.status_code,400)
        with patch.dict(m.os.environ,{},clear=True):
            response=await self.client.post(f'/api/jobs/{j.id}/summary',json={'consent':True})
        self.assertEqual(response.status_code,503)
    async def test_cancel_kills_real_child_and_cleans(self):
        j=m.Job('cancel',Path(tempfile.mkdtemp(prefix='audio-notes-test-')))
        m.JOBS[j.id]=j
        async def task():
            try: await m.command(j,m.sys.executable,'-c','import time;time.sleep(30)')
            except asyncio.CancelledError: pass
        j.task=asyncio.create_task(task())
        for _ in range(100):
            if j.process: break
            await asyncio.sleep(.01)
        self.assertIsNotNone(j.process)
        r=await self.client.post('/api/jobs/cancel/cancel')
        self.assertEqual(r.json()['status'],'cancelled');self.assertIsNotNone(j.process.returncode)
        self.assertFalse(j.directory.exists())
        self.assertEqual((await self.client.post('/api/jobs/cancel/cancel')).status_code,200)
        self.assertEqual((await self.client.delete('/api/jobs/cancel')).status_code,200)
        self.assertEqual((await self.client.get('/api/jobs/cancel')).status_code,404)
    async def test_busy_and_unfinished_export(self):
        j=m.Job('busy',Path(tempfile.mkdtemp(prefix='audio-notes-test-')));m.JOBS[j.id]=j
        self.assertEqual((await self.submit(wav())).status_code,409)
        self.assertEqual((await self.client.get('/api/jobs/busy/export/txt')).status_code,409)
    async def test_duration_and_video_validation(self):
        for duration, streams in [(7201,[{'codec_type':'audio'}]), (1,[{'codec_type':'video'}]), (float('nan'),[{'codec_type':'audio'}])]:
            result=json.dumps({'format':{'format_name':'wav','duration':duration},'streams':streams}).encode()
            with patch.object(m,'command',return_value=result):
                r=await self.submit(wav());j=await self.finish(r.json()['id'])
            self.assertEqual(j.status,'failed');self.assertFalse(j.directory.exists())
    async def test_oversize_summary_body(self):
        j=m.Job('summary',Path(tempfile.mkdtemp(prefix='audio-notes-test-')),status='completed')
        m.JOBS[j.id]=j
        r=await self.client.post('/api/jobs/summary/summary',content=b'x'*1025)
        self.assertEqual(r.status_code,413)
    async def test_summary_rejects_remote_before_chat(self):
        j=m.Job('summary',Path(tempfile.mkdtemp(prefix='audio-notes-test-')),status='completed',segments=[{'id':1,'start':0,'end':1,'text':'SENSITIVE STUB'}])
        m.JOBS[j.id]=j
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return json.dumps({'remote_host':'https://example.invalid','model_info':{'x':1}}).encode()
        class Opener:
            calls=[]
            def open(self,req,**kw):self.calls.append(req);return Response()
        opener=Opener()
        with patch.dict(m.os.environ,{'AUDIO_OLLAMA_MODEL':'model'}),patch.object(m.urllib.request,'build_opener',return_value=opener):
            r=await self.client.post('/api/jobs/summary/summary',json={'consent':True})
        self.assertEqual(r.status_code,502);self.assertEqual(len(opener.calls),1)
        self.assertTrue(opener.calls[0].full_url.endswith('/api/show'))
        self.assertNotIn(b'SENSITIVE',opener.calls[0].data)
    def test_missing_tokenizer_rejected_before_engine_import(self):
        from app import worker
        with tempfile.TemporaryDirectory() as d:
            Path(d,'model.bin').write_bytes(b'stub');Path(d,'config.json').write_text('{}')
            with patch.dict(m.os.environ,{'AUDIO_MODEL_PATH':d}):
                with self.assertRaisesRegex(RuntimeError,'MODEL_FILES_MISSING'):
                    worker.main()
    async def test_bad_id(self):
        self.assertEqual((await self.client.get('/api/jobs/not-a-job')).status_code,404)
    def test_timestamp(self):
        self.assertEqual(m.timestamp(3661.234,True),'01:01:01,234')
        self.assertEqual(m.timestamp(59.9999,True),'00:01:00,000')
    def test_srt(self):
        self.assertEqual(m.export_segments([{'start':0,'end':1.5,'text':'hello'}],'srt'),
                         '1\n00:00:00,000 --> 00:00:01,500\nhello')

if __name__=='__main__':unittest.main()
