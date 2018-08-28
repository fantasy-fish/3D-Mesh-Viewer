#include "Rectangle.h"
#include <iostream>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/string_cast.hpp>

using namespace Model;

Rectangle::Rectangle()
{

	GLuint vao;
	GLuint vbo;
	GLuint ibo;

	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);

	std::vector<unsigned int> indices;//indexed drawing
	std::vector<VertexFormat> vertices;

	//vertices
	vertices.push_back(VertexFormat(glm::vec3(-1, 1, 0.5), glm::vec4(0, 1, 1, 1)));
	vertices.push_back(VertexFormat(glm::vec3( 1, 1, 0.5), glm::vec4(0, 1, 1, 1)));
	vertices.push_back(VertexFormat(glm::vec3( 1,-1, 0.5), glm::vec4(0, 1, 1, 1)));
	vertices.push_back(VertexFormat(glm::vec3(-1,-1, 0.5), glm::vec4(0, 1, 1, 1)));

	//indices
	indices.push_back(0);
	indices.push_back(1);
	indices.push_back(2);
	indices.push_back(3);

	num_indices = indices.size();

	glGenBuffers(1, &vbo);
	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(VertexFormat),
		&vertices[0], GL_STATIC_DRAW);

	glGenBuffers(1, &ibo);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo);
	glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int),
		&indices[0], GL_STATIC_DRAW);

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
		sizeof(VertexFormat), (void*)0);
	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,
		sizeof(VertexFormat),
		(void*)(offsetof(VertexFormat, VertexFormat::color)));

	this->vao = vao;
	this->vbos.push_back(vbo);
	this->vbos.push_back(ibo);

	//set the matrices
	this->model = glm::mat4(1.0);
	this->proj = glm::mat4(1.0);
	this->view = glm::mat4(1.0);
}

Rectangle::~Rectangle()
{
	//delete VAO and VBOs (if many)
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();
}

void Rectangle::Draw()
{
	glUseProgram(program);
	glm::mat4 mvp = proj*view*model;
	GLuint MatrixID = glGetUniformLocation(program, "MVP");
	glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &mvp[0][0]);
	glBindVertexArray(vao);
	glDrawElements(GL_LINE_LOOP, num_indices, GL_UNSIGNED_INT, 0);
}

void Rectangle::SetProgram(GLuint program)
{
	this->program = program;
}

void Rectangle::SetTransform(float w, float h)
{
	glm::vec2 tmptl, tmpbr;
	//convert tl, br to ndc coordinate
	tmptl.x = (tl.x - w / 2) / (w/2);
	tmpbr.x = (br.x - w / 2) / (w/2);
	tmptl.y = (h / 2 - tl.y) / (h/2);
	tmpbr.y = (h / 2 - br.y) / (h/2);
	//-1~1,-1~1,-1~1
	model = glm::mat4(1.0);
	model = glm::translate(model, glm::vec3(glm::mix(tmptl,tmpbr,0.5), 0));
	model = glm::scale(model, glm::vec3((tmpbr.x - tmptl.x)*0.5, (tmptl.y - tmpbr.y)*0.5, 1.0));
}