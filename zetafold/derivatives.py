from .base_pair_types import get_base_pair_type_for_tag, get_base_pair_types_for_tag

def _get_log_derivs( self, deriv_parameters = [] ):
    '''
    Output

       d( log Z )/ d( log parameter )

    using simple expressions that require O( N^2 ) time or less after
    the original O( N^3 ) dynamic programming calculations
    '''
    if deriv_parameters == None: return None
    if deriv_parameters == []:
        for tag in self.params.parameter_tags: deriv_parameters.append( tag )

    derivs = [None]*len(deriv_parameters)

    # Derivatives with respect to each Kd
    N = self.N
    Z = self.Z_final.val( 0 )
    for n,parameter in enumerate(deriv_parameters):
        if parameter == 'l':
            # Derivatives with respect to loop closure parameters
            num_internal_linkages = 0.0
            for i in range( N ):
                if not self.ligated[i]: continue
                num_internal_linkages += self.params.l * self.C_eff_no_coax_singlet.val( i+1, i ) / self.params.C_std / Z
            derivs[ n ] = num_internal_linkages
        elif parameter == 'l_BP':
            derivs[ n ] = get_num_base_pairs_closed_by_loops( self )
        elif parameter == 'C_init':
            num_loops = 0.0
            # first count up loops closed by base pairs (i,j), i < j
            for i in range( N ):
                for j in range( i+2, N ):
                    if not self.ligated[i]: continue
                    if not self.ligated[j-1]: continue
                    num_loops += self.params.l**2 * self.params.l_BP * self.C_eff.val(i+1,j-1) * self.Z_BP.val(j,i) / self.Z_final.val(0)
            # one more loop if RNA is a circle.
            if self.ligated[ N-1 ]: num_loops += 1
            derivs[ n ] = num_loops
        elif len(parameter)>=2 and  parameter[:2] == 'Kd':
            if parameter == 'Kd':
                # currently can only handle case where Kd controls *all* of the base pair types
                for base_pair_type in self.params.base_pair_types: assert( base_pair_type.Kd == self.params.base_pair_types[0].Kd )
                derivs[ n ] = - get_bpp_tot( self )
            else:
                Kd_tag = parameter[3:]
                derivs[ n ] = - get_bpp_tot_for_base_pair_type( self, get_base_pair_type_for_tag( self.params, Kd_tag ) )
        elif len(parameter)>=11 and parameter[:11] == 'C_eff_stack':
            # Derivatives with respect to motifs (stacked pairs first)
            if parameter == 'C_eff_stacked_pair':
                bpts1 = self.params.base_pair_types
                bpts2 = self.params.base_pair_types
            else:
                assert( len(parameter) > 11 )
                tags = parameter[12:].split('_')
                assert( len( tags ) == 2 )
                bpts1 = get_base_pair_types_for_tag( self.params, tags[0] )
                bpts2 = get_base_pair_types_for_tag( self.params, tags[1] )
            derivs[ n ] = 0.0
            motif_types_computed = []
            for bpt1 in bpts1:
                for bpt2 in bpts2:
                    if (bpt1, bpt2) in motif_types_computed: continue
                    derivs[ n ] += get_motif_prob( self, bpt1, bpt2 )
                    motif_types_computed.append( (bpt1, bpt2 ) )
                    motif_types_computed.append( (bpt2.flipped, bpt1.flipped ) ) # prevents overcounting
        elif parameter == 'K_coax':
            coax_prob = get_coax_prob( self )
            derivs[ n ] = coax_prob
        elif parameter == 'l_coax':
            coax_prob = get_loop_closed_coax_prob( self )
            coax_prob = 0.0
            C_eff_for_coax = self.C_eff if self.params.allow_strained_3WJ else self.C_eff_no_BP_singlet
            for i in range( N ):
                for j in range( N ):
                    if ( i - j ) % N < 2: continue
                    if not self.ligated[ i-1 ]: continue
                    if not self.ligated[ j ]: continue
                    coax_prob += self.Z_coax.val(i,j) * self.params.l_coax * self.params.l**2 * C_eff_for_coax.val(j+1,i-1) / Z
            derivs[ n ] = coax_prob
        else:
            print "Did not recognize parameter ", parameter
            pass

    return derivs

def get_bpp_tot_for_base_pair_type( self, base_pair_type ):
    assert( self.calc_all_elements )
    bpp = 0.0
    N = self.N
    for i in range( N ):
        for j in range( N ):
            if self.Z_BPq[base_pair_type].val(i,j) == 0: continue
            bpp += self.Z_BPq[base_pair_type].val(i,j) * self.Z_BPq[base_pair_type.flipped].val(j,i) * base_pair_type.Kd / self.Z_final.val(0)
    return bpp

def get_bpp_tot( self ):
    bpp_tot = []
    for base_pair_type in self.params.base_pair_types: bpp_tot.append( get_bpp_tot_for_base_pair_type( self, base_pair_type ) )
    return sum( bpp_tot ) / 2.0

def get_num_base_pairs_closed_by_loops( self ):
    # base pair forms a stacked pair with previous pair
    #
    #     ~~~~~
    #  i+1     j-1
    #    |     |
    #    i ... j
    #      bp1
    #
    num_base_pairs_closed_by_loops = 0.0
    N = self.N
    # this is slightly different than num_closed_loops for C_init -- each base pair is counted
    # if it closes a loop in either direction (i<j) vs. (i>j)
    for i in range( N ):
        for j in range( N ):
            if ( j - i ) % N < 2: continue
            if not self.ligated[i]: continue
            if not self.ligated[(j-1)%N]: continue
            num_base_pairs_closed_by_loops += self.params.l**2 * self.params.l_BP * self.C_eff.val(i+1,j-1) * self.Z_BP.val(j,i) / self.Z_final.val(0)
    return num_base_pairs_closed_by_loops

def get_motif_prob( self, base_pair_type, base_pair_type2 ):
    # base pair forms a stacked pair with previous pair
    #
    #      bp2
    #  i+1 ... j-1
    #    |     |
    #    i ... j
    #      bp1
    #
    motif_prob = 0.0
    Z_BPq1 = self.Z_BPq[base_pair_type.flipped]
    Z_BPq2 = self.Z_BPq[base_pair_type2]
    N = self.N
    for i in range( N ):
        for j in range( N ):
            if ( j - i ) % N < 3: continue
            if not self.ligated[i]: continue
            if not self.ligated[(j-1)%N]: continue
            if not base_pair_type.flipped.is_match( self.sequence[j],self.sequence[i] ): continue
            if not base_pair_type2       .is_match( self.sequence[(i+1)%N],self.sequence[(j-1)%N] ): continue
            motif_prob += self.params.C_eff_stack[base_pair_type][base_pair_type2] * Z_BPq1.val(j,i) * Z_BPq2.val(i+1,j-1) / self.Z_final.val(0)
    if base_pair_type == base_pair_type2.flipped: motif_prob /= 2.0 # symmetry correction
    return motif_prob

def get_loop_closed_coax_prob( self ):
    # If the two coaxially stacked base pairs are connected by a loop.
    #
    #       ~~~~
    #   -- j    i --
    #  /   :    :   \
    #  \   :    :   /
    #   ------------
    #
    coax_prob = 0.0
    C_eff_for_coax = self.C_eff if self.params.allow_strained_3WJ else self.C_eff_no_BP_singlet
    N = self.N
    for i in range( N ):
        for j in range( N ):
            if ( i - j ) % N < 2: continue
            if not self.ligated[ i-1 ]: continue
            if not self.ligated[ j ]: continue
            coax_prob += self.Z_coax.val(i,j) * self.params.l_coax * self.params.l**2 * C_eff_for_coax.val(j+1,i-1) / self.Z_final.val(0)
    return coax_prob

def get_loop_open_coax_prob( self ):
    # If the two stacked base pairs are in split segments
    #
    #      \    /
    #   -- j    i --
    #  /   :    :   \
    #  \   :    :   /
    #   ------------
    #
    coax_prob = 0.0
    N = self.N
    for i in range( N ):
        for j in range( N ):
            coax_prob += self.Z_coax.val(i,j) * self.Z_cut.val(j,i) / self.Z_final.val(0)
    return coax_prob

def get_coax_prob( self ):
    return get_loop_closed_coax_prob( self ) + get_loop_open_coax_prob( self )

