import cv2
from pyzbar.pyzbar import decode
import time
import pandas as pd
from datetime import datetime

class LectorQRAsistencia:
    def __init__(self):
        self.asistencia_registrada = []
        self.cargar_asistencia_existente()
        
    def cargar_asistencia_existente(self):
        try:
            self.df = pd.read_excel('asistencia.xlsx')
            self.asistencia_registrada = self.df['ID'].tolist()
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=['ID', 'Nombre', 'Fecha', 'Hora'])
            self.asistencia_registrada = []
    
    def escanear_qr(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)  # Ancho
        cap.set(4, 480)   # Alto
        
        print("Escaneando códigos QR para asistencia...")
        print("Presione 'q' para salir")
        
        while True:
            success, img = cap.read()
            
            for barcode in decode(img):
                datos_qr = barcode.data.decode('utf-8')
                
                try:
                    # Suponemos que el QR contiene "ID:Nombre"
                    id_persona, nombre = datos_qr.split(':')
                    
                    if id_persona not in self.asistencia_registrada:
                        ahora = datetime.now()
                        fecha = ahora.strftime("%d/%m/%Y")
                        hora = ahora.strftime("%H:%M:%S")
                        
                        nuevo_registro = {
                            'ID': id_persona,
                            'Nombre': nombre,
                            'Fecha': fecha,
                            'Hora': hora
                        }
                        
                        self.df = pd.concat([self.df, pd.DataFrame([nuevo_registro])], ignore_index=True)
                        self.asistencia_registrada.append(id_persona)
                        
                        print(f"Asistencia registrada: {nombre} ({id_persona}) a las {hora}")
                        
                        # Guardar inmediatamente en el archivo Excel
                        self.df.to_excel('asistencia.xlsx', index=False)
                    else:
                        print(f"{nombre} ya había registrado asistencia anteriormente")
                    
                except ValueError:
                    print("Formato de QR no válido. Debe ser 'ID:Nombre'")
                
                # Dibujar rectángulo alrededor del QR
                pts = barcode.polygon
                if len(pts) == 4:
                    pts = [(int(pt.x), int(pt.y)) for pt in pts]
                    for j in range(4):
                        cv2.line(img, pts[j], pts[(j+1)%4], (0, 255, 0), 3)
            
            cv2.imshow('Lector QR Asistencia', img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    lector = LectorQRAsistencia()
    lector.escanear_qr()