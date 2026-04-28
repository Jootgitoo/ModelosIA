import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# =====================================================================
# 1. CONFIGURACIÓN DE FILTROS (Las variables del Maestro)
# =====================================================================
INP_FAST_MA = 10      # Ventana para la Media Móvil Rápida
INP_RSI_PERIOD = 14   # Periodo del filtro RSI
INP_ATR_PERIOD = 14   # Periodo del filtro de volatilidad ATR
RISK_PERCENT = 0.25   # Gestión de riesgo
MAGIC_NUMBER = 123456 # ID del Proceso (PID)

# =====================================================================
# 2. CONEXIÓN Y DESCARGA DE DATOS
# =====================================================================
if not mt5.initialize():
    print("Error al conectar.")
    mt5.shutdown()

velas = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 10000)
df = pd.DataFrame(velas)
df['time'] = pd.to_datetime(df['time'], unit='s')

# =====================================================================
# 3. APLICACIÓN DE FILTROS (Mates Puras con Pandas)
# =====================================================================
# Filtro 1: Media Móvil (FastMA)
df['MA_Fast'] = df['close'].rolling(window=INP_FAST_MA).mean()

# Filtro 2: RSI Manual
delta = df['close'].diff()
ganancias = delta.clip(lower=0).rolling(window=INP_RSI_PERIOD).mean()
perdidas = -delta.clip(upper=0).rolling(window=INP_RSI_PERIOD).mean()
rs = ganancias / perdidas
df['RSI'] = 100 - (100 / (1 + rs))

# Filtro 3: ATR Manual (Rango Verdadero Medio)
high_low = df['high'] - df['low']
high_close = np.abs(df['high'] - df['close'].shift())
low_close = np.abs(df['low'] - df['close'].shift())
rango_verdadero = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
df['ATR'] = rango_verdadero.rolling(window=INP_ATR_PERIOD).mean()

# Variables básicas
df['Varianza'] = df['high'] - df['low']
df['Retorno'] = df['close'].pct_change()

# Limpiamos las primeras filas que se quedan vacías por los cálculos
df.dropna(inplace=True)

# =====================================================================
# 4. ENTRENAMIENTO DE LA IA
# =====================================================================
X = df[['MA_Fast', 'RSI', 'ATR', 'Varianza', 'Retorno']]
df['Target'] = np.where(df['close'].shift(-1) > df['close'], 1, -1)
Y = df['Target']

# División 80/20
split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
Y_train, Y_test = Y.iloc[:split], Y.iloc[split:]

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, Y_train)

precision = modelo.score(X_test, Y_test)
print(f"--- RESULTADO DEL LABORATORIO ---")
print(f"Filtros aplicados: FastMA({INP_FAST_MA}), RSI({INP_RSI_PERIOD}), ATR({INP_ATR_PERIOD})")
print(f"Exactitud predictiva con estos filtros: {precision * 100:.2f}%")

mt5.shutdown()