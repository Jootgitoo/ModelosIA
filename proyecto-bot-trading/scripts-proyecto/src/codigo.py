import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import sys

# =====================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS
# =====================================================================
# Estos parámetros reemplazan a la interfaz gráfica del Probador de Estrategias
INP_FAST_MA = 10      # Ventana para la Media Móvil Rápida
INP_RSI_PERIOD = 14   # Periodo del filtro RSI
INP_ATR_PERIOD = 14   # Periodo del filtro de volatilidad ATR
RISK_PERCENT = 0.25   # Gestión de riesgo (simulado)
MAGIC_NUMBER = 123456 # ID del Proceso (simulado)

print("Iniciando script de Trading Algorítmico y Machine Learning...")

# =====================================================================
# 2. CONEXIÓN Y EXTRACCIÓN 
# =====================================================================
try:
    import MetaTrader5 as mt5
    # Intentamos inicializar MetaTrader 5
    if not mt5.initialize():
        raise ConnectionError("No se pudo inicializar MetaTrader 5. Asegúrate de que esté abierto.")
    
    print("Conexión a MT5 exitosa. Descargando datos...")
    
    # Extraemos los datos
    velas = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 10000)
    
    if velas is None or len(velas) == 0:
        raise ValueError("No se pudieron descargar datos del símbolo XAUUSD.")
        
    df = pd.DataFrame(velas)
    df['time'] = pd.to_datetime(df['time'], unit='s')

except ImportError:
    print("Error Crítico: El módulo MetaTrader5 no está instalado. Ejecuta: pip install MetaTrader5")
    sys.exit()
except Exception as e:
    print(f"Fallo en la conexión o extracción de datos: {e}")
    sys.exit()

# =====================================================================
# 3. FEATURE ENGINEERING Y FILTROS
# =====================================================================
try:
    print("Calculando indicadores técnicos (Filtros)...")
    
    # Filtro 1: Media Móvil (FastMA)
    df['MA_Fast'] = df['close'].rolling(window=INP_FAST_MA).mean()
    
    # Filtro 2: RSI Manual
    delta = df['close'].diff()
    ganancias = delta.clip(lower=0).rolling(window=INP_RSI_PERIOD).mean()
    perdidas = -delta.clip(upper=0).rolling(window=INP_RSI_PERIOD).mean()
    
    # Evitamos división por cero en el RSI
    perdidas = perdidas.replace(0, 1e-10) 
    rs = ganancias / perdidas
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Filtro 3: ATR Manual (Rango Verdadero Medio)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    rango_verdadero = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = rango_verdadero.rolling(window=INP_ATR_PERIOD).mean()
    
    # Variables de varianza y retorno
    df['Varianza_Vela'] = df['high'] - df['low']
    df['Retorno'] = df['close'].pct_change()
    
    # Creación del Target (Aprendizaje Supervisado)
    df['Target'] = np.where(df['close'].shift(-1) > df['close'], 1, -1)
    
    # Limpiamos los datos nulos generados por los cálculos
    df.dropna(inplace=True)
    
    if len(df) < 100:
        raise ValueError("No hay suficientes datos válidos después de calcular los indicadores.")

except Exception as e:
    print(f"Error durante el Feature Engineering: {e}")
    if mt5.terminal_info() is not None:
        mt5.shutdown()
    sys.exit()

# =====================================================================
# 4. ENTRENAMIENTO DE LA IA Y VALIDACIÓN
# =====================================================================
try:
    print("Iniciando entrenamiento del modelo...")
    
    # División de datos (Train/Test Split)
    split_idx = int(len(df) * 0.8)
    
    # Usamos todas las variables calculadas como predictores
    X = df[['MA_Fast', 'RSI', 'ATR', 'Varianza_Vela', 'Retorno']]
    Y = df['Target']
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    Y_train, Y_test = Y.iloc[:split_idx], Y.iloc[split_idx:]
    
    # Instanciamos y entrenamos el modelo
    modelo_ia = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo_ia.fit(X_train, Y_train)
    
    # Evaluación
    precision = modelo_ia.score(X_test, Y_test)
    
    print("\n" + "="*50)
    print("--- RESULTADO DEL LABORATORIO (TESTING) ---")
    print(f"Filtros configurados en Python: FastMA({INP_FAST_MA}), RSI({INP_RSI_PERIOD}), ATR({INP_ATR_PERIOD})")
    print(f"Exactitud predictiva del modelo Out-of-Sample: {precision * 100:.2f}%")
    print("="*50)

except Exception as e:
    print(f"Error durante el entrenamiento del modelo: {e}")

finally:
    # Este bloque siempre se ejecuta, garantizando que liberamos la conexión
    if mt5.terminal_info() is not None:
        mt5.shutdown()
        print("Conexión con MetaTrader 5 cerrada correctamente.")