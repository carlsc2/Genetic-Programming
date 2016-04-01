/*

Python-compatible modified version of http://mazonka.com/brainf/stackbfi.c

*/
#include <Python.h>
#include <time.h>


struct cell{
	struct cell *p, *n;
	int v;
};
typedef struct cell cell;

#define OUTPUT_LENGTH 4096
#define MAX_DEPTH 255

cell *ip, *mp;
char* input_buffer;
int ibl;
int ri;
int oi;
char output_buffer[OUTPUT_LENGTH] = { '\0' };
double timeout;
int timed_out;
clock_t start;
int depth;

void run(){
	if(depth >= MAX_DEPTH) return;
	while(ip && mp && ip->v){
		int lev=1;
		if( ip->v == '+' ) ++mp->v;
		else if( ip->v == '-' ) --mp->v;
		else if( ip->v == '.' && oi < OUTPUT_LENGTH) output_buffer[oi++] = mp->v;
		else if( ip->v == ',' && ri < ibl) mp->v = input_buffer[ri++];
		else if( ip->v == '<' ) mp = mp->p;
		else if( ip->v == '>' ){
			if( !mp->n ){
				cell m; m.p=mp; 
				m.n=0; m.v=0;
				mp->n=&m; mp=&m;
				ip=ip->n;
				depth++;
				run();
				depth--;
				return;
			}
			mp=mp->n;
		}
		else if( ip->v == '[' && !mp->v ){//skip if not zero
			while(lev && ip->n){
				ip=ip->n;
				lev-=(ip->v==']')-(ip->v=='[');
			}
		}
		else if( ip->v == ']' && mp->v ){
			if(clock() - start > timeout){//timeout can only occur with loops right?
				timed_out = 1;
				return;
			}
			while(lev && ip->p){
				ip=ip->p;
				lev+=(ip->v==']')-(ip->v=='[');
			}
		}
		ip=ip->n;
	}
}

void readp(cell *p){
	int cmd = input_buffer[ri++];
	if( cmd == '!' || cmd<=0 || ri > ibl ){
		cell m; m.p=m.n=0;
		m.v=0; mp=&m;
		start = clock();
		run();
	}
	else{
		cell c; c.p = p;
		c.n=0; c.v=cmd;
		if(p) p->n = &c;
		else ip = &c;
		readp(&c);
	}
}

static PyObject* evaluate(PyObject* self, PyObject *args){
	ibl = ri = oi = timed_out = 0;
	if (!PyArg_ParseTuple(args, "s#|d", &input_buffer, &ibl, &timeout)) {
	  return NULL;
	}
	timeout = timeout * 1000; //convert to seconds
	if(ibl > 0) readp(0); //ignore empty code
	if(timed_out){
		return Py_BuildValue("s","");
	}
	return PyUnicode_DecodeLatin1(output_buffer, oi, NULL);
}

static PyMethodDef cbrainfuck_methods[] = {
	{"evaluate", (PyCFunction)evaluate, METH_VARARGS, NULL},
	{NULL, NULL}
};

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"cbrainfuck",
	NULL,
	(Py_ssize_t)0,
	cbrainfuck_methods,
	NULL,
	NULL,
	NULL,
	NULL
};

PyObject* PyInit_cbrainfuck(void){
	PyObject* module = PyModule_Create(&moduledef);
	if (module == NULL)
		return NULL;
	return module;
}
