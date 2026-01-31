using Iiko.Front.Api;

namespace Views
{
    public static class BonusDialog
    {
        public static async void Show(QrResolveResponse data, Iiko.Front.Api.Data.IOrder order, string qrToken)
        {
            // Расчёт максимальной суммы для списания
            decimal max = Math.Min(data.Client.Balance, order.ResultSum * data.Rules.MaxWriteoffPercent);

            // Показываем прогресс на кассе
            PluginContext.Notifications.ShowMessage("Применение бонусов...");

            // Списываем бонусы через Backend
            var response = await Api.BonusApiClient.ApplyBonus(new Models.BonusApplyRequest
            {
                Action = "writeoff",
                OrderId = order.Id.ToString(),
                OrderNumber = order.Number,
                Amount = max,
                QrToken = qrToken
            });

            if (response.Status == "ok")
            {
                // Помечаем заказ как использовавший бонусы
                order.CustomData["BONUS_APPLIED"] = true;
                PluginContext.Notifications.ShowMessage($"Списано {max} ₽. Новый баланс: {response.NewBalance}");
            }
            else
            {
                PluginContext.Notifications.ShowMessage(response.Message);
            }
        }
    }
}
