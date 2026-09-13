PROGRAM driverCLI
    !**********************************************************************
    !
    ! driverCLI
    !
    ! Wrapper a riga di comando per OptimalPolyCuba3D, pensato per essere
    ! invocato da Python (vedi app/core/fortran_backend.py).
    !
    ! Non contiene alcuna logica numerica propria: legge la mesh dai file
    ! .dat (stesso formato e stessa MeshReader gia' usati nel progetto),
    ! chiama OptimalPolyCuba3D cosi' com'e', e scrive nodi e pesi su due
    ! file di testo che Python rilegge.
    !
    ! USO:
    !   driverCLI <vertex_file> <face_file> <ade> <nodes_out> <weights_out>
    !
    ! Codici di uscita:
    !   0 = OK
    !   1 = argomenti mancanti
    !   2 = errore di scrittura sul file dei nodi
    !   3 = errore di scrittura sul file dei pesi
    !
    !**********************************************************************
    USE TypesDef, ONLY: dp
    USE PolyhedronMesh, ONLY: t_polyhedron, MeshReader
    USE OptimalPolyCuba3D_Module, ONLY: OptimalPolyCuba3D
    IMPLICIT NONE

    CHARACTER(LEN=2048) :: vertex_file, face_file, nodes_file, weights_file, ade_str
    INTEGER :: ade, ierr, u_nodes, u_weights, i, N

    TYPE(t_polyhedron)     :: poly
    REAL(dp), ALLOCATABLE  :: XYZ(:,:)
    REAL(dp), ALLOCATABLE  :: W(:)

    IF (COMMAND_ARGUMENT_COUNT() < 5) THEN
        WRITE(*,'(A)') 'USAGE: driverCLI <vertex_file> <face_file> <ade> <nodes_out> <weights_out>'
        CALL EXIT(1)
    END IF

    CALL GET_COMMAND_ARGUMENT(1, vertex_file)
    CALL GET_COMMAND_ARGUMENT(2, face_file)
    CALL GET_COMMAND_ARGUMENT(3, ade_str)
    CALL GET_COMMAND_ARGUMENT(4, nodes_file)
    CALL GET_COMMAND_ARGUMENT(5, weights_file)

    READ(ade_str, *) ade

    ! Lettura mesh (stesso formato .dat, stessa routine del progetto originale)
    CALL MeshReader(TRIM(vertex_file), TRIM(face_file), poly)

    ! Chiamata al numerical core, invariato
    CALL OptimalPolyCuba3D(ade, poly%vertici, poly%facce, XYZ, W)

    N = SIZE(W)

    !----------------------------------------------------------------
    ! Scrittura nodi: prima riga = numero di nodi, poi x y z per riga
    !----------------------------------------------------------------
    OPEN(NEWUNIT=u_nodes, FILE=TRIM(nodes_file), STATUS='REPLACE', ACTION='WRITE', IOSTAT=ierr)
    IF (ierr /= 0) THEN
        WRITE(*,'(A)') 'ERRORE: impossibile scrivere il file dei nodi.'
        CALL EXIT(2)
    END IF
    WRITE(u_nodes,'(I0)') N
    DO i = 1, N
        WRITE(u_nodes,'(3ES25.16E3)') XYZ(i,1), XYZ(i,2), XYZ(i,3)
    END DO
    CLOSE(u_nodes)

    !----------------------------------------------------------------
    ! Scrittura pesi: prima riga = numero di pesi, poi un peso per riga
    !----------------------------------------------------------------
    OPEN(NEWUNIT=u_weights, FILE=TRIM(weights_file), STATUS='REPLACE', ACTION='WRITE', IOSTAT=ierr)
    IF (ierr /= 0) THEN
        WRITE(*,'(A)') 'ERRORE: impossibile scrivere il file dei pesi.'
        CALL EXIT(3)
    END IF
    WRITE(u_weights,'(I0)') N
    DO i = 1, N
        WRITE(u_weights,'(ES25.16E3)') W(i)
    END DO
    CLOSE(u_weights)

    WRITE(*,'(A)') 'OK'

END PROGRAM driverCLI
