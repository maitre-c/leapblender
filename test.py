import bpy
import Leap
import time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

def enum(**enums):
    return type('Enum', (), enums)

Figure = enum(NONE=0, SECRET=1, TRIANGLE=2, UTRIANGLE=3, CIRCLE=4, UCIRCLE=5)

### ALPHABET ###
# q = quart de cercle
# g = geste
# t = tap
# 1 : g(1,0)        2:  g(0,1)
# 2 : g(-1,0)       4:  g(0,-1)
# 5 : g(1,1)        6:  g(-1,-1)
# 7 : g(1,-1)       8:  g(-1,1)
# 9 : q(0,PI/2)     10: q(PI/2,PI)
# 11: q(PI, 2PI/3)  12: q(2PI/3,0)
# 13: q(0,-PI/2)    14: q(-PI/2,-PI)
# 15: q(-PI,-2PI/3) 16: q(-2PI/3,0)
# 17: tap

#               1       2       3       4       5       6       7       8       9       10      11      12      13      14      15      16      17

machine_etat =   (
              (-1,      -1,     -1,     -1,     -1,      1,     -1,      1,      1,     -1,     -1,     -1,      1,     -1,     -1,     -1,     -1),
              (-1,       2,     -1,     -1,     -1,     -1,     -1,     -1,     -1,      2,     -1,     -1,     -1,      2,     -1,     -1,     -1),
              (-1,      -1,     -1,     -1,     -1,      0,     -1,      0,     -1,     -1,      3,     -1,     -1,     -1,      3,     -1,     -1),
              (-1,      -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,      4,     -1,      0,     -1,     -1,     -1,      0,     -1),
              (-1,      -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,      5,     -1,     -1,     -1,     -1,     -1,     -1),
              (-1,      -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,      6,     -1,     -1,     -1,     -1,     -1),
              (-1,       7,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1),
              (-1,      -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,      8,     -1,     -1,     -1,     -1,     -1),
              (-1,      -1,     -1,     -1,     -1,     -1,     -1,     -1,      9,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1),
              (-1,      -1,     -1,      0,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1,     -1)
            )
            
machine_symb =  (
                {9: {10: {11: {10: {11: {12: {2: {12: {9: {4: Figure.SECRET}}}}}}}, 
                               12: Figure.CIRCLE
                         }}},
                {13: {14: {15: {16: Figure.UCIRCLE}}}},
                {6: {2: {8: Figure.TRIANGLE}}},
                {8: {2: {6: Figure.UTRIANGLE}}},
            )

class SampleListener(Leap.Listener):
    _connected = None
    _hand = None
    _lastFrame = None
    _gestureList = []

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

        self._connected = "CONNECTED"
        # Enable gestures
        #controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        #controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        #controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        print("ON FRAME HERE")
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        self._lastFrame = frame
        if not frame.hands.is_empty:
            self._hand = frame.hands[0]
        self._gestureList.extend(frame.gestures())

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


    def getHandPosition(self):
        if self._connected:
            if self._hand:
                return self._hand.palm_position
    
    def getHandRotation(self):
        if self._connected:
            if self._hand:
                direction = self._hand.direction
                normal = self._hand.palm_normal
                return (direction.pitch,
                        normal.roll,
                        direction.yaw)

    def getGestures(self):
        if self._connected:
            return self._gestureList

    def getFingers(self):
        if self._connected:
            if self._hand:
                return self._hand.fingers

class MyModalOperator(bpy.types.Operator):
    bl_idname = "mine.modal_op"
    bl_label = "Move in XY plane"
    _timer = None
    _controller = None
    _listener = None
    _clicked = False
    _fingersRep = []
    _oldPos = None

    def __init__(self):
        print("Start moving")
 
    def __del__(self):
        if self._listener:
            if self._controller:
                self._controller.remove_listener(self._listener)
        print("Delete Modal")

    def getSelectedObj(self):
        finger = bpy.data.objects["Finger1"]
        for obj in bpy.data.objects:
            if obj not in {bpy.data.objects['Finger1'], bpy.data.objects['Finger2'],\
            bpy.data.objects['Finger3'], bpy.data.objects['Finger4'], bpy.data.objects['Finger5']}:
                print(obj.name)
                if obj.location.x - obj.dimensions.x <= finger.location.x and \
                obj.location.x + obj.dimensions.x >= finger.location.x and \
                obj.location.y - obj.dimensions.y <= finger.location.y and \
                obj.location.y + obj.dimensions.y >= finger.location.y and \
                obj.location.z - obj.dimensions.z <= finger.location.z and \
                obj.location.z + obj.dimensions.z >= finger.location.z:
                    obj.select = True
                    bpy.context.scene.objects.active = obj
                    self._oldPos = self._listener.getHandPosition()
                #print(obj.location.x, obj.location.y, obj.location.z)
                #print(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z, "\n")
                #print(finger.location.x, finger.location.x, finger.location.z)
                #print(finger.dimensions.x, finger.dimensions.y, finger.dimensions.z, "\n")
                
    def execute_script(self, context):
        print("ROCK YOU LIKE A HURICANE")
        leapGestures = self._listener.getGestures()
        while leapGestures:
            gesture = leapGestures.pop(0)
            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                self._clicked = not self._clicked                
                if bpy.context.scene.objects.active:
                    self._oldPos = self._listener.getHandPosition()
                    bpy.context.scene.objects.active.select = False
                    bpy.context.scene.objects.active = None
                return

        if self._clicked:
            if bpy.context.scene.objects.active:
                handVector = self._listener.getHandPosition()
                if handVector:
                    context.object.location.x = handVector.x / 10.0
                    context.object.location.y = -handVector.z / 10.0
                    context.object.location.z = handVector.y / 10.0
                    #if self._oldPos:
                    #   context.object.location.x -= self._oldPos.x
                    #    context.object.location.y -= self._oldPos.z
                    #    context.object.location.z -= self._oldPos.y
                    
                handRotation = self._listener.getHandRotation()
                if handRotation:
                    context.object.rotation_euler.x = handRotation[0]
                    context.object.rotation_euler.y = -handRotation[1]

            fingers = self._listener.getFingers()
            #fingers_id = [f0222    inger.id for finger in fingers]
            #for id in self._fingersRep:
                #if id not in fingers_id:
                    #bpy.data.objects.remove(id)
                    #_fingersRep.remove(str(id))a
            if fingers and not fingers.is_empty:
                i = 1
                for finger in fingers:
                    bpy.data.objects['Finger{}'.format(i)].location.x = finger.tip_position.x / 10.0
                    bpy.data.objects['Finger{}'.format(i)].location.y = -finger.tip_position.z / 10.0
                    bpy.data.objects['Finger{}'.format(i)].location.z = finger.tip_position.y / 10.0
                    i += 1;
                    #if finger.id not in self._fingersRep:
                     #   mesh = bpy.ops.mesh.primitive_uv_sphere_add(location=(finger.tip_position.x /10,\
                    #    -finger.tip_position.z / 10,finger.tip_position.y / 10.0))
                    #    obj = bpy.context.object
                    #    obj.name = str(finger.id)
                    #    self._fingersRep.append(obj.name)
                    #    print(finger.id)
                    
            self.getSelectedObj()
 
    def modal(self, context, event):
        print("HERE I AM")
        if event.type == 'TIMER':  # Apply
            # self.x = event.mouse_x 
            # self.y = event.mouse_y
            self.execute_script(context)
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE':  # Confirm
#            if self._listener:
#                if self._controller:
#                    self._controller.remove_listener(self._listener)
#            context.window_manager.event_timer_remove(self._timer)
            #unregister()
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}
#        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
#            if self._listener:
#                if self._controller:
#                    self._controller.remove_listener(self._listener)
#            return {'CANCELLED'}
        return {'RUNNING_MODAL'}
 
def invoke(self, context, event):
    self._listener = SampleListener()
    self._controller = Leap.Controller()
    self._controller.add_listener(self._listener)
    bpy.context.scene.objects.active = None
    #bpy.ops.object.mode_set(mode='EDIT')
    #self.execute(context)
    self._timer = context.window_manager.event_timer_add(0.005, context.window)
    context.window_manager.modal_handler_add(self)
    return {'RUNNING_MODAL'}
 
#
#    Panel in tools region
#

 
#	Registration
def unregister():
    print("UNREGISTER CALLED")
    bpy.utils.unregister_module(__name__)

def register():
    bpy.utils.register_module(__name__)
 
if __name__ == "__main__":
    register()
 
# Automatically move active object on startup
bpy.ops.mine.modal_op('INVOKE_DEFAULT')