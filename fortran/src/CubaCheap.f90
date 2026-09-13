MODULE CubaCheap

   USE triangleQuadratureGJ
   USE TypesDef

   IMPLICIT NONE

   CONTAINS

   SUBROUTINE dCHEBVAND(deg, X, duples, V)

   !*******************************************************************************
   ! Calcola la matrice di Chebyshev-Vandermonde per il grado totale "deg"
   ! sui punti X (m x d), usando la base tensoriale indicizzata da "duples"
   ! (N x d), shiftata sul cubo unitario [-1,1]^d.
   !*******************************************************************************

      IMPLICIT NONE
      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      INTEGER, INTENT(IN)                                   :: deg
      REAL(dp), INTENT(IN)                                  :: X(:,:)
      INTEGER, INTENT(IN)                                   :: duples(:,:) 
      REAL(dp), ALLOCATABLE, INTENT(OUT)                    :: V(:,:)
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      INTEGER                                               :: m, d, N, i, k, col, g
      REAL(dp)                                              :: min_val, max_val
      REAL(dp), ALLOCATABLE                                 :: dbox(:,:)
      REAL(dp), ALLOCATABLE                                 :: map(:,:)
      REAL(dp), ALLOCATABLE                                 :: T_dim(:,:,:)
      !*******************************************************************************

      m = SIZE(X,1)
      d = SIZE(X,2)
      N = SIZE(duples,1)

      ! dbox: cubo unitario [-1,1] per ogni dimensione 
      ALLOCATE(dbox(2,d))
      dbox(1,:) = -1.0_dp
      dbox(2,:) =  1.0_dp

      ! Porto tutto in [-1,1]
      ALLOCATE(map(m,d))
      DO i = 1, d
         min_val = dbox(1,i)
         max_val = dbox(2,i)
         map(:,i) = (2.0_dp * X(:,i) - max_val - min_val) / (max_val - min_val)
      END DO

      ALLOCATE(V(m,N)) ! Inizializzo la matrice di Vandermonde
      V = 1.0_dp

      ! Costruisco i polinomi di Chebyshev 1D per ciascuna dimensione tramite ricorrenza
      ALLOCATE(T_dim(m, 0:deg, d))
      DO k = 1, d
         T_dim(:,0,k) = 1.0_dp ! T0(x) = 1

         IF (deg >= 1) THEN
            T_dim(:,1,k) = map(:,k) ! T1(x) = x

            DO g = 2, deg
               T_dim(:,g,k) = 2.0_dp * map(:,k) * T_dim(:,g-1,k) - T_dim(:,g-2,k)
            END DO
         END IF

         ! Prodotto tensoriale, aggiorna ogni colonna di V
         DO col = 1, N
            V(:,col) = V(:,col) * T_dim(:, duples(col,k), k)
         END DO

      END DO
      DEALLOCATE(dbox, map, T_dim)
  
   END SUBROUTINE dCHEBVAND


   

   SUBROUTINE tenscheb_norm2sq(chebyshev_indices, coeffs)

   !*******************************************************************************
   ! Calcola la norma quadra (L^2 pesata) di ciascun polinomio ortogonale 
   ! di Chebyshev tensoriale in 3D, utilizzato come fattore di normalizzazione.
   !*******************************************************************************

      IMPLICIT NONE

      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      INTEGER, INTENT(IN)             :: chebyshev_indices(:, :)
      REAL(dp), ALLOCATABLE, INTENT(OUT) :: coeffs(:)
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      INTEGER                         :: i, n
      REAL(dp)                        :: non_zero_counter
      !*******************************************************************************

      n = size(chebyshev_indices, 1)

      IF(ALLOCATED(coeffs))  DEALLOCATE(coeffs)
      ALLOCATE(coeffs(n))

      DO i = 1, n
         non_zero_counter = 0.0_dp
         IF(chebyshev_indices(i, 1) /= 0)   non_zero_counter = non_zero_counter + 1.0_dp
         IF(chebyshev_indices(i, 2) /= 0)   non_zero_counter = non_zero_counter + 1.0_dp
         IF(chebyshev_indices(i, 3) /= 0)   non_zero_counter = non_zero_counter + 1.0_dp
        
         coeffs(i) = (PI**3.0_dp) / (2.0_dp**(non_zero_counter))
      END DO

   END SUBROUTINE tenscheb_norm2sq

   
   SUBROUTINE chebyshev_moments_polyhedron(vertices, facets, ade, chebyshev_indices, dbox, moments)

   !*******************************************************************************
   ! Calcola i momenti di Chebyshev sul poliedro 3D utilizzando il teorema della divergenza. 
   ! Converte l'integrale di volume in un integrale di superficie (somma sui triangoli della 
   ! mesh di superficie), valutando la quadratura numerica su ciascuna faccia triangolare.
   !*******************************************************************************

      IMPLICIT NONE

      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      REAL(dp), INTENT(IN)    :: vertices(:, :)
      INTEGER, INTENT(IN)    :: facets(:, :)
      INTEGER, INTENT(IN)    :: ade
      INTEGER, INTENT(IN)    :: chebyshev_indices(:, :)
      REAL(dp), INTENT(IN)    :: dbox(6)
      REAL(dp), INTENT(OUT), ALLOCATABLE :: moments(:)
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      INTEGER                :: num_indici, n_facce, k
      INTEGER                :: v1_idx, v2_idx, v3_idx
      INTEGER                :: nGP
      REAL(dp) :: A(3), B(3), C(3)
      REAL(dp) :: V_face(3,3)
      REAL(dp) :: vec1(3), vec2(3), cp(3), area2
      REAL(dp), PARAMETER     :: tol = 1.0d-14
      REAL(dp), ALLOCATABLE   :: XYZW(:, :)     
      REAL(dp), ALLOCATABLE   :: WV_CUB(:)      
      REAL(dp)                :: norm_ext(3)    
      REAL(dp), ALLOCATABLE   :: chebyshev_moms(:, :)
      REAL(dp), ALLOCATABLE   :: moms_facet_raw(:)
      !*******************************************************************************

      num_indici = SIZE(chebyshev_indices, 1)
      n_facce = SIZE(facets, 1)

      ! Numero di punti di Gauss-Jacobi 1D necessari per integrare esattamente
      ! sul triangolo un polinomio di grado (ade+1) (il grado sale di 1 per
      ! effetto della primitiva usata nel teorema della divergenza): con nGP
      ! punti la formula e' esatta fino al grado 2*nGP-1, quindi basta
      ! nGP = ceil((ade+2)/2).
      nGP = CEILING((ade + 2.0_dp)/2.0_dp)

      ALLOCATE(chebyshev_moms(num_indici, n_facce))
      chebyshev_moms = 0.0_dp

      DO k = 1, n_facce
         v1_idx = facets(k, 1)
         v2_idx = facets(k, 2)
         v3_idx = facets(k, 3)

         A = vertices(v1_idx, :)
         B = vertices(v2_idx, :)
         C = vertices(v3_idx, :)

         V_face(1,:) = A
         V_face(2,:) = B
         V_face(3,:) = C

         vec1 = B - A
         vec2 = C - A
      
         cp(1) = vec1(2) * vec2(3) - vec1(3) * vec2(2)
         cp(2) = vec1(3) * vec2(1) - vec1(1) * vec2(3)
         cp(3) = vec1(1) * vec2(2) - vec1(2) * vec2(1)
         area2 = SQRT(SUM(cp**2))

         IF (area2 <= tol) THEN
            chebyshev_moms(:, k) = 0.0_dp
            CYCLE
         END IF

         norm_ext = cp / area2

         CALL shiftingTriangleQuadrature(V_face, nGP, XYZW, WV_CUB)

         CALL cubature_tens_chebyshev_facet_V(XYZW, WV_CUB, chebyshev_indices, dbox, moms_facet_raw)

         chebyshev_moms(:, k) = norm_ext(1) * moms_facet_raw

         IF (ALLOCATED(moms_facet_raw)) DEALLOCATE(moms_facet_raw)
         IF (ALLOCATED(XYZW)) DEALLOCATE(XYZW)
         IF (ALLOCATED(WV_CUB)) DEALLOCATE(WV_CUB)
      END DO

      moments = SUM(chebyshev_moms, DIM=2)

      DEALLOCATE(chebyshev_moms)

   END SUBROUTINE chebyshev_moments_polyhedron

   SUBROUTINE cubature_tens_chebyshev_facet_V(nodes, weights, chebyshev_indices, dbox, chebyshev_moms)

   !*******************************************************************************
   ! Calcola i momenti di Chebyshev su una faccia triangolare 3D 
   !*******************************************************************************

      IMPLICIT NONE

      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      REAL(dp), INTENT(IN)    :: nodes(:, :)        
      REAL(dp), INTENT(IN)    :: weights(:)         
      INTEGER, INTENT(IN)    :: chebyshev_indices(:, :) 
      REAL(dp), INTENT(IN)    :: dbox(6)
      REAL(dp), ALLOCATABLE, INTENT(OUT)   :: chebyshev_moms(:)  
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      INTEGER                :: n, m, deg_max, c, iv
      REAL(dp)                :: B1
      REAL(dp), ALLOCATABLE   :: XN(:), YN(:), ZN(:)
      REAL(dp), ALLOCATABLE   :: TX(:, :), TY(:, :), TZ(:, :)
      REAL(dp), ALLOCATABLE   :: IntX(:, :)
      INTEGER, ALLOCATABLE   :: idx_i(:), idx_j(:), idx_k(:)
      REAL(dp), ALLOCATABLE   :: IntX_cols(:, :), TY_cols(:, :), TZ_cols(:, :)
      REAL(dp), ALLOCATABLE   :: TYTZ(:, :), F(:, :)
      REAL(dp), ALLOCATABLE   :: w(:)
      INTEGER, ALLOCATABLE   :: i_vec(:)
      !*******************************************************************************

      n = SIZE(nodes, 1)
      m = SIZE(chebyshev_indices, 1)

      ALLOCATE(XN(n), YN(n), ZN(n))
      ALLOCATE(w(n))

      XN = (nodes(:, 1) - (dbox(1) + dbox(2)) / 2.0_dp) / ((dbox(2) - dbox(1)) / 2.0_dp)
      YN = (nodes(:, 2) - (dbox(3) + dbox(4)) / 2.0_dp) / ((dbox(4) - dbox(3)) / 2.0_dp)
      ZN = (nodes(:, 3) - (dbox(5) + dbox(6)) / 2.0_dp) / ((dbox(6) - dbox(5)) / 2.0_dp)
    
      B1 = (dbox(2) - dbox(1)) / 2.0_dp
      w = weights(:)

      deg_max = MAXVAL(chebyshev_indices(:, 1))

      ALLOCATE(TX(n, deg_max + 2))
      ALLOCATE(TY(n, deg_max + 1))
      ALLOCATE(TZ(n, deg_max + 1))

      CALL chebpolys(deg_max + 1, XN, TX)
      CALL chebpolys(deg_max, YN, TY)
      CALL chebpolys(deg_max, ZN, TZ)

      ALLOCATE(IntX(n, deg_max + 1))
      IntX = 0.0_dp
    
      IntX(:, 1) = XN 

      IF (deg_max >= 1) THEN
         IntX(:, 2) = (XN**2) / 2.0_dp
      END IF

      IF (deg_max >= 2) THEN
         ALLOCATE(i_vec(deg_max - 1))
         DO c = 1, deg_max - 1
            i_vec(c) = c + 1  
         END DO
         
         DO c = 1, SIZE(i_vec)
            iv = i_vec(c)
            IntX(:, iv + 1) = TX(:, iv+2) / (2.0_dp*(iv+1)) - TX(:, iv) / (2.0_dp*(iv-1))
         END DO
         DEALLOCATE(i_vec)
      END IF

      ALLOCATE(idx_i(m), idx_j(m), idx_k(m))
      idx_i = chebyshev_indices(:, 1) + 1
      idx_j = chebyshev_indices(:, 2) + 1
      idx_k = chebyshev_indices(:, 3) + 1

      ALLOCATE(IntX_cols(n, m), TY_cols(n, m), TZ_cols(n, m))
      DO c = 1, m
         IntX_cols(:, c) = IntX(:, idx_i(c))
         TY_cols(:, c)   = TY(:,   idx_j(c))
         TZ_cols(:, c)   = TZ(:,   idx_k(c))
      END DO

      ALLOCATE(TYTZ(n, m))
      TYTZ = TY_cols * TZ_cols

      ALLOCATE(F(n, m))
      F = (B1 * IntX_cols) * TYTZ

      IF (ALLOCATED(chebyshev_moms)) DEALLOCATE(chebyshev_moms)
      ALLOCATE(chebyshev_moms(m))

      DO c = 1, m
         chebyshev_moms(c) = SUM(w * F(:, c))
      END DO

      DEALLOCATE(XN, YN, ZN, w, TX, TY, TZ, IntX, idx_i, idx_j, idx_k, IntX_cols, TY_cols, TZ_cols, TYTZ, F)

   END SUBROUTINE cubature_tens_chebyshev_facet_V

   SUBROUTINE chebpolys(deg, x, T)

   !*******************************************************************************
   ! Calcola i polinomi di Chebyshev di prima specie T_j(x) fino al grado "deg" 
   ! valutati su un vettore di punti "x", utilizzando la formula di ricorrenza 
   ! a tre termini e memorizzando i risultati in una matrice T.
   !*******************************************************************************

      IMPLICIT NONE

      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      INTEGER, INTENT(IN)    :: deg
      REAL(dp), INTENT(IN)    :: x(:)
      REAL(dp), INTENT(OUT)   :: T(:, :)
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      INTEGER                :: n, j
      REAL(dp), ALLOCATABLE   :: t0(:), t1(:), t2(:)
      !*******************************************************************************

      n = SIZE(x)

      ALLOCATE(t0(n), t1(n), t2(n))

      t0 = 1.0_dp
      T(:, 1) = t0

      IF (deg >= 1) THEN
         t1 = x
         T(:, 2) = t1
      END IF

      DO j = 2, deg
         t2 = 2.0_dp * x * t1 - t0
         T(:, j + 1) = t2
         t0 = t1
         t1 = t2
      END DO

      DEALLOCATE(t0, t1, t2)

   END SUBROUTINE chebpolys

   SUBROUTINE scale_rule(XYZW_tens_ref, dbox, XYZW_tens)

   !*******************************************************************************
   ! Scala le coordinate dei punti di quadratura di una regola tensoriale 
   ! dal dominio di riferimento standard $[-1, 1]^3$ al bounding box geometrico 
   ! effettivo del dominio, lasciando inalterati i pesi di cubatura.
   !*******************************************************************************

      IMPLICIT NONE

      !*******************************************************************************
      ! Argomenti
      !*******************************************************************************
      REAL(dp), INTENT(IN)  :: XYZW_tens_ref(:,:)
      REAL(dp), INTENT(IN)  :: dbox(6)
      REAL(dp), ALLOCATABLE, INTENT(OUT) :: XYZW_tens(:,:)
      !*******************************************************************************
      ! Variabili locali
      !*******************************************************************************
      REAL(dp) :: a, b
      !*******************************************************************************
      
      IF (ALLOCATED(XYZW_tens)) DEALLOCATE(XYZW_tens)
      ALLOCATE(XYZW_tens(SIZE(XYZW_tens_ref, 1), SIZE(XYZW_tens_ref, 2)))

      ! X dimension scaling
      a = dbox(1); b = dbox(2)
      XYZW_tens(:,1) = (a + b) / 2.0_dp + ((b - a) / 2.0_dp) * XYZW_tens_ref(:,1)

      ! Y dimension scaling
      a = dbox(3); b = dbox(4)
      XYZW_tens(:,2) = (a + b) / 2.0_dp + ((b - a) / 2.0_dp) * XYZW_tens_ref(:,2)

      ! Z dimension scaling
      a = dbox(5); b = dbox(6)
      XYZW_tens(:,3) = (a + b) / 2.0_dp + ((b - a) / 2.0_dp) * XYZW_tens_ref(:,3)

      ! I pesi rimangono inalterati
      IF (SIZE(XYZW_tens_ref, 2) >= 4) THEN
         XYZW_tens(:,4) = XYZW_tens_ref(:,4)
      END IF

   END SUBROUTINE scale_rule

END MODULE CubaCheap