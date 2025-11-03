/*********************************************
 * OPL 22.1.1.0 Model
 * Author: Santiago
 * Creation Date: Oct 27, 2025 at 2:26:29 PM
 *********************************************/

// --- Conjuntos y parámetros base ---
{string} I = ...;            // Activos financieros
int H = ...;                 // Número de periodos
range T = 1..H;              // Índice de periodos (1..H)
{string} C = ...;            // Clases de activo
{string} D = ...; // Para mostrar fechas -> Realmente es T pero es necesario que T sean enteros.


// --- Parámetros ---
float W0 = ...;              // Capital inicial
float r[I][T] = ...;         // r[i][t] = retorno esperado del activo i en periodo t (t = 1..H)
float c_buy[I] = ...;        // c_buy[i] = costo proporcional por comprar el activo i
float c_sell[I] = ...;       // c_sell[i] = costo proporcional por vender el activo i
int   g[I][C] = ...;         // g[i][c] = pertenencia binaria activo->clase
float L[C] = ...;            // Límite mínimo por clase (si aplica)
float U[C] = ...;            // Límite máximo por clase (si aplica)
float X_min[I] = ...;        // Límite mínimo por clase (si aplica)
float X_max[I] = ...;        // Límite máximo por clase (si aplica)

// --- Validación de compatibilidad de límites ---
assert forall(i in I, c in C)
  (X_min[i] <= L[c] && L[c] <= U[c] && U[c] <= X_max[i]);


// --- Variables de decisión ---
dvar float+ x[I][T];         // posición en activo i al final del periodo t
dvar float+ y[I][T];         // cantidad comprada del activo i en el periodo t
dvar float+ z[I][T];         // cantidad vendida del activo i en el periodo t
dvar float+ W[0..H];         // capital disponible al inicio de cada periodo; W[0] = W0


// --- Función Objetivo ---
// Maximizar riqueza final (capital al final del horizonte)
maximize
  W[H];


// --- Restricciones ---


subject to {
  // Capital inicial
  W_initial:
    W[0] == W0;


  // Dinámica del capital: W[t] = W[t-1] + sum_i r[i][t] * x[i][t], para t = 1..H
  forall(t in T)
    W_dynamic:
      W[t] == W[t-1] + sum(i in I) r[i][t] * x[i][t] - sum(i in I) (c_buy[i] * y[i][t] + c_sell[i] * z[i][t]);


  // Presupuesto por periodo: sum_i x[i][t] <= W[t-1]  (capital disponible al inicio del periodo)
  forall(t in T)
    budget:
      sum(i in I) x[i][t] <= W[t-1];


  // Flujo de cartera: posiciones en funcion de compras/ventas
  // Primer periodo: x[i,1] = y[i,1]  (si se parte sin posiciones iniciales)
  forall(i in I)
    flow_first:
      x[i][1] == y[i][1];


  // Para t >= 2: x[i,t] = x[i,t-1] + y[i,t] - z[i,t]
  forall(i in I, t in T: t >= 2)
    flow_follow:
      x[i][t] == x[i][t-1] + y[i][t] - z[i][t];


  // No vender más de lo que se posee: z[i,t] <= x[i,t-1]  (para t >= 2)
  // Prohibir ventas en t=1 (si se parte sin posiciones)
  forall(i in I)
    no_sell_first:
      z[i][1] == 0;

  forall(i in I, t in T: t >= 2)
    no_sell_follow:
      z[i][t] <= x[i][t-1];


  // Restricción de compras inicial: sum_i y[i,1] <= W0
  buys_initial:
    sum(i in I) y[i][1] <= W0;


  // Diversificación por clase (mínimo y máximo) -- se aplican en cada período
  forall(c in C, t in T) {
    class_min:
      sum(i in I) g[i][c] * x[i][t] >= L[c] * W[t];

    class_max:
      sum(i in I) g[i][c] * x[i][t] <= U[c] * W[t];
  }
  
  // Inversión por activo (mínimo y máximo) -- se aplican en cada periodo
  forall(i in I, t in T) {
    asset_min:
      x[i][t] >= X_min[i] * W[t];
      
    asset_max:
      x[i][t] <= X_max[i] * W[t]; 
  }
}


execute {
  var f = new IloOplOutputFile("results.csv");

  // --- Encabezado ---
  f.write("Variable,Activo");
  for (var d in D)
  	f.write("," + d);
  f.writeln();

  // --- Posiciones x[i][t] ---
  for (var i in I) {
    f.write("x," + i);
    for (var t in T)
      f.write("," + x[i][t]);
    f.writeln();
  }

  // --- Compras y[i][t] ---
  for (var i in I) {
    f.write("y," + i);
    for (var t in T)
      f.write("," + y[i][t]);
    f.writeln();
  }

  // --- Ventas z[i][t] ---
  for (var i in I) {
    f.write("z," + i);
    for (var t in T)
      f.write("," + z[i][t]);
    f.writeln();
  }

  // --- Capital W[t] ---
  f.write("W,Capital");
  for (var t in T)
    f.write("," + W[t]);
  f.writeln();


  f.close();
  writeln("Resultados exportados a 'resultados.csv'");
}

execute {
  var f = new IloOplOutputFile("params.txt");

  f.writeln("=== RESUMEN DE PARÁMETROS UTILIZADOS ===\n");

  // --- Conjuntos ---
  f.writeln("Conjunto de activos (I):");
  f.writeln(I);
  f.writeln();

  f.writeln("Conjunto de clases de activos (C):");
  f.writeln(C);
  f.writeln();

  f.writeln("Conjunto de períodos (T):");
  f.writeln(T);
  f.writeln();

  // --- Parámetros globales ---
  f.writeln("Capital inicial (W0): ", W0);
  f.writeln();

  // --- Costos de transacción ---
  f.writeln("Costos de compra (c_buy[i]):");
  for (var i in I)
    f.writeln("  ", i, ": ", c_buy[i]);
  f.writeln();

  f.writeln("Costos de venta (c_sell[i]):");
  for (var i in I)
    f.writeln("  ", i, ": ", c_sell[i]);
  f.writeln();
  
  // --- Límites por clase ---
  f.writeln("Límites mínimos por clase (L[c]):");
  for (var c in C)
    f.writeln("  ", c, ": ", L[c]);
  f.writeln();

  f.writeln("Límites máximos por clase (U[c]):");
  for (var c in C)
    f.writeln("  ", c, ": ", U[c]);
  f.writeln();

  // --- Límites por activo ---
  f.writeln("Límites mínimos por activo (X_min[i]):");
  for (var i in I)
    f.writeln("  ", i, ": ", X_min[i]);
  f.writeln();

  f.writeln("Límites máximos por activo (X_max[i]):");
  for (var i in I)
    f.writeln("  ", i, ": ", X_max[i]);
  f.writeln();

  // --- Relación activo-clase ---
  f.writeln("Matriz de pertenencia g[i][c] (1 si el activo pertenece a la clase):");
  for (var i in I) {
    var line = i + ": ";
    for (var c in C)
      line += g[i][c] + " ";
    f.writeln("  " + line);
  }

  f.writeln("\n=== FIN DEL RESUMEN ===");
  f.close();

  writeln("Archivo 'params.txt' generado correctamente.");
}

