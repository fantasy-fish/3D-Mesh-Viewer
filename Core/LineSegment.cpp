#include "LineSegment.h"
#include <fstream>
#include <iostream>
#include <sstream>

using namespace Model;

LineSegment::LineSegment()
{
}

LineSegment::~LineSegment()
{
	//delete VAO and VBOs (if many)
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();
}

bool LineSegment::LoadTXT(const std::string& fName)
{
	std::ifstream stream(fName);
	if (!stream)
	{
		std::cout << "Can't find the txt file" << std::endl;
		return false;
	}

	std::vector<VertexFormat> vertices;
	std::string line;
	std::getline(stream, line);//read the header
	while (getline(stream, line))
	{
		std::istringstream s(line);
		std::string field;
		float x1, y1, z1, x2, y2, z2;
		//x1 y1 z1 x2 y2 z2
		std::getline(s, field, ' ');
		x1 = stof(field);
		std::getline(s, field, ' ');
		y1 = stof(field);
		std::getline(s, field, ' ');
		z1 = stof(field);
		std::getline(s, field, ' ');
		x2 = stof(field);
		std::getline(s, field, ' ');
		y2 = stof(field);
		std::getline(s, field);
		z2 = stof(field);
		vertices.push_back(VertexFormat(glm::vec3(x1, y1, z1),
			glm::vec4(128.0/255,66.0/255,244.0/255,1)));
		vertices.push_back(VertexFormat(glm::vec3(x2, y2, z2),
			glm::vec4(128.0 / 255, 66.0 / 255, 244.0 / 255, 1)));
	}

	num_vertices = vertices.size();

	//create the vao and vbo
	GLuint vao;
	GLuint vbo;

	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);

	glGenBuffers(1, &vbo);
	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(VertexFormat),
		&vertices[0], GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
		sizeof(VertexFormat), (void*)0);
	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,
		sizeof(VertexFormat),
		(void*)(offsetof(VertexFormat, VertexFormat::color)));

	this->vao = vao;
	this->vbos.push_back(vbo);
	return true;
}

void LineSegment::SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model)
{
	this->proj = proj;
	this->view = view;
	this->model = model;
}

void LineSegment::SetProgram(GLuint program)
{
	this->program = program;
}

void LineSegment::Draw()
{
	glUseProgram(program);
	glm::mat4 mvp = proj*view*model;
	GLuint MatrixID = glGetUniformLocation(program, "MVP");
	glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &mvp[0][0]);
	glBindVertexArray(vao);
	glDrawArrays(GL_LINES, 0, num_vertices);
}