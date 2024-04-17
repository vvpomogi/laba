using System;
using System.Text.Json;
using System.Threading;


namespace ControllerApp
{
  internal class TempController
  {
    public Guid guid { get; set; }

    public string uuid { get; set; }

    public int UpdateInterval { get; set; }

    public string Status { get; private set; }

    public int Temperature { get; private set; }

    public int CriticalTemperatureLow { get; set; }

    public int CriticalTemperatureHigh { get; set; }

    public int VentTemp { get; set; }

    public int HeatTemp { get; set; }

    public string PhoneNumber { get; set; }

    public TempController(Guid GUID)
    {
      Random random = new Random();
      this.guid = GUID;
      this.Temperature = random.Next(0, 30);
      this.VentTemp = 27;
      this.HeatTemp = 22;
      this.UpdateInterval = 300;
      this.Status = "Initializing... https://www.youtube.com/watch?v=n_GsoDOuqD8";
    }

    public bool NeedToChangeCurrentSettings(TempController.PostDataResponse NewData)
    {
      TempController.PostDataResponse postDataResponse = new TempController.PostDataResponse()
      {
        updateInterval = this.UpdateInterval,
        temperatureHighLimit = this.VentTemp,
        temperatureLowLimit = this.HeatTemp,
        criticalHighTemperature = this.CriticalTemperatureHigh,
        criticalLowTemperature = this.CriticalTemperatureLow,
        phoneNumber = this.PhoneNumber
      };
      return !(NewData == postDataResponse);
    }

    public void ThermalRegulation()
    {
      while (true)
      {
        if (this.Temperature > this.CriticalTemperatureHigh || this.Temperature < this.CriticalTemperatureLow)
          this.AlarmSMS(this.Temperature);
        Random random = new Random();
        int num = 0;
        switch (this.Status)
        {
          case "Venting":
            num = -random.Next(3, 4);
            break;
          case "Heating":
            num = random.Next(3, 4);
            break;
        }
        this.Temperature += num + random.Next(-3, 3);
        this.Status = this.Temperature <= this.VentTemp ? (this.Temperature >= this.HeatTemp ? "Idle" : "Heating") : "Venting";
        Thread.Sleep(1000);
      }
    }

    public string PostDataBuilder()
    {
      return JsonSerializer.Serialize<TempController.PostDataRequest>(new TempController.PostDataRequest()
      {
        stats = this.Temperature,
        type = "Thermometer",
        guid = this.guid.ToString(),
        status = this.Status
      }, (JsonSerializerOptions) null);
    }

    public void UpdateSettings(string json)
    {
      JsonSerializerOptions serializerOptions = new JsonSerializerOptions()
      {
        IgnoreNullValues = true
      };
      if (!json.Contains("null"))
      {
        TempController.PostDataResponse NewData = JsonSerializer.Deserialize<TempController.PostDataResponse>(json, serializerOptions);
        if (!this.NeedToChangeCurrentSettings(NewData))
          return;
        this.UpdateInterval = NewData.updateInterval;
        this.VentTemp = NewData.temperatureHighLimit;
        this.HeatTemp = NewData.temperatureLowLimit;
        this.CriticalTemperatureHigh = NewData.criticalHighTemperature;
        this.CriticalTemperatureLow = NewData.criticalLowTemperature;
        this.PhoneNumber = NewData.phoneNumber;
      }
      else
        Environment.Exit(0);
    }

    public void AlarmSMS(int temperature)
    {
    }

    public struct PostDataRequest
    {
      public string type { get; set; }

      public string guid { get; set; }

      public int stats { get; set; }

      public string status { get; set; }
    }

    public struct PostDataResponse
    {
      public int updateInterval { get; set; }

      public int temperatureHighLimit { get; set; }

      public int temperatureLowLimit { get; set; }

      public int criticalHighTemperature { get; set; }

      public int criticalLowTemperature { get; set; }

      public string phoneNumber { get; set; }

      public static bool operator ==(
        TempController.PostDataResponse Data1,
        TempController.PostDataResponse Data2)
      {
        return Data1.updateInterval == Data2.updateInterval && Data1.phoneNumber == Data2.phoneNumber && Data1.temperatureHighLimit == Data2.temperatureHighLimit && Data1.temperatureLowLimit == Data2.temperatureLowLimit && Data1.criticalHighTemperature == Data2.criticalHighTemperature && Data1.criticalLowTemperature == Data2.criticalLowTemperature;
      }

      public static bool operator !=(
        TempController.PostDataResponse Data1,
        TempController.PostDataResponse Data2)
      {
        return Data1.updateInterval != Data2.updateInterval || !(Data1.phoneNumber == Data2.phoneNumber) || Data1.temperatureHighLimit != Data2.temperatureHighLimit || Data1.temperatureLowLimit != Data2.temperatureLowLimit || Data1.criticalHighTemperature != Data2.criticalHighTemperature || Data1.criticalLowTemperature != Data2.criticalLowTemperature;
      }

      public override string ToString()
      {
        return Convert.ToString(this.updateInterval) + " " + Convert.ToString(this.temperatureHighLimit) + " " + Convert.ToString(this.temperatureLowLimit);
      }
    }
  }
}
