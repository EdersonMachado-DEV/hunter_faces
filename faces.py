import cv2
import os
import numpy as np
from deepface import DeepFace
import pymysql
import customtkinter as ctk
from PIL import Image, ImageTk

# Configuração do MySQL (sem timestamp)cls

db_config = {
    'host': 'localhost',
    'user': 'jetaii',
    'password': '123456',
    'database': 'face_counter'
}

class FaceCounter:
    def __init__(self):
        self.detected_hashes = set()  # Armazena hashes únicos
        self.current_count = 0
    
    def get_face_hash(self, embedding):
        """Gera hash único baseado no embedding facial"""
        return hash(tuple(embedding.round(2).tobytes()))  # Arredonda para reduzir variações

    def process_frame(self, frame):
        try:
            # Detecção rápida com OpenCV
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                
                try:
                    embedding = np.array(DeepFace.represent(face_img, model_name="Facenet")[0]["embedding"])
                    face_hash = self.get_face_hash(embedding)
                    
                    if face_hash not in self.detected_hashes:
                        self.detected_hashes.add(face_hash)
                        self.current_count += 1
                        self.save_count()  # Registra apenas a contagem total
                        
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                except Exception as e:
                    continue
                    
            return frame
            
        except Exception as e:
            print(f"Erro: {e}")
            return frame

    def save_count(self):
        """Salva apenas a contagem atual (sem timestamp)"""
        try:
            conn = pymysql.Connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO face_counts (name) VALUES (%s)", (f"Rosto {self.current_count}",))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erro DB: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Contador de Rostos Únicos")
        self.geometry("640x480")
        
        # Componentes
        self.video_label = ctk.CTkLabel(self)
        self.video_label.pack(pady=20)
        
        self.count_label = ctk.CTkLabel(self, text="Rostos Únicos: 0", font=("Arial", 24))
        self.count_label.pack()
        
        self.counter = FaceCounter()
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            processed_frame = self.counter.process_frame(frame)
            img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk
            self.count_label.configure(text=f"Rostos Únicos: {self.counter.current_count}")
        
        self.after(10, self.update_frame)

    def on_close(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()