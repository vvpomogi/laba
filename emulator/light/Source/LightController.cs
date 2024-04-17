using System;
using System.Text.Json;
using System.Threading;

namespace ControllerApp
{
  internal class LightController
  {
    public Guid guid { get; set; }

    public string uuid { get; set; }

    public int UpdateInterval { get; set; }

    public string Status { get; private set; }

    public int LightRays { get; private set; }

    public int LightHighLimit { get; set; }

    public int LightLowLimit { get; set; }

    public LightController(Guid GUID)
    {
      Random random = new Random();
      this.guid = GUID;
      this.LightRays = random.Next(0, 100);
      this.UpdateInterval = 300;
      this.Status = "Initializing... https://www.youtube.com/watch?v=n_GsoDOuqD8";
    }

    public bool NeedToChangeCurrentSettings(LightController.PostDataResponse NewData)
    {
      LightController.PostDataResponse postDataResponse = new LightController.PostDataResponse()
      {
        updateInterval = this.UpdateInterval,
        lightHighLimit = this.LightHighLimit,
        lightLowLimit = this.LightLowLimit
      };
      return !(NewData == postDataResponse);
    }

    public void LightRegulation()
    {
      while (true)
      {
        Random random = new Random();
        int num = 0;
        switch (this.Status)
        {
          case "Blackout":
            num = -random.Next(2, 4);
            break;
          case "Shine":
            num = random.Next(2, 4);
            break;
        }
        this.LightRays += num + random.Next(-2, 2);
        this.Status = this.LightRays <= this.LightHighLimit ? (this.LightRays >= this.LightLowLimit ? "Idle" : "Shine") : "Blackout";
        if (this.LightRays > 100)
          this.LightRays = 100;
        if (this.LightRays < 0)
          this.LightRays = 0;
        Thread.Sleep(1000);
      }
    }

    public string PostDataBuilder()
    {
      return JsonSerializer.Serialize<LightController.PostDataRequest>(new LightController.PostDataRequest()
      {
        stats = this.LightRays,
        type = "Light",
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
        LightController.PostDataResponse NewData = JsonSerializer.Deserialize<LightController.PostDataResponse>(json, serializerOptions);
        if (!this.NeedToChangeCurrentSettings(NewData))
          return;
        this.UpdateInterval = NewData.updateInterval;
        this.LightHighLimit = NewData.lightHighLimit;
        this.LightLowLimit = NewData.lightLowLimit;
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

      public int lightHighLimit { get; set; }

      public int lightLowLimit { get; set; }

      public static bool operator ==(
        LightController.PostDataResponse Data1,
        LightController.PostDataResponse Data2)
      {
        return Data1.updateInterval == Data2.updateInterval && Data1.lightHighLimit == Data2.lightHighLimit && Data1.lightLowLimit == Data2.lightLowLimit;
      }

      public static bool operator !=(
        LightController.PostDataResponse Data1,
        LightController.PostDataResponse Data2)
      {
        return Data1.updateInterval != Data2.updateInterval || Data1.lightHighLimit != Data2.lightHighLimit || Data1.lightLowLimit != Data2.lightLowLimit;
      }

      public override string ToString()
      {
        return Convert.ToString(this.updateInterval) + " " + Convert.ToString(this.lightLowLimit) + " " + Convert.ToString(this.lightHighLimit);
      }
    }
  }
}
