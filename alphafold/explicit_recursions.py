##################################################################################################
# recursions.py          = user-editable, easier to read (but slower in Python) recursions. Edit this one!
#                           can force alphafold.py to use it with --simple.
#
# explicit_recursions.py = generated by create_explicit_recursions.py from recursions.py. This
#                           is the one used by default in alphafold.py due to speed.
##################################################################################################
def update_Z_cut( self, i, j ):
    '''
    Z_cut is the partition function for independently combining one contiguous/bonded segment emerging out of i to a cutpoint c, and another segment that goes from c+1 to j.
    Useful for Z_BP and Z_final calcs below.
    Analogous to 'exterior' Z in Mathews calc & Dirks multistrand calc.
    '''
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
    offset = ( j - i ) % N
    for c in range( i, i+offset ):
        if not ligated[c%N]:
            # strand 1  (i --> c), strand 2  (c+1 -- > j)
            if c == i and (c+1)%N == j: Z_cut.Q[i][j] += 1.0
            if c == i and (c+1)%N != j: Z_cut.Q[i%N][j%N] += Z_linear.Q[(c+1)%N][(j-1)%N]
            if c != i and (c+1)%N == j: Z_cut.Q[i%N][j%N] += Z_linear.Q[(i+1)%N][c%N]
            if c != i and (c+1)%N != j: Z_cut.Q[i%N][j%N] += Z_linear.Q[(i+1)%N][c%N] * Z_linear.Q[(c+1)%N][(j-1)%N]

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        for c in range( i, i+offset ):
            if not ligated[c%N]:
                if c == i and (c+1)%N != j: Z_cut.dQ[i%N][j%N] += Z_linear.dQ[(c+1)%N][(j-1)%N]
                if c != i and (c+1)%N == j: Z_cut.dQ[i%N][j%N] += Z_linear.dQ[(i+1)%N][c%N]
                if c != i and (c+1)%N != j: Z_cut.dQ[i%N][j%N] += Z_linear.dQ[(i+1)%N][c%N] * Z_linear.Q[(c+1)%N][(j-1)%N]
                if c != i and (c+1)%N != j: Z_cut.dQ[i%N][j%N] += Z_linear.Q[(i+1)%N][c%N] * Z_linear.dQ[(c+1)%N][(j-1)%N]

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        for c in range( i, i+offset ):
            if not ligated[c%N]:
                if c == i and (c+1)%N != j: Z_cut.contribs[i%N][j%N] +=  [ (Z_linear.Q[(c+1)%N][(j-1)%N], [(Z_linear,(c+1)%N,(j-1)%N)] ) ]
                if c != i and (c+1)%N == j: Z_cut.contribs[i%N][j%N] +=  [ (Z_linear.Q[(i+1)%N][c%N], [(Z_linear,(i+1)%N,c%N)] ) ]
                if c != i and (c+1)%N != j: Z_cut.contribs[i%N][j%N] +=  [ (Z_linear.Q[(i+1)%N][c%N] * Z_linear.Q[(c+1)%N][(j-1)%N], [(Z_linear,(i+1)%N,c%N), (Z_linear,(c+1)%N,(j-1)%N)] ) ]

##################################################################################################
def update_Z_BPq( self, i, j, base_pair_type ):
    '''
    Z_BPq is the partition function for all structures that base pair i and j with base_pair_type
    Relies on previous Z contributions available for subfragments, and Z_cut for this fragment i,j
    '''

    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
    offset = ( j - i ) % N

    ( C_eff_for_coax, C_eff_for_BP ) = (C_eff, C_eff ) if allow_strained_3WJ else (C_eff_no_BP_singlet, C_eff_no_coax_singlet )

    if self.force_base_pair and not self.force_base_pair[i%N][j%N]: return

    # minimum loop length -- no other way to penalize short segments.
    if ( all_ligated[i%N][j%N] and ( ((j-i-1) % N)) < min_loop_length ): return
    if ( all_ligated[j%N][i%N] and ( ((i-j-1) % N)) < min_loop_length ): return

    if base_pair_type.match_lowercase:
        if not ( sequence[i].islower() and sequence[j].islower() and sequence[i] == sequence[j] ): return
    else:
        if not ( sequence[i] == base_pair_type.nt1 and sequence[j] == base_pair_type.nt2 ) and \
           not ( sequence[i] == base_pair_type.nt2 and sequence[j] == base_pair_type.nt1 ): return

    (Z_BPq, Kd_BPq)  = ( self.Z_BPq[ base_pair_type ], base_pair_type.Kd_BP )

    if ligated[i%N] and ligated[(j-1)%N]:
        # base pair closes a loop
        #
        #    ~~~~~~
        #   ~      ~
        # i+1      j-1
        #   \       /
        #    i ... j
        #
        Z_BPq.Q[i%N][j%N]  += (1.0/Kd_BPq ) * ( C_eff_for_BP.Q[(i+1)%N][(j-1)%N] * l * l * l_BP)

        # base pair forms a stacked pair with previous pair
        #      ___
        #     /   \
        #  i+1 ... j-1
        #    |     |
        #    i ... j
        #
        # TODO: generalize C_eff_stacked_pair to be function of base pairs q (at i,j) and r (at i+1,j-1)
        Z_BPq.Q[i%N][j%N]  += (1.0/Kd_BPq ) * C_eff_stacked_pair * Z_BP.Q[(i+1)%N][(j-1)%N]

    # base pair brings together two strands that were previously disconnected
    #
    #   \       /
    #    i ... j
    #
    Z_BPq.Q[i%N][j%N] += (C_std/Kd_BPq) * Z_cut.Q[i%N][j%N]

    if ligated[i%N] and ligated[(j-1)%N]:

        # coaxial stack of bp (i,j) and (i+1,k)...  "left stack",  and closes loop on right.
        #      ___
        #     /   \
        #  i+1 ... k - k+1 ~
        #    |              ~
        #    i ... j - j-1 ~
        #
        for k in range( i+2, i+offset-1 ):
            if ligated[k%N]: Z_BPq.Q[i%N][j%N] += Z_BP.Q[(i+1)%N][k%N] * C_eff_for_coax.Q[(k+1)%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq

        # coaxial stack of bp (i,j) and (k,j-1)...  close loop on left, and "right stack"
        #            ___
        #           /   \
        #  ~ k-1 - k ... j-1
        # ~              |
        #  ~ i+1 - i ... j
        #
        for k in range( i+2, i+offset-1 ):
            if ligated[(k-1)%N]: Z_BPq.Q[i%N][j%N] += C_eff_for_coax.Q[(i+1)%N][(k-1)%N] * Z_BP.Q[k%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq

    # "left stack" but no loop closed on right (free strands hanging off j end)
    #      ___
    #     /   \
    #  i+1 ... k -
    #    |
    #    i ... j -
    #
    if ligated[i%N]:
        for k in range( i+2, i+offset ): Z_BPq.Q[i%N][j%N] += Z_BP.Q[(i+1)%N][k%N] * Z_cut.Q[k%N][j%N] * C_std * K_coax / Kd_BPq

    # "right stack" but no loop closed on left (free strands hanging off i end)
    #       ___
    #      /   \
    #   - k ... j-1
    #           |
    #   - i ... j
    #
    if ligated[(j-1)%N]:
        for k in range( i, i+offset-1 ): Z_BPq.Q[i%N][j%N] += Z_cut.Q[i%N][k%N] * Z_BP.Q[k%N][(j-1)%N] * C_std * K_coax / Kd_BPq

    # key 'special sauce' for derivative w.r.t. Kd_BP
    if self.options.calc_deriv: Z_BPq.dQ[i][j] += -(1.0/Kd_BPq) * Z_BPq.Q[i][j]

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        ( C_eff_for_coax, C_eff_for_BP ) = (C_eff, C_eff ) if allow_strained_3WJ else (C_eff_no_BP_singlet, C_eff_no_coax_singlet )
        if self.force_base_pair and not self.force_base_pair[i%N][j%N]: return
        if ( all_ligated[i%N][j%N] and ( ((j-i-1) % N)) < min_loop_length ): return
        if ( all_ligated[j%N][i%N] and ( ((i-j-1) % N)) < min_loop_length ): return
        if base_pair_type.match_lowercase:
            if not ( sequence[i].islower() and sequence[j].islower() and sequence[i] == sequence[j] ): return
        else:
            if not ( sequence[i] == base_pair_type.nt1 and sequence[j] == base_pair_type.nt2 ) and \
               not ( sequence[i] == base_pair_type.nt2 and sequence[j] == base_pair_type.nt1 ): return
        (Z_BPq, Kd_BPq)  = ( self.Z_BPq[ base_pair_type ], base_pair_type.Kd_BP )
        if ligated[i%N] and ligated[(j-1)%N]:
            Z_BPq.dQ[i%N][j%N]  += (1.0/Kd_BPq ) * ( C_eff_for_BP.dQ[(i+1)%N][(j-1)%N] * l * l * l_BP)
            Z_BPq.dQ[i%N][j%N]  += (1.0/Kd_BPq ) * C_eff_stacked_pair * Z_BP.dQ[(i+1)%N][(j-1)%N]
        Z_BPq.dQ[i%N][j%N] += (C_std/Kd_BPq) * Z_cut.dQ[i%N][j%N]
        if ligated[i%N] and ligated[(j-1)%N]:
            for k in range( i+2, i+offset-1 ):
                if ligated[k%N]: Z_BPq.dQ[i%N][j%N] += Z_BP.dQ[(i+1)%N][k%N] * C_eff_for_coax.Q[(k+1)%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq
                if ligated[k%N]: Z_BPq.dQ[i%N][j%N] += Z_BP.Q[(i+1)%N][k%N] * C_eff_for_coax.dQ[(k+1)%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq
            for k in range( i+2, i+offset-1 ):
                if ligated[(k-1)%N]: Z_BPq.dQ[i%N][j%N] += C_eff_for_coax.dQ[(i+1)%N][(k-1)%N] * Z_BP.Q[k%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq
                if ligated[(k-1)%N]: Z_BPq.dQ[i%N][j%N] += C_eff_for_coax.Q[(i+1)%N][(k-1)%N] * Z_BP.dQ[k%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq
        if ligated[i%N]:
            for k in range( i+2, i+offset ): Z_BPq.dQ[i%N][j%N] += Z_BP.dQ[(i+1)%N][k%N] * Z_cut.Q[k%N][j%N] * C_std * K_coax / Kd_BPq
            for k in range( i+2, i+offset ): Z_BPq.dQ[i%N][j%N] += Z_BP.Q[(i+1)%N][k%N] * Z_cut.dQ[k%N][j%N] * C_std * K_coax / Kd_BPq
        if ligated[(j-1)%N]:
            for k in range( i, i+offset-1 ): Z_BPq.dQ[i%N][j%N] += Z_cut.dQ[i%N][k%N] * Z_BP.Q[k%N][(j-1)%N] * C_std * K_coax / Kd_BPq
            for k in range( i, i+offset-1 ): Z_BPq.dQ[i%N][j%N] += Z_cut.Q[i%N][k%N] * Z_BP.dQ[k%N][(j-1)%N] * C_std * K_coax / Kd_BPq

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        ( C_eff_for_coax, C_eff_for_BP ) = (C_eff, C_eff ) if allow_strained_3WJ else (C_eff_no_BP_singlet, C_eff_no_coax_singlet )
        if self.force_base_pair and not self.force_base_pair[i%N][j%N]: return
        if ( all_ligated[i%N][j%N] and ( ((j-i-1) % N)) < min_loop_length ): return
        if ( all_ligated[j%N][i%N] and ( ((i-j-1) % N)) < min_loop_length ): return
        if base_pair_type.match_lowercase:
            if not ( sequence[i].islower() and sequence[j].islower() and sequence[i] == sequence[j] ): return
        else:
            if not ( sequence[i] == base_pair_type.nt1 and sequence[j] == base_pair_type.nt2 ) and \
               not ( sequence[i] == base_pair_type.nt2 and sequence[j] == base_pair_type.nt1 ): return
        (Z_BPq, Kd_BPq)  = ( self.Z_BPq[ base_pair_type ], base_pair_type.Kd_BP )
        if ligated[i%N] and ligated[(j-1)%N]:
            Z_BPq.contribs[i%N][j%N]  +=  [ ((1.0/Kd_BPq ) * ( C_eff_for_BP.Q[(i+1)%N][(j-1)%N] * l * l * l_BP), [(C_eff_for_BP,(i+1)%N,(j-1)%N)] ) ]
            Z_BPq.contribs[i%N][j%N]  +=  [ ((1.0/Kd_BPq ) * C_eff_stacked_pair * Z_BP.Q[(i+1)%N][(j-1)%N], [(Z_BP,(i+1)%N,(j-1)%N)] ) ]
        Z_BPq.contribs[i%N][j%N] +=  [ ((C_std/Kd_BPq) * Z_cut.Q[i%N][j%N], [(Z_cut,i%N,j%N)] ) ]
        if ligated[i%N] and ligated[(j-1)%N]:
            for k in range( i+2, i+offset-1 ):
                if ligated[k%N]: Z_BPq.contribs[i%N][j%N] +=  [ (Z_BP.Q[(i+1)%N][k%N] * C_eff_for_coax.Q[(k+1)%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq, [(Z_BP,(i+1)%N,k%N), (C_eff_for_coax,(k+1)%N,(j-1)%N)] ) ]
            for k in range( i+2, i+offset-1 ):
                if ligated[(k-1)%N]: Z_BPq.contribs[i%N][j%N] +=  [ (C_eff_for_coax.Q[(i+1)%N][(k-1)%N] * Z_BP.Q[k%N][(j-1)%N] * l**2 * l_coax * K_coax / Kd_BPq, [(C_eff_for_coax,(i+1)%N,(k-1)%N), (Z_BP,k%N,(j-1)%N)] ) ]
        if ligated[i%N]:
            for k in range( i+2, i+offset ): Z_BPq.contribs[i%N][j%N] +=  [ (Z_BP.Q[(i+1)%N][k%N] * Z_cut.Q[k%N][j%N] * C_std * K_coax / Kd_BPq, [(Z_BP,(i+1)%N,k%N), (Z_cut,k%N,j%N)] ) ]
        if ligated[(j-1)%N]:
            for k in range( i, i+offset-1 ): Z_BPq.contribs[i%N][j%N] +=  [ (Z_cut.Q[i%N][k%N] * Z_BP.Q[k%N][(j-1)%N] * C_std * K_coax / Kd_BPq, [(Z_cut,i%N,k%N), (Z_BP,k%N,(j-1)%N)] ) ]

##################################################################################################
def update_Z_BP( self, i, j ):
    '''
    Z_BP is the partition function for all structures that base pair i and j.
    All the Z_BPq (partition functions for each base pair type) must have been
    filled in already for i,j.
    '''
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    for base_pair_type in self.base_pair_types:
        Z_BPq = self.Z_BPq[base_pair_type]
        Z_BP.Q[i%N][j%N]  += Z_BPq.Q[i%N][j%N]

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        for base_pair_type in self.base_pair_types:
            Z_BPq = self.Z_BPq[base_pair_type]
            Z_BP.dQ[i%N][j%N]  += Z_BPq.dQ[i%N][j%N]

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        for base_pair_type in self.base_pair_types:
            Z_BPq = self.Z_BPq[base_pair_type]
            Z_BP.contribs[i%N][j%N]  +=  [ (Z_BPq.Q[i%N][j%N], [(Z_BPq,i%N,j%N)] ) ]

##################################################################################################
def update_Z_coax( self, i, j ):
    '''
    Z_coax(i,j) is the partition function for all structures that form coaxial stacks between (i,k) and (k+1,j) for some k
    '''
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
    offset = ( j - i ) % N

    #  all structures that form coaxial stacks between (i,k) and (k+1,j) for some k
    #
    #       -- k - k+1 -
    #      /   :    :   \
    #      \   :    :   /
    #       -- i    j --
    #
    for k in range( i+1, i+offset-1 ):
        if ligated[k%N]: Z_coax.Q[i%N][j%N]  += Z_BP.Q[i%N][k%N] * Z_BP.Q[(k+1)%N][j%N] * K_coax

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        for k in range( i+1, i+offset-1 ):
            if ligated[k%N]: Z_coax.dQ[i%N][j%N]  += Z_BP.dQ[i%N][k%N] * Z_BP.Q[(k+1)%N][j%N] * K_coax
            if ligated[k%N]: Z_coax.dQ[i%N][j%N]  += Z_BP.Q[i%N][k%N] * Z_BP.dQ[(k+1)%N][j%N] * K_coax

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        offset = ( j - i ) % N
        for k in range( i+1, i+offset-1 ):
            if ligated[k%N]: Z_coax.contribs[i%N][j%N]  +=  [ (Z_BP.Q[i%N][k%N] * Z_BP.Q[(k+1)%N][j%N] * K_coax, [(Z_BP,i%N,k%N), (Z_BP,(k+1)%N,j%N)] ) ]

##################################################################################################
def update_C_eff_basic( self, i, j ):
    '''
    C_eff tracks the effective molarity of a loop starting at i and ending at j
    Assumes a model where each additional element multiplicatively reduces the effective molarity, by
      the variables l, l_BP, C_eff_stacked_pair, K_coax, etc.
    Relies on previous Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear available for subfragments.
    Relies on Z_BP being already filled out for i,j
    TODO: In near future, will include possibility of multiple C_eff terms, which combined together will
      allow for free energy costs of loop closure to scale approximately log-linearly rather than
      linearly with loop size.
    '''
    offset = ( j - i ) % self.N

    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )

    # j is not base paired or coaxially stacked: Extension by one residue from j-1 to j.
    #
    #    i ~~~~~~ j-1 - j
    #
    if ligated[(j-1)%N] and allow_loop_extension: C_eff_basic.Q[i%N][j%N] += C_eff.Q[i%N][(j-1)%N] * l

    exclude_strained_3WJ = (not allow_strained_3WJ) and (offset == N-1) and ligated[j%N]

    # j is base paired, and its partner is k > i. (look below for case with i and j base paired)
    #                 ___
    #                /   \
    #    i ~~~~k-1 - k...j
    #
    C_eff_for_BP = C_eff_no_coax_singlet if exclude_strained_3WJ else C_eff
    for k in range( i+1, i+offset):
        if ligated[(k-1)%N]: C_eff_basic.Q[i%N][j%N] += C_eff_for_BP.Q[i%N][(k-1)%N] * l * Z_BP.Q[k%N][j%N] * l_BP

    # j is coax-stacked, and its partner is k > i.  (look below for case with i and j coaxially stacked)
    #               _______
    #              / :   : \
    #              \ :   : /
    #    i ~~~~k-1 - k   j
    #
    C_eff_for_coax = C_eff_no_BP_singlet if exclude_strained_3WJ else C_eff
    for k in range( i+1, i+offset):
        if ligated[(k-1)%N]: C_eff_basic.Q[i%N][j%N] += C_eff_for_coax.Q[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N] * l * l_coax


    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        offset = ( j - i ) % self.N
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )
        if ligated[(j-1)%N] and allow_loop_extension: C_eff_basic.dQ[i%N][j%N] += C_eff.dQ[i%N][(j-1)%N] * l
        exclude_strained_3WJ = (not allow_strained_3WJ) and (offset == N-1) and ligated[j%N]
        C_eff_for_BP = C_eff_no_coax_singlet if exclude_strained_3WJ else C_eff
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: C_eff_basic.dQ[i%N][j%N] += C_eff_for_BP.dQ[i%N][(k-1)%N] * l * Z_BP.Q[k%N][j%N] * l_BP
            if ligated[(k-1)%N]: C_eff_basic.dQ[i%N][j%N] += C_eff_for_BP.Q[i%N][(k-1)%N] * l * Z_BP.dQ[k%N][j%N] * l_BP
        C_eff_for_coax = C_eff_no_BP_singlet if exclude_strained_3WJ else C_eff
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: C_eff_basic.dQ[i%N][j%N] += C_eff_for_coax.dQ[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N] * l * l_coax
            if ligated[(k-1)%N]: C_eff_basic.dQ[i%N][j%N] += C_eff_for_coax.Q[i%N][(k-1)%N] * Z_coax.dQ[k%N][j%N] * l * l_coax

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        offset = ( j - i ) % self.N
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )
        if ligated[(j-1)%N] and allow_loop_extension: C_eff_basic.contribs[i%N][j%N] +=  [ (C_eff.Q[i%N][(j-1)%N] * l, [(C_eff,i%N,(j-1)%N)] ) ]
        exclude_strained_3WJ = (not allow_strained_3WJ) and (offset == N-1) and ligated[j%N]
        C_eff_for_BP = C_eff_no_coax_singlet if exclude_strained_3WJ else C_eff
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: C_eff_basic.contribs[i%N][j%N] +=  [ (C_eff_for_BP.Q[i%N][(k-1)%N] * l * Z_BP.Q[k%N][j%N] * l_BP, [(C_eff_for_BP,i%N,(k-1)%N), (Z_BP,k%N,j%N)] ) ]
        C_eff_for_coax = C_eff_no_BP_singlet if exclude_strained_3WJ else C_eff
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: C_eff_basic.contribs[i%N][j%N] +=  [ (C_eff_for_coax.Q[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N] * l * l_coax, [(C_eff_for_coax,i%N,(k-1)%N), (Z_coax,k%N,j%N)] ) ]

##################################################################################################
def update_C_eff_no_coax_singlet( self, i, j ):
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    # some helper arrays that prevent closure of any 3WJ with a single coaxial stack and single helix with not intervening loop nucleotides
    C_eff_no_coax_singlet.Q[i%N][j%N] += C_eff_basic.Q[i%N][j%N]
    C_eff_no_coax_singlet.Q[i%N][j%N] += C_init * Z_BP.Q[i%N][j%N] * l_BP

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff_no_coax_singlet.dQ[i%N][j%N] += C_eff_basic.dQ[i%N][j%N]
        C_eff_no_coax_singlet.dQ[i%N][j%N] += C_init * Z_BP.dQ[i%N][j%N] * l_BP

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff_no_coax_singlet.contribs[i%N][j%N] +=  [ (C_eff_basic.Q[i%N][j%N], [(C_eff_basic,i%N,j%N)] ) ]
        C_eff_no_coax_singlet.contribs[i%N][j%N] +=  [ (C_init * Z_BP.Q[i%N][j%N] * l_BP, [(Z_BP,i%N,j%N)] ) ]

##################################################################################################
def update_C_eff_no_BP_singlet( self, i, j ):
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    C_eff_no_BP_singlet.Q[i%N][j%N] += C_eff_basic.Q[i%N][j%N]
    C_eff_no_BP_singlet.Q[i%N][j%N] += C_init * Z_coax.Q[i%N][j%N] * l_coax

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff_no_BP_singlet.dQ[i%N][j%N] += C_eff_basic.dQ[i%N][j%N]
        C_eff_no_BP_singlet.dQ[i%N][j%N] += C_init * Z_coax.dQ[i%N][j%N] * l_coax

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff_no_BP_singlet.contribs[i%N][j%N] +=  [ (C_eff_basic.Q[i%N][j%N], [(C_eff_basic,i%N,j%N)] ) ]
        C_eff_no_BP_singlet.contribs[i%N][j%N] +=  [ (C_init * Z_coax.Q[i%N][j%N] * l_coax, [(Z_coax,i%N,j%N)] ) ]

##################################################################################################
def update_C_eff( self, i, j ):
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    C_eff.Q[i%N][j%N] += C_eff_basic.Q[i%N][j%N]

    # j is base paired, and its partner is i
    #      ___
    #     /   \
    #  i+1 ... j-1
    #    |     |
    #    i ... j
    #
    C_eff.Q[i%N][j%N] += C_init * Z_BP.Q[i%N][j%N] * l_BP

    # j is coax-stacked, and its partner is i.
    #       ------------
    #      /   :    :   \
    #      \   :    :   /
    #       -- i    j --
    #
    C_eff.Q[i%N][j%N] += C_init * Z_coax.Q[i%N][j%N] * l_coax

    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff.dQ[i%N][j%N] += C_eff_basic.dQ[i%N][j%N]
        C_eff.dQ[i%N][j%N] += C_init * Z_BP.dQ[i%N][j%N] * l_BP
        C_eff.dQ[i%N][j%N] += C_init * Z_coax.dQ[i%N][j%N] * l_coax

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        C_eff.contribs[i%N][j%N] +=  [ (C_eff_basic.Q[i%N][j%N], [(C_eff_basic,i%N,j%N)] ) ]
        C_eff.contribs[i%N][j%N] +=  [ (C_init * Z_BP.Q[i%N][j%N] * l_BP, [(Z_BP,i%N,j%N)] ) ]
        C_eff.contribs[i%N][j%N] +=  [ (C_init * Z_coax.Q[i%N][j%N] * l_coax, [(Z_coax,i%N,j%N)] ) ]

##################################################################################################
def update_Z_linear( self, i, j ):
    '''
    Z_linear tracks the total partition function from i to j, assuming all intervening residues are covalently connected (or base-paired).
    Relies on previous Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear available for subfragments.
    Relies on Z_BP being already filled out for i,j
    '''
    offset = ( j - i ) % self.N

    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )

    # j is not base paired: Extension by one residue from j-1 to j.
    #
    #    i ~~~~~~ j-1 - j
    #
    if ligated[(j-1)%N] and allow_loop_extension: Z_linear.Q[i%N][j%N] += Z_linear.Q[i%N][(j-1)%N]

    # j is base paired, and its partner is i
    #     ___
    #    /   \
    #    i...j
    #
    Z_linear.Q[i%N][j%N] += Z_BP.Q[i%N][j%N]

    # j is base paired, and its partner is k > i
    #                 ___
    #                /   \
    #    i ~~~~k-1 - k...j
    #
    for k in range( i+1, i+offset):
        if ligated[(k-1)%N]: Z_linear.Q[i%N][j%N] += Z_linear.Q[i%N][(k-1)%N] * Z_BP.Q[k%N][j%N]

    # j is coax-stacked, and its partner is i.
    #       ------------
    #      /   :    :   \
    #      \   :    :   /
    #       -- i    j --
    #
    Z_linear.Q[i%N][j%N] += Z_coax.Q[i%N][j%N]

    # j is coax-stacked, and its partner is k > i.
    #
    #               _______
    #              / :   : \
    #              \ :   : /
    #    i ~~~~k-1 - k   j
    #
    for k in range( i+1, i+offset):
        if ligated[(k-1)%N]: Z_linear.Q[i%N][j%N] += Z_linear.Q[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N]


    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        offset = ( j - i ) % self.N
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )
        if ligated[(j-1)%N] and allow_loop_extension: Z_linear.dQ[i%N][j%N] += Z_linear.dQ[i%N][(j-1)%N]
        Z_linear.dQ[i%N][j%N] += Z_BP.dQ[i%N][j%N]
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: Z_linear.dQ[i%N][j%N] += Z_linear.dQ[i%N][(k-1)%N] * Z_BP.Q[k%N][j%N]
            if ligated[(k-1)%N]: Z_linear.dQ[i%N][j%N] += Z_linear.Q[i%N][(k-1)%N] * Z_BP.dQ[k%N][j%N]
        Z_linear.dQ[i%N][j%N] += Z_coax.dQ[i%N][j%N]
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: Z_linear.dQ[i%N][j%N] += Z_linear.dQ[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N]
            if ligated[(k-1)%N]: Z_linear.dQ[i%N][j%N] += Z_linear.Q[i%N][(k-1)%N] * Z_coax.dQ[k%N][j%N]

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        offset = ( j - i ) % self.N
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[j%N] )
        if ligated[(j-1)%N] and allow_loop_extension: Z_linear.contribs[i%N][j%N] +=  [ (Z_linear.Q[i%N][(j-1)%N], [(Z_linear,i%N,(j-1)%N)] ) ]
        Z_linear.contribs[i%N][j%N] +=  [ (Z_BP.Q[i%N][j%N], [(Z_BP,i%N,j%N)] ) ]
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: Z_linear.contribs[i%N][j%N] +=  [ (Z_linear.Q[i%N][(k-1)%N] * Z_BP.Q[k%N][j%N], [(Z_linear,i%N,(k-1)%N), (Z_BP,k%N,j%N)] ) ]
        Z_linear.contribs[i%N][j%N] +=  [ (Z_coax.Q[i%N][j%N], [(Z_coax,i%N,j%N)] ) ]
        for k in range( i+1, i+offset):
            if ligated[(k-1)%N]: Z_linear.contribs[i%N][j%N] +=  [ (Z_linear.Q[i%N][(k-1)%N] * Z_coax.Q[k%N][j%N], [(Z_linear,i%N,(k-1)%N), (Z_coax,k%N,j%N)] ) ]

##################################################################################################
def update_Z_final( self, i ):
    # Z_final is total partition function, and is computed at end of filling dynamic programming arrays
    # Get the answer (in N ways!) --> so final output is actually Z_final(i), an array.
    # Equality of the array is tested in run_cross_checks()
    (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
     sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )

    Z_final = self.Z_final
    if not ligated[((i - 1))%N]:
        #
        #      i ------- i-1
        #
        #     or equivalently
        #        ________
        #       /        \
        #       \        /
        #        i-1    i
        #
        Z_final.Q[i%N] += Z_linear.Q[i%N][(i-1)%N]
    else:
        # Need to 'ligate' across i-1 to i
        # Scaling Z_final by Kd_lig/C_std to match previous literature conventions

        # Need to remove Z_coax contribution from C_eff, since its covered by C_eff_stacked_pair below.
        Z_final.Q[i%N] += C_eff_no_coax_singlet.Q[i%N][(i-1)%N] * l / C_std

        #any split segments, combined independently
        #
        #   c+1 --- i-1 - i --- c
        #               *
        allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[i%N] )
        if allow_loop_extension:
            for c in range( i, i + N - 1):
                if not ligated[c%N]: Z_final.Q[i%N] += Z_linear.Q[i%N][c%N] * Z_linear.Q[(c+1)%N][(i-1)%N]

        # base pair forms a stacked pair with previous pair
        #
        #   - j+1 - j -
        #      :    :
        #      :    :
        #   - i-1 - i -
        #         *
        for j in range( i+1, (i + N - 1) ):
            if ligated[j%N]: Z_final.Q[i%N] += C_eff_stacked_pair * Z_BP.Q[i%N][j%N] * Z_BP.Q[(j+1)%N][(i-1)%N]

        C_eff_for_coax = C_eff if allow_strained_3WJ else C_eff_no_BP_singlet

        # New co-axial stack might form across ligation junction
        for j in range( i + 1, i + N - 2):
            # If the two coaxially stacked base pairs are connected by a loop.
            #
            #       ~~~~
            #   -- k    j --
            #  /   :    :   \
            #  \   :    :   /
            #   - i-1 - i --
            #         *
            for k in range( j + 2, i + N - 1):
                if not ligated[j%N]: continue
                if not ligated[(k-1)%N]: continue
                Z_final.Q[i%N] += Z_BP.Q[i%N][j%N] * C_eff_for_coax.Q[(j+1)%N][(k-1)%N] * Z_BP.Q[k%N][(i-1)%N] * l * l * l_coax * K_coax

            # If the two stacked base pairs are in split segments
            #
            #      \    /
            #   -- k    j --
            #  /   :    :   \
            #  \   :    :   /
            #   - i-1 - i --
            #         *
            for k in range( j + 1, i + N - 1):
                Z_final.Q[i%N] += Z_BP.Q[i%N][j%N] * Z_cut.Q[j%N][k%N] * Z_BP.Q[k%N][(i-1)%N] * K_coax


    if self.options.calc_deriv: # AUTOGENERATED DERIV BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        Z_final = self.Z_final
        if not ligated[((i - 1))%N]:
            Z_final.dQ[i%N] += Z_linear.dQ[i%N][(i-1)%N]
        else:
            Z_final.dQ[i%N] += C_eff_no_coax_singlet.dQ[i%N][(i-1)%N] * l / C_std
            allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[i%N] )
            if allow_loop_extension:
                for c in range( i, i + N - 1):
                    if not ligated[c%N]: Z_final.dQ[i%N] += Z_linear.dQ[i%N][c%N] * Z_linear.Q[(c+1)%N][(i-1)%N]
                    if not ligated[c%N]: Z_final.dQ[i%N] += Z_linear.Q[i%N][c%N] * Z_linear.dQ[(c+1)%N][(i-1)%N]
            for j in range( i+1, (i + N - 1) ):
                if ligated[j%N]: Z_final.dQ[i%N] += C_eff_stacked_pair * Z_BP.dQ[i%N][j%N] * Z_BP.Q[(j+1)%N][(i-1)%N]
                if ligated[j%N]: Z_final.dQ[i%N] += C_eff_stacked_pair * Z_BP.Q[i%N][j%N] * Z_BP.dQ[(j+1)%N][(i-1)%N]
            C_eff_for_coax = C_eff if allow_strained_3WJ else C_eff_no_BP_singlet
            for j in range( i + 1, i + N - 2):
                for k in range( j + 2, i + N - 1):
                    if not ligated[j%N]: continue
                    if not ligated[(k-1)%N]: continue
                    Z_final.dQ[i%N] += Z_BP.dQ[i%N][j%N] * C_eff_for_coax.Q[(j+1)%N][(k-1)%N] * Z_BP.Q[k%N][(i-1)%N] * l * l * l_coax * K_coax
                    Z_final.dQ[i%N] += Z_BP.Q[i%N][j%N] * C_eff_for_coax.dQ[(j+1)%N][(k-1)%N] * Z_BP.Q[k%N][(i-1)%N] * l * l * l_coax * K_coax
                    Z_final.dQ[i%N] += Z_BP.Q[i%N][j%N] * C_eff_for_coax.Q[(j+1)%N][(k-1)%N] * Z_BP.dQ[k%N][(i-1)%N] * l * l * l_coax * K_coax
                for k in range( j + 1, i + N - 1):
                    Z_final.dQ[i%N] += Z_BP.dQ[i%N][j%N] * Z_cut.Q[j%N][k%N] * Z_BP.Q[k%N][(i-1)%N] * K_coax
                    Z_final.dQ[i%N] += Z_BP.Q[i%N][j%N] * Z_cut.dQ[j%N][k%N] * Z_BP.Q[k%N][(i-1)%N] * K_coax
                    Z_final.dQ[i%N] += Z_BP.Q[i%N][j%N] * Z_cut.Q[j%N][k%N] * Z_BP.dQ[k%N][(i-1)%N] * K_coax

    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK
        (C_init, l, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ, N, \
         sequence, ligated, all_ligated, Z_BP, C_eff_basic, C_eff_no_BP_singlet, C_eff_no_coax_singlet, C_eff, Z_linear, Z_cut, Z_coax ) = unpack_variables( self )
        Z_final = self.Z_final
        if not ligated[((i - 1))%N]:
            Z_final.contribs[i%N] +=  [ (Z_linear.Q[i%N][(i-1)%N], [(Z_linear,i%N,(i-1)%N)] ) ]
        else:
            Z_final.contribs[i%N] +=  [ (C_eff_no_coax_singlet.Q[i%N][(i-1)%N] * l / C_std, [(C_eff_no_coax_singlet,i%N,(i-1)%N)] ) ]
            allow_loop_extension = ( not self.in_forced_base_pair ) or ( not self.in_forced_base_pair[i%N] )
            if allow_loop_extension:
                for c in range( i, i + N - 1):
                    if not ligated[c%N]: Z_final.contribs[i%N] +=  [ (Z_linear.Q[i%N][c%N] * Z_linear.Q[(c+1)%N][(i-1)%N], [(Z_linear,i%N,c%N), (Z_linear,(c+1)%N,(i-1)%N)] ) ]
            for j in range( i+1, (i + N - 1) ):
                if ligated[j%N]: Z_final.contribs[i%N] +=  [ (C_eff_stacked_pair * Z_BP.Q[i%N][j%N] * Z_BP.Q[(j+1)%N][(i-1)%N], [(Z_BP,i%N,j%N), (Z_BP,(j+1)%N,(i-1)%N)] ) ]
            C_eff_for_coax = C_eff if allow_strained_3WJ else C_eff_no_BP_singlet
            for j in range( i + 1, i + N - 2):
                for k in range( j + 2, i + N - 1):
                    if not ligated[j%N]: continue
                    if not ligated[(k-1)%N]: continue
                    Z_final.contribs[i%N] +=  [ (Z_BP.Q[i%N][j%N] * C_eff_for_coax.Q[(j+1)%N][(k-1)%N] * Z_BP.Q[k%N][(i-1)%N] * l * l * l_coax * K_coax, [(Z_BP,i%N,j%N), (C_eff_for_coax,(j+1)%N,(k-1)%N), (Z_BP,k%N,(i-1)%N)] ) ]
                for k in range( j + 1, i + N - 1):
                    Z_final.contribs[i%N] +=  [ (Z_BP.Q[i%N][j%N] * Z_cut.Q[j%N][k%N] * Z_BP.Q[k%N][(i-1)%N] * K_coax, [(Z_BP,i%N,j%N), (Z_cut,j%N,k%N), (Z_BP,k%N,(i-1)%N)] ) ]

##################################################################################################
def unpack_variables( self ):
    '''
    This helper function just lets me write out equations without
    using "self" which obscures connection to my handwritten equations
    In C++, will just use convention of object variables like N_, sequence_.
    '''
    return self.params.get_variables() + \
           ( self.N, self.sequence, self.ligated, self.all_ligated,  \
             self.Z_BP,self.C_eff_basic,self.C_eff_no_BP_singlet,self.C_eff_no_coax_singlet,self.C_eff,\
             self.Z_linear,self.Z_cut,self.Z_coax )

