#include "Structure.h"
#include "Python.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <limits>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtx/transform.hpp>

using namespace Model;

Structure::Structure()
{
	isMousePressed = false;
	picked = false;
	rect = new Rectangle();
	rectset = NOTYET;
	firstSim = true;
	simNum = 0;
	curID = 0;
}

Structure::~Structure()
{
	//delete VAO and VBOs (if many)
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();
	//delete graph
	this->graph.clear();
	this->IDs.clear();
	this->endPosition.clear();
	//delete rect
	delete(rect);
}

void Structure::SetProgram(GLuint program) 
{ 
	this->program = program; 
	rect->SetProgram(program);
}

glm::vec3 Structure::LoadCSV(const std::string& fName)
{
	std::ifstream stream(fName);
	if (!stream)
	{
		std::cout << "Can't find the csv file" << std::endl;
		return glm::vec3(0,0,0);
	}
	std::string line;
	std::getline(stream, line);//read the header
	while (getline(stream, line))
	{
		//cout<<line<<endl;
		std::istringstream s(line);
		std::string field;
		//ID
		std::getline(s, field, ',');
		std::string ID = field;
		//node
		Node n;
		getline(s, field, ',');//label
		n.label = field;
		getline(s, field, ',');//x
		n.coord[0] = stof(field);
		getline(s, field, ',');//y
		n.coord[1] = stof(field);
		getline(s, field, ',');//z
		n.coord[2] = stof(field);
		if (!isfinite(n.coord.x) || !isfinite(n.coord.y) || !isfinite(n.coord.z))
			std::cout << "Wrong format in Node " << ID << std::endl;
		getline(s, field, ',');
		n.LBP = field;
		getline(s, field, ',');
		n.RBP = field;
		for (int i = 0; i < 5; i++)
		{
			getline(s, field, ',');
			n.LJP[i] = field;
		}
		getline(s, field, ',');
		n.LPP = field;
		for (int i = 0; i < 5; i++)
		{
			getline(s, field, ',');
			n.PJP[i] = field;
		}
		getline(s, field);
		n.PPP = field;
		//add this line for linux code
		//n.PPP.pop_back();
		graph.insert(make_pair(ID, n));
	}
	
	std::map<std::string, Node>::iterator it;
	int num = 0;
	glm::vec3 center;
	for (it = graph.begin(); it != graph.end(); it++)
	{
		IDs[it->first] = num++;
		center += it->second.coord / (1.0f*graph.size());
		if (it->second.label == "end")
			endPosition.push_back(
				glm::vec3(it->second.coord.x,it->second.coord.y, it->second.coord.z));
	}
	return glm::vec3(center.x,center.y,center.z);
}

void Structure::Create()
{
	GLuint vao;
	GLuint vbo;

	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);

	std::vector<unsigned int> indices;//indexed drawing
	std::vector<unsigned int> indicesB, indicesJ, indicesP;
	std::map<std::string, Node>::iterator it;
	for (it = graph.begin(); it != graph.end(); it++)
	{
		//Joist
		for (int i = 0; i < 5; i++)
		{
			if (it->second.LJP[i] != "None")
			{
				indices.push_back(3 * IDs[it->first]);
				indices.push_back(3 * IDs[it->second.LJP[i]]);
				indicesJ.push_back(3 * IDs[it->first]);
				indicesJ.push_back(3 * IDs[it->second.LJP[i]]);
			}
			if (it->second.PJP[i] != "None")
			{
				indices.push_back(3 * IDs[it->first]);
				indices.push_back(3 * IDs[it->second.PJP[i]]);
				indicesJ.push_back(3 * IDs[it->first]);
				indicesJ.push_back(3 * IDs[it->second.PJP[i]]);
			}
		}
		//Beam
		if (it->second.LBP != "None")
		{
			indices.push_back(3*IDs[it->first]+1);
			indices.push_back(3*IDs[it->second.LBP]+1);
			indicesB.push_back(3 * IDs[it->first] + 1);
			indicesB.push_back(3 * IDs[it->second.LBP] + 1);
		}
		if (it->second.RBP != "None")
		{
			indices.push_back(3*IDs[it->first]+1);
			indices.push_back(3*IDs[it->second.RBP]+1);
			indicesB.push_back(3 * IDs[it->first] + 1);
			indicesB.push_back(3 * IDs[it->second.RBP] + 1);
		}
		//Pillar
		if (it->second.LPP != "None")
		{
			indices.push_back(3*IDs[it->first]+2);
			indices.push_back(3*IDs[it->second.LPP]+2);
			indicesP.push_back(3 * IDs[it->first] + 2);
			indicesP.push_back(3 * IDs[it->second.LPP] + 2);
		}
		if (it->second.PPP != "None")
		{
			indices.push_back(3*IDs[it->first]+2);
			indices.push_back(3*IDs[it->second.PPP]+2);
			indicesP.push_back(3 * IDs[it->first] + 2);
			indicesP.push_back(3 * IDs[it->second.PPP] + 2);
		}
	}
	num_indices[0] = indices.size();
	num_indices[1] = indicesJ.size();
	num_indices[2] = indicesB.size();
	num_indices[3] = indicesP.size();

	std::vector<VertexFormat> vertices;
	for (it = graph.begin(); it != graph.end(); it++)
	{
		//Joist,red
		vertices.push_back((VertexFormat(it->second.coord,
			glm::vec4(1, 0, 0, 1))));
		//Beam,green
		vertices.push_back((VertexFormat(it->second.coord,
			glm::vec4(0, 1, 0, 1))));
		//Pillar,blue
		vertices.push_back((VertexFormat(it->second.coord,
			glm::vec4(0, 0, 1, 1))));
	}

	glGenBuffers(1, &vbo);
	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(VertexFormat),
				&vertices[0], GL_STATIC_DRAW);
 
	glGenBuffers(4,	ibo);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo[0]);
	glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int),
				&indices[0], GL_STATIC_DRAW);
	if (indicesJ.size())
	{
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo[1]);
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, indicesJ.size() * sizeof(unsigned int),
			&indicesJ[0], GL_STATIC_DRAW);
	}
	if (indicesB.size())
	{
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo[2]);
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, indicesB.size() * sizeof(unsigned int),
			&indicesB[0], GL_STATIC_DRAW);
	}
	if (indicesP.size())
	{
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo[3]);
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, indicesP.size() * sizeof(unsigned int),
			&indicesP[0], GL_STATIC_DRAW);
	}

	glEnableVertexAttribArray(0);
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
						sizeof(VertexFormat), (void*)0);
	glEnableVertexAttribArray(1);
	glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,
						sizeof(VertexFormat),
						(void*)(offsetof(VertexFormat, VertexFormat::color)));

	this->vao = vao;
	this->vbos.push_back(vbo);
	for(int i=0;i<4;i++)
		this->vbos.push_back(ibo[i]);
}

void Structure::ExportCSV(const std::string& fName)
{
	std::string csv_name = fName + ".csv";
	std::ofstream csv_file;
	csv_file.open(csv_name);
	csv_file << "#id,label,x,y,z,LBP,RBP,LJP[0],LJP[1],LJP[2],LJP[3],LJP[4]";
	csv_file << "LPP,PJP[0],PJP[1],PJP[2],PJP[3],PJP[4],PPP" << std::endl;
	std::map<std::string, Node>::iterator it;
	for (it = graph.begin(); it != graph.end(); it++)
	{
		csv_file << it->first;
		csv_file << ',';
		csv_file << it->second.label;
		csv_file << ',';
		csv_file << it->second.coord.x;
		csv_file << ',';
		csv_file << it->second.coord.y;
		csv_file << ',';
		csv_file << it->second.coord.z;
		csv_file << ',';
		csv_file << it->second.LBP;
		csv_file << ',';
		csv_file << it->second.RBP;
		csv_file << ',';
		for (int i = 0; i < 5; i++)
		{
			csv_file << it->second.LJP[i];
			csv_file << ',';
		}
		csv_file << it->second.LPP;
		csv_file << ',';
		for (int i = 0; i < 5; i++)
		{
			csv_file << it->second.PJP[i];
			csv_file << ',';
		}
		csv_file << it->second.PPP;
		csv_file << std::endl;
	}
	csv_file.close();

	std::cout << "Complete!" << std::endl;
}

void Structure::ExportOBJ(const std::string& fName)
{
	//mtl
	std::string mtl_name = fName + ".mtl";
	std::ofstream mtl_file;
	mtl_file.open(mtl_name);
	//comment
	mtl_file << "# MTL file exported from CSV\n";
	mtl_file << "# Material Count: 3\n";
	mtl_file << "\n";
	//joist
	mtl_file << "newmtl joist\n";
	mtl_file << "Ns 96.078431\n";
	mtl_file << "Ka 1.000000 1.000000 1.000000\n";
	mtl_file << "Kd 1.000000 0.000000 0.000000\n";
	mtl_file << "Ks 0.500000 0.500000 0.500000\n";
	//mtl_file << "Ke 0.000000 0.000000 0.000000\n";
	mtl_file << "Ni 1.000000\n";
	mtl_file << "d 1.000000\n";
	mtl_file << "illum 2\n";
	mtl_file << "\n";
	//beam
	mtl_file << "newmtl beam\n";
	mtl_file << "Ns 96.078431\n";
	mtl_file << "Ka 1.000000 1.000000 1.000000\n";
	mtl_file << "Kd 0.000000 1.000000 0.000000\n";
	mtl_file << "Ks 0.500000 0.500000 0.500000\n";
	//mtl_file << "Ke 0.000000 0.000000 0.000000\n";
	mtl_file << "Ni 1.000000\n";
	mtl_file << "d 1.000000\n";
	mtl_file << "illum 2\n";
	mtl_file << "\n";
	//pillar
	mtl_file << "newmtl pillar\n";
	mtl_file << "Ns 96.078431\n";
	mtl_file << "Ka 1.000000 1.000000 1.000000\n";
	mtl_file << "Kd 0.000000 0.000000 1.000000\n";
	mtl_file << "Ks 0.500000 0.500000 0.500000\n";
	//mtl_file << "Ke 0.000000 0.000000 0.000000\n";
	mtl_file << "Ni 1.000000\n";
	mtl_file << "d 1.000000\n";
	mtl_file << "illum 2\n";
	mtl_file.close();

	//obj
	std::string obj_name = fName + ".obj";
	std::ofstream obj_file;
	obj_file.open(obj_name);
	obj_file << "# OBJ file exported from CSV\n";
	obj_file << "mtllib " << mtl_name << std::endl;
	obj_file << "o structure" << std::endl;
	std::map<std::string, int> nodeID;
	std::map<std::string, Node>::iterator it;
	int ID = 1;
	for (it = graph.begin(); it != graph.end(); ++it)
	{
		obj_file << "v ";
		obj_file << it->second.coord[0] << ' ';
		obj_file << it->second.coord[1] << ' ';
		obj_file << it->second.coord[2] << std::endl;
		nodeID[it->first] = ID++;
	}
	obj_file << std::endl;
	//joist
	obj_file << "usemtl joist" << std:: endl;
	obj_file << "s off" << std::endl;
	for (it = graph.begin(); it != graph.end(); ++it)
	{
		for (int i = 0; i < 5; i++)
		{
			if (it->second.LJP[i] != "None")
			{
				obj_file << "l ";
				obj_file << nodeID[it->first] << ' ';
				obj_file << nodeID[it->second.LJP[i]] << std::endl;
			}
			if (it->second.PJP[i] != "None")
			{
				obj_file << "l ";
				obj_file << nodeID[it->first] << ' ';
				obj_file << nodeID[it->second.PJP[i]] << std::endl;
			}
		}
	}
	//beam
	obj_file << "usemtl beam" << std::endl;
	obj_file << "s off" << std::endl;
	for (it = graph.begin(); it != graph.end(); ++it)
	{
		if (it->second.LBP != "None")
		{
			obj_file << "l ";
			obj_file << nodeID[it->first] << ' ';
			obj_file << nodeID[it->second.LBP] << std::endl;
		}
		if (it->second.RBP != "None")
		{
			obj_file << "l ";
			obj_file << nodeID[it->first] << ' ';
			obj_file << nodeID[it->second.RBP] << std::endl;
		}
	}
	//pillar
	obj_file << "usemtl pillar" << std::endl;
	obj_file << "s off" << std::endl;
	for (it = graph.begin(); it != graph.end(); ++it)
	{
		if (it->second.LPP != "None")
		{
			obj_file << "l ";
			obj_file << nodeID[it->first] << ' ';
			obj_file << nodeID[it->second.LPP] << std::endl;
		}
		if (it->second.PPP != "None")
		{
			obj_file << "l ";
			obj_file << nodeID[it->first] << ' ';
			obj_file << nodeID[it->second.PPP] << std::endl;
		}
	}
	obj_file.close();

	std::cout << "Complete!" << std::endl;
}

void Structure::Draw(enum View_Mode v)
{
	glUseProgram(program);
	glm::mat4 mvp = proj*view*model; 
	GLuint MatrixID = glGetUniformLocation(program, "MVP");
	glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &mvp[0][0]);
	glBindVertexArray(vao);
	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo[v]);
	glDrawElements(GL_LINES, num_indices[0], GL_UNSIGNED_INT, 0);

	if (rectset==SETTING)
		rect->Draw();
}

void Structure::MouseMove(int x, int y)
{
	if (rectset)
	{
		rect->br.x = x;
		rect->br.y = y;
		//draw the rectangle
		rect->SetTransform(viewport[2], viewport[3]);
		//std::cout << "Top left: " << rect->tl.x << ',' << rect->tl.y << std::endl;
		//std::cout << "Bottom right: " << rect->br.x << ',' << rect->br.y << std::endl;
	}
}

void Structure::MousePressed(int button, int state, int x, int y)
{
	if (state == GLUT_UP)
	{
		isMousePressed = false;
		switch (glutGetModifiers())
		{
			case GLUT_ACTIVE_CTRL:
				rectset = COMPLETE;
				PickRectangle();
				break;
			default:
				rectset = NOTYET;
				break;
		}
		
	}
	if (state == GLUT_DOWN)
	{
		isMousePressed = true;
		mousePosition.x = x;
		mousePosition.y = y;
		switch (glutGetModifiers())
		{
			case GLUT_ACTIVE_CTRL:
				rect->tl = mousePosition;
				rect->br = mousePosition;
				rect->SetTransform(viewport[2], viewport[3]);
				rectset = SETTING;
				break;
			default:
				rectset = NOTYET;
				if (!picked || abs(x - pick_mouse.x) > 5 || abs(y - pick_mouse.y) > 5)
					PickPoint();
				break;
		}
	}
}

void Structure::SetMatrix(const glm::mat4& proj, const glm::mat4& view, const glm::mat4& model)
{
	this->proj = proj;
	this->view = view;
	this->model = model;
}

void Structure::SetViewport(const glm::vec4& viewport)
{
	this->viewport = viewport;
}

void Structure::PickPoint()
{
	//empty the selection vector
	selection.clear();
	picked = false;
	float winZ;
	std::string closest;
	//scan a 10*10 window around the pixel
	for (int i = -5; i<6; i++)
	{
		for (int j = -5; j<6; j++)
		{
			float winX = mousePosition.x + i;
			float winY = viewport[3]-1 - (mousePosition.y + j);
			winX = glm::clamp(winX, 0.f, viewport[2]);
			winY = glm::clamp(winY, 0.f, viewport[3]);
			glReadPixels((int)winX, //width
				(int)winY, //hight
				1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &winZ);
			if (winZ != 1.0f)
			{
				glm::vec3 sel = glm::unProject(glm::vec3(winX,winY,winZ), view*model, proj, viewport);
				//find the closest node in the map
				float dist = std::numeric_limits<float>::max();
				std::map<std::string, Node>::iterator it;
				for (it = graph.begin(); it != graph.end(); ++it)
				{
					//weighted norm
					glm::vec3 weighted_cur = glm::vec3(0.005*it->second.coord.x, 0.005*it->second.coord.y,it->second.coord.z);
					glm::vec3 weighted_sel = glm::vec3(0.005*sel.x, 0.005*sel.y, sel.z);
					if (glm::distance(weighted_cur,weighted_sel)<dist)
					{
						closest = it->first;
						dist = glm::distance(weighted_cur, weighted_sel);
					}
				}
				float err = 1e-2;
				if (dist<err)
				{
					//cout<<"winX: "<<winX<<','<<"winY:"<<winY<<endl;
					std::cout << "ID: " << closest << std::endl;
					Node cn = graph[closest];//closest node
					std::cout << "Coordinate: " << cn.coord[0] << ',' << cn.coord[1] << ',' << cn.coord[2] << std::endl;
					//cout<<"Coordinate: "<<sel[0]<<','<<sel[1]<<','<<sel[2]<<endl;
					picked = true;
					pick_mouse = mousePosition;
					selection.push_back(closest);
					//cout<<i<<','<<j<<endl;
					break;
				}
			}
		}
		if (picked)
			break;
	}
}

void Structure::PickRectangle()
{
	//empty the selection vector
	selection.clear();
	picked = false;
	std::map<std::string, Node>::iterator it;
	for (it = graph.begin(); it != graph.end(); it++)
	{
		glm::vec3 win = glm::project(it->second.coord,view*model,proj,viewport);
		if (InRectangle(glm::vec2(win.x, viewport[3]-1 - win.y)))
		{
			selection.push_back(it->first);
			std::cout << "ID: " << it->first << std::endl;
			std::cout << "Coordinate: " << it->second.coord[0] << ',' << it->second.coord[1] << ',' << it->second.coord[2] << std::endl;
		}
	}
	if (!selection.empty())
	{
		picked = true;
		std::cout << "-------------------------" << std::endl;
	}
}

bool Structure::IsPicked() const
{
	return picked;
}

const std::vector<glm::vec3> Structure::PickPosition() const
{
	if (selection.size())
	{
		std::vector<std::string>::const_iterator it;
		std::vector<glm::vec3> pos;
		for (it = selection.begin(); it != selection.end(); it++)
		{
			pos.push_back(glm::vec3(graph.at(*it).coord.x,graph.at(*it).coord.y,graph.at(*it).coord.z));
		}
		return pos;
	}
	else
	{
		std::cout << "Out of Range(Nothing selected)" << std::endl;
		return std::vector<glm::vec3>();
	}
		
}

const std::vector<glm::vec3> Structure::EndPosition() const
{
	return endPosition;
}

void Structure::Elevate()
{
	std::vector<std::string>::iterator it;
	for (it = selection.begin(); it != selection.end(); ++it)
	{
		graph[*it].coord.z += 0.05;
		int offset1 = 3*IDs[*it]*sizeof(VertexFormat)+2*sizeof(GL_FLOAT);
		int offset2 = (3*IDs[*it]+1)*sizeof(VertexFormat)+2*sizeof(GL_FLOAT);
		int offset3 = (3*IDs[*it]+2)*sizeof(VertexFormat)+2*sizeof(GL_FLOAT);
		int size = sizeof(GL_FLOAT);
		glNamedBufferSubData(vbos[0], offset1, size, &graph[*it].coord.z);
		glNamedBufferSubData(vbos[0], offset2, size, &graph[*it].coord.z);
		glNamedBufferSubData(vbos[0], offset3, size, &graph[*it].coord.z);
	}
}

void Structure::Lower()
{
	std::vector<std::string>::iterator it;
	for (it = selection.begin(); it != selection.end(); ++it)
	{
		graph[*it].coord.z -= 0.05;
		int offset1 = 3 * IDs[*it] * sizeof(VertexFormat) + 2 * sizeof(GL_FLOAT);
		int offset2 = (3 * IDs[*it] + 1) * sizeof(VertexFormat) + 2 * sizeof(GL_FLOAT);
		int offset3 = (3 * IDs[*it] + 2) * sizeof(VertexFormat) + 2 * sizeof(GL_FLOAT);
		int size = sizeof(GL_FLOAT);
		glNamedBufferSubData(vbos[0], offset1, size, &graph[*it].coord.z);
		glNamedBufferSubData(vbos[0], offset2, size, &graph[*it].coord.z);
		glNamedBufferSubData(vbos[0], offset3, size, &graph[*it].coord.z);
	}
}

void Structure::Simplify(int algoID)
{
	std::string tmpinfName, tmpoutfName;
	if (firstSim)
	{
		firstSim = false;
		//delete all the remaining files
		int delID = 0;
		while (true)
		{
			char* delfName = new char[14];
			sprintf_s(delfName,14,"sub/%s%02d.csv","out",delID++);
			if (remove(delfName))
				break;
		}
		remove("sub/meta.txt");
		//get the input/output fname
		//std::cout << "Please input the output file name:" << std::endl;
		//std::cin >> outfName;
		outfName = "sub/out.csv";
		outfName = outfName.substr(0,outfName.length()-4); //take .csv
		//outfName = outfName.substr(4,outfName.length()-4); //take sub/
		char *tmpoutfNameID = new char[outfName.length()+3];//extra room for the null pointer
		sprintf_s(tmpoutfNameID,outfName.length()+3,"%s%02d",outfName.c_str(),simNum++);
		curID++;
		tmpinfName = infName;
		tmpoutfName = tmpoutfNameID;
		//write to meta.txt
		std::ofstream meta("sub/meta.txt");
		meta << tmpinfName << std::endl;
		meta << tmpoutfName << std::endl;
		meta << algoID << std::endl;
		if (!this->IsPicked())
		{
			meta << "-1" << std::endl;
		}
		else
		{
			std::cout << "You are not allowed to select nodes at this time" << std::endl;
			std::vector<std::string>::iterator it;
			for (it = selection.begin(); it != selection.end(); it++)
				meta << *it << std::endl;
		}
		meta.close();
		delete[] tmpoutfNameID;
	}
	else
	{
		//read the meta file
		std::fstream meta("sub/meta.txt");
		std::getline(meta, tmpoutfName);
		std::getline(meta, tmpinfName);
		char *tmpoutfNameID = new char[tmpinfName.length()+1];//extra room for the null pointer
		std::size_t found = tmpinfName.find_first_of("0123456789");
		sprintf_s(tmpoutfNameID,tmpinfName.length()+1,"%s%02d",tmpinfName.substr(0,found).c_str(),simNum++);
		curID++;
		//write to the tmp file
		std::ofstream tmp("sub/tmp.txt");
		tmp << tmpinfName << std::endl;
		tmp << tmpoutfNameID << std::endl;
		tmpoutfName = tmpoutfNameID;
		/*
		std::string line;
		while (getline(meta, line))
			tmp << line << std::endl;
		*/
		tmp << algoID << std::endl;
		if (!this->IsPicked())
		{
			tmp << "-1" << std::endl;
		}
		else
		{
			std::cout << "You are not allowed to select nodes at this time" << std::endl;
			std::vector<std::string>::iterator it;
			for (it = selection.begin(); it != selection.end(); it++)
				meta << *it << std::endl;
		}
		
		//delete the old meta, rename the new one
		meta.close();
		tmp.close();
		remove("sub/meta.txt");
		rename("sub/tmp.txt", "sub/meta.txt");
		delete[] tmpoutfNameID;
	}

	//simplification
	std::cout << "Iteration " << simNum << std::endl;
	//PyRun_SimpleString("import sub.sim");
	PyRun_SimpleString("sim.main()");

	//delete the original data
	this->graph.clear();
	this->IDs.clear();
	this->endPosition.clear();
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();

	//load the new data
	//std::cout << "Loading the new structure" << std::endl;
	LoadCSV(tmpoutfName+".csv");
	Create();
	//std::cout << "Loading complete" << std::endl;
	std::cout << "-------------------------" << std::endl;
}

void Structure::Previous()
{
	std::string newfName;
	if (curID == 0)
	{
		std::cout << "This is the first file. No previous one available." << std::endl;
		std::cout << "-------------------------" << std::endl;
		return;
	}
	else if (curID == 1)
	{
		newfName = infName;
		curID = 0;
	}
	else
	{
		char *newfNameID = new char[outfName.length() + 3];//extra room for the null pointer
		sprintf_s(newfNameID, outfName.length() + 3, "%s%02d", outfName.c_str(), --curID);
		newfName = newfNameID;
	}
	//delete the original data
	this->graph.clear();
	this->IDs.clear();
	this->endPosition.clear();
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();

	//load the new data
	std::cout << "Go to the result of Iteration " << curID << std::endl;
	LoadCSV(newfName + ".csv");
	Create();
	std::cout << "-------------------------" << std::endl;
}

void Structure::Next()
{
	std::string newfName;
	if (curID == simNum)
	{
		std::cout << "This is the last file. No next one available." << std::endl;
		std::cout << "-------------------------" << std::endl;
		return;
	}
	else
	{
		char *newfNameID = new char[outfName.length() + 3];//extra room for the null pointer
		sprintf_s(newfNameID, outfName.length() + 3, "%s%02d", outfName.c_str(), curID++);
		newfName = newfNameID;
	}
	//delete the original data
	this->graph.clear();
	this->IDs.clear();
	this->endPosition.clear();
	glDeleteVertexArrays(1, &this->vao);
	glDeleteBuffers(this->vbos.size(), &this->vbos[0]);
	this->vbos.clear();

	//load the new data
	std::cout << "Go to the result of Iteration " << curID << std::endl;
	LoadCSV(newfName + ".csv");
	Create();
	std::cout << "-------------------------" << std::endl;
}

void Structure::SetInputFName(std::string s)
{
	infName = s.substr(0,s.length()-4);
	//infName = s.substr(4, infName.length()-4);
}

const std::vector<glm::vec3> Structure::PointCloud() const
{
	return pointCloud;
}

bool Structure::LoadPointCloud(const std::string& fName)
{
	std::ifstream stream(fName);
	if (!stream)
	{
		std::cout << "Can't find the dem file" << std::endl;
		return false;
	}

	std::string line;
	while (getline(stream, line))
	{
		std::istringstream s(line);
		std::string field;
		float x, y, z;
		//x1 y1 z1 x2 y2 z2
		std::getline(s, field, ' ');
		x = stof(field);
		std::getline(s, field, ' ');
		y = stof(field);
		std::getline(s, field);
		z = stof(field);
		pointCloud.push_back(glm::vec3(x,y,z));
	}
	return true;
}

const std::vector<glm::vec4>  Structure::Confidence()
{
	if (conf_value.empty())
	{
		for (int i = 0; i < pointCloud.size(); i++)
			conf_color.push_back(glm::vec4(0.26, 0.93, 0.93,1));//cyan
	}
	return conf_color;
}

bool Structure::LoadConfidence(const std::string& fName)
{
	std::ifstream stream(fName);
	if (!stream)
	{
		std::cout << "Can't find the confidence file" << std::endl;
		return false;
	}
	std::string line;
	while (getline(stream, line))
	{
		std::istringstream s(line);
		std::string field;
		float conf;
		//x1 y1 z1 x2 y2 z2
		std::getline(s, field, ' ');
		std::getline(s, field, ' ');
		std::getline(s, field);
		conf = stof(field);
		conf_value.push_back(conf);
	}
	return true;
}

void Structure::SetThreshold(float threshold)
{
	conf_color.clear();
	for (int i = 0; i < conf_value.size(); i++)
	{
		if (conf_value[i] < threshold)
			conf_color.push_back(glm::vec4(1, 0, 1, 1));//purple
		else
			conf_color.push_back(glm::vec4(1, 0.65, 0, 1));//orange
	}
}