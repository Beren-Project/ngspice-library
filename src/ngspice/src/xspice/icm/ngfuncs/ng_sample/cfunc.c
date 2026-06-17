#include "ngspice/cm.h"
extern void ucm_ng_sample(Mif_Private_t *);
#include <math.h>

#define STATE_HELD 1
#define STATE_TRIG_HIGH 2
#define STATE_TRIG_RAW 3

static int ngf_schmitt(double raw, double prev_high, double vth, double vhyst)
{
    double half = 0.5 * fabs(vhyst);
    double rise = vth + half;
    double fall = vth - half;

    if (prev_high != 0.0)
        return raw > fall;
    return raw >= rise;
}

void ucm_ng_sample(Mif_Private_t *mif_private)
{
    double *held;
    double *trig_high;
    double *prev_trig_high;
    double *trig_raw;
    double raw;
    int high;
    int prev_high;
    int sample;

    if (mif_private->circuit.init) {
        cm_analog_alloc(STATE_HELD, sizeof(double));
        cm_analog_alloc(STATE_TRIG_HIGH, sizeof(double));
        cm_analog_alloc(STATE_TRIG_RAW, sizeof(double));
    }

    held = (double *) cm_analog_get_ptr(STATE_HELD, 0);
    trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 0);
    prev_trig_high = (double *) cm_analog_get_ptr(STATE_TRIG_HIGH, 1);
    trig_raw = (double *) cm_analog_get_ptr(STATE_TRIG_RAW, 0);

    raw = mif_private->conn[1]->port[0]->input.rvalue;
    if (mif_private->circuit.init) {
        *held = mif_private->param[1]->element[0].rvalue;
        *trig_high = ngf_schmitt(raw, 0.0, mif_private->param[2]->element[0].rvalue, mif_private->param[3]->element[0].rvalue) ? 1.0 : 0.0;
        *trig_raw = raw;
    }

    prev_high = (*prev_trig_high != 0.0);
    high = ngf_schmitt(raw, *trig_high, mif_private->param[2]->element[0].rvalue, mif_private->param[3]->element[0].rvalue);

    if (mif_private->circuit.anal_type != TRANSIENT || mif_private->circuit.time == 0.0) {
        *trig_high = high ? 1.0 : 0.0;
        *trig_raw = raw;
        mif_private->conn[2]->port[0]->output.rvalue = *held;
         mif_private->conn[2]->port[0]->partial[0].port[0] = 0.0;
         mif_private->conn[2]->port[0]->partial[1].port[0] = 0.0;
        return;
    }

    sample = 0;
    if (mif_private->param[0]->element[0].ivalue == 1)
        sample = (!prev_high && high);
    else if (mif_private->param[0]->element[0].ivalue == 2)
        sample = (prev_high && !high);

    if (sample)
        *held = mif_private->conn[0]->port[0]->input.rvalue;

    *trig_high = high ? 1.0 : 0.0;
    *trig_raw = raw;

    mif_private->conn[2]->port[0]->output.rvalue = *held;
     mif_private->conn[2]->port[0]->partial[0].port[0] = 0.0;
     mif_private->conn[2]->port[0]->partial[1].port[0] = 0.0;
}
