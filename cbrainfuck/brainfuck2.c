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

cell *ip, *mp;
char* input_buffer;
unsigned int ibl;
unsigned int ri;
unsigned int oi;
char output_buffer[OUTPUT_LENGTH] = { '\0' };
double timeout = 5;
clock_t start;

void run(){
	while(ip){
		if(clock() - start > timeout) return;
		int lev=1;
		if( ip->v == '+' ) ++mp->v;
		else if( ip->v == '-' ) --mp->v;
		else if( ip->v == '.' && oi < OUTPUT_LENGTH) output_buffer[oi++] = (mp->v);
		else if( ip->v == ',' && ri < ibl) mp->v = input_buffer[ri++];
		else if( ip->v == '<' ) mp=mp->p;
		else if( ip->v == '>' ){
			if( !mp->n ){
				cell m; m.p=mp; 
				m.n=0; m.v=0;
				mp->n=&m; mp=&m;
				ip=ip->n;
				run();
				return;
			}
			mp=mp->n;
		}
		else if( ip->v == '[' && !mp->v )
		while(lev){ ip=ip->n; lev-=(ip->v==']')-(ip->v=='['); }
		else if( ip->v == ']' && mp->v )
		while(lev){ ip=ip->p; lev+=(ip->v==']')-(ip->v=='['); }

		ip=ip->n;
	}
}

void readp(cell *p){
	int cmd = input_buffer[ri++];
	if( cmd == '!' || cmd<0 ){
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
	ri = 0;
	oi = 0;
	if (!PyArg_ParseTuple(args, "s#|d", &input_buffer, &ibl, &timeout)) {
      return NULL;
	}
	timeout = timeout * 1000; //convert to seconds
	readp(0);
	return PyUnicode_DecodeLatin1(output_buffer, oi, NULL);
}

static PyMethodDef cbrainfuck_methods[] = {
    {"evaluate", (PyCFunction)evaluate, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
static struct module_state _state;

static int cbrainfuck_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int cbrainfuck_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cbrainfuck",
        NULL,
        sizeof(struct module_state),
        cbrainfuck_methods,
        NULL,
        cbrainfuck_traverse,
        cbrainfuck_clear,
        NULL
};

PyObject* PyInit_cbrainfuck(void){

    PyObject *module = PyModule_Create(&moduledef);

    if (module == NULL)
        return NULL;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("cbrainfuck.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        return NULL;
    }
    return module;

}
