#include "ngspice/cm.h"
extern void ucm_ng_int_rst(Mif_Private_t *);
#include <math.h>

#define STATE_INPUT 1
#define STATE_INTEGRAL 2
#define STATE_TRIG_HIGH 3
#define STATE_TRIG_RAW 4

static double ngf_clamp(double x, double lo, double hi)
{
    if (x < lo)
        return lo;
    if (x > hi)
        return hi;
    return x;
}

static int ngf_schmitt(double raw, double prev_high, double vth, double vhyst)
{
    double half = 0.5 * fabs(vhyst);
    double rise = vth + half;
    double fall = vth - half;

    if (prev_high != 0.0)
        return raw > fall;
    return raw >= rise;
}

void ucm_ng_int_rst(Mif_Private_t *mif_private)
{
    double in;
    double raw;
    double out;
    double partial;
    double *input_state;
    double *state;
    double *trig_high;
    double *prev_trig_high;
    double *trig_raw;
    int high;
    int prev_high;
    int do_reset;
    int err;

    if (mif_private->circuit.init) {
        cm_analog_alloc(STATE_INPUT, sizeof(double));
        cm_analog_alloc(STATE_INTEGRAL, sizeof(double));
        cm_analog_alloc(STATE_TRIG_HIGH, sizeof(double));
        cm_analog_alloc(STATE_TRIG_RAW, sizeof(double));
    }

    input_state = (double *) cm_analog_get_ptr(STATE_INPUT, 0);
    state = (double *) cm_analog_get_ptr(STATE_INTEGRAL, 0);
    trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 0);
    prev_trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 1);
    trig_raw = (double *) cm_analog_get_ptr(STATE_TRIG_RAW, 0);

    raw = mif_private->conn[1]->port[0]->input.rvalue;
    if (mif_private->circuit.init) {
        *state = mif_private->param[1]->element[0].rvalue;
        *trig_high = ngf_schmitt(raw, 0.0, mif_private->param[3]->element[0].rvalue, mif_private->param[4]->element[0].rvalue) ? 1.0 : 0.0;
        *trig_raw = raw;
    }

    prev_high = (*prev_trig_high != 0.0);
    high = ngf_schmitt(raw, *trig_high, mif_private->param[3]->element[0].rvalue, mif_private->param[4]->element[0].rvalue);

    if (mif_private->circuit.anal_type != TRANSIENT || mif_private->circuit.time == 0.0) {
        *trig_high = high ? 1.0 : 0.0;
        *trig_raw = raw;
        mif_private->conn[2]->port[0]->output.rvalue = *state;
         mif_private->conn[2]->port[0]->partial[0].port[0] = 0.0;
         mif_private->conn[2]->port[0]->partial[1].port[0] = 0.0;
        return;
    }

    in = mif_private->param[2]->element[0].rvalue * mif_private->conn[0]->port[0]->input.rvalue;

    do_reset = 0;
    if (mif_private->param[0]->element[0].ivalue == 0)
        do_reset = high;
    else if (mif_private->param[0]->element[0].ivalue == 1)
        do_reset = (!prev_high && high);
    else if (mif_private->param[0]->element[0].ivalue == 2)
        do_reset = (prev_high && !high);

    if (do_reset) {
        *state = mif_private->param[1]->element[0].rvalue;
        out = mif_private->param[1]->element[0].rvalue;
        partial = 0.0;
    } else {
        *input_state = in;
        if (mif_private->param[8]->element[0].bvalue) {
            if (*state >= mif_private->param[6]->element[0].rvalue && in > 0.0)
                *input_state = 0.0;
            else if (*state <= mif_private->param[5]->element[0].rvalue && in < 0.0)
                *input_state = 0.0;
        }

        err = cm_analog_integrate(*input_state, state, &partial);
        if (err)
            cm_message_send(cm_message_get_errmsg());
        out = ngf_clamp(*state, mif_private->param[5]->element[0].rvalue, mif_private->param[6]->element[0].rvalue);
        *state = out;
        if (mif_private->param[8]->element[0].bvalue && *input_state == 0.0)
            partial = 0.0;
    }

    *trig_high = high ? 1.0 : 0.0;
    *trig_raw = raw;

    mif_private->conn[2]->port[0]->output.rvalue = out;
     mif_private->conn[2]->port[0]->partial[0].port[0] = partial * mif_private->param[2]->element[0].rvalue;
     mif_private->conn[2]->port[0]->partial[1].port[0] = 0.0;
}
