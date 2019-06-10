# GUI Demo of 2D Forward Kinematics
## Description
This is an exercise I created as I was reviewing my forward kinemaitcs math while simultaneously learning PyQt5.

The interface contains 3 input boxes which, when changed, will control the lengths of the "robot" arms.

The interface also contains 3 input sliders which, when changed, will control the angle of the "robot" arms.
* Angles are relative to the angle of the arm before it, not to the overall X-axis of the window.

Window displaying the "robot" is updated in real-time.

Location point of the end effector is also displayed in real-time

### To get this running:
* Download both .py files, put in same directory
* pip install the Pyside2 package
* In the GUI file, remove or change line 217 so it's pointing to valid image
