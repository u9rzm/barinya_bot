namespace Models
{
    public class BonusApplyRequest
    {
        public string Action { get; set; }   // writeoff | accrual
        public string OrderId { get; set; }
        public int OrderNumber { get; set; }
        public decimal Amount { get; set; }
        public string QrToken { get; set; }
        public string RestaurantId { get; set; }
    }
}
