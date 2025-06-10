import customtkinter as ctk
import pymysql
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FaceDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração inicial
        self.title("Dashboard de Reconhecimento Facial")
        self.geometry("1200x800")
        
        # Configurações do banco de dados
        self.db_config = {
            'host': 'localhost',
            'user': 'jetaii',
            'password': '123456',
            'database': 'face_counter'
        }
        
        # Dicionário para armazenar os campos de entrada
        self.entries = {}
        
        # Configuração do layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Criar abas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Adicionar abas
        self.tabview.add("24 Horas")
        self.tabview.add("Mensal")
        self.tabview.add("Anual")
        self.tabview.add("Configurações")
        
        # Criar as abas
        self._create_settings_tab()
        self._create_24h_tab()
        self._create_monthly_tab()
        self._create_yearly_tab()
        
        # Atualizar dados
        self.update_all_charts()

    def get_db_connection(self):
        """Estabelece conexão com o banco de dados"""
        try:
            return pymysql.connect(**self.db_config)
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")
            return None

    def update_24h_chart(self):
        """Atualiza o gráfico das últimas 24 horas"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            # Consulta para as últimas 24 horas
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            query = """
                SELECT HOUR(detection_time) as hora, COUNT(*) as total
                FROM face_counts
                WHERE detection_time BETWEEN %s AND %s
                GROUP BY HOUR(detection_time)
                ORDER BY hora
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (start_time, end_time))
            results = cursor.fetchall()
            
            # Processar resultados
            hours = list(range(24))
            counts = [0] * 24
            
            for hora, total in results:
                counts[hora] = total
            
            # Atualizar gráfico
            self.ax_24h.clear()
            self.ax_24h.plot(hours, counts, marker='o')
            self.ax_24h.set_title("Rostos Detectados nas Últimas 24 Horas")
            self.ax_24h.set_xlabel("Hora do Dia")
            self.ax_24h.set_ylabel("Número de Rostos")
            self.ax_24h.set_xticks(range(24))
            self.ax_24h.grid(True)
            
            self.canvas_24h.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico 24h: {e}")
        finally:
            conn.close()

    def update_monthly_chart(self):
        """Atualiza o gráfico mensal"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            year = int(self.year_entry.get())
            month = int(self.month_combobox.get())
            
            query = """
                SELECT DAY(detection_time) as dia, COUNT(*) as total
                FROM face_counts
                WHERE YEAR(detection_time) = %s AND MONTH(detection_time) = %s
                GROUP BY DAY(detection_time)
                ORDER BY dia
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (year, month))
            results = cursor.fetchall()
            
            # Processar resultados
            days_in_month = 31  # Simplificação - poderia calcular o número exato de dias
            days = list(range(1, days_in_month + 1))
            counts = [0] * days_in_month
            
            for dia, total in results:
                if dia <= days_in_month:
                    counts[dia-1] = total
            
            # Atualizar gráfico
            self.ax_month.clear()
            self.ax_month.bar(days, counts)
            self.ax_month.set_title(f"Rostos Detectados em {month}/{year}")
            self.ax_month.set_xlabel("Dia do Mês")
            self.ax_month.set_ylabel("Número de Rostos")
            self.ax_month.grid(True)
            
            self.canvas_month.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico mensal: {e}")
        finally:
            conn.close()

    def update_yearly_chart(self):
        """Atualiza o gráfico anual"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            year = int(self.year_entry_annual.get())
            
            query = """
                SELECT MONTH(detection_time) as mes, COUNT(*) as total
                FROM face_counts
                WHERE YEAR(detection_time) = %s
                GROUP BY MONTH(detection_time)
                ORDER BY mes
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (year,))
            results = cursor.fetchall()
            
            # Processar resultados
            months = list(range(1, 13))
            month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                          'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            counts = [0] * 12
            
            for mes, total in results:
                counts[mes-1] = total
            
            # Atualizar gráfico
            self.ax_year.clear()
            bars = self.ax_year.bar(month_names, counts)
            self.ax_year.set_title(f"Rostos Detectados em {year}")
            self.ax_year.set_xlabel("Mês")
            self.ax_year.set_ylabel("Número de Rostos")
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                self.ax_year.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height)}',
                                ha='center', va='bottom')
            
            self.canvas_year.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico anual: {e}")
        finally:
            conn.close()

    def update_all_charts(self):
        """Atualiza todos os gráficos"""
        self.update_24h_chart()
        self.update_monthly_chart()
        self.update_yearly_chart()

    def _save_db_settings(self):
        """Salva as configurações do banco de dados"""
        try:
            self.db_config = {
                'host': self.entries['host'].get(),
                'user': self.entries['user'].get(),
                'password': self.entries['password'].get(),
                'database': self.entries['database'].get()
            }
            print("Configurações atualizadas:", self.db_config)
            self.update_all_charts()
        except Exception as e:
            print("Erro ao salvar configurações:", e)

    def _create_settings_tab(self):
        """Cria a aba de configurações"""
        frame = ctk.CTkFrame(self.tabview.tab("Configurações"))
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Título
        ctk.CTkLabel(frame, text="Configurações do Banco de Dados", font=("Arial", 16)).pack(pady=10)
        
        # Frame para os campos
        db_frame = ctk.CTkFrame(frame)
        db_frame.pack(pady=10)
        
        # Configurações
        settings = [
            {'label': 'Host:', 'key': 'host'},
            {'label': 'Usuário:', 'key': 'user'},
            {'label': 'Senha:', 'key': 'password'},
            {'label': 'Banco de Dados:', 'key': 'database'}
        ]
        
        # Criar campos de entrada
        for i, setting in enumerate(settings):
            ctk.CTkLabel(db_frame, text=setting['label']).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ctk.CTkEntry(db_frame)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, self.db_config[setting['key']])
            self.entries[setting['key']] = entry
        
        # Botão de salvar
        ctk.CTkButton(
            frame,
            text="Salvar Configurações",
            command=self._save_db_settings
        ).pack(pady=10)

    def _create_24h_tab(self):
        """Cria a aba de 24 horas"""
        frame = ctk.CTkFrame(self.tabview.tab("24 Horas"))
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Gráfico
        self.fig_24h = plt.Figure(figsize=(10, 4), dpi=100)
        self.ax_24h = self.fig_24h.add_subplot(111)
        self.canvas_24h = FigureCanvasTkAgg(self.fig_24h, master=frame)
        self.canvas_24h.get_tk_widget().pack(expand=True, fill="both")
        
        # Botão de atualização
        ctk.CTkButton(
            frame, 
            text="Atualizar Dados",
            command=self.update_24h_chart
        ).pack(pady=10)

    def _create_monthly_tab(self):
        """Cria a aba mensal"""
        frame = ctk.CTkFrame(self.tabview.tab("Mensal"))
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Gráfico
        self.fig_month = plt.Figure(figsize=(10, 4), dpi=100)
        self.ax_month = self.fig_month.add_subplot(111)
        self.canvas_month = FigureCanvasTkAgg(self.fig_month, master=frame)
        self.canvas_month.get_tk_widget().pack(expand=True, fill="both")
        
        # Controles
        control_frame = ctk.CTkFrame(frame)
        control_frame.pack(pady=10)
        
        ctk.CTkLabel(control_frame, text="Ano:").pack(side="left", padx=5)
        self.year_entry = ctk.CTkEntry(control_frame, width=80)
        self.year_entry.pack(side="left", padx=5)
        self.year_entry.insert(0, str(datetime.now().year))
        
        ctk.CTkLabel(control_frame, text="Mês:").pack(side="left", padx=5)
        self.month_combobox = ctk.CTkComboBox(
            control_frame,
            values=[str(i) for i in range(1, 13)],
            width=50
        )
        self.month_combobox.pack(side="left", padx=5)
        self.month_combobox.set(str(datetime.now().month))
        
        ctk.CTkButton(
            control_frame,
            text="Atualizar",
            command=self.update_monthly_chart
        ).pack(side="left", padx=10)

    def _create_yearly_tab(self):
        """Cria a aba anual"""
        frame = ctk.CTkFrame(self.tabview.tab("Anual"))
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Gráfico
        self.fig_year = plt.Figure(figsize=(10, 4), dpi=100)
        self.ax_year = self.fig_year.add_subplot(111)
        self.canvas_year = FigureCanvasTkAgg(self.fig_year, master=frame)
        self.canvas_year.get_tk_widget().pack(expand=True, fill="both")
        
        # Controles
        control_frame = ctk.CTkFrame(frame)
        control_frame.pack(pady=10)
        
        ctk.CTkLabel(control_frame, text="Ano:").pack(side="left", padx=5)
        self.year_entry_annual = ctk.CTkEntry(control_frame, width=80)
        self.year_entry_annual.pack(side="left", padx=5)
        self.year_entry_annual.insert(0, str(datetime.now().year))
        
        ctk.CTkButton(
            control_frame,
            text="Atualizar",
            command=self.update_yearly_chart
        ).pack(side="left", padx=10)

if __name__ == "__main__":
    app = FaceDashboard()
    app.mainloop()