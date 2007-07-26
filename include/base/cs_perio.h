/*============================================================================
*
*                    Code_Saturne version 1.3
*                    ------------------------
*
*
*     This file is part of the Code_Saturne Kernel, element of the
*     Code_Saturne CFD tool.
*
*     Copyright (C) 1998-2007 EDF S.A., France
*
*     contact: saturne-support@edf.fr
*
*     The Code_Saturne Kernel is free software; you can redistribute it
*     and/or modify it under the terms of the GNU General Public License
*     as published by the Free Software Foundation; either version 2 of
*     the License, or (at your option) any later version.
*
*     The Code_Saturne Kernel is distributed in the hope that it will be
*     useful, but WITHOUT ANY WARRANTY; without even the implied warranty
*     of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*     GNU General Public License for more details.
*
*     You should have received a copy of the GNU General Public License
*     along with the Code_Saturne Kernel; if not, write to the
*     Free Software Foundation, Inc.,
*     51 Franklin St, Fifth Floor,
*     Boston, MA  02110-1301  USA
*
*============================================================================*/

#ifndef __CS_PERIO_H__
#define __CS_PERIO_H__

/*============================================================================
 * Structure and function headers associated to periodicity
 *
 * Library : Code_Saturne 1.3                          Copyright EDF 1999-2006
 *============================================================================*/

/*----------------------------------------------------------------------------
 *  Local headers
 *----------------------------------------------------------------------------*/

#include "cs_base.h"
#include "cs_mesh.h"

/*----------------------------------------------------------------------------*/

#ifdef __cplusplus
extern "C" {
#if 0
} /* Fake brace to force Emacs auto-indentation back to column 0 */
#endif
#endif /* __cplusplus */

/*=============================================================================
 * Macro Definition
 *============================================================================*/

#define CS_NPHSMX  3  /* Max number of phases */

/*============================================================================
 * Type definitions
 *============================================================================*/

/*----------------------------------------------------------------------------
 * Periodicity treatment for the halo when the periodicity is a rotation
 *----------------------------------------------------------------------------*/

typedef enum {

  CS_PERIO_ROTA_COPY         , /* Copy halo (for scalar)                      */
  CS_PERIO_ROTA_RESET        , /* Reset halo in case of rotation              */
  CS_PERIO_ROTA_IGNORE         /* Ignore halo in case of rotation             */

} cs_perio_rota_t ;

/*============================================================================
 *  Public function header for Fortran API
 *============================================================================*/

/*----------------------------------------------------------------------------
 * Update values of periodic cells.
 *
 * VARIJ stands for the periodic variable to deal with.
 *
 * Several cases are possible:
 *
 *   IDIMTE = 0  : VAR11 is a scalar.
 *   IDIMTE = 1  : VAR11, VAR22, VAR33 is a vector.
 *   IDIMTE = 2  : VARIJ is a 3*3 matrix.
 *   IDIMTE = 21 : VARIJ is a diagonal 3*3 matrix (VAR11, VAR22, VAR33).
 *
 * Translation is always treated. Several treatment can be done for rotation:
 *
 *   ITENSO = 0  : only copy values of elements generated by rotation
 *   ITENSO = 1  : ignore rotation.
 *   ITENSO = 11 : reset values of elements generated by rotation
 *
 * - Periodicity for a scalar (IDIMTE = 0, ITENSO = 0). We update VAR11
 *   for translation or rotation periodicity.
 * - Periodicity for a scalar (IDIMTE = 0, ITENSO = 1). We update VAR11 only
 *   for translation periodicity.
 * - Periodicity for a scalar (IDIMTE = 0, ITENSO = 11). We update VAR11 only
 *   for translation periodicity. VAR11 is reseted for rotation periodicicty.
 *
 *   We use this option to cancel the halo for rotational periodicities
 *   in iterative solvers when solving for vectors and tensors by
 *   increment. This is an approximative solution, which does not seem
 *   worse than another.
 *
 * - with a vector (IDIMTE = 0, ITENSO = 2), we update
 *   VAR11, VAR22, VAR33, for translation only.
 * - with a vector (IDIMTE = 1, ITENSO = *), we update
 *   VAR11, VAR22, VAR33, for translation and rotation.
 * - with a tensor of rank 2 (IDIMTE = 2, ITENSO = *), we update
 *   VAR11, V12, VAR13, VAR21, VAR22, VAR23, VAR31, VAR32, VAR33,
 *   for translation and rotation.
 * - with a tensor or rank 2 (IDIMTE = 21, ITENSO = *) , we update
 *   VAR11, VAR22, VAR33, for translation and rotation (the tensor
 *   is considered diagonal).
 *
 * Fortran API:
 *
 * SUBROUTINE PERCOM
 * *****************
 *
 * INTEGER          IDIMTE        :  -> : variable dimension (maximum 3)
 *                                        0 : scalar (VAR11), or considered
 *                                            scalar
 *                                        1 : vector (VAR11,VAR22,VAR33)
 *                                        2 : tensor of rank 2 (VARIJ)
 *                                       21 : tensor of rank 2 supposed
 *                                            diagonal (VAR11, VAR22, VAR33)
 * INTEGER          ITENSO        :  -> : to define rotation behavior
 *                                        0 : scalar (VAR11)
 *                                        1 : tensor or vector component
 *                                            (VAR11), implicit in
 *                                            translation case
 *                                       11 : same as ITENSO=1 with vector
 *                                            or tensor component cancelled
 *                                            for rotation
 *                                        2 : vector (VAR11, VAR22, VAR33)
 *                                            implicit for rotation
 * DOUBLE PRECISION VAR11(NCELET) :  -  : component 11 of rank 2 tensor
 * DOUBLE PRECISION VAR12(NCELET) :  -  : component 12 of rank 2 tensor
 * DOUBLE PRECISION VAR13(NCELET) :  -  : component 13 of rank 2 tensor
 * DOUBLE PRECISION VAR21(NCELET) :  -  : component 21 of rank 2 tensor
 * DOUBLE PRECISION VAR22(NCELET) :  -  : component 22 of rank 2 tensor
 * DOUBLE PRECISION VAR23(NCELET) :  -  : component 23 of rank 2 tensor
 * DOUBLE PRECISION VAR31(NCELET) :  -  : component 31 of rank 2 tensor
 * DOUBLE PRECISION VAR32(NCELET) :  -  : component 32 of rank 2 tensor
 * DOUBLE PRECISION VAR33(NCELET) :  -  : component 33 of rank 2 tensor
 *----------------------------------------------------------------------------*/

void
CS_PROCF (percom, PERCOM) (const cs_int_t  *idimte,
                           const cs_int_t  *itenso,
                           cs_real_t        var11[],
                           cs_real_t        var12[],
                           cs_real_t        var13[],
                           cs_real_t        var21[],
                           cs_real_t        var22[],
                           cs_real_t        var23[],
                           cs_real_t        var31[],
                           cs_real_t        var32[],
                           cs_real_t        var33[]);

/*----------------------------------------------------------------------------
 * Update values for periodic cells (standard + extended) linked by
 * translation.
 *
 * Only called if periodicity is defined.
 *
 * FORTRAN Interface:
 *
 * SUBROUTINE PERCVE
 * *****************
 *
 *    & ( PVAR )
 *
 * PVAR         <->  variable to sync.
 *----------------------------------------------------------------------------*/

void
CS_PROCF (percve, PERCVE)(cs_real_t       pvar[]);

/*----------------------------------------------------------------------------
 * Periodicity management for INIMAS
 *
 * If INIMAS is called by NAVSTO :
 *    We assume that gradient on ghost cells given by a rotation is known
 *    and is equal to the velocity one for the previous time step.
 * If INIMAS is called by DIVRIJ
 *    We assume that (more justifiable than in previous case) gradient on
 *    ghost cells given by rotation is equal to Rij gradient for the previous
 *    time step.
 *
 * Fortran Interface:
 *
 * SUBROUTINE PERMAS
 * *****************
 *
 * INTEGER          IMASPE      :  -> : suivant l'appel de INIMAS
 *                                          = 1 si appel de RESOLP ou NAVSTO
 *                                          = 2 si appel de DIVRIJ
 * INTEGER          IPHAS       :  -> : numero de phase courante
 * INTEGER          IMASPE      :  -> : indicateur d'appel dans INIMAS
 *                                          = 1 si appel au debut
 *                                          = 2 si appel a la fin
 * DOUBLE PRECISION ROM(NCELET) :  -> : masse volumique aux cellules
 * DOUBLE PRECISION DUDXYZ      :  -> : gradient de U aux cellules halo pour
 *                                      l'approche explicite en periodicite
 * DOUBLE PRECISION DRDXYZ      :  -> : gradient de R aux cellules halo pour
 *                                      l'approche explicite en periodicite
 * DOUBLE PRECISION WDUDXY      :  -  : tableau de travail pour DUDXYZ
 * DOUBLE PRECISION WDRDXY      :  -  : tableau de travail pour DRDXYZ
 *
 * Size of DUDXYZ and WDUDXY = n_ghost_cells*3*3*NPHAS
 * Size of DRDXYZ and WDRDXY = n_ghost_cells*6*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (permas, PERMAS)(const cs_int_t    *imaspe,
                          const cs_int_t    *iphas,
                          const cs_int_t    *iappel,
                          const cs_real_t    rom[],
                          cs_real_t         *dudxyz,
                          cs_real_t         *drdxyz,
                          cs_real_t         *wdudxy,
                          cs_real_t         *wdrdxy);

/*----------------------------------------------------------------------------
 * Process DPDX, DPDY, DPDZ buffers in case of rotation on velocity vector and
 * Reynolds stress tensor.
 *
 * We retrieve the gradient given by PERINU and PERINR (PHYVAR) for the
 * velocity and the Reynolds stress tensor in a buffer on ghost cells. Then
 * we define DPDX, DPDY and DPDZ gradient (1 -> n_cells_with_ghosts).
 *
 * We can't implicitly take into account rotation of a gradient of a non-scalar
 * variable because we have to know the all three components in GRADRC.
 *
 * Otherwise, we can implicitly treat values given by translation. There will
 * be replace further in GRADRC.
 *
 * We define IDIMTE to 0 and ITENSO to 2 for the velocity vector and the
 * Reynolds stress tensor. We will still have to apply translation to these
 * variables so we define a tag to not forget to do it.
 *
 * We assume that is correct to treat implicitly periodicities for the other
 * variables in GRADRC. We define IDIMTE to 1 and ITENSO to 0.
 *
 * Fortran Interface:
 *
 * SUBROUTINE PERING
 * *****************
 *
 * INTEGER          NPHAS        :  -> : numero de phase courante
 * INTEGER          IVAR         :  -> : numero de la variable
 * INTEGER          IDIMTE       :  -> : dimension de la variable (maximum 3)
 *                                        0 : scalaire (VAR11), ou assimile
 *                                            scalaire
 *                                        1 : vecteur (VAR11,VAR22,VAR33)
 *                                        2 : tenseur d'ordre 2 (VARIJ)
 *                                       21 : tenseur d'ordre 2 suppose
 *                                            diagonal (VAR11, VAR22, VAR33)
 * INTEGER          ITENSO       :  -> : pour l'explicitation de la rotation
 *                                        0 : scalaire (VAR11)
 *                                        1 : composante de vecteur ou de
 *                                            tenseur (VAR11) implicite pour
 *                                            la translation
 *                                       11 : reprend le traitement ITENSO=1
 *                                            et composante de vecteur ou de
 *                                            tenseur annulee pour la rotation
 *                                        2 : vecteur (VAR11 et VAR22 et VAR33)
 *                                            implicite pour la rotation
 * INTEGER          IPEROT       :  -> : indicateur du nombre de periodicte de
 *                                       rotation
 * INTEGER          IGUPER       :  -> : 0/1 indique qu'on a /n'a pas calcule
 *                                       les gradients dans DUDXYZ
 * INTEGER          IGRPER       :  -> : 0/1 indique qu'on a /n'a pas calcule
 *                                       les gradients dans DRDXYZ
 * INTEGER          IU           :  -> : position de la Vitesse(x,y,z)
 * INTEGER          IV           :  -> : dans RTP, RTPA
 * INTEGER          IW           :  -> :     "                   "
 * INTEGER          ITYTUR       :  -> : turbulence (Rij-epsilon ITYTUR = 3)
 * INTEGER          IR11         :  -> : position des Tensions de Reynolds
 * INTEGER          IR22         :  -> : en Rij dans RTP, RTPA
 * INTEGER          IR33         :  -> :     "                   "
 * INTEGER          IR12         :  -> :     "                   "
 * INTEGER          IR13         :  -> :     "                   "
 * INTEGER          IR23         :  -> :     "                   "
 * DOUBLE PRECISION DPDX(NCELET) :  -> : gradient de IVAR
 * DOUBLE PRECISION DPDY(NCELET) :  -> :    "        "
 * DOUBLE PRECISION DPDZ(NCELET) :  -> :    "        "
 * DOUBLE PRECISION DUDXYZ       :  -> : gradient de U aux cellules halo pour
 *                                       l'approche explicite en periodicite
 * DOUBLE PRECISION DRDXYZ       :  -> : gradient de R aux cellules halo pour
 *                                       l'approche explicite en periodicite
 *
 * Size of DUDXYZ and WDUDXY = n_ghost_cells*3*3*NPHAS
 * Size of DRDXYZ and WDRDXY = n_ghost_cells*6*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (pering, PERING)(const cs_int_t    *nphas,
                          const cs_int_t    *ivar,
                          cs_int_t          *idimte,
                          cs_int_t          *itenso,
                          const cs_int_t    *iperot,
                          const cs_int_t    *iguper,
                          const cs_int_t    *igrper,
                          const cs_int_t     iu[CS_NPHSMX],
                          const cs_int_t     iv[CS_NPHSMX],
                          const cs_int_t     iw[CS_NPHSMX],
                          const cs_int_t     itytur[CS_NPHSMX],
                          const cs_int_t     ir11[CS_NPHSMX],
                          const cs_int_t     ir22[CS_NPHSMX],
                          const cs_int_t     ir33[CS_NPHSMX],
                          const cs_int_t     ir12[CS_NPHSMX],
                          const cs_int_t     ir13[CS_NPHSMX],
                          const cs_int_t     ir23[CS_NPHSMX],
                          cs_real_t          dpdx[],
                          cs_real_t          dpdy[],
                          cs_real_t          dpdz[],
                          cs_real_t         *dudxyz,
                          cs_real_t         *drdxyz);

/*----------------------------------------------------------------------------
 * Exchange buffers for PERINU
 *
 * Fortran Interface:
 *
 * SUBROUTINE PEINU1
 * *****************
 *
 * INTEGER          ISOU          :  -> : component of the velocity vector
 * INTEGER          IPHAS         :  -> : current phase number
 * DOUBLE PRECISION DUDXYZ        :  -> : gradient of the velocity vector
 *                                        for ghost cells and for an explicit
 *                                        treatment of the periodicity.
 * DOUBLE PRECISION W1..3(NCELET) :  -  : working buffers
 *
 * Size of DUDXYZ and WDUDXY = n_ghost_cells*3*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (peinu1, PEINU1)(const cs_int_t    *isou,
                          const cs_int_t    *iphas,
                          cs_real_t         *dudxyz,
                          cs_real_t          w1[],
                          cs_real_t          w2[],
                          cs_real_t          w3[]);

/*----------------------------------------------------------------------------
 * Apply rotation on DUDXYZ tensor.
 *
 * Fortran Interface:
 *
 * SUBROUTINE PEINU2 (VAR)
 * *****************
 *
 * INTEGER          IPHAS         :  -> : current phase number
 * DOUBLE PRECISION DUDXYZ        :  -> : gradient of the velocity vector
 *                                        for ghost cells and for an explicit
 *                                        treatment of the periodicity.
 *
 * Size of DUDXYZ and WDUDXY = n_ghost_cells*3*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (peinu2, PEINU2)(const cs_int_t    *iphas,
                          cs_real_t         *dudxyz);

/*----------------------------------------------------------------------------
 * Exchange buffers for PERINR
 *
 * Fortran Interface:
 *
 * SUBROUTINE PEINR1 (VAR)
 * *****************
 *
 * INTEGER          ISOU          : -> : component of the Reynolds stress tensor
 * INTEGER          IPHAS         : -> : current phase number
 * DOUBLE PRECISION DRDXYZ        : -> : gradient of the Reynolds stress tensor
 *                                       for ghost cells and for an explicit
 *                                       treatment of the periodicity.
 * DOUBLE PRECISION W1..3(NCELET) : -  : working buffers
 *
 * Size of DRDXYZ and WDRDXY = n_ghost_cells*6*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (peinr1, PEINR1)(const cs_int_t    *isou,
                          const cs_int_t    *iphas,
                          cs_real_t         *drdxyz,
                          cs_real_t          w1[],
                          cs_real_t          w2[],
                          cs_real_t          w3[]);

/*----------------------------------------------------------------------------
 * Apply rotation on the gradient of Reynolds stress tensor
 *
 * Fortran Interface:
 *
 * SUBROUTINE PEINR2 (VAR)
 * *****************
 *
 * INTEGER          IPHAS         :  -> : current phase number
 * DOUBLE PRECISION DRDXYZ        :  -> : gradient of the Reynolds stress tensor
 *                                       for ghost cells and for an explicit
 *                                       treatment of the periodicity.
 *
 * Size of DRDXYZ and WDRDXY = n_ghost_cells*6*3*NPHAS
 *----------------------------------------------------------------------------*/

void
CS_PROCF (peinr2, PEINR2)(const cs_int_t    *iphas,
                          cs_real_t         *drdxyz);

/*=============================================================================
 * Public function prototypes
 *============================================================================*/

/*----------------------------------------------------------------------------
 * Apply transformation on coordinates.
 *
 * parameters:
 *   coords     -->  coordinates on which transformation have to be done.
 *   halo_mode  -->  type of halo to treat
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_coords(cs_real_t            *coords,
                     cs_mesh_halo_type_t   halo_mode);

/*----------------------------------------------------------------------------
 * Initialize cs_mesh_quantities_t elements for periodicity.
 *
 * Updates cell center and cell family for halo cells.
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_geo(void);

/*----------------------------------------------------------------------------
 * Update values for a real scalar between periodic cells.
 *
 * parameters:
 *   var         <-> scalar to update
 *   mode_rota   --> Kind of treatment to do on periodic cells of the halo.
 *                   COPY, IGNORE or RESET
 *   halo_mode   --> kind of halo treatment
 *   stride      --> stride of variable to sync
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_var_scal(cs_real_t            var[],
                       cs_perio_rota_t      rota_mode,
                       cs_mesh_halo_type_t  halo_mode,
                       cs_int_t             stride);

/*----------------------------------------------------------------------------
 * Update values for a real vector between periodic cells.
 *
 * parameters:
 *   var_x       <-> component of the vector to update
 *   var_y       <-> component of the vector to update
 *   var_z       <-> component of the vector to update
 *   mode_rota   --> Kind of treatment to do on periodic cells of the halo.
 *                   COPY, IGNORE or RESET
 *   halo_mode   --> kind of halo treatment
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_var_vect(cs_real_t            varX[],
                       cs_real_t            varY[],
                       cs_real_t            varZ[],
                       cs_perio_rota_t      rota_mode,
                       cs_mesh_halo_type_t  halo_mode);

/*----------------------------------------------------------------------------
 * Update values for a real tensor between periodic cells.
 *
 * parameters:
 *   var11     <-> component of the tensor to update
 *   var12     <-> component of the tensor to update
 *   var13     <-> component of the tensor to update
 *   var21     <-> component of the tensor to update
 *   var22     <-> component of the tensor to update
 *   var23     <-> component of the tensor to update
 *   var31     <-> component of the tensor to update
 *   var32     <-> component of the tensor to update
 *   var33     <-> component of the tensor to update
 *   halo_mode --> kind of halo treatment
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_var_tens(cs_real_t            var11[],
                       cs_real_t            var12[],
                       cs_real_t            var13[],
                       cs_real_t            var21[],
                       cs_real_t            var22[],
                       cs_real_t            var23[],
                       cs_real_t            var31[],
                       cs_real_t            var32[],
                       cs_real_t            var33[],
                       cs_mesh_halo_type_t  halo_mode);

/*----------------------------------------------------------------------------
 * Update values for a real tensor between periodic cells.
 *
 * We only know the diagonal of the tensor.
 *
 * parameters:
 *   var11     <-> component of the tensor to update
 *   var22     <-> component of the tensor to update
 *   var33     <-> component of the tensor to update
 *   halo_mode --> kind of halo treatment
 *----------------------------------------------------------------------------*/

void
cs_perio_sync_var_diag(cs_real_t            var11[],
                       cs_real_t            var22[],
                       cs_real_t            var33[],
                       cs_mesh_halo_type_t  halo_mode);

/*----------------------------------------------------------------------------
 * Define parameters for building an interface set structure on the main mesh.
 *
 * parameters:
 *   p_n_periodic_lists   <-> pointer to the number of periodic lists (may
 *                            be local)
 *   p_periodic_num       <-> pointer to the periodicity number (1 to n)
 *                            associated with each periodic list (primary
 *                            periodicities only)
 *   p_n_periodic_couples <-> pointer to the number of periodic couples
 *   p_periodic_couples   <-> pointer to the periodic couple list
 *----------------------------------------------------------------------------*/

void
cs_perio_define_couples(int         *p_n_periodic_lists,
                        int         *p_periodic_num[],
                        fvm_lnum_t  *p_n_periodic_couples[],
                        fvm_gnum_t  **p_periodic_couples[]);

/*----------------------------------------------------------------------------*/

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __CS_PERIO_H__ */

