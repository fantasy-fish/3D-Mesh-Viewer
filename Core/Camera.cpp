#include "Camera.h"
#include "../Dependencies/freeglut/freeglut.h"

#include <glm/gtx/string_cast.hpp>
#include <glm/gtx/rotate_vector.hpp>
#include <iostream>

using namespace Core;

Camera::Camera(glm::vec3 center)
{
	eye = center + glm::vec3(2.0f, 2.0f, 2.0f);
	//eye = glm::vec3(4.0f, 4.0f, 4.0f);
	this->center = center;
	up = glm::vec3(0,1,0);
	viewMatrix = glm::lookAt(eye,center,up);
	mode = ROTATE;
}

Camera::~Camera()
{
}

glm::mat4 Camera::GetViewMatrix() const
{
	return viewMatrix;
}

void Camera::UpdateView()
{
	viewMatrix = glm::lookAt(eye, center, up);
}

void Camera::MouseMove(int x, int y)
{
	if (isMousePressed == false)
		return;
	//always compute delta
	//mousePosition is the last mouse position
	glm::vec2 mouse_delta = glm::vec2(x, y) - mousePosition;
	const float mouseX_Sensitivity = 2e-3f;
	const float mouseY_Sensitivity = 2e-3f;
	
	//get current view matrix
	glm::mat4 mat = GetViewMatrix();
	//row major
	glm::vec3 upward(mat[0][1], mat[1][1], mat[2][1]);
	glm::vec3 strafe(mat[0][0], mat[1][0], mat[2][0]);
	switch (mode)
	{
		case ROTATE:
			{
				glm::vec3 eyecenter = center - eye;
				eyecenter = glm::rotate(eyecenter, -1.5f * mouseX_Sensitivity*mouse_delta.x, upward);
				eyecenter = glm::rotate(eyecenter, -1.5f * mouseY_Sensitivity*mouse_delta.y, strafe);
				eye = center - eyecenter;
				up = upward;
				break;
			}
		case TRANSLATE:
			{
				eye += 2 * mouseX_Sensitivity * mouse_delta.x * strafe;
				eye -= 2 * mouseY_Sensitivity * mouse_delta.y * upward;
				center += 2 * mouseX_Sensitivity * mouse_delta.x * strafe;
				center -= 2 * mouseY_Sensitivity * mouse_delta.y * upward;
				break;
			}
	}
	mousePosition = glm::vec2(x, y);
	UpdateView();
}

void Camera::MousePressed(int button, int state, int x, int y)
{
	if (state == GLUT_UP)
	{
		isMousePressed = false;
		if (button == 3)//scroll up
		{
			glm::mat4 mat = GetViewMatrix();
			glm::vec3 forward(mat[0][2], mat[1][2], mat[2][2]);
			const float speed = 0.20f;//how fast we move
			//forward vector must be negative to look forward. 
			eye -= forward * speed;
		}
		if (button == 4)//scroll down
		{
			glm::mat4 mat = GetViewMatrix();
			glm::vec3 forward(mat[0][2], mat[1][2], mat[2][2]);
			const float speed = 0.20f;//how fast we move
			//forward vector must be negative to look forward. 
			eye += forward * speed;
		}
	}
	if (state == GLUT_DOWN)
	{
		isMousePressed = true;
		mousePosition.x = x;
		mousePosition.y = y;
		if (button == GLUT_LEFT_BUTTON)
		{
			mode = ROTATE;
		}
		if (button == GLUT_MIDDLE_BUTTON)
		{
			mode = TRANSLATE;
		}
	}
	UpdateView();
}
