# 	 -*- coding: utf-8 -*-
#
#    This file is part of DO-MPC
#
#    DO-MPC: An environment for the easy, modular and efficient implementation of
#            robust nonlinear model predictive control
#
#    The MIT License (MIT)
#
#    Copyright (c) 2014-2015 Sergio Lucia, Alexandru Tatulea-Codrean
#                            TU Dortmund. All rights reserved
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.



import matplotlib.pyplot as plt
from casadi import *
import numpy as NP
import core_do_mpc
from matplotlib.ticker import MaxNLocator



class mpc_data:
    "A class for the definition of the mpc data that is managed throughout the mpc loop"
    def __init__(self, configuration):
        # get sizes
        nx = configuration.model.x.size(1)
        nu = configuration.model.u.size(1)
        np = configuration.model.p.size(1)
        nz = configuration.model.p.size(1) # TODO: Adapt for DAEs
        t_end = configuration.optimizer.t_end
        t_step = configuration.simulator.t_step_simulator
        # Initialize the data structures
        self.mpc_states = NP.resize(NP.array([]),(t_end/t_step + 1,nx))
        self.mpc_control = NP.resize(NP.array([]),(t_end/t_step + 1,nu))
        self.mpc_alg = NP.resize(NP.array([]),(t_end/t_step + 1,nz))
        self.mpc_time = NP.resize(NP.array([]),(t_end/t_step + 1))
        self.mpc_cost = NP.resize(NP.array([]),(t_end/t_step + 1))
        self.mpc_ref = NP.resize(NP.array([]),(t_end/t_step + 1))
        self.mpc_cpu = NP.resize(NP.array([]),(t_end/t_step + 1))
        self.mpc_parameters = NP.resize(NP.array([]),(t_end/t_step + 1,np))
        # Initialize with initial conditions
        self.mpc_states[0,:] = configuration.model.ocp.x0
        self.mpc_control[0,:] = configuration.model.ocp.u0
        self.mpc_time[0] = 0

class opt_result:
    """ A class for the definition of the result of an optimization problem containing optimal solution, optimal cost and value of the nonlinear constraints"""
    def __init__(self,res):
        self.optimal_solution = NP.array(res["x"])
        self.optimal_cost = NP.array(res["f"])
        self.constraints = NP.array(res["g"])



def export_to_matlab(configuration):
    if configuration.simulator.export_to_matlab:
        data = configuration.mpc_data
        x_scaling = configuration.model.ocp.x_scaling
        u_scaling = configuration.model.ocp.u_scaling
        # mpc_iteration = configuration.simulator.mpc_iteration
        # mpc_states = configuration.mpc_data.mpc_states[:mpc_iteration, :] * x_scaling
        # mpc_control = mpc_control[1:mpc_iteration, :] * u_scaling
        # mpc_alg =
        # mpc_time = NP.array([mpc_time[:mpc_iteration]]).T
        # mpc_cost =
        # mpc_ref =
        # mpc_cpu = NP.array([mpc_cpu[1:mpc_iteration]]).T
        export_dict = {
        "mpc_states":data.mpc_states * x_scaling,
        "mpc_control":data.mpc_control * u_scaling,
        "mpc_alg": data.mpc_alg,
        "mpc_time": data.mpc_time,
        "mpc_cost": data.mpc_cost,
        "mpc_ref": data.mpc_ref,
        "mpc_parameters": data.mpc_parameters,
        }
        scipy.io.savemat(export_name, mdict={"mpc_states":mpc_states[:mpc_iteration, :] * x_scaling,"mpc_control":mpc_control, "mpc_time":mpc_time, "mpc_cpu":mpc_cpu})
        print("Exporting to Matlab as ''" + export_name + "''")

def plot_mpc(configuration):
    mpc_data = configuration.mpc_data
    mpc_states = mpc_data.mpc_states
    mpc_control = mpc_data.mpc_control
    mpc_time = mpc_data.mpc_time
    index_mpc = configuration.simulator.mpc_iteration
    plot_states = configuration.simulator.plot_states
    plot_control = configuration.simulator.plot_control
    x = configuration.model.x
    x_scaling = configuration.model.ocp.x_scaling
    u = configuration.model.u
    u_scaling = configuration.model.ocp.u_scaling
    # This function plots the states and controls chosen in the variables plot_states and plot_control until a certain index (index_mpc)
    plt.ion()
    fig = plt.figure(1)
    total_subplots = len(plot_states) + len(plot_control)
    # First plot the states
    for index in range(len(plot_states)):
    	plot = plt.subplot(total_subplots, 1, index + 1)
    	plt.plot(mpc_time[0:index_mpc], mpc_states[0:index_mpc,plot_states[index]] * x_scaling[plot_states[index]])
    	plt.ylabel(str(x[plot_states[index]]))
    	plt.xlabel("Time")
    	plt.grid()
    	plot.yaxis.set_major_locator(MaxNLocator(4))

    # Plot the control inputs
    for index in range(len(plot_control)):
    	plot = plt.subplot(total_subplots, 1, len(plot_states) + index + 1)
    	plt.plot(mpc_time[0:index_mpc], mpc_control[0:index_mpc,plot_control[index]] * u_scaling[plot_control[index]] ,drawstyle='steps')
    	plt.ylabel(str(u[plot_control[index]]))
    	plt.xlabel("Time")
    	plt.grid()
    	plot.yaxis.set_major_locator(MaxNLocator(4))



def plot_state_pred(v,t0,el,lineop, n_scenarios, n_branches, nk, child_scenario, X_offset, x_scaling, t_step):
  # This function plots the prediction of a state
  #plt.clf()
  plt.hold(True)
  # Time grid
  tf = t_step * nk
  tgrid = NP.linspace(t0,t0+tf,nk+1)
  # For all control intervals
  for k in range(nk):
    # For all scenarios
    for s in range(n_scenarios[k]):
      # For all uncertainty realizations
      for b in range(n_branches[k]):
        # Get state trajectory segment
        x_beginning = v[el+X_offset[k][s]]
        s_next = child_scenario[k][s][b]
        x_end = v[el+X_offset[k+1][s_next]]
        x_segment = NP.array([x_beginning,x_end])*x_scaling[el]
        plt.plot(tgrid[k:k+2],x_segment,lineop)


def plot_control_pred(v,t0,el,lineop, n_scenarios, n_branches, nk, parent_scenario, U_offset, u_scaling, t_step, u_last_step):
	# This function plots the prediction of a control input
	plt.hold(True)
	# Time grid
	tf = t_step * nk
	tgrid = NP.linspace(t0,t0+tf,nk+1)
	# For all control intervals
	for k in range(nk):
		# For all scenarios
		for s in range(n_scenarios[k]):
			# Time segment
			t_beginning = tgrid[k]
			t_end = tgrid[k+1]

			# Plot state trajectory segment
			u_this = v[el+U_offset[k][s]]*u_scaling[el]
			plt.plot(NP.array([t_beginning,t_end]),NP.array([u_this,u_this]),lineop)

			# Plot vertical line connecting the scenarios
			if k == 0:
				u_prev = u_last_step
			else:
				u_prev = v[el+U_offset[k-1][parent_scenario[k][s]]]*u_scaling[el]
			plt.plot(NP.array([t_beginning,t_beginning]),NP.array([u_prev,u_this]),lineop)



def plot_animation(configuration):
    if configuration.simulator.plot_anim:
        mpc_data = configuration.mpc_data
        mpc_states = mpc_data.mpc_states
        mpc_control = mpc_data.mpc_control
        mpc_time = mpc_data.mpc_time
        index_mpc = configuration.simulator.mpc_iteration
        plot_states = configuration.simulator.plot_states
        plot_control = configuration.simulator.plot_control
        x = configuration.model.x
        x_scaling = configuration.model.ocp.x_scaling
        u = configuration.model.u
        u_scaling = configuration.model.ocp.u_scaling
        X_offset = configuration.optimizer.nlp_dict_out['X_offset']
        U_offset = configuration.optimizer.nlp_dict_out['U_offset']
        n_branches = configuration.optimizer.nlp_dict_out['n_branches']
        n_scenarios = configuration.optimizer.nlp_dict_out['n_scenarios']
        child_scenario = configuration.optimizer.nlp_dict_out['child_scenario']
        parent_scenario = configuration.optimizer.nlp_dict_out['parent_scenario']
        nk = configuration.optimizer.n_horizon
        t0 = configuration.simulator.t0_sim - configuration.simulator.t_step_simulator
        t_step = configuration.simulator.t_step_simulator
        v_opt = configuration.optimizer.opt_result_step.optimal_solution
        plt.ion()
        total_subplots = len(plot_states) + len(plot_control)
        plt.figure(2)
        # Clear the previous animation
        plt.clf()
        # First plot the states
        for index in range(len(plot_states)):
        	plot = plt.subplot(total_subplots, 1, index + 1)
        	# First plot the prediction
        	plot_state_pred(v_opt, t0, plot_states[index], '-b', n_scenarios, n_branches, nk, child_scenario, X_offset, x_scaling, t_step)
        	plt.plot(mpc_time[0:index_mpc], mpc_states[0:index_mpc,plot_states[index]] * x_scaling[plot_states[index]], '-k', linewidth=2.0)
        	plt.ylabel(str(x[plot_states[index]]))
        	plt.xlabel("Time")
        	plt.grid()
        	plot.yaxis.set_major_locator(MaxNLocator(4))

        # Plot the control inputs
        for index in range(len(plot_control)):
        	plot = plt.subplot(total_subplots, 1, len(plot_states) + index + 1)
        	# First plot the prediction
        	plot_control_pred(v_opt, t0, plot_control[index], '-b', n_scenarios, n_branches, nk, parent_scenario, U_offset, u_scaling, t_step, mpc_control[index_mpc-1,plot_control[index]])
        	plt.plot(mpc_time[0:index_mpc], mpc_control[0:index_mpc,plot_control[index]] * u_scaling[plot_control[index]],'-k' ,drawstyle='steps', linewidth=2.0)
        	plt.ylabel(str(u[plot_control[index]]))
        	plt.xlabel("Time")
        	plt.grid()
        	plot.yaxis.set_major_locator(MaxNLocator(4))
        raw_input("Press Enter to continue...")

    else:
        # nothing to be done if no animation is chosen
        dummy = 0 # TODO: correct way to do this?