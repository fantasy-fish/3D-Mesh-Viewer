#ifndef _STRUCTURE_H_
#define _STRUCTURE_H_

#pragma once
#include "../Dependencies/glew/glew.h"
#include "../Dependencies/freeglut/freeglut.h"
#include "VertexFormat.h" 
#include "Rectangle.h"

#include <vector>
#include <map>
#include <string>

namespace Model
{
	struct Node {
		std::string label;
		glm::vec3 coord;
		std::string LBP;
		std::string RBP;
		std::string LJP[5];
		std::string LPP;
		std::string PJP[5];
		std::string PPP;
	};

	enum Mode
	{
		NOTYET,
		SETTING,
		COMPLETE
	};

	enum View_Mode
	{
		ALL,
		JOIST,
		BEAM,
		PILLAR
	};

	enum Node_Mode
	{
		NORMAL,
		END
	};

	class Structure
	{
	public:
		Structure();
		~Structure();

		void SetProgram(GLuint program);

		glm::vec3 LoadCSV(const std::string& fName); //return the center of the structure
		void Create();
		void ExportCSV(const std::string& fName);
		void ExportOBJ(const std::string& fName);
		void Draw(enum View_Mode v);
		//callback functions
		void MouseMove(int x, int y);
		void MousePressed(int button, int state, int x, int y);
		void SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model);
		void SetViewport(const glm::vec4& viewport);
		//picking
		bool IsPicked() const;
		const std::vector<glm::vec3> PickPosition() const;
		const std::vector<glm::vec3> EndPosition() const;
		void Elevate();
		void Lower();
		//simplification
		void Simplify(int algoID);
		void Previous();
		void Next();
		void SetInputFName(std::string s);
		//point cloud(dem)
		const std::vector<glm::vec3> PointCloud() const;
		bool LoadPointCloud(const std::string& fName);
		//confidence
		const std::vector<glm::vec4> Confidence();//color coded confidence value
		bool LoadConfidence(const std::string& fName);
		void SetThreshold(float threshold);

	private:
		GLuint vao;
		std::vector<GLuint> vbos;
		GLuint ibo[4];
		GLuint program;
		unsigned int num_indices[4]; //for drawing elements
		std::map<std::string, Node> graph;
		std::map<std::string, unsigned int> IDs;
		std::vector<glm::vec3> endPosition;
		std::vector<glm::vec3> pointCloud;
		std::vector<float> conf_value;
		std::vector<glm::vec4> conf_color;
		//picking
		bool isMousePressed;
		glm::vec2 mousePosition;
		bool picked;
		glm::mat4 model;
		glm::mat4 view;
		glm::mat4 proj;
		glm::vec4 viewport;
		std::vector<std::string> selection;
		glm::vec2 pick_mouse;
		void PickPoint();
		//window selection
		Rectangle* rect;
		Mode rectset;
		void PickRectangle();
		inline bool InRectangle(glm::vec2 p)
		{
			return (p.x > rect->tl.x) && (p.x < rect->br.x) && (p.y > rect->tl.y) && (p.y < rect->br.y);
		}
		//Simplification
		bool firstSim;
		int simNum;//total number of iterations of simplification
		int curID;
		std::string infName;
		std::string outfName;
	};
}
#endif