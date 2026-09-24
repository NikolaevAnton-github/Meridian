"""Evaluate the native pose math on a transient AnimInstance, without a world/tick."""
import math
import unreal as u

def rotate(q,v): return q.rotate_vector(v)
def dot(a,b): return a.x*b.x+a.y*b.y+a.z*b.z
def sub(a,b): return u.Vector(a.x-b.x,a.y-b.y,a.z-b.z)
def normal(v):
    length=math.sqrt(dot(v,v)); return u.Vector(v.x/length,v.y/length,v.z/length)
def check_pose():
    component=u.new_object(u.SkeletalMeshComponent)
    obj=u.new_object(u.GASPALSRifleAnimInstance,outer=component)
    obj.set_editor_property('rifle_alpha',1)
    obj.set_editor_property('rifle_aim_alpha',1)
    source=normal(u.Vector(.22681,.97307,.041112))
    rows=[]
    for pitch in (-35,0,35):
        half=math.radians(pitch)*.5
        swept=rotate(u.Quat(math.sin(half),0,0,math.cos(half)),source)
        obj.set_editor_property('rifle_pitch_time',.5-pitch/180)
        for yaw in (-45,0,45):
            obj.set_editor_property('rifle_lean_degrees',0)
            neutral=obj.get_rifle_aim_correction(u.Vector2D(yaw,0)).quaternion()
            neutral_barrel=rotate(neutral,swept)
            # Transform a child offset at the head/chest and a barrel direction
            # through the actual native control result. Pelvis/feet are outside
            # spine_01's subtree as separately verified on the retained graph.
            up=u.Vector(0,0,75)
            right=normal(u.Vector(-neutral_barrel.y,neutral_barrel.x,0))
            baseline=rotate(neutral,up)
            for lean in (-32,32):
                obj.set_editor_property('rifle_lean_degrees',lean)
                q=obj.get_rifle_aim_correction(u.Vector2D(yaw,0)).quaternion()
                barrel=rotate(q,swept)
                displacement=dot(sub(rotate(q,up),baseline),right)
                row=dict(pitch=pitch,yaw=yaw,lean=lean,barrel_dot=dot(barrel,neutral_barrel),signed_head_offset=displacement,
                    passed=dot(barrel,neutral_barrel)>.99999 and displacement*lean>0 and abs(displacement)>25)
                assert row['passed'],row
                rows.append(row)
            obj.set_editor_property('rifle_lean_degrees',0)
            returned=obj.get_rifle_aim_correction(u.Vector2D(yaw,0)).quaternion()
            assert dot(rotate(returned,swept),neutral_barrel)>.99999
    return dict(passed=True,cases=rows,scope='Transient native function and quaternion math only; no actor/world, animation playback, PIE or gameplay simulation.')
