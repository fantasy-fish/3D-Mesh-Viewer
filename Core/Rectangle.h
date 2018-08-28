#ifndef _RECTANGLE_H_
#define _RECTANGLE_H_

#pragma once

#include "../Dependencies/glew/glew.h"
#include "../Dependencies/freeglut/freeglut.h"
#include "VertexFormat.h" 
#include <vector>

namespace Model
{
	class Rectangle 
	{
		public:
			Rectangle();
			~Rectangle();
			void Draw();
			void SetProgram(GLuint program);
			void SetTransform(float w, float h);
			//rectangle parameters
			glm::vec2 tl;
			glm::vec2 br;
		private:
			GLuint vao;
			std::vector<GLuint> vbos;
			GLuint program;
			unsigned int num_indices; //for drawing elements
			glm::mat4 model;
			glm::mat4 view;
			glm::mat4 proj;
	};
}
#endif