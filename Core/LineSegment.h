#pragma once
#ifndef _LINESEGMENT_H_
#define _LINESEGMENT_H_

#pragma once
#include "../Dependencies/glew/glew.h"
#include "../Dependencies/freeglut/freeglut.h"
#include "VertexFormat.h" 
#include <vector>

namespace Model
{
	class LineSegment
	{
	public:
		LineSegment();
		~LineSegment();
		bool LoadTXT(const std::string& fName);
		void Draw();
		void SetProgram(GLuint program);
		void SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model);
	private:
		GLuint vao;
		std::vector<GLuint> vbos;
		GLuint program;
		unsigned int num_vertices; //for drawing elements
		glm::mat4 model;
		glm::mat4 view;
		glm::mat4 proj;
	};
}
#endif