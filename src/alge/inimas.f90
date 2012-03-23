!-------------------------------------------------------------------------------

! This file is part of Code_Saturne, a general-purpose CFD tool.
!
! Copyright (C) 1998-2012 EDF S.A.
!
! This program is free software; you can redistribute it and/or modify it under
! the terms of the GNU General Public License as published by the Free Software
! Foundation; either version 2 of the License, or (at your option) any later
! version.
!
! This program is distributed in the hope that it will be useful, but WITHOUT
! ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
! FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
! details.
!
! You should have received a copy of the GNU General Public License along with
! this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
! Street, Fifth Floor, Boston, MA 02110-1301, USA.

!-------------------------------------------------------------------------------

!===============================================================================
! Function:
! ---------

!> \file inimas.f90
!>
!> \brief This function adds \f$ \rho \vect{u} \cdot \vect{S}_\ij\f$ to the mass
!> flux \f$ \dot{m}_\fij \f$ for the segregated algorithm on the velocity
!> components.
!>
!> For the reconstruction, \f$ \grad \left(\rho \vect{u} \right) \f$ is
!> computed with the following approximated boundary conditions:
!>  - \f$ \vect{A}_{\rho u} = \rho_\fib \vect{A}_u \f$
!>  - \f$ \tens{B}_{\rho u} = \vect{B}_u \f$
!> Be carefull: here \f$ \tens{B}_{u} \f$ is a diagonal tensor.
!>
!> For the mass flux at the boundary we have:
!> \f[
!> \dot{m}_\fib = \left[ \rho_\fib \vect{A}_u  + \rho_\fib \tens{B}_u \vect{u}
!> + \tens{B}_u \left(\gradv \vect{u} \cdot \vect{\centi \centip}\right)\right]
!> \cdot \vect{S}_\ij
!> \f]
!> The last equation uses some approximations detailed in the theory guide.
!-------------------------------------------------------------------------------

!-------------------------------------------------------------------------------
! Arguments
!______________________________________________________________________________.
!  mode           name          role                                           !
!______________________________________________________________________________!
!> \param[in]     nvar          total number of variables
!> \param[in]     nscal         total number of scalars
!> \param[in]     ivar1         current variable in the x direction
!> \param[in]     ivar2         current variable in the y direction
!> \param[in]     ivar3         current variable in the z direction
!> \param[in]     imaspe        indicator
!>                               - 1 if we deal with a vector field such as the
!>                                 velocity
!>                               - 2 if we deal with a tensor field such as the
!>                                 Reynolds stresses
!> \param[in]     iflmb0        the mass flux is set to 0 on walls and
!>                               symmetries if = 1
!> \param[in]     init          the mass flux is initialize to 0 if > 0
!> \param[in]     inc           indicator
!>                               - 0 solve an increment
!>                               - 1 otherwise
!> \param[in]     imrgra        indicator
!>                               - 0 iterative gradient
!>                               - 1 least square gradient
!> \param[in]     iccocg        indicator
!>                               - recompute the non-orthogonalities matrix
!>                                 cocg for the iterative gradients
!>                               - 0 otherwise
!> \param[in]     nswrgu        number of sweeps for the reconstruction
!>                               of the gradients
!> \param[in]     imligu        clipping gradient method
!>                               - < 0 no clipping
!>                               - = 0 thank to neighbooring gradients
!>                               - = 1 thank to the mean gradient
!> \param[in]     iwarnu        verbosity
!> \param[in]     nfecra        unit of the standard output file
!> \param[in]     epsrgu        relative precision for the gradient
!>                               reconstruction
!> \param[in]     climgu        clipping coeffecient for the computation of
!>                               the gradient
!> \param[in]     extrau        coefficient for extrapolation of the gradient
!> \param[in]     isympa        face indicator to set the mass flux to 0
!>                              (symmetries and walls with coupled BCs)
!> \param[in]     rom           cell density
!> \param[in]     romb          border face density
!> \param[in]     ux            variable in the x direction
!> \param[in]     uy            variable in the y direction
!> \param[in]     uz            variable in the z direction
!> \param[in]     coefa*        boundary condition array for the variable
!>                               (Explicit part - for the component * )
!> \param[in]     coefb*        boundary condition array for the variable
!>                               (Impplicit part - for the component *)
!> \param[in,out] flumas        interior mass flux \f$ \dot{m}_\fij \f$
!> \param[in,out] flumab        border mass flux \f$ \dot{m}_\fib \f$
!_______________________________________________________________________________

subroutine inimas &
!================

 ( nvar   , nscal  ,                                              &
   ivar1  , ivar2  , ivar3  , imaspe ,                            &
   iflmb0 , init   , inc    , imrgra , iccocg , nswrgu , imligu , &
   iwarnu , nfecra ,                                              &
   epsrgu , climgu , extrau ,                                     &
   rom    , romb   ,                                              &
   ux     , uy     , uz     ,                                     &
   coefax , coefay , coefaz , coefbx , coefby , coefbz ,          &
   flumas , flumab )

!===============================================================================

!===============================================================================
! Module files
!===============================================================================

use paramx
use dimens, only: ndimfb
use pointe
use optcal, only: iporos
use parall
use period
use mesh

!===============================================================================

implicit none

! Arguments

integer          nvar   , nscal
integer          ivar1  , ivar2  , ivar3  , imaspe
integer          iflmb0 , init   , inc    , imrgra , iccocg
integer          nswrgu , imligu
integer          iwarnu , nfecra
double precision epsrgu , climgu , extrau


double precision rom(ncelet), romb(nfabor)
double precision ux(ncelet), uy(ncelet), uz(ncelet)
double precision coefax(nfabor), coefay(nfabor), coefaz(nfabor)
double precision coefbx(nfabor), coefby(nfabor), coefbz(nfabor)
double precision flumas(nfac), flumab(nfabor)

! Local variables

integer          ifac, ii, jj, iel, iii
integer          iappel

double precision pfac,pip,uxfac,uyfac,uzfac
double precision dofx,dofy,dofz,pnd
double precision diipbx, diipby, diipbz

double precision, allocatable, dimension(:,:) :: grad
double precision, allocatable, dimension(:) :: qdmx, qdmy, qdmz
double precision, allocatable, dimension(:,:) :: coefqa

!===============================================================================

!===============================================================================
! 1.  INITIALISATION
!===============================================================================

! Allocate temporary arrays
allocate(qdmx(ncelet), qdmy(ncelet), qdmz(ncelet))
allocate(coefqa(ndimfb,3))


! ---> CALCUL DE LA QTE DE MOUVEMENT


if( init.eq.1 ) then
  do ifac = 1, nfac
    flumas(ifac) = 0.d0
  enddo
  do ifac = 1, nfabor
    flumab(ifac) = 0.d0
  enddo

elseif(init.ne.0) then
  write(nfecra,1000) init
  call csexit (1)
endif

! Without porosity
if (iporos.eq.0) then
  do iel = 1, ncel
    qdmx(iel) = rom(iel)*ux(iel)
    qdmy(iel) = rom(iel)*uy(iel)
    qdmz(iel) = rom(iel)*uz(iel)
  enddo

  ! Periodicity and parallelism treatment

  if (irangp.ge.0.or.iperio.eq.1) then
    call synvec(qdmx, qdmy, qdmz)
  endif

  do ifac =1, nfabor
    coefqa(ifac,1) = romb(ifac)*coefax(ifac)
    coefqa(ifac,2) = romb(ifac)*coefay(ifac)
    coefqa(ifac,3) = romb(ifac)*coefaz(ifac)
  enddo

! With porosity
else
  do iel = 1, ncel
    qdmx(iel) = rom(iel)*ux(iel)*porosi(iel)
    qdmy(iel) = rom(iel)*uy(iel)*porosi(iel)
    qdmz(iel) = rom(iel)*uz(iel)*porosi(iel)
  enddo

  ! Periodicity and parallelism treatment

  if (irangp.ge.0.or.iperio.eq.1) then
    call synvec(qdmx, qdmy, qdmz)
  endif

  do ifac =1, nfabor
    iel = ifabor(ifac)
    coefqa(ifac,1) = romb(ifac)*coefax(ifac)*porosi(iel)
    coefqa(ifac,2) = romb(ifac)*coefay(ifac)*porosi(iel)
    coefqa(ifac,3) = romb(ifac)*coefaz(ifac)*porosi(iel)
  enddo
endif

!===============================================================================
! 2.  CALCUL DU FLUX DE MASSE SANS TECHNIQUE DE RECONSTRUCTION
!===============================================================================

if( nswrgu.le.1 ) then

!     FLUX DE MASSE SUR LES FACETTES FLUIDES

  do ifac = 1, nfac

    ii = ifacel(1,ifac)
    jj = ifacel(2,ifac)

    pnd = pond(ifac)

    flumas(ifac) =  flumas(ifac)                                  &
     +(pnd*qdmx(ii)+(1.d0-pnd)*qdmx(jj) )*surfac(1,ifac)        &
     +(pnd*qdmy(ii)+(1.d0-pnd)*qdmy(jj) )*surfac(2,ifac)        &
     +(pnd*qdmz(ii)+(1.d0-pnd)*qdmz(jj) )*surfac(3,ifac)

  enddo


!     FLUX DE MASSE SUR LES FACETTES DE BORD

  do ifac = 1, nfabor

    ii = ifabor(ifac)
    uxfac = inc*coefqa(ifac,1) +coefbx(ifac)*romb(ifac)*ux(ii)
    uyfac = inc*coefqa(ifac,2) +coefby(ifac)*romb(ifac)*uy(ii)
    uzfac = inc*coefqa(ifac,3) +coefbz(ifac)*romb(ifac)*uz(ii)

    flumab(ifac) = flumab(ifac)                                   &
     +( uxfac*surfbo(1,ifac)                                      &
                    +uyfac*surfbo(2,ifac) +uzfac*surfbo(3,ifac) )

  enddo

endif


!===============================================================================
! 4.  CALCUL DU FLUX DE MASSE AVEC TECHNIQUE DE RECONSTRUCTION
!        SI LE MAILLAGE EST NON ORTHOGONAL
!===============================================================================

if( nswrgu.gt.1 ) then


  ! Allocate a temporary array for the gradient calculation
  allocate(grad(ncelet,3))


!     TRAITEMENT DE LA PERIODICITE SPEFICIQUE A INIMAS AU DEBUT
!     =========================================================

  if(iperot.gt.0) then
    iappel = 1

    call permas &
    !==========
 ( imaspe , iappel ,                 &
   rom    ,                          &
   dudxy  , drdxy  , wdudxy , wdrdxy )

  endif

!     FLUX DE MASSE SUIVANT X
!     =======================

! ---> CALCUL DU GRADIENT

  call grdcel                                                     &
  !==========
 ( ivar1  , imrgra , inc    , iccocg , nswrgu , imligu ,          &
   iwarnu , nfecra , epsrgu , climgu , extrau ,                   &
   qdmx   , coefqa(1,1) , coefbx ,                                &
   grad   )


! ---> FLUX DE MASSE SUR LES FACETTES FLUIDES

  do ifac = 1, nfac

    ii = ifacel(1,ifac)
    jj = ifacel(2,ifac)

    pnd = pond(ifac)

    dofx = dofij(1,ifac)
    dofy = dofij(2,ifac)
    dofz = dofij(3,ifac)

    flumas(ifac) = flumas(ifac)                                   &
         +( pnd*qdmx(ii) +(1.d0-pnd)*qdmx(jj)                     &
           +0.5d0*( grad(ii,1) +grad(jj,1) )*dofx                     &
           +0.5d0*( grad(ii,2) +grad(jj,2) )*dofy                     &
           +0.5d0*( grad(ii,3) +grad(jj,3) )*dofz    )*surfac(1,ifac)

  enddo

! ---> FLUX DE MASSE SUR LES FACETTES DE BORD

  do ifac = 1, nfabor

    ii = ifabor(ifac)

    diipbx = diipb(1,ifac)
    diipby = diipb(2,ifac)
    diipbz = diipb(3,ifac)

    pip = romb(ifac) * ux(ii)                                     &
          +grad(ii,1)*diipbx                                      &
          +grad(ii,2)*diipby +grad(ii,3)*diipbz
    pfac = inc*coefqa(ifac,1) +coefbx(ifac)*pip

    flumab(ifac) = flumab(ifac) +pfac*surfbo(1,ifac)

  enddo


!     FLUX DE MASSE SUIVANT Y
!     =======================

! ---> CALCUL DU GRADIENT

  call grdcel                                                     &
  !==========
 ( ivar2  , imrgra , inc    , iccocg , nswrgu , imligu ,          &
   iwarnu , nfecra , epsrgu , climgu , extrau ,                   &
   qdmy   , coefqa(1,2) , coefby ,                                &
   grad   )


! ---> FLUX DE MASSE SUR LES FACETTES FLUIDES

  do ifac = 1, nfac

    ii = ifacel(1,ifac)
    jj = ifacel(2,ifac)

    pnd = pond(ifac)

    dofx = dofij(1,ifac)
    dofy = dofij(2,ifac)
    dofz = dofij(3,ifac)

    flumas(ifac) = flumas(ifac)                                   &
         +( pnd*qdmy(ii) +(1.d0-pnd)*qdmy(jj)                     &
           +0.5d0*( grad(ii,1) +grad(jj,1) )*dofx                     &
           +0.5d0*( grad(ii,2) +grad(jj,2) )*dofy                     &
           +0.5d0*( grad(ii,3) +grad(jj,3) )*dofz    )*surfac(2,ifac)

  enddo

! ---> FLUX DE MASSE SUR LES FACETTES DE BORD

  do ifac = 1, nfabor

    ii = ifabor(ifac)

    diipbx = diipb(1,ifac)
    diipby = diipb(2,ifac)
    diipbz = diipb(3,ifac)

    pip = romb(ifac) * uy(ii)                                     &
        +grad(ii,1)*diipbx                                        &
        +grad(ii,2)*diipby +grad(ii,3)*diipbz
    pfac = inc*coefqa(ifac,2) +coefby(ifac)*pip

    flumab(ifac) = flumab(ifac) +pfac*surfbo(2,ifac)

  enddo

!     FLUX DE MASSE SUIVANT Z
!     =======================

! ---> CALCUL DU GRADIENT

  call grdcel                                                     &
  !==========
 ( ivar3  , imrgra , inc    , iccocg , nswrgu , imligu ,          &
   iwarnu , nfecra , epsrgu , climgu , extrau ,                   &
   qdmz   , coefqa(1,3) , coefbz ,                                &
   grad   )

!     FLUX DE MASSE SUR LES FACETTES FLUIDES

  do ifac = 1, nfac

    ii = ifacel(1,ifac)
    jj = ifacel(2,ifac)

    pnd = pond(ifac)

    dofx = dofij(1,ifac)
    dofy = dofij(2,ifac)
    dofz = dofij(3,ifac)

    flumas(ifac) = flumas(ifac)                                   &
         +( pnd*qdmz(ii) +(1.d0-pnd)*qdmz(jj)                     &
           +0.5d0*( grad(ii,1) +grad(jj,1) )*dofx                     &
           +0.5d0*( grad(ii,2) +grad(jj,2) )*dofy                     &
           +0.5d0*( grad(ii,3) +grad(jj,3) )*dofz    )*surfac(3,ifac)

  enddo

! ---> FLUX DE MASSE SUR LES FACETTES DE BORD

  do ifac = 1, nfabor

    ii = ifabor(ifac)

    diipbx = diipb(1,ifac)
    diipby = diipb(2,ifac)
    diipbz = diipb(3,ifac)

    pip = romb(ifac) * uz(ii)                                     &
        +grad(ii,1)*diipbx                                        &
        +grad(ii,2)*diipby +grad(ii,3)*diipbz
    pfac = inc*coefqa(ifac,3) +coefbz(ifac)*pip

    flumab(ifac) = flumab(ifac) +pfac*surfbo(3,ifac)

  enddo

  ! Free memory
  deallocate(grad)

!     TRAITEMENT DE LA PERIODICITE SPEFICIQUE A INIMAS A LA FIN
!     =========================================================

  if(iperot.gt.0) then
    iappel = 2

    call permas &
    !==========
 ( imaspe , iappel ,                 &
   rom    ,                          &
   dudxy  , drdxy  , wdudxy , wdrdxy )

  endif




endif


!===============================================================================
! 6.  POUR S'ASSURER DE LA NULLITE DU FLUX DE MASSE AUX LIMITES
!       SYMETRIES PAROIS COUPLEES
!===============================================================================

if(iflmb0.eq.1) then
! FORCAGE DE FLUMAB a 0 pour la vitesse'
  do ifac = 1, nfabor
    if(isympa(ifac).eq.0) then
      flumab(ifac) = 0.d0
    endif
  enddo
endif

! Free memory
deallocate(qdmx, qdmy, qdmz)
deallocate(coefqa)

!--------
! FORMATS
!--------

#if defined(_CS_LANG_FR)

 1000 format('INIMAS APPELE AVEC INIT =',I10)

#else

 1000 format('INIMAS CALLED WITH INIT =',I10)

#endif

!----
! FIN
!----

return

end subroutine
