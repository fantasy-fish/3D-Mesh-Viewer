//vertex shader
#version 440 core //lower this version if your card does not support GLSL 4.5
layout(location = 0) in vec3 in_position;
layout(location = 1) in vec4 in_color;
 
uniform mat4 MVP;

out vec4 color;
 
void main()
{
  color = in_color;
  gl_Position = MVP * vec4(in_position, 1);
}