using Iiko.Front.Api;
using System.Threading.Tasks;

namespace Services;

/// <summary>
/// Обработка QR-кода, проверка TON и вызов UI.
/// </summary>
public static class QrHandler
{
    public static async Task Handle(string qrText)
    {
        // 1. Получаем текущий заказ iiko
        var order = PluginContext.Operations.GetCurrentOrder();
        if (order == null)
        {
            Show("Нет активного заказа");
            return;
        }

        // 2. Проверяем, применялись ли бонусы ранее
        if (order.CustomData.ContainsKey("BONUS_APPLIED"))
        {
            Show("Бонусы уже применены к этому чеку");
            return;
        }

        // 3. Парсим QR token
        var qrToken = ParseToken(qrText);

        // 4. Backend проверка QR + получение данных клиента
        var resolve = await Api.BonusApiClient.ResolveQr(qrToken);

        // 5. Показываем прогресс проверки TON
        PluginContext.Notifications.ShowMessage("Проверка бонусов в блокчейне TON...");

        // 6. Проверка статуса клиента в TON
        bool tonOk = await Api.BonusApiClient.CheckTonStatus(resolve.Client.Id);

        if (!tonOk)
        {
            Show("Ошибка проверки в TON. Бонус не подтверждён.");
            return;
        }

        // 7. Открываем диалог начисления/списания бонусов
        Views.BonusDialog.Show(resolve, order, qrToken);
    }

    private static string ParseToken(string qr)
    {
        // Пример формата QR: bonus://qr?t=qr_abc123
        var uri = new Uri(qr);
        var query = System.Web.HttpUtility.ParseQueryString(uri.Query);
        return query["t"];
    }

    private static void Show(string message)
    {
        PluginContext.Notifications.ShowMessage(message);
    }
}
