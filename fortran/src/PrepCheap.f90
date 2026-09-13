MODULE PrepCheap

    IMPLICIT NONE

    CONTAINS

    SUBROUTINE cub_gausscheb_tens3D(deg, xyzw)

    USE TypesDef, ONLY: dp, PI
    
    !*******************************************************************************
    ! Calcola i punti e i pesi per l'integrazione numerica in 3D.
    ! Utilizza una griglia a prodotto tensoriale basata sui nodi di Gauss-Chebyshev.
    !*******************************************************************************
        INTEGER, INTENT(IN)                     :: deg
        REAL(dp), ALLOCATABLE, INTENT(OUT)      :: xyzw(:,:)
        INTEGER                                 :: n,n3,i,j,k, idx
        REAL(dp), ALLOCATABLE                   :: x(:), w(:)

        n = (deg+2)/2
        n3 = n**3

        IF (ALLOCATED(xyzw)) DEALLOCATE(xyzw)
        ALLOCATE(xyzw(n3, 4))

        IF (ALLOCATED(x)) DEALLOCATE(x)
        ALLOCATE(x(n))

        IF (ALLOCATED(w)) DEALLOCATE(w)
        ALLOCATE(w(n))

        DO i = 1,n
            x(i) = cos( ((2.0_dp * i - 1.0_dp) * PI) / (2.0_dp * n) )
            w(i) = PI / REAL(n, dp)
        END DO

        idx = 1
        DO k = 1, n ! Z
            DO j = 1, n ! Y
                DO i = 1, n ! X
                    
                    xyzw(idx, 1) = x(i)
                    xyzw(idx, 2) = x(j)
                    xyzw(idx, 3) = x(k)
                    xyzw(idx, 4) = w(i) * w(j) * w(k) ! W3 e' dato dal prodotto dei pesi
                    
                    idx = idx + 1
                    
                END DO
            END DO
        END DO



    END SUBROUTINE cub_gausscheb_tens3D







    SUBROUTINE mono_next_grlex(m, x)

    !**************************************************************************
    ! Calcola il monomio successivo in ordinamento grlex.
    !**************************************************************************
    
        INTEGER, INTENT(IN)    :: m
        INTEGER, INTENT(INOUT) :: x(m)

        INTEGER                :: i, j, t, im1

        ! Mi assicuro che M >= 1
        IF (m < 1) THEN
            WRITE(*,*) ' '
            WRITE(*,*) 'MONO_NEXT_GRLEX - Fatal error!'
            WRITE(*,*) '  M < 1, m = ', m
            ERROR STOP 'MONO_NEXT_GRLEX - Fatal error!'
        END IF

        ! Mi assicuro che X(I) => 0
        DO i = 1, m
            IF (x(i) < 0) THEN
                WRITE(*,*) ' '
                WRITE(*,*) 'MONO_NEXT_GRLEX - Fatal error!'
                WRITE(*,*) '  X(I) < 0 presso indice ', i
                ERROR STOP 'MONO_NEXT_GRLEX - Fatal error!'
            END IF
        END DO

        ! Trova I, l'indice dell'elemento più a destra diverso da zero
        i = 0
        DO j = m, 1, -1
            IF (x(j) > 0) THEN
                i = j
                EXIT
            END IF
        END DO

        IF (i == 0) THEN
            x(m) = 1
            RETURN
        ELSE IF (i == 1) THEN
            t = x(1) + 1
            im1 = m
        ELSE 
            t = x(i)
            im1 = i - 1
        END IF

        x(i) = 0
        x(im1) = x(im1) + 1
        x(m) = x(m) + t - 1

    END SUBROUTINE mono_next_grlex

END MODULE PrepCheap