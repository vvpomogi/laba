using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ControllerApp
{
  public class Program
  {
    private static async Task<string> cnnct(string postData, string url, string port)
    {
      string uri = "http://" + url + ":" + port + "/controller";
      WebRequest request = WebRequest.Create(uri);
      request.Method = "POST";
      byte[] byteArray = Encoding.UTF8.GetBytes(postData);
      request.ContentType = "Humidity";
      request.ContentLength = (long) byteArray.Length;
      Stream dataStream = request.GetRequestStream();
      dataStream.Write(byteArray, 0, byteArray.Length);
      dataStream.Close();
      WebResponse response = await request.GetResponseAsync();
      string responseFromServer = "";
      using (dataStream = response.GetResponseStream())
      {
        StreamReader reader = new StreamReader(dataStream);
        responseFromServer = ((TextReader) reader).ReadToEnd();
        reader = (StreamReader) null;
      }
      response.Close();
      string str = responseFromServer;
      request = (WebRequest) null;
      byteArray = (byte[]) null;
      dataStream = (Stream) null;
      response = (WebResponse) null;
      responseFromServer = (string) null;
      return str;
    }

    public static async Task Main(string[] args)
    {
      Guid guid = Guid.Parse(args[0]);
      string url = args[1];
      string port = args[2];
      HumidityController humidityController1 = new HumidityController(guid);
      Thread LiveController = new Thread(new ThreadStart(humidityController1.HumidityRegulation));
      LiveController.Start();
      while (true)
      {
        try
        {
          HumidityController humidityController2 = humidityController1;
          string json = await Program.cnnct(humidityController1.PostDataBuilder(), url, port);
          humidityController2.UpdateSettings(json);
          humidityController2 = (HumidityController) null;
          json = (string) null;
          Thread.Sleep(humidityController1.UpdateInterval * 1000);
        }
        catch (WebException ex)
        {
          WebException e = ex;
        }
      }
    }
  }
}
