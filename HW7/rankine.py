from steam import steam
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

class rankine():
    def __init__(self, p_low=8, p_high=8000, eff_turbine=0.95, t_high=None, name='Rankine Cycle'):
        '''
        Constructor for rankine power cycle.  If t_high is not specified, the State 1
        is assigned x=1 (saturated steam @ p_high).  Otherwise, use t_high to find State 1.
        :param p_low: the low pressure isobar for the cycle in kPa
        :param p_high: the high pressure isobar for the cycle in kPa
        :param t_high: optional temperature for State1 (turbine inlet) in degrees C
        :param name: a convenient name
        '''
        self.p_low=p_low
        self.p_high=p_high
        self.t_high=t_high
        self.name=name
        self.s1x = None
        self.efficiency=None
        self.turbine_work=0
        self.pump_work=0
        self.heat_added=0
        self.state1=None
        self.state2=None
        self.state3=None
        self.state4=None
        self.effturb=eff_turbine


    def calc_efficiency(self):
        #calculate the 4 states
        #state 1: turbine inlet (p_high, t_high) superheated or saturated vapor
        if(self.s1x is not None):
            self.state1 = steam(self.p_high, x=self.s1x, name='Turbine Inlet')
        elif(self.t_high==None):
            self.state1=steam(self.p_high, x=1, name='Turbine Inlet') # instantiate a steam object with conditions of state 1 as saturated steam, named 'Turbine Inlet'
        else:
            self.state1=steam(self.p_high, T=self.t_high, name='Turbine Inlet') # instantiate a steam object with conditions of state 1 at t_high, named 'Turbine Inlet'
        #state 2: turbine exit (p_low, s=s_turbine inlet) two-phase
        self.state2=steam(self.p_low, s=self.state1.s, name='Turbine Exit') # instantiate a steam object with conditions of state 2, named 'Turbine Exit'
        #state 3: pump inlet (p_low, x=0) saturated liquid
        self.state3=steam(self.p_low, x=0, name='Pump Inlet') # instantiate a steam object with conditions of state 3 as saturated liquid, named 'Pump Inlet'
        #state 4: pump exit (p_high,s=s_pump_inlet) typically sub-cooled, but estimate as saturated liquid
        self.state4=steam(self.p_high,s=self.state3.s, name='Pump Exit')
        self.state4.h=self.state3.h+self.state3.v*(self.p_high-self.p_low)

        self.turbine_work=self.effturb*(self.state1.h-self.state2.h)  # calculate turbine work
        self.pump_work=self.state4.h-self.state3.h     # calculate pump work
        self.heat_added=self.state1.h-self.state4.h    # calculate heat added
        self.efficiency=(self.turbine_work - self.pump_work)/self.heat_added
        return self.efficiency

    def print_summary(self):

        if self.efficiency==None:
            self.calc_efficiency()
        print('Cycle Summary for: ', self.name)
        print('\tEfficiency: {:0.3f}%'.format(self.efficiency))
        print('\tTurbine Efficiency: {:0.3f}%'.format(self.effturb))
        print('\tTurbine Work: {:0.3f} kJ/kg'.format(self.turbine_work))
        print('\tPump Work: {:0.3f} kJ/kg'.format(self.pump_work))
        print('\tHeat Added: {:0.3f} kJ/kg'.format(self.heat_added))
        self.state1.print()
        self.state2.print()
        self.state3.print()
        self.state4.print()

    def plot_cycle_TS(self):
        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = np.loadtxt('saturated_properties.txt', skiprows=1,unpack=True)  # use np.loadtxt to read the saturated properties
        tcol, hcol, scol, pcol = np.loadtxt('superheated_properties.txt', skiprows=1,unpack=True)  # use np.loadtxt to read the superheated properties
        """Dome"""
        domexvals1 = sfs                        # get dome values from saturated table
        domexvals2 = np.flip(sgs)               # flip sgs and ts for second half because they are backwards
        domeyvals1 = ts
        domeyvals2 = np.flip(ts)
        plt.plot(domexvals1, domeyvals1, 'b')       # Plot left side of dome
        plt.plot(domexvals2, domeyvals2, 'r')       # Plot ride side of dome
        plt.xlim(0, sgs[0])     # Constricts the graph
        plt.ylim(0, 550)
        """State 4-1"""
        sf = float(griddata((ps), sfs, (self.state1.p/100)))        # Finds the start and endpoint of bar in dome
        sg = float(griddata((ps), sgs, (self.state1.p/100)))
        bartemp = float(griddata((ps), ts, (self.state1.p/100)))    # Gets temp of the bar
        if sg > self.state1.s:                  # Checks if it is superheated if it is go to else
            s1xvals = [sf, self.state1.s]
            s1yvals = [bartemp, bartemp]
        else:
            s1xvals = [sf, sg]
            s1yvals = [bartemp, bartemp]
            index = np.where(pcol == self.state1.p)     # Finds index where state 1 p equals superheat table p
            indstart = index[0][0]
            for num in range(len(index[0])-1):          # Adds tcol to y vals and scol to x vals at the index above
                if tcol[indstart+num] >= bartemp and tcol[indstart+num] < self.state1.T:    # Only adds if greater than bar temp and less than state 1 temp
                    s1xvals.append(scol[indstart+num])
                    s1yvals.append(tcol[indstart+num])
            s1xvals.append(self.state1.s)
            s1yvals.append(self.state1.T)
        plt.plot(s1xvals, s1yvals, 'g')     # Plots the top line 4 to 1
        """State 1-2"""
        s2xvals = [self.state2.s, self.state2.s]    # Strait line down from 1 to 2
        s2yvals = [self.state1.T, self.state2.T]
        plt.plot(s2xvals, s2yvals, 'g')
        """State 2-3"""
        s3xvals = [self.state3.s, self.state2.s]    # Strait line from 2 to 3
        s3yvals = [self.state3.T, self.state3.T]
        plt.plot(s3xvals, s3yvals, 'k')
        """State 3-4"""
        s4xvals = [self.state3.s, sf]               # Diagonal line from 3 to 4
        s4yvals = [self.state3.T, self.state4.T]
        plt.plot(s4xvals, s4yvals, 'g')
        """Markers"""
        plt.plot(self.state1.s, self.state1.T,'k', marker='o', fillstyle='none')        # plots markers at 1, 2, and 3
        plt.plot(self.state2.s, self.state2.T,'k', marker='o', fillstyle='none')
        plt.plot(self.state3.s, self.state3.T,'k', marker='o', fillstyle='none')
        """Titles"""
        plt.title(self.name)        # Title and labels for graph with text showing the summary
        plt.xlabel('S (kJ/kg*K)')
        plt.ylabel('T (C)')
        plt.text(0.25, 350, 'Summary:\nn: ' + str('{0:.1f}'.format(self.efficiency*100)) + ' %\nnTurbine: ' +
                 str('{0:.2f}'.format(self.effturb)) + '\nWTurbine: '+ str('{0:.1f}'.format(self.turbine_work))
                 + ' kJ/K\nWPump: ' + str('{0:.1f}'.format(self.pump_work)) + ' kJ/kg\nQBoiler: ' +
                 str('{0:.1f}'.format(self.heat_added)) + ' kJ/kg')
        """Fill"""
        for x in s1xvals:           # Consolidates the x vals from 4 to 1
            s4xvals.append(x)
        for y in s1yvals:           # Consolidates the y vals on the top line and the y vals on the bottom line
            s4yvals.append(y)
            s3yvals.append(self.state3.T)   # Adds the same number to make them have the same amount of points
        plt.fill_between(x=s4xvals, y1=s4yvals, y2=s3yvals, color='0.8')    # Fills in the graph

        plt.show()


def main():
    rankine1= rankine(t_high=500) #instantiate a rankine object to test it.
    #t_high is specified
    #if t_high were not specified, then x_high = 1 is assumed
    eff=rankine1.calc_efficiency()
    print(eff)
    rankine1.print_summary()

if __name__=="__main__":
    main()