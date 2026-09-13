# CubatureApp

<p align="center">
  <img src="./app/assets/cubature_icon.png" width="150" alt="CubatureApp">
</p>

<p align="center">
  <strong>Interfaccia grafica per la cubatura numerica su domini poliedrici 3D</strong>
</p>

<p align="center">
  <a href="https://github.com/longoedoardo/CubatureApp">Repository</a>
  ·
  <a href="https://github.com/longoedoardo/OptimalPolyCubatureND">Metodo numerico</a>
</p>

---

## Descrizione

**CubatureApp** è un'applicazione desktop per calcolare numericamente integrali di volume su domini poliedrici tridimensionali rappresentati mediante mesh superficiali triangolari.

Il progetto combina:

- interfaccia grafica desktop sviluppata con **Python** e **PySide6**;
- visualizzazione 3D interattiva basata su **PyVista**, **VTK** e **pyvistaqt**;
- parser simbolico delle funzioni basato su **SymPy**;
- lettura e validazione di mesh triangolari;
- backend numerico ad alte prestazioni scritto in **Fortran**;
- esportazione dei risultati in formato **CSV**;
- generazione di report tecnici in formato **PDF**;
- sistema di compilazione e packaging con **PyInstaller**.

L'implementazione numerica del metodo di cubatura è contenuta nel backend Fortran e viene richiamata dall'applicazione Python tramite un driver a riga di comando.

La teoria matematica del metodo, la costruzione delle regole di cubatura e i dettagli relativi alla base di Chebyshev e ai momenti sul poliedro sono documentati nel progetto dedicato:

> [OptimalPolyCubatureND](https://github.com/longoedoardo/OptimalPolyCubatureND)

Questo repository si concentra principalmente sull'applicazione desktop, sull'integrazione tra Python e Fortran e sul flusso di utilizzo.

---

## Funzionalità

CubatureApp permette di:

- selezionare un file di vertici e un file di facce triangolari;
- caricare e validare una mesh 3D;
- visualizzare il dominio poliedrico;
- definire una funzione \(f(x,y,z)\);
- selezionare il grado algebrico di esattezza della regola;
- generare automaticamente i nodi e i pesi di cubatura;
- calcolare l'integrale numerico;
- visualizzare i punti di quadratura nella scena 3D;
- confrontare il risultato con un valore atteso;
- analizzare il numero e il segno dei pesi;
- esportare risultati e nodi in CSV;
- generare un report PDF contenente dati, grafici e diagnostica;
- compilare automaticamente il backend Fortran quando necessario;
- creare un'applicazione desktop distribuibile tramite PyInstaller.

---

## Architettura del progetto

L'applicazione è organizzata in più livelli.

```text
┌─────────────────────────────┐
│          GUI PySide6        │
│ Input, risultati, controlli │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       CubatureEngine        │
│ Orchestrazione della pipeline│
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌───────────────┐
│ Mesh e parser│  │ FortranBackend│
│ Python       │  │ Driver CLI    │
└──────────────┘  └───────┬───────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Numerical Core   │
                │ Fortran          │
                └──────────────────┘

```

Il flusso principale è:

1. l'utente seleziona i file della mesh;

2. Python legge i dati geometrici;

3. la mesh viene controllata;

4. la funzione integranda viene analizzata da SymPy;

5. il backend Fortran viene compilato se necessario;

6. il driver Fortran costruisce nodi e pesi di cubatura;

7. Python valuta la funzione sui nodi;

8. l'integrale viene calcolato tramite prodotto scalare tra valori e pesi;

9. GUI, CSV e PDF mostrano o esportano i risultati.

## Struttura della repository

```
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

### Componenti principali
#### `app/gui/`
Contiene l'interfaccia grafica:

- `main_window.py`: finestra principale e coordinamento degli eventi;

- `input_panel.py`: selezione della mesh, funzione, grado e controlli 3D;

- `results_panel.py`: visualizzazione dei risultati numerici;

- `export_dialog.py`: esportazione dei dati in CSV;

- `style.py`: tema grafico dell'applicazione.

#### `app/core/`

Contiene il nucleo applicativo:

- `cubature_engine.py`: coordina l'intera pipeline;

- `fortran_backend.py`: verifica i sorgenti, compila il driver ed esegue il backend Fortran.

#### `app/geometry/`

Gestisce i file della mesh:

- `mesh_io.py`: lettura dei file `.dat`;

- `mesh_validation.py`: verifica della consistenza geometrica e topologica.

#### `app/function_parser/`

Contiene il parser SymPy della funzione integranda.

Il parser utilizza una whitelist di variabili e funzioni consentite e non utilizza `eval()` sull'input dell'utente.

#### `app/visualization/`

Contiene il visualizzatore 3D integrato nella GUI.

#### `fortran/src/`

Contiene il backend numerico e il programma wrapper:

- `OptimalPolyCuba3D.f90`: routine principale del metodo;

- `CubaCheap.f90`: costruzione della matrice di Vandermonde, momenti e trasformazioni;

- `triangleQuadratureGJ.f90`: quadratura sulle facce triangolari;

- `PolyhedronMesh.f90`: lettura delle mesh;

- `PrepCheap.f90`: routine di preparazione e griglia di riferimento;

- `TypesDef.f90`: tipi e variabili condivise;

- `driverCLI.f90`: interfaccia a riga di comando utilizzata da Python.

## Requisiti

### Requisiti minimi

- Python 3.10 o versione successiva consigliata;

- `pip`;

- compilatore Fortran `gfortran`;

- sistema operativo con supporto a Qt e OpenGL.

Il progetto è sviluppato principalmente per **macOS**. La struttura Python è in gran parte portabile, ma la compilazione e il packaging possono richiedere configurazioni specifiche su Windows e Linux.

### Dipendenze Python

Le dipendenze runtime sono definite in `requirements.txt`:

Plain text

```
PySide6
pyvista
pyvistaqt
numpy
sympy
matplotlib

```

Le dipendenze utilizzate per il packaging sono definite in `requirements-build.txt`:

Plain text

```
pyinstaller

```

### Verifica degli strumenti


Bash

```
python3 --version
gfortran --version

```

Su macOS, `gfortran` può essere installato tramite Homebrew:

Bash

```
brew install gcc

```

Dopo l'installazione è possibile verificare il percorso del compilatore:

Bash

```
which gfortran

```

## Installazione da sorgente

Clonare la repository:

Bash

```
git clone https://github.com/longoedoardo/CubatureApp.git
cd CubatureApp

```

Creare un ambiente virtuale:

Bash

```
python3 -m venv .venv

```

Attivare l'ambiente virtuale. Su macOS e Linux:

Bash






```
source .venv/bin/activate

```







Su Windows PowerShell:


PowerShell






```
.venv\Scripts\Activate.ps1

```







Installare le dipendenze:


Bash






```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

```







Per compilare un'applicazione standalone:


Bash






```
python -m pip install -r requirements-build.txt

```








## Avvio dell'applicazione


Dalla directory principale della repository:


Bash






```
python -m app

```







In alternativa:


Bash






```
python app/main.py

```







Il comando consigliato è:


Bash






```
python -m app

```







perché mantiene correttamente la struttura del package Python.


All'avvio viene mostrata la finestra principale dell'applicazione, composta da:



- pannello degli input;

- visualizzatore 3D;

- barra dei risultati;

- controlli per mesh, funzione e visualizzazione.




## Primo avvio e configurazione del backend Fortran


CubatureApp utilizza i sorgenti Fortran presenti nella directory:


Plain text






```
fortran/src/

```







La configurazione viene memorizzata nella directory utente:


Plain text






```
~/.OptimalPolyCuba3D/

```







Il file di configurazione principale è:


Plain text






```
~/.OptimalPolyCuba3D/config.json

```







La configurazione contiene principalmente:



- percorso dei sorgenti Fortran;

- directory di compilazione;

- ultimo file dei vertici utilizzato;

- ultimo file delle facce utilizzato;

- ultima funzione inserita;

- ultimo grado selezionato.



Il percorso predefinito dei sorgenti è:


Plain text






```
<repository>/fortran/src

```







Il backend richiede i seguenti file:


Plain text






```
TypesDef.f90
PrepCheap.f90
PolyhedronMesh.f90
triangleQuadratureGJ.f90
CubaCheap.f90
OptimalPolyCuba3D.f90

```







Il file `driverCLI.f90` viene cercato prima nella directory configurata e, se non presente, nella directory `fortran/src` della repository.



## Compilazione del backend numerico


Il backend può essere compilato in due modi.


### Compilazione automatica dalla GUI


Quando si esegue un calcolo, `FortranBackend`:



1. verifica che i sorgenti richiesti siano presenti;

2. cerca `gfortran`;

3. controlla se l'eseguibile esiste già;

4. confronta le date di modifica dei sorgenti;

5. ricompila solo se necessario;

6. esegue il driver Fortran;

7. legge i file di output generati.



La directory di build predefinita è:


Plain text






```
~/.OptimalPolyCuba3D/build/

```







### Compilazione tramite `build.py`


Per preparare un driver compilato e creare l'applicazione standalone:


Bash






```
python build.py

```







Il comando:



1. compila i moduli Fortran;

2. produce il driver `driverCLI`;

3. utilizza PyInstaller;

4. include asset, sorgenti e backend compilato;

5. genera il risultato nella directory `dist/`.



Il backend viene compilato con opzioni simili a:


Bash






```
gfortran -O2 -ffree-line-length-none ...

```








## Formato dei file della mesh


La mesh è descritta da due file separati:



1. file dei vertici;

2. file delle facce triangolari.



Il formato è un semplice file di testo `.dat`.


### File dei vertici


La prima riga contiene il numero di vertici.


Le righe successive contengono le coordinate `x`, `y`, `z`.


Esempio:


Plain text






```
4
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0

```







Formalmente:


Plain text






```
N
x1 y1 z1
x2 y2 z2
...
xN yN zN

```







### File delle facce


La prima riga contiene il numero di facce.


Ogni riga successiva contiene gli indici dei tre vertici della faccia:


Plain text






```
4
1 2 3
1 4 2
1 3 4
2 4 3

```







Formalmente:


Plain text






```
M
i1 j1 k1
i2 j2 k2
...
iM jM kM

```







Gli indici sono **1-based**, come richiesto dal codice Fortran.


Gli indici devono quindi essere compresi nell'intervallo:


Plain text






```
1 <= indice <= N

```







Le facce devono essere triangolari e la superficie dovrebbe essere chiusa e coerentemente orientata.



## Mesh di esempio


La directory `examples/` contiene alcuni domini di test:


Plain text






```
examples/
├── convex_vertex.dat
├── convex_tri.dat
├── concave_vertex.dat
├── concave_tri.dat
├── bunny_vertex.dat
└── bunny_tri.dat

```







Le coppie di file da utilizzare sono:


Plain text






```
convex_vertex.dat + convex_tri.dat
concave_vertex.dat + concave_tri.dat
bunny_vertex.dat + bunny_tri.dat

```







Per iniziare è consigliabile utilizzare la mesh convessa:


Plain text






```
examples/convex_vertex.dat
examples/convex_tri.dat

```








## Inserimento della funzione integranda


La funzione viene inserita nel campo:


Plain text






```
f(x, y, z)

```







La funzione viene interpretata da SymPy e successivamente convertita in una funzione numerica NumPy tramite `lambdify`.


Sono disponibili le variabili:


Plain text






```
x
y
z

```







Sono supportate, tra le altre, le seguenti funzioni:


Plain text






```
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







Sono inoltre disponibili:


Plain text






```
pi
e

```







### Esempi di funzioni


Funzione costante:


Plain text






```
1

```







Funzione lineare:


Plain text






```
x + y + z

```







Polinomio:


Plain text






```
x^2 + y^2 + z^2

```







Prodotto:


Plain text






```
x*y*z

```







Funzione trigonometrica:


Plain text






```
sin(x) * cos(y)

```







Esponenziale:


Plain text






```
exp(-(x^2 + y^2 + z^2))

```







Radice:


Plain text






```
sqrt(x^2 + y^2 + z^2)

```







È possibile utilizzare anche alcune forme LaTeX comuni:


Plain text






```
\sin(x)
\cos(y)
\sqrt{x^2+y^2}
\exp(-z^2)
\pi*x

```







Il parser converte automaticamente alcuni comandi LaTeX nella sintassi SymPy equivalente.


### Sicurezza del parser


L'input non viene eseguito come codice Python.


Il parser:



- utilizza una whitelist di simboli e funzioni;

- rifiuta nomi non riconosciuti;

- accetta solo le variabili `x`, `y`, `z`;

- rifiuta pattern come `import`, `eval`, `exec`, `open(` e `__`;

- genera una funzione vettorizzata NumPy.




## Grado algebrico di esattezza


Il campo **Algebraic Degree of Exactness (ADE)** controlla il grado della regola di cubatura.


Nella GUI il valore è selezionabile nell'intervallo:


Plain text






```
0 - 20

```







Un valore maggiore generalmente produce una regola con più punti di quadratura e può aumentare il costo computazionale.


Il numero di punti viene determinato dal backend Fortran a partire dal grado richiesto. La costruzione della regola e la teoria matematica sono descritte nel repository:


[OptimalPolyCubatureND](https://github.com/longoedoardo/OptimalPolyCubatureND)



## Procedura di utilizzo


### 1. Selezionare la mesh


Nel pannello **Mesh input**:



1. premere `Browse…` per il file dei vertici;

2. selezionare il file `*_vertex.dat`;

3. premere `Browse…` per il file delle facce;

4. selezionare il file `*_tri.dat`.



### 2. Inserire la funzione


Nel pannello **Integrand** inserire una funzione nelle variabili `x`, `y` e `z`.


Esempio:


Plain text






```
x^2 + y^2 + z^2

```







### 3. Selezionare il grado


Impostare il grado algebrico di esattezza, ad esempio:


Plain text






```
4

```







### 4. Inserire opzionalmente il risultato atteso


Il campo `Expected Result` è opzionale.


Se valorizzato, l'applicazione calcola automaticamente l'errore assoluto:


Plain text






```
|risultato numerico - risultato atteso|

```







### 5. Eseguire il calcolo


Premere:


Plain text






```
COMPUTE CUBATURE

```







Durante il calcolo:



- la GUI segnala lo stato dell'operazione;

- il backend Fortran viene compilato se necessario;

- vengono generati nodi e pesi;

- la funzione viene valutata sui nodi;

- l'integrale viene calcolato.



### 6. Analizzare il risultato


La barra dei risultati mostra:



- valore dell'integrale;

- errore assoluto, se è stato inserito un valore atteso;

- numero di punti di quadratura;

- grado algebrico;

- numero di vertici;

- numero di triangoli;

- tempo di calcolo;

- volume stimato dalla somma dei pesi;

- numero di pesi negativi;

- numero di pesi positivi.




## Visualizzazione 3D


Il visualizzatore è implementato in `app/visualization/viewer3d.py` usando PyVista e pyvistaqt.


Sono disponibili i seguenti controlli:



- visualizzazione o occultamento della mesh;

- modalità wireframe;

- visualizzazione degli assi;

- visualizzazione dei punti di quadratura;

- regolazione della dimensione dei punti;

- ripristino della camera isometrica.



I punti di quadratura vengono colorati in base al valore assoluto del peso associato.


La mesh viene visualizzata con:



- superficie semitrasparente;

- bordi triangolari;

- shading per la modalità superficie;

- colori distinti per la distribuzione dei pesi.




## Validazione della mesh


Prima del calcolo vengono verificati:



- presenza del file dei vertici;

- presenza del file delle facce;

- formato `N x 3` dei vertici;

- formato `M x 3` delle facce;

- coordinate numeriche finite;

- indici di vertice validi;

- facce triangolari;

- facce degeneri;

- facce duplicate;

- vertici isolati;

- edge aperti o non-manifold;

- orientazione incoerente delle facce;

- bounding box della geometria.



Gli errori bloccanti impediscono il calcolo.


Gli avvisi non bloccanti vengono utilizzati per segnalare possibili problemi della mesh, lasciando comunque la possibilità di proseguire.



## Esportazione CSV


Dopo un calcolo completato è possibile esportare i dati tramite il dialogo di esportazione.


Il file CSV può contenere:



- riepilogo dei risultati;

- informazioni sulla mesh;

- nodi e pesi di quadratura.



Il riepilogo include, quando disponibili:



- integrale;

- grado;

- numero di punti;

- tempo di calcolo;

- volume;

- numero di pesi positivi;

- numero di pesi negativi;

- errore assoluto.



La sezione dei nodi contiene:


Plain text






```
Index, X, Y, Z, Weight

```







Il file viene scritto in formato UTF-8 con BOM per una migliore compatibilità con Microsoft Excel.



## Generazione del report PDF


Il modulo `app/report_pdf.py` genera un report tecnico composto da più pagine.


Il PDF contiene:


### Pagina riepilogativa


Include:



- versione dell'applicazione;

- nome della mesh;

- funzione integranda;

- grado algebrico;

- integrale;

- valore atteso;

- errore assoluto;

- volume;

- numero di punti;

- numero di pesi positivi e negativi;

- dimensioni della mesh;

- tempo di calcolo.



### Pagina geometrica


Include una rappresentazione 3D di:



- mesh;

- nodi di quadratura;

- distribuzione dei pesi.



### Pagina dei pesi


Include:



- istogramma dei pesi;

- pesi ordinati;

- distribuzione dei valori positivi e negativi.




## Packaging con PyInstaller


Il file `build.py` prepara una versione standalone dell'applicazione.


Eseguire:


Bash






```
python build.py

```







Il comando:



- compila il driver Fortran;

- include il backend nell'applicazione;

- include gli asset grafici;

- include i dati necessari a PyVista e pyvistaqt;

- esclude moduli non necessari come Jupyter e IPython;

- genera la directory `dist/`.



Il risultato principale è:


Plain text






```
dist/CubatureApp/

```







Su macOS viene normalmente generato:


Plain text






```
dist/CubatureApp.app

```







Il packaging richiede comunque `gfortran` sulla macchina di build.



## Creazione del DMG su macOS


Dopo aver eseguito:


Bash






```
python build.py

```







è possibile creare un installer DMG con:


Bash






```
bash installer/create_macos_dmg.sh

```







Lo script:



1. verifica la presenza di `dist/CubatureApp.app`;

2. crea lo sfondo dell'installer;

3. crea un'immagine DMG temporanea;

4. inserisce l'applicazione;

5. crea il collegamento alla directory `/Applications`;

6. converte il DMG in formato compresso;

7. produce:



Plain text






```
dist/CubatureApp-Installer.dmg

```







Lo script utilizza strumenti macOS come:



- `hdiutil`;

- `osascript`;

- `Finder`.



Per generare lo sfondo è richiesto ImageMagick e il comando `magick`.



## Esecuzione diretta del driver Fortran


Il driver può essere eseguito manualmente dopo la compilazione.


Sintassi:


Bash






```
driverCLI <vertex_file> <face_file> <ade> <nodes_out> <weights_out>

```







Esempio:


Bash






```
./driverCLI \
  examples/convex_vertex.dat \
  examples/convex_tri.dat \
  4 \
  nodes.dat \
  weights.dat

```







Il file dei nodi contiene:


Plain text






```
N
x1 y1 z1
x2 y2 z2
...

```







Il file dei pesi contiene:


Plain text






```
N
w1
w2
...

```







Normalmente non è necessario utilizzare direttamente il driver, perché viene invocato automaticamente da Python.



## Gestione degli errori


Gli errori vengono convertiti in messaggi leggibili dalla GUI.


Le principali categorie sono:



- file mesh mancanti;

- formato mesh non valido;

- indici fuori intervallo;

- funzione non riconosciuta;

- sorgenti Fortran mancanti;

- compilatore `gfortran` non disponibile;

- errore di compilazione;

- errore di esecuzione del driver;

- file di output mancanti;

- numero di nodi e pesi non coincidente;

- valori `NaN` o `Inf`.



Il backend Python non considera valido un output Fortran se:



- i file attesi non sono stati prodotti;

- gli output sono vuoti;

- il numero di nodi è diverso dal numero di pesi;

- sono presenti valori non finiti.




## Risoluzione dei problemi


### `ModuleNotFoundError: No module named 'app'`


Eseguire il comando dalla directory principale:


Bash






```
cd CubatureApp
python -m app

```







### `gfortran` non trovato


Verificare:


Bash






```
which gfortran
gfortran --version

```







Su macOS:


Bash






```
brew install gcc

```







Dopo l'installazione chiudere e riaprire il terminale o l'applicazione.


### Dipendenze Python mancanti


Attivare l'ambiente virtuale e reinstallare:


Bash






```
source .venv/bin/activate
python -m pip install -r requirements.txt

```







### Il backend non trova i sorgenti Fortran


Verificare che esistano:


Plain text






```
fortran/src/TypesDef.f90
fortran/src/OptimalPolyCuba3D.f90
fortran/src/PolyhedronMesh.f90
fortran/src/CubaCheap.f90
fortran/src/PrepCheap.f90
fortran/src/triangleQuadratureGJ.f90

```







### Il calcolo fallisce con una mesh


Controllare:



- che i due file appartengano alla stessa mesh;

- che il numero dichiarato nella prima riga corrisponda alle righe successive;

- che gli indici siano 1-based;

- che ogni faccia contenga esattamente tre indici;

- che non siano presenti coordinate `NaN` o `Inf`;

- che la mesh sia chiusa e coerentemente orientata.



### PyVista non visualizza correttamente la scena


Verificare:



- disponibilità del supporto OpenGL;

- installazione di `pyvista` e `pyvistaqt`;

- esecuzione dell'applicazione in un ambiente grafico;

- aggiornamento dei driver grafici.




## Sviluppo


Per modificare l'applicazione:


Bash






```
git clone https://github.com/longoedoardo/CubatureApp.git
cd CubatureApp
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

```







Per lavorare anche sul packaging:


Bash






```
python -m pip install -r requirements-build.txt

```







L'entry point principale è:


Plain text






```
app/main.py

```







L'entry point del package è:


Plain text






```
app/__main__.py

```







Il punto di accesso consigliato è:


Bash






```
python -m app

```







Il codice Python è separato dal codice numerico Fortran. Questa separazione permette di modificare:



- la GUI senza modificare il metodo numerico;

- il parser senza modificare il visualizzatore;

- il backend di comunicazione senza modificare la GUI;

- il packaging senza modificare la pipeline numerica.




## Metodo numerico


CubatureApp utilizza il metodo implementato nel backend Fortran `OptimalPolyCuba3D`.


Il metodo riceve:



- il grado algebrico di esattezza;

- i vertici del poliedro;

- la connettività delle facce triangolari.



Restituisce:



- coordinate dei nodi di quadratura;

- pesi associati ai nodi.



La GUI valuta poi la funzione integranda sui nodi e calcola:


Plain text






```
integrale ≈ Σᵢ wᵢ f(xᵢ, yᵢ, zᵢ)

```







Per la descrizione teorica completa del metodo consultare:


[OptimalPolyCubatureND](https://github.com/longoedoardo/OptimalPolyCubatureND)



## Licenza


Il progetto è distribuito secondo la licenza presente nel file:


Plain text






```
LICENSE

```







Consultare il file per le condizioni complete di utilizzo, modifica e distribuzione.



##