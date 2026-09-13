MODULE OptimalPolyCuba3D_Module

USE TypesDef

IMPLICIT NONE

CONTAINS

!**********************************************************************
!
! SUBROUTINE OptimalPolyCuba3D(ade, vertices, facets, XYZ, W)
!
! Calcola un'approssimazione numerica di un integrale di volume
! tridimensionale su un dominio poliedrico rappresentato mediante
! una mesh superficiale triangolare chiusa.
!
! La regola di cubatura è costruita combinando una base di Chebyshev
! tensoriale shape-independent con i momenti shape-dependent calcolati
! a partire dalla rappresentazione superficiale del dominio poliedrico.
!
!**********************************************************************
!
!   INPUTS:
!   - ade:
!       Grado polinomiale totale massimo della regola di cubatura.
!
!   - vertices:
!       Matrice N x 3 contenente le coordinate cartesiane dei vertici
!       della mesh. Ogni riga rappresenta un vertice [x_i, y_i, z_i].
!
!   - facets:
!       Matrice M x 3 contenente la connettività della mesh superficiale
!       triangolare. Ogni riga contiene gli indici dei tre vertici che
!       definiscono una faccia triangolare.
!
!   OUTPUT:
!   - XYZ:
!       Nodi di quadratura
!   - W:
!       Pesi relativi ai nodi di quadratura
!
!**************************************************************************
!
!   Autore:
!       Edoardo Longo, Università degli Studi di Verona
!
!   Data:
!       Settembre 2026
!
!**************************************************************************

SUBROUTINE OptimalPolyCuba3D(ade, vertices, facets, XYZ, W)

USE PrepCheap
USE CubaCheap

IMPLICIT NONE

!**********************************************************************
! Argomenti
!**********************************************************************
INTEGER,               INTENT(IN)  :: ade
REAL(dp),              INTENT(IN)  :: vertices(:,:)
INTEGER,               INTENT(IN)  :: facets(:,:)
REAL(dp), ALLOCATABLE, INTENT(OUT) :: XYZ(:,:)
REAL(dp), ALLOCATABLE, INTENT(OUT) :: W(:)
!**********************************************************************
! Variabili locali
!**********************************************************************
INTEGER :: k

!**********************************************************************
! INIZIO PARTE SHAPE-INDEPENDENT
!**********************************************************************

! Griglia tensoriale di Gauss-Chebyshev sul cubo di riferimento [-1,1]^3
CALL cub_gausscheb_tens3D(2*ade, XYZW_tens_ref)

! Dimensione dello spazio polinomiale di grado totale <= ade
N = SIZE(XYZW_tens_ref, 1)
N_mom = ((ade + 1) * (ade + 2) * (ade + 3)) / 6

! Indici (i,j,k) dei monomi tensoriali di Chebyshev, ordinamento GRLEX
IF (ALLOCATED(chebyshev_indices)) THEN
    DEALLOCATE(chebyshev_indices)
END IF
ALLOCATE(chebyshev_indices(N_mom,3))
chebyshev_indices(1,:) = 0
DO k = 2, N_mom
    ind_curr = chebyshev_indices(k-1,:)
    CALL mono_next_grlex(3, ind_curr)
    chebyshev_indices(k,:) = ind_curr
END DO

IF (ALLOCATED(X)) DEALLOCATE(X)
ALLOCATE(X(N,3))

X(:,1) = XYZW_tens_ref(:,1)
X(:,2) = XYZW_tens_ref(:,2)
X(:,3) = XYZW_tens_ref(:,3)

! Matrice di Vandermonde-Chebyshev 3D sui nodi della griglia di riferimento
CALL dCHEBVAND(ade, X, chebyshev_indices, V_ref)

! Coefficienti di normalizzazione della base di Chebyshev tensoriale
CALL tenscheb_norm2sq(chebyshev_indices, coeffs)

!**********************************************************************
! INIZIO PARTE SHAPE-DEPENDENT
!**********************************************************************

IF (ALLOCATED(bbox)) DEALLOCATE(bbox)
ALLOCATE(bbox(6))

bbox(1) = MINVAL(vertices(:,1))
bbox(2) = MAXVAL(vertices(:,1))
bbox(3) = MINVAL(vertices(:,2))
bbox(4) = MAXVAL(vertices(:,2))
bbox(5) = MINVAL(vertices(:,3))
bbox(6) = MAXVAL(vertices(:,3))

! % Momenti della base sul poliedro (teorema della divergenza sulle facce)
CALL chebyshev_moments_polyhedron(vertices, facets, ade, chebyshev_indices, bbox, moments_ch)

! % Riscalamento della griglia di riferimento sulla bounding box reale
CALL scale_rule(XYZW_tens_ref, bbox, XYZW_tens)

! Pesi di cubatura ottenuti ricombinando la regola di riferimento
IF (ALLOCATED(W)) DEALLOCATE(W)
ALLOCATE(W(N))
DO k = 1, N
    W(k) = XYZW_tens(k,4) * DOT_PRODUCT(V_ref(k,:), moments_ch / coeffs)
END DO
IF (ALLOCATED(XYZ)) DEALLOCATE(XYZ)
ALLOCATE(XYZ(N,3))
XYZ(:,1) = XYZW_tens(:,1)
XYZ(:,2) = XYZW_tens(:,2)
XYZ(:,3) = XYZW_tens(:,3)

END SUBROUTINE OptimalPolyCuba3D

END MODULE OptimalPolyCuba3D_Module