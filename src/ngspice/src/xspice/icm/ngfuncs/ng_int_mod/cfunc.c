#include "ngspice/cm.h"
extern void ucm_ng_int_mod(Mif_Private_t *);
#include <math.h>

#define STATE_INPUT 1
#define STATE_INTEGRAL 2

static double ngf_mod_wrap(double value, double ic, double modulus)
{
    double rel = value - ic;
    double wrapped = fmod(rel, modulus);

    if (wrapped < 0.0)
        wrapped += modulus;
    return ic + wrapped;
}

static double ngf_clamp_mod(double x, double lo, double hi)
{
    if (x < lo)
        return lo;
    if (x > hi)
        return hi;
    return x;
}

void ucm_ng_int_mod(Mif_Private_t *mif_private)
{
    double *input_state;
    double *state;
    double partial;
    double value;
    int err;

    if (mif_private->circuit.init) {
        cm_analog_alloc(STATE_INPUT, sizeof(double));
        cm_analog_alloc(STATE_INTEGRAL, sizeof(double));
    }

    input_state = (double *) cm_analog_get_ptr(STATE_INPUT, 0);
    state = (double *) cm_analog_get_ptr(STATE_INTEGRAL, 0);

    if (mif_private->circuit.init)
        *state = mif_private->param[0]->element[0].rvalue;

    if (mif_private->circuit.anal_type != TRANSIENT || mif_private->circuit.time == 0.0) {
        mif_private->conn[1]->port[0]->output.rvalue = ngf_clamp_mod(*state, mif_private->param[3]->element[0].rvalue, mif_private->param[4]->element[0].rvalue);
         mif_private->conn[1]->port[0]->partial[0].port[0] = 0.0;
        return;
    }

    *input_state = mif_private->param[1]->element[0].rvalue * mif_private->conn[0]->port[0]->input.rvalue;
    err = cm_analog_integrate(*input_state, state, &partial);
    if (err)
        cm_message_send(cm_message_get_errmsg());

    value = ngf_mod_wrap(*state, mif_private->param[0]->element[0].rvalue, mif_private->param[2]->element[0].rvalue);
    value = ngf_clamp_mod(value, mif_private->param[3]->element[0].rvalue, mif_private->param[4]->element[0].rvalue);
    *state = value;

    mif_private->conn[1]->port[0]->output.rvalue = value;
     mif_private->conn[1]->port[0]->partial[0].port[0] = partial * mif_private->param[1]->element[0].rvalue;
}
