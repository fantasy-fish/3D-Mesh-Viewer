#ifndef _SPHERE_H_
#define _SPHERE_H_

#pragma once
#include "../Dependencies/glew/glew.h"
#include "../Dependencies/freeglut/freeglut.h"
#include "VertexFormat.h" 
#include <vector>

namespace Model
{
	class Sphere 
	{
		public:
			Sphere(float Radius,int Stacks,int Slices,glm::vec3 color);
			~Sphere();
			void Draw();
			void SetProgram(GLuint program);
			void SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model);
			//instancing
			void SetDEM(const std::vector<glm::vec3>& pos, const std::vector<glm::vec4>& color);
			void SetDEMColor(const std::vector<glm::vec4>& color);
			void DrawInstances();
		private:
			GLuint vao;
			std::vector<GLuint> vbos; //vertices, indices, positions
			GLuint program;
			unsigned int num_indices; //for drawing elements
			glm::mat4 model;
			glm::mat4 view;
			glm::mat4 proj;
			unsigned int num_instances;
			//std::vector<glm::vec3> point_cloud;
	};
}
#endif