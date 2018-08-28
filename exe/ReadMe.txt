This program is a 3D viewer which can visualize the SSG data and run real-time simpilification method on it.

Dependency:
The only package we need is python(x86) and numpy.
The recommended version of python is 2.7.13, which comes with pip. The download link: https://www.python.org/downloads/release/python-2713/
When you install python, make sure to select "Add python.exe to Path" and pip.
After installing the python, just open the cmd window and type "pip install numpy".


Version:
V2(integrated with the python simplification module)

System requirements:
Window 7, 8, 8.1, 10

Control:
Press 'o' to export obj model
Press 'c' to export csv file
Press 'v' for different view modes (all,joist,beam,pillar)
Press 'n' to highlight the end nodes
Press 'r' to load a new file
Press 'a' to view the result of the previous iteration of simplification
Press 'd' to view the result of the next iteration of simplification
Press 'p' to visualize the initial point cloud(dem&confidence)
Press 's' to set the threshold for the visulization of the confidence
Press 'l' to visualize the 3d line segments
Press the left button to select the node
Press the right button to select the simplification algorithms
Press 'ctrl' when dragging the mouse to do window selection
Press 'alt' when dragging the mouse to move the camera(left button to rotate, middle button to translate and zoom)
Press 'esc' to exit