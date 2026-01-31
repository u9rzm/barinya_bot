using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Models;

namespace Api;

/// <summary>
/// Клиент для Backend Bonus API + проверка TON.
/// </summary>
public static class BonusApiClient
{
    private static readonly HttpClient http = new HttpClient
    {
        BaseAddress = new Uri("https://api.example.com"),
        Timeout = TimeSpan.FromSeconds(5)
    };

    static BonusApiClient()
    {
        http.DefaultRequestHeaders.Add("X-IIKO-API-KEY", "YOUR_IIKO_API_KEY");
    }

    // ===== Проверка QR + получение данных клиента =====
    public static async Task<QrResolveResponse> ResolveQr(string token)
    {
        return await Post<QrResolveResponse>("/qr/resolve", new { token });
    }

    // ===== Списание / начисление бонусов =====
    public static async Task<BonusApplyResponse> ApplyBonus(BonusApplyRequest request)
    {
        return await Post<BonusApplyResponse>("/bonus/apply", request);
    }

    // ===== Проверка TON Blockchain =====
    public static async Task<bool> CheckTonStatus(string clientId)
    {
        // Используем REST endpoint TON или RPC
        string rpcUrl = "https://toncenter.com/api/v2/getAccountState";
        string accountAddress = GetTonAddressByClient(clientId);
        string queryUrl = $"{rpcUrl}?address={accountAddress}";

        using var response = await http.GetAsync(queryUrl);
        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync();
        var data = JObject.Parse(json);

        // Пример: проверяем баланс или наличие NFT
        decimal balance = data["balance"]?.Value<decimal>() ?? 0;
        return balance > 0;
    }

    private static string GetTonAddressByClient(string clientId)
    {
        // В реальном проекте → запрос к backend mapping
        return "EQCXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"; // заглушка
    }

    // ===== Универсальный POST =====
    private static async Task<T> Post<T>(string url, object body)
    {
        var json = JsonConvert.SerializeObject(body);
        var response = await http.PostAsync(url,
            new StringContent(json, Encoding.UTF8, "application/json"));
        response.EnsureSuccessStatusCode();
        return JsonConvert.DeserializeObject<T>(await response.Content.ReadAsStringAsync());
    }
}
