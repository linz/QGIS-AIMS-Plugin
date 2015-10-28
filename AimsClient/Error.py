################################################################################
#
# Copyright 2015 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the 
# LICENSE file for more information.
#
################################################################################

class Error ( Exception ):
    """Exception class for Address exceptions"""

    def __init__( self, message ) :
        Exception.__init__(self,message)
