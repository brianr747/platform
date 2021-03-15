source('startup.R')
#------------------------


# Baseline model: no lag.

N = 40
t_axis = 1:40

y = rep(NA, N)
y[1] = .8
y[2] = 1
for (i in 3:N){
  y[i] = 1.549 * y[i-1] + (-0.608 * y[i-2])
}

pp <- PlotXYReal(t_axis[1:40], y[1:40], '', 'Output Gap After Initial Disturbance', has_marker=T)

pp <- pp + geom_vline(colour="red", xintercept=2)
OnePanelChart(pp, 'c202011_state_trajectory.png', 'Vertical Line Indicates Initial Condition Period')

y = rep(NA, N)
e = rep(0,N)
y[1] = 0
y[2] = 0
e[5] = -2
for (i in 3:N){
  y[i] = 1.549 * y[i-1] + (-0.608 * y[i-2]) + e[i]
}

pp <- PlotXYReal(t_axis[1:N], y[1:N], '', 'Output Gap With Shock', has_marker=T)

pp <- pp + geom_vline(colour="red", xintercept=5)
OnePanelChart(pp, 'c202011_state_trajectory_2.png', 'Vertical Line Indicates One Period Shock')
