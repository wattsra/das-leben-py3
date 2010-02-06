'''
 * This file is part of La Vida
 * Copyright (C) 2009 Mike Hibbert
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
'''

from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import pygame
from pygame.locals import *
from vector_3d import *
from object_3d import *
from collisions import BoundingBox3d
import random


REGION_NORMAL = 1
REGION_EDITING = 2

# which parts of the height values to change
quad_adjustments = []; qadd = quad_adjustments.append
# first row
qadd( { 'ul': 0.0, 'ur': 1.0, 'll': 0.0, 'lr': 0.0, 'name':'top left' } )
qadd( { 'ul': 1.0, 'ur': 1.0, 'll': 0.0, 'lr': 0.0, 'name':'top middle' } )
qadd( { 'ul': 1.0, 'ur': 0.0, 'll': 0.0, 'lr': 0.0, 'name':'top right' } )
# second row
qadd( { 'ul': 0.0, 'ur': 1.0, 'll': 0.0, 'lr': 1.0, 'name':'middle left' } )
qadd( { 'ul': 1.0, 'ur': 1.0, 'll': 1.0, 'lr': 1.0, 'name':'middle middle' } )
qadd( { 'ul': 1.0, 'ur': 0.0, 'll': 1.0, 'lr': 0.0, 'name':'middle right' } )
# third row
qadd( { 'ul': 0.0, 'ur': 0.0, 'll': 0.0, 'lr': 1.0, 'name':'bottom left' } )
qadd( { 'ul': 0.0, 'ur': 0.0, 'll': 1.0, 'lr': 1.0, 'name':'bottom middle' } )
qadd( { 'ul': 0.0, 'ur': 0.0, 'll': 1.0, 'lr': 0.0, 'name':'bottom right' } )

class RegionQuad( BoundingBox3d ):
    def __init__( self, a_X=0.0, a_Y=0.0, a_Z=0.0, a_Size=0.5 ):
        BoundingBox3d.__init__( self, a_X, a_Y, a_Z, a_Size )
        
        # y values for quad
        self.ul = 0.0
        self.ur = 0.0
        self.ll = 0.0
        self.lr = 0.0
        
        # quad size
        self.size = a_Size
        
        self.selected = False
        self.compiled = False
        self.oldListID = 0
        self.listID = 0        
        
    def __repr__( self ):
        return "ul:%f,ur:%f,ll:%f,lr:%f" % ( self.ul, self.ur, self.ll, self.lr )
    
    def SetHeights( self, a_Heights ):
        self.ul = a_Heights[ 'ul' ]
        self.ur = a_Heights[ 'ur' ]
        self.ll = a_Heights[ 'll' ]
        self.lr = a_Heights[ 'lr' ]
        
       
    def SetAsObject( self, a_Object3d ):
        self.ObjectToRender = a_Object3d
        self.ObjectToRender.SetPosition( self.GetX(), self.GetY(), self.GetY() )
        
    def GetGLName( self ):
        return self.ObjectToRender.GetGLName()
        
    def compile_list( self ):
        if not self.compiled:
            self.listID = glGenLists( 1 )
            glNewList( self.listID, GL_COMPILE )
            glBegin( GL_QUADS )
            colour_adjust = random.random()
            glColor3f( 0.5 - colour_adjust, 1.0 - colour_adjust , 0.5 - colour_adjust ) # green grass
            glNormal3f( 0.0, 1.0, 0.0 )
            glVertex3f( float( self.GetX() - ( self.size / 2.0 ) ) , float( self.GetY() + self.ul ), float( self.GetZ() + ( self.size / 2.0 ) ) )
            glNormal3f( 0.0, 1.0, 0.0 )
            glVertex3f( float( self.GetX() + ( self.size / 2.0 ) ) , float( self.GetY() + self.ur ), float( self.GetZ() + ( self.size / 2.0 ) ) )
            glNormal3f( 0.0, 1.0, 0.0 )
            glVertex3f( float( self.GetX() + ( self.size / 2.0 ) ) , float( self.GetY() + self.lr ), float( self.GetZ() - ( self.size / 2.0 ) ) )
            glNormal3f( 0.0, 1.0, 0.0 )
            glVertex3f( float( self.GetX() - ( self.size / 2.0 ) ) , float( self.GetY() + self.ll ), float( self.GetZ() - ( self.size / 2.0 ) ) )
            glEnd()
            glEndList()
            
    def recompile_list( self ):
        self.oldListID = self.listID
        glDeleteLists( self.listID, 1 )
        self.compile_list()
        
    def __del__( self ):
        glDeleteLists( self.listID, 1 )
    
    
class Region( Vector3d ):
    def __init__( self, a_X=0.0, a_Y=0.0, a_Z=0.0, a_Width=50, a_Size=0.5 ):
        Vector3d.__init__( self, a_X, a_Y, a_Z )
        self.quads = []; qadd = self.quads.append
        self.quadIDS = []; iadd = self.quadIDS.append
        
        self.m_Width = a_Width
        self.m_Size = a_Size
        
        for x in xrange( a_Width ):
            for z in xrange( a_Width ):
                rq = RegionQuad( a_X + ( float( x ) * a_Size ), 
                                  a_Y, 
                                  a_Z + ( float( z ) * a_Size ),
                                  a_Size ) 
                rq.SetAsObject( Object3d() )
                rq.compile_list()
                
                qadd( rq )
                iadd( rq.listID )
                
        
        self.mode = REGION_NORMAL
        
        self.selected_quads = []
        
        self.m_ObjectType = OBJECT_3D_MESH
        
        self.compiled = False
        
    def Save( self, a_Filename ):
        f = open( a_Filename, "w" )
        for quad in self.quads:
            f.writelines( quad )
            
        f.close()
        
    def Load( self, a_Filename ):
        self.DeleteAllQuads()
        
        f = open( a_Filename, "r" )
        lines = f.read()
        
        self.quads = []; qadd = self.quads.append
        self.quadIDS = []; iadd = self.quadIDS.append
        for x in xrange( self.m_Width ):
            for z in xrange( self.m_Width ):
                rq = RegionQuad( self.GetX() + ( float( x ) * self.m_Size ), 
                                  self.GetY(), 
                                  self.GetZ() + ( float( z ) * self.m_Size ),
                                  self.m_Size ) 
                rq.SetAsObject( Object3d() )
                line = lines[ ( x * self.m_Width ) + z ]
                parts = line.split(",")
                heights = {}
                for part in parts:
                    key, value = part.split(":")
                    heights[ key ] = value
                    
                rq.SetHeights( heights )
                rq.compile_list()
                
                qadd( rq )
                iadd( rq.listID )
        
    def DeleteAllQuads( self ):
        for quad in self.quads:
            del quad
            
    def ClearSelection( self ):
        self.selected_quads = []
        
    def SelectWithPoint( self, a_Point ):
        for quad in self.quads:
            if quad.PointInside( a_Point ):
                self.selected_quads.append( quad )
        
    def SetMode( self, a_Mode ):
        self.mode = a_Mode
                
    def Draw( self ):
        glPushMatrix()
        glTranslatef( self.GetX(), self.GetY(), self.GetZ() )
        
        glCallLists( self.quadIDS )
        
        glPopMatrix()
            
        #if self.mode == REGION_EDITING:
            #for quad in self.quads:
                #quad.SetDrawMode( OBJECT_3D_DRAW_WIREFRAME ) 
                #quad.Draw()
                #quad.SetDrawMode( OBJECT_3D_DRAW_SOLID )
        
            #for quad in self.selected_quads:
                #quad.SetDrawMode( OBJECT_3D_DRAW_HIGHLIGHTED ) 
                #quad.Draw()
                #quad.SetDrawMode( OBJECT_3D_DRAW_SOLID )
                
                
    def GetGLNames( self ):
        quads = []; qadd = quads.append
        for quad in self.quads:
            qadd( quad.GetGLName() )
            
        return quads
    
    def raiseQuad( self, a_Location ):
        for x in xrange( self.m_Width ):
            for z in xrange( self.m_Width ):
                quad = self.quads[ ( x * self.m_Width ) + z ]
                if quad.PointInsideXZPlane( a_Location ):
                    
                    cur_x = x - 1
                    cur_z = z - 1
                    for u in xrange( 3 ):
                        for v in xrange( 3 ):
                            try:
                                adjusted_quad = self.quads[ ( cur_x * self.m_Width ) + cur_z ]
                                line = adjusted_quad.__repr__()
                                parts = line.split(",")
                                heights = {}
                                adjustment = quad_adjustments[ ( u * 3 ) + v ]
                                if adjustment[ 'name' ] == "middle middle": 
                                    adjusted_quad = quad
                                for part in parts:
                                    key, value = part.split(":")
                                    heights[ key ] = float( value ) + ( float( adjustment[ key ] ) * float( self.m_Size / 5.0 ) )
                                adjusted_quad.SetHeights( heights )
                                if adjusted_quad == quad: 
                                    xco, yco, zco, wco = adjusted_quad.GetPosition() 
                                    yco += float( self.m_Size ) / 5.0 
                                    adjusted_quad.SetPostion( xco, yco, zco )
                                adjusted_quad.recompile_list()
                                self.quadIDS[ self.quadIDS.index( adjusted_quad.oldListID ) ] = adjusted_quad.listID
                            except:
                                pass
                            
                            cur_x += 1
                            
                        cur_x -= 3
                        cur_z += 1
                        
                    
                    quad.SetHeights( heights )
                    quad.recompile_list()
                    self.quadIDS[ self.quadIDS.index( quad.oldListID ) ] = quad.listID
                    
    
            
        
    
    def getQuad( self, a_X, a_Z ):
        try:
            self.quads[ ( a_X * self.m_Width ) + a_Z ]
        except:
            pass
        return quad
        
        
        