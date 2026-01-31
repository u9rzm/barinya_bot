using Iiko.Front.Api;
using Iiko.Front.Api.Attributes;

/// <summary>
/// Главный класс плагина.
/// iikoFront загружает его автоматически.
/// </summary>
[Plugin]
public class Plugin : IFrontPlugin
{
    public void Initialize()
    {
        // Подписка на сканирование QR-кода
        PluginContext.Notifications
            .SubscribeOnQrCodeScanned(OnQrScanned);
    }

    private async void OnQrScanned(string qrText)
    {
        // Вся логика обработки QR в QrHandler
        await Services.QrHandler.Handle(qrText);
    }

    public void Dispose() { }
}
