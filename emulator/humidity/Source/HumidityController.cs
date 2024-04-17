using System;
using System.Text.Json;
using System.Threading;


namespace ControllerApp
{
  internal class HumidityController
  {
    public Guid guid { get; set; }

    public int UpdateInterval { get; set; }

    public string Status { get; private set; }

    public int Humidity { get; private set; }

    public int HumidityLowLimit { get; set; }

    public HumidityController(Guid GUID)
    {
      Random random = new Random();
      this.guid = GUID;
      this.Humidity = random.Next(0, 100);
      this.UpdateInterval = 1;
      this.Status = "Initializing... https://www.youtube.com/watch?v=n_GsoDOuqD8";
    }

    public bool NeedToChangeCurrentSettings(HumidityController.PostDataResponse NewData)
    {
      HumidityController.PostDataResponse postDataResponse = new HumidityController.PostDataResponse()
      {
        updateInterval = this.UpdateInterval,
        humidityLowLimit = this.HumidityLowLimit
      };
      return !(NewData == postDataResponse);
    }

    public void HumidityRegulation()
    {
      while (true)
      {
        Random random = new Random();
        int num = 0;
        if (this.Status == "Watering")
          num += random.Next(2, 4);
        this.Humidity += num + random.Next(-2, 0);
        if (this.Humidity > 100)
          this.Humidity = 100;
        if (this.Humidity < 0)
          this.Humidity = 0;
        this.Status = this.Humidity >= this.HumidityLowLimit ? "Idle" : "Watering";
        Thread.Sleep(1000);
      }
    }

    public string PostDataBuilder()
    {
      return JsonSerializer.Serialize<HumidityController.PostDataRequest>(new HumidityController.PostDataRequest()
      {
        stats = this.Humidity,
        type = "Humidity",
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
        HumidityController.PostDataResponse NewData = JsonSerializer.Deserialize<HumidityController.PostDataResponse>(json, serializerOptions);
        if (!this.NeedToChangeCurrentSettings(NewData))
          return;
        this.UpdateInterval = NewData.updateInterval;
        this.HumidityLowLimit = NewData.humidityLowLimit;
      }
      else
        Environment.Exit(0);
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

      public int humidityLowLimit { get; set; }

      public static bool operator ==(
        HumidityController.PostDataResponse Data1,
        HumidityController.PostDataResponse Data2)
      {
        return Data1.updateInterval == Data2.updateInterval && Data1.humidityLowLimit == Data2.humidityLowLimit;
      }

      public static bool operator !=(
        HumidityController.PostDataResponse Data1,
        HumidityController.PostDataResponse Data2)
      {
        return Data1.updateInterval != Data2.updateInterval || Data1.humidityLowLimit != Data2.humidityLowLimit;
      }

      public override string ToString()
      {
        return Convert.ToString(this.updateInterval) + " " + Convert.ToString(this.humidityLowLimit);
      }
    }
  }
}
