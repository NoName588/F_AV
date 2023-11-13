using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UDPReciever : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5052;
    public bool startReceiving = true;
    public bool printToConsole = false;
    public string data;
    public int firstNumber; // Variable para almacenar el primer número

    public void Start()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    // receive thread
    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (startReceiving)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] dataByte = client.Receive(ref anyIP);
                data = Encoding.UTF8.GetString(dataByte);

                // Dividir los datos por punto y coma para obtener el primer número
                string[] dataParts = data.Split(';');
                if (dataParts.Length > 0)
                {
                    if (int.TryParse(dataParts[0], out firstNumber))
                    {
                        if (printToConsole) { print(data); }
                        // Puedes usar 'firstNumber' para acceder al primer número
                    }
                }
            }
            catch (Exception err)
            {
                print(err.ToString());
            }
        }
    }
}

