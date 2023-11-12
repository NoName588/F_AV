using UnityEngine;

public class HandTracking : MonoBehaviour
{
    public UDPReciever udpReceive;
    public Transform[] handPoints; // Usa Transform en lugar de GameObject para cambiar la posición.

    void Update()
    {
        string data = udpReceive.data;
        if (!string.IsNullOrEmpty(data))
        {
            string[] handData = data.Split(';');

            if (handData.Length == handPoints.Length)
            {
                for (int i = 0; i < handData.Length; i++)
                {
                    string[] pointData = handData[i].Split(',');
                    if (pointData.Length == 3)
                    {
                        if (float.TryParse(pointData[0], out float x) && float.TryParse(pointData[1], out float y) && float.TryParse(pointData[2], out float z))
                        {
                            // Ajusta la escala y las coordenadas según tus necesidades
                            x = x / 100; // Escala x
                            y = y / 100; // Escala y
                            z = z / 100; // Escala z

                            // Actualiza la posición de los objetos handPoints.
                            handPoints[i].localPosition = new Vector3(x, y, z);
                        }
                        else
                        {
                            // Manejar el caso en el que la conversión no sea exitosa
                            Debug.LogError("No se pudo convertir una cadena a número de punto flotante.");
                        }
                    }
                }
            }
        }
    }
}

