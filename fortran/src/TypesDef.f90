MODULE TypesDef

IMPLICIT NONE

!**********************************************************************
! Definizione della precisione doppia (dp)
!**********************************************************************
INTEGER, PARAMETER :: dp = KIND(0.0d0)

!**********************************************************************
! Costanti matematiche
!**********************************************************************
REAL(dp), PARAMETER :: PI = 3.14159265358979323846_dp

!**********************************************************************
! Parametri del metodo di cubatura
!**********************************************************************
INTEGER :: N, N_mom
INTEGER :: ind_curr(3)

!**********************************************************************
! Variabili
!**********************************************************************
REAL(dp), ALLOCATABLE :: XYZW_tens_ref(:,:)
REAL(dp), ALLOCATABLE :: X(:,:)
REAL(dp), ALLOCATABLE :: XYZW_tens(:,:)
REAL(dp), ALLOCATABLE :: fXYZW(:)

REAL(dp) :: I_risultato

INTEGER, ALLOCATABLE :: chebyshev_indices(:,:)

REAL(dp), ALLOCATABLE :: bbox(:)

REAL(dp), ALLOCATABLE :: XYZW_ref(:,:)

REAL(dp), ALLOCATABLE :: XYZW(:,:)

REAL(dp), ALLOCATABLE :: V_ref(:,:)
REAL(dp), ALLOCATABLE :: coeffs(:)
REAL(dp), ALLOCATABLE :: moments_ch(:)

END MODULE TypesDef