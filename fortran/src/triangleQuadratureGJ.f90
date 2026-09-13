MODULE triangleQuadratureGJ

  USE TypesDef

  !**********************************************************************
  ! Quadratura di Gauss-Jacobi su un triangolo generico (3D), ottenuta
  ! mediante shifting affine dei punti/pesi calcolati sul triangolo di
  ! riferimento (0,0), (1,0), (0,1) tramite prodotto conico di formule
  ! 1D di Gauss-Jacobi.
  !**********************************************************************

  IMPLICIT NONE

CONTAINS

  SUBROUTINE shiftingTriangleQuadrature(V, nGP, P, W)

    IMPLICIT NONE
    !**********************************************************************    
    ! Argomenti
    !**********************************************************************                                                    
    REAL(dp),    INTENT(IN)                  :: V(3,3)  ! Vertici del triangolo, per riga
    INTEGER, INTENT(IN)                      :: nGP     ! N. punti di Gauss-Jacobi 1D
    REAL(dp),    ALLOCATABLE, INTENT(OUT)    :: P(:,:)  ! Punti quadratura reali (n_points,3)
    REAL(dp),    ALLOCATABLE, INTENT(OUT)    :: W(:)    ! Pesi quadratura reali (n_points)
    !**********************************************************************
    ! Variabili locali                             
    !**********************************************************************                        
    INTEGER                                  :: i, n_points
    REAL(dp)                                 :: Area
    REAL(dp)                                 :: A(3), B(3)
    REAL(dp), ALLOCATABLE                    :: P_std(:,:), W_std(:)   ! Punti e pesi sul triangolo di riferimento
    !**********************************************************************

    n_points = nGP * nGP

    ALLOCATE(P_std(2, n_points))
    ALLOCATE(W_std(n_points))

    ! Punti e pesi sul triangolo di riferimento (0,0), (1,0), (0,1)
    CALL TriangleQuadraturePoints(P_std, W_std, n_points, nGP)

    IF (ALLOCATED(P)) DEALLOCATE(P)
    ALLOCATE(P(n_points, 3))

    IF (ALLOCATED(W)) DEALLOCATE(W)
    ALLOCATE(W(n_points))

    ! Lati del triangolo reale a partire dal primo vertice
    A = V(2,:) - V(1,:)
    B = V(3,:) - V(1,:)

    ! Shifting affine dei punti dal triangolo di riferimento a quello reale.
    ! NB: P_std ha shape (2, n_points) -> coordinata (riga), punto (colonna)
    DO i = 1, n_points
       P(i,:) = V(1,:) + P_std(1,i)*A + P_std(2,i)*B
    END DO

    ! Area del triangolo reale: metà del modulo del prodotto vettoriale A x B
    Area = 0.5 * SQRT( (A(2)*B(3) - A(3)*B(2))**2 &
                      + (A(3)*B(1) - A(1)*B(3))**2 &
                      + (A(1)*B(2) - A(2)*B(1))**2 )

    ! I pesi standard sommano a 0.5 (area del triangolo di riferimento):
    ! si riscalano quindi con il rapporto Area / 0.5 = 2 * Area
    W = 2.0 * Area * W_std

    DEALLOCATE(P_std, W_std)

  END SUBROUTINE shiftingTriangleQuadrature


  SUBROUTINE TriangleQuadraturePoints(IntGaussP,IntGaussW,nIntGP,nGP) 

   IMPLICIT NONE

   !**********************************************************************
   ! Argomenti
   !**********************************************************************
   INTEGER, INTENT(IN) :: nGP
   INTEGER, INTENT(OUT) :: nIntGP
   REAL(dp), INTENT(OUT) :: IntGaussP(2, nGP*nGP)
   REAL(dp), INTENT(OUT) :: IntGaussW(nGP*nGP)

   !**********************************************************************
   ! Variabili locali
   !**********************************************************************
   INTEGER :: i, j
   INTEGER :: iIntGP

   REAL(dp) :: tol
   REAL(dp) :: mu1(nGP)
   REAL(dp) :: mu2(nGP)
   REAL(dp) :: A1(nGP)
   REAL(dp) :: A2(nGP)
    tol = 1.0 / (10.0**(PRECISION(1.0)-2) )                                   
    !**********************************************************************                                                                         
    ! Quadrature points are defined by the conical product of 1D Gauss-Jacobi 
    ! formulas with nGP quadrature points. See Stround, p. 28ff for details.
    ! **********************************************************************
    nIntGP = nGP*nGP 
    ! 
    CALL gaujac(mu1,A1,nGP,1.0_dp,0.0_dp)     ! Get the Gauss-Jacobi positions and weights
    CALL gaujac(mu2,A2,nGP,0.0_dp,0.0_dp)     ! Get the Gauss-Jacobi positions and weights
    !
    mu1(:) = 0.5*mu1(:) + 0.5       ! Shift and rescale positions, because Stroud
    A1(:)  = 0.5**2*A1(:)           ! integrates over the interval [0,1] and
    mu2(:) = 0.5*mu2(:) + 0.5       ! the function gaujac of the num. recipes
    A2(:)  = 0.5**1*A2(:)           ! integrates over the interval [-1,1].
    !
    iIntGP = 1
    DO i = 1, nGP 
       DO j = 1, nGP
          intGaussP(1,iIntGP) = mu1(i)
          intGaussP(2,iIntGP) = mu2(j)*(1.-mu1(i))
          intGaussW(iIntGP)   = A1(i)*A2(j)      
          iIntGP              = iIntGP + 1
       ENDDO
    ENDDO
    !
    IF (     ((ABS(SUM(intGaussW(:)))-0.5).GT.tol)  ) THEN
       WRITE(*,*) '| Integration points calculated with conical product.'
       WRITE(*,*) '| Number of integration points is  ', nIntGP
       WRITE(*,*) '| SUM of Weights is ', SUM(intGaussW(:)), ' and must be 0.5! '
    END IF
    ! 
  END SUBROUTINE TriangleQuadraturePoints


  PURE ELEMENTAL FUNCTION gammln(xx)
  !**********************************************************************
  IMPLICIT NONE
  !**********************************************************************
  REAL(dp)             :: gammln,xx
  INTEGER          :: j
  REAL(dp)             :: ser,stp,tmp,x,y,cof(6)
  PARAMETER(stp=  2.5066282746310005_dp  )
  PARAMETER(cof= (/           &
       76.18009172947146_dp    , &
       -86.50532032941677_dp   , &
       24.01409824083091_dp    , &
       -1.231739572450155_dp   , &
       .1208650973866179e-2_dp , &
       -.5395239384953e-5_dp    /)       )
  !**********************************************************************
  INTENT(IN) :: xx
  !**********************************************************************

  x   = xx
  y   = x
  tmp = x+5.5d0
  tmp = (x+0.5d0)*LOG(tmp)-tmp
  ser = 1.000000000190015d0

  DO  j=1,6
     y  = y+1.d0
     ser= ser+cof(j)/y
  END DO

  gammln=tmp+LOG(stp*ser/x)

  RETURN

END FUNCTION gammln

PURE SUBROUTINE gauleg(x1,x2,x,w,n)
  !**********************************************************************
  IMPLICIT NONE
  !**********************************************************************
  INTEGER     ::  n
  REAL(dp)        :: x1,x2,x(n),w(n)
  REAL(dp)        :: EPS
  INTEGER     :: i,j,m
  REAL(dp)        :: p1,p2,p3,pp,xl,xm,z,z1
  !**********************************************************************
  INTENT(IN)  :: x1,x2,n
  INTENT(OUT) :: x,w
  !**********************************************************************
  PARAMETER (EPS=3.E-14)
  !**********************************************************************

  m  = (n+1)/2
  xm = 0.5*(x2+x1)
  xl = 0.5*(x2-x1)

  DO i=1,m
     z = COS(3.141592654*(i-.25)/(n+.5))
1 CONTINUE
     p1 = 1.
     p2 = 0.
     DO j = 1,n
        p3 = p2
        p2 = p1
        p1 = ((2.*j-1.)*z*p2-(j-1.)*p3)/j
     END DO
     pp = n*(z*p1-p2)/(z*z-1.)
     z1 = z
     z  = z1-p1/pp
     IF(ABS(z-z1).GT.EPS)GOTO 1
     x(i)    = xm-xl*z
     x(n+1-i)= xm+xl*z
     w(i)    = 2.*xl/((1.-z*z)*pp*pp)
     w(n+1-i)= w(i)
  END DO
  RETURN
END SUBROUTINE gauleg

SUBROUTINE gaujac(x,w,n,alf,bet)
  !**********************************************************************
  INTEGER ::  MAXIT
  INTEGER, INTENT(IN) :: n
   REAL(dp), INTENT(IN) :: alf, bet
   REAL(dp), INTENT(OUT) :: x(n), w(n)
  REAL(dp)    :: EPS
  INTEGER :: i,its,j,pr
  REAL(dp)    :: alfbet,an,bn,r1,r2,r3
  REAL(dp)    :: a,b,c,p1,p2,p3,pp,temp,z,z1
  REAL(dp)    :: test
  !**********************************************************************
  test = 1. 
  MAXIT=50
  pr = PRECISION(test)
  eps = 0.1**REAL(pr)
  DO i=1,n
     IF(i.EQ.1)THEN
        an=alf/n
        bn=bet/n
        r1=(1.+alf)*(2.78/(4.+n*n)+.768*an/n)
        r2=1.+1.48*an+.96*bn+.452*an*an+.83*an*bn
        z=1.-r1/r2
     ELSE IF(i.EQ.2)THEN
        r1=(4.1+alf)/((1.+alf)*(1.+.156*alf))
        r2=1.+.06*(n-8.)*(1.+.12*alf)/n
        r3=1.+.012*bet*(1.+.25*ABS(alf))/n
        z=z-(1.-z)*r1*r2*r3
     ELSE IF(i.EQ.3)THEN
        r1=(1.67+.28*alf)/(1.+.37*alf)
        r2=1.+.22*(n-8.)/n
        r3=1.+8.*bet/((6.28+bet)*n*n)
        z=z-(x(1)-z)*r1*r2*r3
     ELSE IF(i.EQ.n-1)THEN
        r1=(1.+.235*bet)/(.766+.119*bet)
        r2=1./(1.+.639*(n-4.)/(1.+.71*(n-4.)))
        r3=1./(1.+20.*alf/((7.5+alf)*n*n))
        z=z+(z-x(n-3))*r1*r2*r3
     ELSE IF(i.EQ.n)THEN
        r1=(1.+.37*bet)/(1.67+.28*bet)
        r2=1./(1.+.22*(n-8.)/n)
        r3=1./(1.+8.*alf/((6.28+alf)*n*n))
        z=z+(z-x(n-2))*r1*r2*r3
     ELSE
        z=3.*x(i-1)-3.*x(i-2)+x(i-3)
     ENDIF
     alfbet=alf+bet
     DO its=1,MAXIT
        temp=2.0+alfbet
        p1=(alf-bet+temp*z)/2.0
        p2=1.0
        DO j=2,n
           p3=p2
           p2=p1
           temp=2*j+alfbet
           a=2*j*(j+alfbet)*(temp-2.0)
           b=(temp-1.0)*(alf*alf-bet*bet+temp*(temp-2.0)*z)
           c=2.0*(j-1+alf)*(j-1+bet)*temp
           p1=(b*p2-c*p3)/a
        END DO
        pp=(n*(alf-bet-temp*z)*p1+2.0*(n+alf)*(n+bet)*p2)/(temp*(1.0-z*z))
        z1=z
        z=z1-p1/pp
        IF(ABS(z-z1).LE.EPS) GOTO 1
     END DO

     stop 'too many iterations in gaujac'
1    x(i)=z
     w(i)=EXP(gammln(alf+n)+gammln(bet+n)-gammln(n+1.0_dp)-gammln(n+alfbet+1.0_dp))*temp*2.0_dp**alfbet/(pp*p2)
  END DO
  RETURN
END SUBROUTINE gaujac

END MODULE triangleQuadratureGJ