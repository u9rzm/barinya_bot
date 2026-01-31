namespace Models
{
    public class BonusApplyResponse
    {
        public string Status { get; set; }   // ok | rejected
        public decimal NewBalance { get; set; }
        public string Message { get; set; }
    }
}
