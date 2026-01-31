namespace Models
{
    public class QrResolveResponse
    {
        public Client Client { get; set; }
        public Rules Rules { get; set; }
    }

    public class Client
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public decimal Balance { get; set; }
    }

    public class Rules
    {
        public decimal MaxWriteoffPercent { get; set; }
    }
}
