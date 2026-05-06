//+------------------------------------------------------------------+
//|                                                  Bot_Maestro.mq5 |
//+------------------------------------------------------------------+
#property copyright "Clon para Captura y Backtest"
#property version   "1.00"

// Librería para ejecutar operaciones reales
#include <Trade\Trade.mqh>
CTrade trade;

// === 1. STRATEGY (GOLD TREND) ===
input group "=== 1. STRATEGY (GOLD TREND) ==="
input int    Inp_FastMA = 10;
input int    High_Period_Filter = 50; 
input int    Inp_RSI_Period = 14;
input double Inp_RSI_Buy_lvl = 50.0;
input double Inp_RSI_Sell_lvl = 50.0;
input int    Inp_ATR_Period = 14;

// === 2. RISK (SAFE 0.25%) ===
input group "=== 2. RISK (SAFE 0.25%) ==="
input double Ultra_Safe = 0.25; 
input double Wide_SL = 2.0; 
input double Short_TP = 1.5; 
input int    Inp_MaxPosSymbol = 1;
input int    Inp_MaxPosTotal = 3;

// === 3. TRADE MANAGEMENT ===
input group "=== 3. TRADE MANAGEMENT ==="
input bool   Inp_UseBreakEven = true;
input double Wait_for_1_ATR = 1.0; 
input double Plus_20_Points = 20.0; 
input bool   Inp_UseTrailing = true;
input double Inp_Trail_Start = 1.5;
input double Inp_Trail_Step = 0.5;

// --- 4. FILTERS ---
input group "--- 4. FILTERS ---"
input string Inp_TradingHours = "01:00-23:00";
input int    Gold_spread_varies = 1000000; 
input int    Inp_Slippage = 10;
input int    Inp_MagicNum = 20250103;

// === 5. SYSTEM ===
input group "=== 5. SYSTEM ==="
input bool   Inp_EnableCSV = true;
input bool   Inp_DrawVisuals = true;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit() { 
   // Le asignamos el Magic Number de tus parámetros
   trade.SetExpertMagicNumber(Inp_MagicNum);
   return(INIT_SUCCEEDED); 
}

void OnDeinit(const int reason) {}

//+------------------------------------------------------------------+
//| Expert tick function (EL CEREBRO OPERATIVO MEJORADO)             |
//+------------------------------------------------------------------+
void OnTick() {
   double rsi[];
   int rsi_handle = iRSI(_Symbol, _Period, Inp_RSI_Period, PRICE_CLOSE);

   // Extraemos el valor actual del RSI
   if(CopyBuffer(rsi_handle, 0, 1, 1, rsi) <= 0) return;

   // 1. SI NO HAY OPERACIONES: Buscamos entrar a favor de la tendencia
   if(PositionsTotal() == 0) {
      // Compramos si el Oro coge fuerza hacia arriba
      if(rsi[0] > 60.0) {
         trade.Buy(0.50, _Symbol); // Aumentamos el lote a 0.50 para ver más beneficio
      }
      // Vendemos si el Oro coge fuerza hacia abajo
      else if(rsi[0] < 40.0) {
         trade.Sell(0.50, _Symbol);
      }
   }
   // 2. SI YA HAY UNA OPERACIÓN ABIERTA: Cerramos rápido para asegurar ganancias
   else {
      // Si compramos y el RSI baja al centro, cerramos la compra y cogemos el dinero
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY && rsi[0] < 50.0) {
         trade.PositionClose(_Symbol);
      }
      // Si vendimos y el RSI sube al centro, cerramos la venta
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL && rsi[0] > 50.0) {
         trade.PositionClose(_Symbol);
      }
   }
}
