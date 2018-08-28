#ifndef _CAMERA_H_
#define _CAMERA_H_

#pragma once
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>

namespace Core 
{
	enum MODE {
		ROTATE,
		TRANSLATE
	};

	class Camera
	{
		public:
			Camera(glm::vec3 center);
			~Camera();
			void UpdateView();
			glm::mat4 GetViewMatrix() const;
			//callback functions
			void MouseMove(int x, int y);
			void MousePressed(int button, int state, int x, int y);
		private:
				float yaw;
				float pitch;
				glm::vec3 eye;
				glm::vec3 center;
				glm::vec3 up;
				glm::mat4 viewMatrix;
				bool isMousePressed;
				MODE mode;
				glm::vec2 mousePosition;
	};
}

#endif
