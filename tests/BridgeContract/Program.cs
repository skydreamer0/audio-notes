// Local mock handler only. No real sockets, credentials, microphone or upstream services.
using System.Net;
using VoiceInput.Core.Recognition;
using VoiceInput.Core.Capsule;
using VoiceInput.Protocol;
var path = Path.GetTempFileName();
await File.WriteAllBytesAsync(path, new byte[64]);
Environment.SetEnvironmentVariable("AUDIO_CODEX_ASR_URL", "http://127.0.0.1:8788/v1/audio/transcriptions");
Environment.SetEnvironmentVariable("AUDIO_CODEX_ASR_KEY", "TEST-ONLY");
try
{
    using var success = new Fake(async (r, ct) => {
        Check(r.RequestUri!.Host == "127.0.0.1", "loopback");
        Check(r.Headers.Authorization?.Parameter == "TEST-ONLY", "local key");
        var body = await r.Content!.ReadAsStringAsync(ct);
        Check(body.Contains("response_format") && body.Contains("json"), "format");
        return new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent("{\"text\":\" MOCK ONLY \"}") };
    });
    var result = await new CodexAsrRecognitionEngine(success).TranscribeAsync(path, new(), default);
    Check(result.Text == "MOCK ONLY", "text contract");
    foreach (var code in new[] { 302, 401, 403, 429, 500 })
    {
        using var failure = new Fake((r, ct) => Task.FromResult(new HttpResponseMessage((HttpStatusCode)code) { Content = new StringContent("SECRET-RAW-BODY") }));
        try { await new CodexAsrRecognitionEngine(failure).TranscribeAsync(path, new(), default); throw new Exception("Expected failure"); }
        catch (InvalidOperationException e) { Check(!e.Message.Contains("SECRET"), "safe errors"); }
    }
    using var malformed = new Fake((r, ct) => Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK) { Content = new StringContent("SECRET") }));
    try { await new CodexAsrRecognitionEngine(malformed).TranscribeAsync(path, new(), default); throw new Exception("Expected invalid JSON"); }
    catch (InvalidOperationException e) { Check(!e.Message.Contains("SECRET"), "safe JSON error"); }
    using var cancel = new CancellationTokenSource();
    using var wait = new Fake(async (r, ct) => { cancel.Cancel(); await Task.Delay(10000, ct); return new HttpResponseMessage(); });
    try { await new CodexAsrRecognitionEngine(wait).TranscribeAsync(path, new(), cancel.Token); throw new Exception("Expected cancellation"); }
    catch (OperationCanceledException) { }
    Environment.SetEnvironmentVariable("AUDIO_CODEX_ASR_URL", "http://example.invalid:8788/v1/audio/transcriptions");
    using var never = new Fake((r, ct) => throw new Exception("Must not send"));
    try { await new CodexAsrRecognitionEngine(never).TranscribeAsync(path, new(), default); throw new Exception("Expected rejection"); }
    catch (InvalidOperationException) { }
    var delayed = new Delayed();
    var controller = new CapsuleController(delayed);
    var observed = new List<CapsuleState>();
    controller.SnapshotChanged += (_, state) => observed.Add(state.State);
    var pending = controller.StopAndTranscribeAsync(path);
    Check(controller.CancelTranscription(), "cancel active");
    controller.Reset();
    delayed.Result.SetResult(new RecognitionResult("LATE RESULT MUST NOT APPEAR"));
    await pending;
    Check(!observed.Contains(CapsuleState.Ready), "late ready suppressed");
    var queuedEngine = new Delayed();
    var queuedController = new CapsuleController(queuedEngine);
    var queue = new Queue<Action>();
    var applied = new List<CapsuleState>();
    queuedController.SnapshotChanged += (_, state) => queue.Enqueue(() => {
        if (queuedController.IsCurrentSnapshot(state)) applied.Add(state.State);
    });
    var queuedWork = queuedController.StopAndTranscribeAsync(path);
    queuedEngine.Result.SetResult(new RecognitionResult("QUEUED READY"));
    await queuedWork;
    queuedController.CancelTranscription();
    queuedController.Reset();
    while (queue.TryDequeue(out var callback)) callback();
    Check(!applied.Contains(CapsuleState.Ready), "stale queued Ready suppressed");
    Console.WriteLine("PASS: mock protocol/errors/cancellation/endpoint; not actual ASR.");
}
finally { File.Delete(path); }
static void Check(bool ok, string label) { if (!ok) throw new Exception(label); }
sealed class Fake(Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handle) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage r, CancellationToken ct) => handle(r, ct);
}

sealed class Delayed : IRecognitionEngine
{
    public string DisplayName => "deliberately ignores cancellation";
    public TaskCompletionSource<RecognitionResult> Result { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public Task<RecognitionResult> TranscribeAsync(string path, RecognitionOptions options, CancellationToken ct) => Result.Task;
}
