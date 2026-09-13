# CubatureApp

<p align="center">
  <img src="./app/assets/cubature_icon.png" width="150" alt="CubatureApp">
</p>

<h3 align="center">Cubatura numerica su domini poliedrici tridimensionali</h3>

<p align="center">
  Applicazione desktop per l'integrazione numerica di funzioni su domini poliedrici tridimensionali.
</p>

<p align="center">
  <a href="https://github.com/longoedoardo/CubatureApp">Repository</a>
  ·
  <a href="https://github.com/longoedoardo/OptimalPolyCubatureND">Metodo numerico</a>
</p>

---

## Descrizione

**CubatureApp** è un'applicazione desktop di calcolo scientifico per l'integrazione numerica di funzioni su domini poliedrici tridimensionali rappresentati mediante mesh superficiali triangolari.

L'applicazione fornisce un flusso di lavoro integrato che combina:

- un'interfaccia grafica sviluppata con **Python** e **PySide6**;
- visualizzazione 3D interattiva basata su **PyVista**, **VTK** e **pyvistaqt**;
- parsing simbolico delle funzioni integrande tramite **SymPy**;
- caricamento e validazione geometrica e topologica delle mesh;
- un backend numerico ad alte prestazioni scritto in **Fortran**;
- generazione automatica di nodi e pesi di cubatura;
- valutazione numerica dell'integrale;
- esportazione in formato CSV dei risultati numerici e dei dati di cubatura;
- generazione automatica di report tecnici in formato PDF;
- compilazione automatica del backend Fortran quando necessario;
- creazione di un'applicazione standalone tramite **PyInstaller**.

L'applicazione Python svolge il ruolo di livello di orchestrazione, mentre l'algoritmo numerico di cubatura è implementato in Fortran ed eseguito tramite un driver a riga di comando.

La teoria matematica alla base del metodo, inclusa la costruzione delle regole di cubatura, la base di polinomi di Chebyshev, il calcolo dei momenti e la procedura di ottimizzazione, è sviluppata nel repository dedicato:

> [**OptimalPolyCubatureND**](https://github.com/longoedoardo/OptimalPolyCubatureND)

Questo repository è invece focalizzato principalmente sull'applicazione desktop, sull'integrazione Python/Fortran, sulla gestione delle mesh, sulla visualizzazione e sull'intero flusso di utilizzo.

---

## Funzionalità

CubatureApp offre le seguenti funzionalità:

- caricamento di vertici e facce triangolari da file `.dat`;
- validazione della mesh prima dell'integrazione numerica;
- visualizzazione interattiva del dominio poliedrico in 3D;
- definizione della funzione integranda \(f(x,y,z)\);
- parsing delle espressioni matematiche tramite SymPy;
- selezione del **Grado Algebrico di Esattezza (ADE)**;
- generazione automatica dei nodi e dei pesi di cubatura;
- valutazione della funzione integranda nei nodi di cubatura;
- calcolo dell'integrale numerico;
- visualizzazione dei punti di cubatura nella scena 3D;
- confronto del risultato numerico con un valore atteso;
- analisi dei pesi di cubatura positivi e negativi;
- esportazione in CSV dei risultati numerici e dei dati di cubatura;
- generazione di report PDF contenenti risultati, grafici e diagnostica;
- compilazione automatica del backend Fortran quando necessario;
- creazione di un'applicazione desktop standalone tramite PyInstaller;
- creazione di un installer DMG per macOS.

---

## Architettura

L'applicazione segue un'architettura a livelli, nella quale l'interfaccia grafica comunica con un motore computazionale Python, che gestisce a sua volta l'elaborazione geometrica e il backend numerico Fortran.

```text
┌──────────────────────────────────┐
│       Interfaccia grafica        │
│            PySide6               │
│ Input · Risultati · Visualizz.   │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│        Motore di cubatura        │
│     Orchestrazione pipeline      │
└───────────────┬──────────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌───────────────┐  ┌────────────────┐
│ Geometria e   │  │ Backend Fortran│
│ funzioni      │  │   Driver CLI   │
│ Python        │  └───────┬────────┘
└───────────────┘          │
                           ▼
                  ┌──────────────────┐
                  │ Nucleo numerico  │
                  │     Fortran      │
                  └──────────────────┘
```

### Flusso computazionale

La pipeline computazionale principale è la seguente:

1. l'utente seleziona i file della mesh;
2. Python carica i dati geometrici;
3. la mesh viene sottoposta a validazione;
4. la funzione integranda viene analizzata tramite SymPy;
5. il backend Fortran viene compilato, se necessario;
6. il driver Fortran costruisce la regola di cubatura;
7. Python valuta la funzione nei nodi generati;
8. l'integrale viene calcolato come somma pesata dei valori della funzione;
9. il risultato viene visualizzato nella GUI;
10. i dati numerici possono essere esportati in CSV o inclusi in un report PDF.

---

## Struttura della repository

```text
CubatureApp/
├── app/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── report_pdf.py
│   ├── version.py
│   │
│   ├── assets/
│   │   ├── cubature_icon.ico
│   │   ├── cubature_icon.png
│   │   ├── cubature_icon.svg
│   │   └── CubatureApp.icns
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── cubature_engine.py
│   │   └── fortran_backend.py
│   │
│   ├── function_parser/
│   │   └── parser.py
│   │
│   ├── geometry/
│   │   ├── mesh_io.py
│   │   └── mesh_validation.py
│   │
│   ├── gui/
│   │   ├── export_dialog.py
│   │   ├── input_panel.py
│   │   ├── main_window.py
│   │   ├── results_panel.py
│   │   └── style.py
│   │
│   └── visualization/
│       └── viewer3d.py
│
├── examples/
│   ├── bunny_tri.dat
│   ├── bunny_vertex.dat
│   ├── concave_tri.dat
│   ├── concave_vertex.dat
│   ├── convex_tri.dat
│   └── convex_vertex.dat
│
├── fortran/
│   └── src/
│       ├── CubaCheap.f90
│       ├── driverCLI.f90
│       ├── OptimalPolyCuba3D.f90
│       ├── PolyhedronMesh.f90
│       ├── PrepCheap.f90
│       ├── triangleQuadratureGJ.f90
│       └── TypesDef.f90
│
├── installer/
│   └── create_macos_dmg.sh
│
├── build.py
├── requirements.txt
├── requirements-build.txt
├── LICENSE
└── README.md
```

---

## Componenti principali

### `app/gui/`

Contiene l'interfaccia grafica dell'applicazione.

| File | Descrizione |
|---|---|
| `main_window.py` | Finestra principale e coordinamento degli eventi |
| `input_panel.py` | Controlli per mesh, funzione integranda, grado e visualizzazione |
| `results_panel.py` | Visualizzazione dei risultati numerici |
| `export_dialog.py` | Interfaccia per l'esportazione in CSV |
| `style.py` | Stile grafico e tema dell'applicazione |

### `app/core/`

Contiene il nucleo computazionale dell'applicazione Python.

| File | Descrizione |
|---|---|
| `cubature_engine.py` | Coordina l'intera pipeline di cubatura |
| `fortran_backend.py` | Verifica, compila ed esegue il backend Fortran |

### `app/geometry/`

Gestisce le mesh in ingresso e la relativa validazione geometrica.

| File | Descrizione |
|---|---|
| `mesh_io.py` | Lettura dei file `.dat` contenenti la mesh |
| `mesh_validation.py` | Verifica della consistenza geometrica e topologica |

### `app/function_parser/`

Contiene il parser della funzione integranda basato su SymPy.

Il parser:

- accetta le variabili `x`, `y` e `z`;
- utilizza una whitelist delle funzioni matematiche consentite;
- converte le espressioni simboliche in funzioni numeriche NumPy;
- non esegue codice Python arbitrario tramite `eval()`.

### `app/visualization/`

Contiene il visualizzatore 3D integrato, basato su **PyVista** e **pyvistaqt**.

### `fortran/src/`

Contiene il backend numerico e il driver a riga di comando.

| File | Descrizione |
|---|---|
| `OptimalPolyCuba3D.f90` | Implementazione principale del metodo di cubatura |
| `CubaCheap.f90` | Matrice di Vandermonde, momenti e trasformazioni correlate |
| `triangleQuadratureGJ.f90` | Regole di quadratura sulle facce triangolari |
| `PolyhedronMesh.f90` | Gestione della mesh poliedrica |
| `PrepCheap.f90` | Routine di preparazione numerica e griglia di riferimento |
| `TypesDef.f90` | Definizione dei tipi e delle strutture dati condivise |
| `driverCLI.f90` | Interfaccia a riga di comando utilizzata da Python |

---

## Requisiti

### Requisiti minimi

- **Python 3.10+**
- `pip`
- **GFortran**
- Sistema operativo con supporto a Qt e OpenGL

Il progetto è sviluppato e testato principalmente su **macOS**.

I componenti Python sono in gran parte indipendenti dalla piattaforma, mentre la compilazione del codice Fortran e il packaging dell'applicazione possono richiedere configurazioni specifiche su Windows e Linux.

---

## Dipendenze Python

Le dipendenze necessarie per l'esecuzione sono elencate in `requirements.txt`:

```text
PySide6
pyvista
pyvistaqt
numpy
sympy
matplotlib
```

Le dipendenze necessarie per il build e il packaging sono elencate in `requirements-build.txt`:

```text
pyinstaller
```

---

## Installazione

### 1. Clonare la repository

```bash
git clone https://github.com/longoedoardo/CubatureApp.git
cd CubatureApp
```

### 2. Creare un ambiente virtuale

```bash
python3 -m venv .venv
```

### 3. Attivare l'ambiente virtuale

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Installare le dipendenze runtime

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Installare le dipendenze di build

Se si desidera creare un'applicazione standalone:

```bash
python -m pip install -r requirements-build.txt
```

---

## Compilatore Fortran

Verificare che Python e GFortran siano disponibili:

```bash
python3 --version
gfortran --version
```

Su macOS, GFortran può essere installato tramite Homebrew:

```bash
brew install gcc
```

È quindi possibile verificare il percorso del compilatore con:

```bash
which gfortran
```

---

## Avvio dell'applicazione

Dalla directory principale della repository:

```bash
python -m app
```

Questo è il metodo consigliato per avviare l'applicazione, poiché mantiene correttamente la struttura del package Python.

In alternativa:

```bash
python app/main.py
```

All'avvio, la finestra principale dell'applicazione fornisce:

- controlli per l'inserimento della mesh;
- campo per la funzione integranda;
- selezione del Grado Algebrico di Esattezza;
- visualizzazione 3D interattiva;
- risultati numerici;
- controlli per l'esportazione e la generazione dei report.

---

## Primo avvio e configurazione del backend

CubatureApp utilizza i sorgenti Fortran contenuti nella directory:

```text
fortran/src/
```

La configurazione specifica dell'utente viene memorizzata in:

```text
~/.OptimalPolyCuba3D/
```

Il file principale di configurazione è:

```text
~/.OptimalPolyCuba3D/config.json
```

La configurazione contiene informazioni quali:

- directory dei sorgenti Fortran;
- directory di compilazione;
- ultimo file dei vertici selezionato;
- ultimo file delle facce selezionato;
- ultima funzione integranda inserita;
- ultimo grado algebrico selezionato.

La directory predefinita dei sorgenti Fortran è:

```text
<repository>/fortran/src
```

Il backend numerico richiede i seguenti file:

```text
TypesDef.f90
PrepCheap.f90
PolyhedronMesh.f90
triangleQuadratureGJ.f90
CubaCheap.f90
OptimalPolyCuba3D.f90
```

Il file `driverCLI.f90` viene cercato prima nella directory dei sorgenti configurata e, se non disponibile, nella directory `fortran/src/` della repository.

---

## Compilazione del backend Fortran

Il backend numerico può essere compilato automaticamente dall'applicazione oppure manualmente tramite `build.py`.

### Compilazione automatica

Quando viene richiesto un calcolo, `FortranBackend`:

1. verifica che tutti i sorgenti necessari siano disponibili;
2. cerca il compilatore `gfortran`;
3. controlla se esiste già un eseguibile compilato;
4. confronta le date di modifica dei sorgenti;
5. ricompila il backend solo quando necessario;
6. esegue il driver Fortran;
7. legge i file di output generati.

La directory di compilazione predefinita è:

```text
~/.OptimalPolyCuba3D/build/
```

Questo meccanismo evita compilazioni non necessarie durante l'esecuzione ripetuta dei calcoli.

### Compilazione tramite `build.py`

Per compilare il backend e creare l'applicazione standalone:

```bash
python build.py
```

Il processo di build:

1. compila i moduli Fortran;
2. genera l'eseguibile `driverCLI`;
3. avvia PyInstaller;
4. include gli asset dell'applicazione e i file necessari al backend;
5. genera l'applicazione nella directory `dist/`.

Il backend Fortran viene compilato con opzioni di ottimizzazione analoghe a:

```bash
gfortran -O2 -ffree-line-length-none ...
```

---

## Formato della mesh

Un dominio poliedrico è rappresentato mediante due file di testo separati:

1. un **file dei vertici**;
2. un **file delle facce triangolari**.

I file utilizzano un semplice formato `.dat`.

### File dei vertici

La prima riga contiene il numero di vertici.

Le righe successive contengono le coordinate \(x\), \(y\) e \(z\).

Esempio:

```text
4
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0
```

Formalmente:

```text
N
x1 y1 z1
x2 y2 z2
...
xN yN zN
```

### File delle facce

La prima riga contiene il numero di facce triangolari.

Ogni riga successiva contiene gli indici dei tre vertici che definiscono una faccia:

```text
4
1 2 3
1 4 2
1 3 4
2 4 3
```

Formalmente:

```text
M
i1 j1 k1
i2 j2 k2
...
iM jM kM
```

Gli indici dei vertici sono **1-based**, come richiesto dal backend Fortran.

Pertanto:

```text
1 <= indice <= N
```

Le facce devono essere triangolari. La superficie in ingresso dovrebbe rappresentare una frontiera poliedrica chiusa e coerentemente orientata.

---

## Mesh di esempio

La directory `examples/` contiene diversi domini di test:

```text
examples/
├── convex_vertex.dat
├── convex_tri.dat
├── concave_vertex.dat
├── concave_tri.dat
├── bunny_vertex.dat
└── bunny_tri.dat
```

Le corrispondenti coppie vertici/facce sono:

```text
convex_vertex.dat  + convex_tri.dat
concave_vertex.dat + concave_tri.dat
bunny_vertex.dat   + bunny_tri.dat
```

Per una prima prova si consiglia di utilizzare l'esempio convesso:

```text
examples/convex_vertex.dat
examples/convex_tri.dat
```

---

## Definizione della funzione integranda

La funzione integranda viene inserita nella forma:

```text
f(x, y, z)
```

L'espressione viene analizzata da SymPy e convertita in una funzione numerica NumPy tramite `lambdify`.

Le variabili disponibili sono:

```text
x
y
z
```

Tra le funzioni matematiche supportate sono incluse:

```text
sin
cos
tan
asin
acos
atan
sinh
cosh
tanh
exp
log
ln
sqrt
abs
Abs
```

Sono inoltre disponibili le costanti matematiche:

```text
pi
e
```

Il parser converte le costruzioni LaTeX supportate nella corrispondente rappresentazione SymPy.

---

## Grado Algebrico di Esattezza

Il **Grado Algebrico di Esattezza (ADE)** determina il grado dei polinomi fino al quale la regola di cubatura è costruita per risultare esatta.

La GUI consente di selezionare valori nell'intervallo:

```text
0 - 20
```

In generale, un grado maggiore porta alla costruzione di una regola di cubatura con un numero maggiore di punti e può quindi aumentare il costo computazionale.

Il numero di punti di cubatura viene determinato dal backend Fortran in funzione del grado richiesto.

La costruzione matematica delle regole di cubatura è descritta nel repository:

> [**OptimalPolyCubatureND**](https://github.com/longoedoardo/OptimalPolyCubatureND)

---

## Utilizzo dell'applicazione

### 1. Selezionare la mesh

Nel pannello **Mesh Input**:

1. premere `Browse...` per il file dei vertici;
2. selezionare il corrispondente file `*_vertex.dat`;
3. premere `Browse...` per il file delle facce;
4. selezionare il corrispondente file `*_tri.dat`.

### 2. Inserire la funzione integranda

Nel pannello **Integrand**, inserire una funzione delle variabili `x`, `y` e `z`.

Ad esempio:

```text
x^2 + y^2 + z^2
```

### 3. Selezionare il grado algebrico

Selezionare il Grado Algebrico di Esattezza desiderato.

Ad esempio:

```text
4
```

### 4. Inserire un eventuale risultato atteso

Il campo `Expected Result` è opzionale.

Se viene inserito un valore atteso, l'applicazione calcola automaticamente l'errore assoluto:

\[
\left|I_{\mathrm{numerico}}-I_{\mathrm{atteso}}\right|.
\]

### 5. Eseguire il calcolo

Premere:

```text
COMPUTE CUBATURE
```

Durante il calcolo:

- la GUI mostra lo stato dell'operazione;
- il backend Fortran viene compilato se necessario;
- vengono generati nodi e pesi di cubatura;
- la funzione integranda viene valutata nei nodi;
- viene calcolato l'integrale numerico.

### 6. Analizzare il risultato

Il pannello dei risultati mostra informazioni quali:

- integrale numerico;
- errore assoluto, se è stato inserito un valore atteso;
- numero di punti di cubatura;
- grado algebrico;
- numero di vertici;
- numero di facce triangolari;
- tempo di calcolo;
- volume stimato tramite la somma dei pesi;
- numero di pesi negativi;
- numero di pesi positivi.

---

## Visualizzazione 3D

Il visualizzatore 3D è implementato in:

```text
app/visualization/viewer3d.py
```

e utilizza **PyVista** e **pyvistaqt**.

Il visualizzatore fornisce controlli per:

- mostrare o nascondere la mesh;
- attivare la modalità wireframe;
- visualizzare gli assi cartesiani;
- visualizzare i punti di cubatura;
- modificare la dimensione dei punti;
- ripristinare la vista isometrica.

I punti di cubatura vengono visualizzati in funzione del valore assoluto del peso associato.

La mesh poliedrica viene visualizzata mediante:

- superfici semitrasparenti;
- bordi triangolari;
- shading della superficie;
- distinzione visiva della distribuzione dei punti di cubatura.

---

## Validazione della mesh

Prima di eseguire un calcolo, l'applicazione sottopone la mesh a una procedura di validazione.

Vengono controllati:

- esistenza del file dei vertici;
- esistenza del file delle facce;
- formato `N × 3` dei vertici;
- formato `M × 3` delle facce;
- finitezza delle coordinate numeriche;
- validità degli indici dei vertici;
- presenza esclusiva di facce triangolari;
- facce degeneri;
- facce duplicate;
- vertici isolati;
- edge aperti;
- edge non-manifold;
- orientazione incoerente delle facce;
- bounding box geometrica.

Gli errori bloccanti impediscono l'esecuzione del calcolo numerico.

Gli avvisi non bloccanti segnalano invece caratteristiche potenzialmente problematiche della mesh, consentendo comunque all'utente di proseguire.

---

## Creazione dell'applicazione standalone

L'intera applicazione può essere impacchettata tramite PyInstaller.

Installare innanzitutto le dipendenze di build:

```bash
python -m pip install -r requirements-build.txt
```

Quindi eseguire:

```bash
python build.py
```

L'applicazione risultante viene generata nella directory:

```text
dist/
```

Su macOS, il bundle dell'applicazione sarà:

```text
dist/CubatureApp.app
```

---

## Creazione del DMG per macOS

Dopo aver eseguito correttamente:

```bash
python build.py
```

è possibile creare l'installer con:

```bash
bash installer/create_macos_dmg.sh
```

Lo script:

1. verifica che `dist/CubatureApp.app` esista;
2. crea lo sfondo dell'installer;
3. crea un'immagine DMG temporanea;
4. inserisce l'applicazione nell'immagine;
5. crea un collegamento alla directory `/Applications`;
6. converte l'immagine in un DMG compresso;
7. genera:

```text
dist/CubatureApp-Installer.dmg
```

Il DMG risultante può essere distribuito come installer per macOS.

---

## Metodo numerico

CubatureApp implementa un metodo di cubatura numerica per domini poliedrici tridimensionali. La costruzione della regola si basa sulle informazioni relative ai momenti polinomiali e su una rappresentazione ottimizzata della regola di cubatura.

L'implementazione comprende:

- basi polinomiali;
- calcolo dei momenti;
- sistemi di Vandermonde;
- quadratura numerica sulle facce triangolari;
- gestione della geometria poliedrica;
- generazione dei nodi e dei pesi di cubatura.

Per lo sviluppo matematico completo, le dimostrazioni, i risultati teorici e gli esperimenti numerici si rimanda a:

> [**OptimalPolyCubatureND**](https://github.com/longoedoardo/OptimalPolyCubatureND)

---

## Progetto correlato

### OptimalPolyCubatureND

Lo sviluppo matematico e numerico del metodo di cubatura è mantenuto separatamente nel repository:

[**github.com/longoedoardo/OptimalPolyCubatureND**](https://github.com/longoedoardo/OptimalPolyCubatureND)

Il repository contiene i componenti teorici e computazionali alla base delle regole di cubatura utilizzate da CubatureApp.

---

## Licenza

Il progetto è distribuito secondo i termini della licenza specificata nel file [`LICENSE`](./LICENSE).

---

<p align="center">
  <b>CubatureApp</b><br>
  Cubatura numerica su domini poliedrici tridimensionali
</p>