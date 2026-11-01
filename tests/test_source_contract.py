"""Static source-contract checks only: these are NOT a C# build or runtime test."""
from pathlib import Path
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import verify_sources as v
D=v.ROOT/'desktop/src'
class SourceTests(unittest.TestCase):
    def test_provenance_patch_xml(self):v.verify()
    def test_desktop_no_auth_discovery(self):
        engine=(D/'VoiceInput.Core/Recognition/CodexAsrRecognitionEngine.cs').read_text()
        main=(D/'VoiceInput.App/MainWindow.xaml.cs').read_text()
        for text in (engine,main):
            for forbidden in ['auth.json','LoadAuth','ResolveAuthFile','backend-api/transcribe','access_token','CODEX_HOME']:
                self.assertNotIn(forbidden,text)
    def test_loopback_no_proxy_or_redirect(self):
        s=(D/'VoiceInput.Core/Recognition/CodexAsrRecognitionEngine.cs').read_text()
        for required in ['uri.Host == "127.0.0.1"','uri.Host == "[::1]"','uri.Scheme == "http"','/v1/audio/transcriptions','AllowAutoRedirect = false','UseProxy = false','deadline.Token','1024 * 1024','response_format']:
            self.assertIn(required,s)
        self.assertNotIn('Clip(body)',s);self.assertNotIn('WebRequest.GetSystemWebProxy',s)
    def test_both_send_flows_consent(self):
        s=(D/'VoiceInput.App/MainWindow.xaml.cs').read_text()
        self.assertEqual(s.count('if (!ConfirmCloud())'),2)
        self.assertIn('if (!ConfirmCloud()) return;\n            readyText = string.Empty;\n            await controller.StopAndTranscribeAsync(file.Path);',s)
        self.assertIn('if (!ConfirmCloud()) { controller.Reset(); return; }\n            await controller.StopAndTranscribeAsync(audioPath);',s)
    def test_no_asset_build_refs(self):
        s=(D/'VoiceInput.App/VoiceInput.App.csproj').read_text()
        self.assertNotIn('<ApplicationIcon>',s);self.assertNotIn('<Content Include="Assets',s)
    def test_no_default_injection_and_separate_data(self):
        main=(D/'VoiceInput.App/MainWindow.xaml.cs').read_text()
        self.assertNotIn('await InjectReadyTextAsync();',main)
        self.assertIn('AUDIO_NOTES_ENABLE_HOTKEY',main)
        self.assertIn('"AudioNotesCodex"',(D/'VoiceInput.App/Services/AppConfig.cs').read_text())
    def test_lifecycle_guards(self):
        recorder=(D/'VoiceInput.App/Services/WavAudioRecorder.cs').read_text()
        self.assertNotIn('"CodexVoiceInput"',recorder)
        self.assertIn('Guid.NewGuid()',recorder)
        controller=(D/'VoiceInput.Core/Capsule/CapsuleController.cs').read_text()
        self.assertIn('requestCancellation.IsCancellationRequested',controller)
        self.assertIn('!ReferenceEquals(activeTranscription, requestCancellation)',controller)
        main=(D/'VoiceInput.App/MainWindow.xaml.cs').read_text()
        self.assertIn('currentSnapshot.State != CapsuleState.Ready',main)
        self.assertIn('var exportText = readyText;',main)
        self.assertIn('if (disposed) return;',main)
        self.assertIn('if (controller.IsCurrentSnapshot(snapshot)) ApplySnapshot(snapshot);',main)
    def test_no_fake_timestamps(self):
        s=(D/'VoiceInput.App/MainWindow.xaml.cs').read_text()
        self.assertNotIn('"srt"',s);self.assertIn('kind == "prompt"',s)
if __name__=='__main__':unittest.main()
