MODULE PolyhedronMesh
    USE TypesDef
    IMPLICIT NONE

    ! Definizione della struttura dei dati
    TYPE :: t_polyhedron
        REAL(dp), ALLOCATABLE               :: vertici(:,:)
        INTEGER, ALLOCATABLE                :: facce(:,:)
        REAL(dp)                            :: bbox(6)
    END TYPE t_polyhedron

CONTAINS

    SUBROUTINE MeshReader(vertici_file, tri_file, poly)
        CHARACTER(LEN=*), INTENT(IN)            :: vertici_file
        CHARACTER(LEN=*), INTENT(IN)            :: tri_file
        TYPE(t_polyhedron), INTENT(OUT)         :: poly

        INTEGER                                 :: u_vert, u_tri, ierr, n_vertici, n_facce, i, j

        ! Lettura vertici, richiedo che il file esista gia con OLD e che lo apriro' solo in lettura READ, 
        ! impedendo cosi' una possibile scrittura su file accidentale. Ponendo IOSTAT=ierr se l'apertura
        ! fallisce, il programma non crasha ma inserisce un codice di errore e blocca l'esecuzione

        OPEN(NEWUNIT=u_vert, FILE=vertici_file, STATUS='OLD', ACTION='READ', IOSTAT=ierr)
        IF (ierr /= 0) STOP "ERRORE: Impossibile aprire il file dei vertici."

        READ(u_vert, *) n_vertici ! Leggo il primo numero in cima al file e lo salvo (numero vertici), deve essere presente senno' la lettura si blocca
        ALLOCATE(poly%vertici(n_vertici, 3)) 

        READ(u_vert, *) ((poly%vertici(i, j), j=1,3), i=1,n_vertici)
        CLOSE(u_vert)

        ! Lettura delle facce
        OPEN(NEWUNIT=u_tri, FILE=tri_file, STATUS='OLD', ACTION='READ', IOSTAT=ierr)
        IF (ierr /= 0) STOP "ERRORE: Impossibile aprire il file delle facce."

        READ(u_tri, *) n_facce ! Leggo il primo numero in cima al file e lo salvo (numero facce), deve essere presente senno' la lettura si blocca
        ALLOCATE(poly%facce(n_facce, 3))
        
        READ(u_tri, *) ((poly%facce(i, j), j=1,3), i=1,n_facce)
        CLOSE(u_tri)

        ! Calcolo della bounding box, prendo l'intera prima colonna e analizzo prendendo il max o il min, il risultato
        ! finale e' un vettore di 6 valori che viene inserito in poly%bbox
        poly%bbox = [ MINVAL(poly%vertici(:,1)), MAXVAL(poly%vertici(:,1)), &
                      MINVAL(poly%vertici(:,2)), MAXVAL(poly%vertici(:,2)), &
                      MINVAL(poly%vertici(:,3)), MAXVAL(poly%vertici(:,3)) ]

    END SUBROUTINE MeshReader

END MODULE PolyhedronMesh