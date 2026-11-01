using System.Net;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace VoiceInput.Core.Recognition;

public sealed class CodexAsrRecognitionEngine : IRecognitionEngine
{
    // Integration patch: only Wangnov/codex-asr loopback REST, never direct login files.
    private readonly Uri? endpoint;
    private readonly string? apiKey;
    private readonly HttpMessageHandler? testHandler;

    public CodexAsrRecognitionEngine(HttpMessageHandler? testHandler = null)
    {
        this.testHandler = testHandler;
        var configured = Environment.GetEnvironmentVariable("AUDIO_CODEX_ASR_URL");
        if (Uri.TryCreate(configured, UriKind.Absolute, out var uri)
            && uri.Scheme == "http" && (uri.Host == "127.0.0.1" || uri.Host == "[::1]")
            && uri.Port > 0 && uri.AbsolutePath == "/v1/audio/transcriptions"
            && string.IsNullOrEmpty(uri.UserInfo) && string.IsNullOrEmpty(uri.Query)
            && string.IsNullOrEmpty(uri.Fragment))
        {
            endpoint = uri;
        }
        apiKey = Environment.GetEnvironmentVariable("AUDIO_CODEX_ASR_KEY");
    }

    public string DisplayName => "Codex ASR local bridge";

    public async Task<RecognitionResult> TranscribeAsync(
        string audioPath,
        RecognitionOptions options,
        CancellationToken cancellationToken)
    {
        if (endpoint is null)
            throw new InvalidOperationException("请先配置 loopback AUDIO_CODEX_ASR_URL");
        ValidateAudio(audioPath);
        if (apiKey is not null && apiKey.Any(c => c <= 32 || c >= 127))
            throw new InvalidOperationException("本機 bridge API key 格式無效");
        using var client = testHandler is null ? CreateHttpClient() : new HttpClient(testHandler, false);
        using var request = new HttpRequestMessage(HttpMethod.Post, endpoint);
        if (!string.IsNullOrWhiteSpace(apiKey))
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

        await using var audio = File.OpenRead(audioPath);
        using var multipart = new MultipartFormDataContent();
        using var audioContent = new StreamContent(audio);
        audioContent.Headers.ContentType = new MediaTypeHeaderValue(InferContentType(audioPath));
        multipart.Add(audioContent, "file", "audio" + Path.GetExtension(audioPath).ToLowerInvariant());
        if (HasExplicitLanguage(options.Language))
        {
            multipart.Add(new StringContent(options.Language!, Encoding.UTF8), "language");
        }
        multipart.Add(new StringContent("json"), "response_format");
        request.Content = multipart;

        using var deadline = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        deadline.CancelAfter(TimeSpan.FromMinutes(5));
        string body;
        try
        {
            using var response = await client.SendAsync(request,
                HttpCompletionOption.ResponseHeadersRead, deadline.Token);
            if (!response.IsSuccessStatusCode)
                throw new InvalidOperationException(CreateHttpErrorMessage(response.StatusCode));
            await using var stream = await response.Content.ReadAsStreamAsync(deadline.Token);
            using var buffer = new MemoryStream();
            var chunk = new byte[8192];
            int count;
            while ((count = await stream.ReadAsync(chunk.AsMemory(), deadline.Token)) != 0)
            {
                if (buffer.Length + count > 1024 * 1024)
                    throw new InvalidOperationException("转写回應超過大小上限");
                buffer.Write(chunk, 0, count);
            }
            body = Encoding.UTF8.GetString(buffer.ToArray());
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new InvalidOperationException("Codex ASR 逾時，未自動重試");
        }
        catch (HttpRequestException)
        {
            throw new InvalidOperationException("Codex ASR 連線失敗，請檢查本機 bridge");
        }

        CodexAsrJson? parsed;
        try
        {
            parsed = JsonSerializer.Deserialize<CodexAsrJson>(body);
        }
        catch (JsonException)
        {
            throw new InvalidOperationException("Codex ASR 回應格式無效");
        }

        var text = parsed?.Text?.Trim();
        if (string.IsNullOrWhiteSpace(text))
        {
            throw new InvalidOperationException("没有识别到文本");
        }

        return new RecognitionResult(text);
    }

    private static string CreateHttpErrorMessage(HttpStatusCode statusCode)
    {
        return statusCode switch
        {
            HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden => "Codex 登录已失效，请重新登录",
            HttpStatusCode.TooManyRequests => "请求过于频繁，请稍后重试",
            _ => $"转写失败：HTTP {(int)statusCode}",
        };
    }

    private static HttpClient CreateHttpClient()
    {
        return new HttpClient(new HttpClientHandler
        {
            UseProxy = false,
            AllowAutoRedirect = false,
        }, disposeHandler: true) { Timeout = TimeSpan.FromMinutes(5) };
    }

    private static void ValidateAudio(string path)
    {
        if (!File.Exists(path)) throw new FileNotFoundException("录音文件不存在", path);
        if (new FileInfo(path).Length > 50L * 1024 * 1024) throw new InvalidOperationException("音檔超過 50 MiB");
        if (new FileInfo(path).Length <= 44) throw new InvalidOperationException("录音内容为空");
    }

    private static string InferContentType(string path) =>
        Path.GetExtension(path).ToLowerInvariant() switch
        {
            ".wav" or ".wave" => "audio/wav",
            ".webm" => "audio/webm",
            ".mp3" => "audio/mpeg",
            ".m4a" or ".mp4" => "audio/mp4",
            ".ogg" or ".oga" => "audio/ogg",
            ".flac" => "audio/flac",
            _ => "application/octet-stream",
        };

    private static bool HasExplicitLanguage(string? language) =>
        !string.IsNullOrWhiteSpace(language)
        && !language.Equals("auto", StringComparison.OrdinalIgnoreCase);

    private sealed class CodexAsrJson
    {
        [JsonPropertyName("text")]
        public string? Text { get; set; }
    }
}
