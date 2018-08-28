#include "Sphere.h"
#include <iostream>
#include <string>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>

using namespace Model;

Sphere::Sphere(float Radius, int Stacks, int Slices,glm::vec3 color)
{
	GLuint vao;
	GLuint vbo;
	GLuint ibo;

	std::vector<unsigned int> indices;//indexed drawing
	std::vector<VertexFormat> vertices;

	// Calc The Vertices
	for (int i = 0; i <= Stacks; ++i) {

		float V = i / (float)Stacks;
		
		float phi = V * glm::pi <float>();

		// Loop Through Slices
		for (int j = 0; j <= Slices; ++j) {

			float U = j / (float)Slices;
			float theta = U * (glm::pi <float>() * 2);

			// Calc The Vertex Positions
			float x = cosf(theta) * sinf(phi);
			float y = cosf(phi);
			float z = sinf(theta) * sinf(phi);

			// Push Back Vertex Data
			vertices.push_back(VertexFormat(glm::vec3(x, y, z) * Radius,
				glm::vec4(color.r, color.g, color.b, 1)));
		}
	}

	// Calc The Index Positions
	for (int i = 0; i < Slices * Stacks + Slices; ++i) {

		indices.push_back(i);
		indices.push_back(i + Slices + 1);
		indices.push_back(i + Slices);

		indices.push_back(i + Slices + 1);
		indices.push_back(i);
		indices.push_back(i + 1);
	}
	num_indices = indices.size();

	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);

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
}

Sphere::~Sphere()
{
	//delete VAO and VBOs (if many)
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();
}

void Sphere::SetProgram(GLuint program)
{
	this->program = program;
}

void Sphere::SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model)
{
	this->proj = proj;
	this->view = view;
	this->model = model;
}

void Sphere::Draw()
{
	glUseProgram(program);
	glm::mat4 mvp = proj*view*model;
	GLuint MatrixID = glGetUniformLocation(program, "MVP");
	glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &mvp[0][0]);
	glBindVertexArray(vao);
	glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, 0);
}

void Sphere::SetDEM(const std::vector<glm::vec3>& pos, const std::vector<glm::vec4>& color)
{
	glBindVertexArray(vao);

	GLuint position_buffer;
	glGenBuffers(1, &position_buffer);
	glBindBuffer(GL_ARRAY_BUFFER, position_buffer);
	glBufferData(GL_ARRAY_BUFFER, pos.size() * sizeof(glm::vec3), &pos[0], GL_STATIC_DRAW);
	
	glEnableVertexAttribArray(2);
	glVertexAttribPointer(2, 3,
		GL_FLOAT, GL_FALSE, 0, (void*)0);

	glVertexAttribDivisor(2, 1); // each sphere has different position

	GLuint color_buffer;
	glGenBuffers(1, &color_buffer);
	glBindBuffer(GL_ARRAY_BUFFER, color_buffer);
	glBufferData(GL_ARRAY_BUFFER, color.size() * sizeof(glm::vec4), &color[0], GL_STATIC_DRAW);

	glEnableVertexAttribArray(3);
	glVertexAttribPointer(3, 4,
		GL_FLOAT, GL_FALSE, 0, (void*)0);

	glVertexAttribDivisor(3, 1); // each sphere has different position

	num_instances = pos.size();
	this->vbos.push_back(position_buffer);
	this->vbos.push_back(color_buffer);
}

void Sphere::SetDEMColor(const std::vector<glm::vec4>& color)
{
	glNamedBufferSubData(vbos[3], 0, sizeof(glm::vec4)*color.size(), &color[0]);
}

void Sphere::DrawInstances()
{
	glUseProgram(program);
	glm::mat4 mvp = proj*view*model;
	GLuint MatrixID = glGetUniformLocation(program, "MVP");
	glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &mvp[0][0]);
	glBindVertexArray(vao);
	glDrawElementsInstanced(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, 0 ,num_instances);
}