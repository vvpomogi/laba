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
      request.ContentType = "Thermometer";
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
            TempController tempController1 = new TempController(guid);
      Thread LiveController = new Thread(new ThreadStart(tempController1.ThermalRegulation));
      LiveController.Start();
      while (true)
      {
        try
        {
          TempController tempController2 = tempController1;
          string json = await Program.cnnct(tempController1.PostDataBuilder(), url, port);
          tempController2.UpdateSettings(json);
          tempController2 = (TempController) null;
          json = (string) null;
          Thread.Sleep(tempController1.UpdateInterval * 1000);
        }
        catch (WebException ex)
        {
          WebException e = ex;
        }
      }
    }
  }
}
