import numpy as np

from rankine import rankine  # import any of your own classes as you wish

import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from scipy.interpolate import griddata

from Rankine_GUI import Ui_Form  # from the GUI file your created


class main_window(QWidget, Ui_Form):
    def __init__(self):
        """
        Constructor for the main window of the application.  This class inherits from QWidget and Ui_Form
        """
        super().__init__()  # run constructor of parent classes
        self.setupUi(self)  # run setupUi() (see Ui_Form)
        self.setWindowTitle('Rankine Cycle Calculator')  # set the window title

        self.assign_widgets()  # connects signals and slots
        self.show()

    def assign_widgets(self):
        self.btn_Calculate.clicked.connect(self.Calculate)  # connect clicked signal of pushButton_Calculate to self.Calculate

    def Calculate(self):
        """
        Set the properties of the rankine object and calculate the
        rankine cycle.  Finally, output the results to the line edit widgets.
        :return:
        """
        self.Rankine = rankine()  # instantiate a rankine object

        # Set the input text to the respective variables
        self.Rankine.p_high = float(self.le_PHigh.displayText()) * 100
        self.Rankine.p_low = float(self.le_PLow.displayText()) * 100
        if self.rdo_Quality.isChecked():        # Checks if user wants to use quality or temp high
            self.Rankine.s1x = float(self.le_TurbineInletCondition.displayText())
        elif self.rdo_THigh.isChecked():
            self.Rankine.t_high = float(self.le_TurbineInletCondition.displayText())
        self.Rankine.effturb = float(self.le_TurbineEff.displayText()) if len(self.le_TurbineEff.displayText()) > 0 else 1

        self.Rankine.calc_efficiency()
        cycle = self.Rankine
        # set the text in each line edit
        self.le_H1.setText(str('%.2f' % cycle.state1.h))
        self.le_H2.setText(str('%.2f' % cycle.state2.h))
        self.le_H3.setText(str('%.2f' % cycle.state3.h))
        self.le_H4.setText(str('%.2f' % cycle.state4.h))
        self.le_TurbineWork.setText(str('%.2f' % cycle.turbine_work))
        self.le_PumpWork.setText(str('%.2f' % cycle.pump_work))
        self.le_HeatAdded.setText(str('%.2f' % cycle.heat_added))
        self.le_Efficiency.setText(str('%.2f' % (cycle.efficiency*100)))

        # Labels for the Saturated Properties at P_high and P_low
        # Used np.loadtxt to read the saturated properties
        ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = np.loadtxt('saturated_properties.txt', skiprows=1,
                                                          unpack=True)
        # P_high interpolation formatted
        PbarH = cycle.p_high/100
        TsatH = '%.2f' % float(griddata((ps), ts, (PbarH)))
        hfH = '%.2f' % float(griddata((ps), hfs, (PbarH)))
        hgH = '%.2f' % float(griddata((ps), hgs, (PbarH)))
        sfH = '%.2f' % float(griddata((ps), sfs, (PbarH)))
        sgH = '%.2f' % float(griddata((ps), sgs, (PbarH)))
        vfH = '%.4f' % float(griddata((ps), vfs, (PbarH)))
        vgH = '%.2f' % float(griddata((ps), vgs, (PbarH)))
        # Set text label with the above values and units
        self.lbl_SatPropHigh.setText("PSat = " + str(PbarH) + " bar, TSat = " + str(TsatH) + " C\nhf = " + str(hfH) +
                                     " kJ/kg, hg = " + str(hgH) + " kJ/kg\nsf = " + str(sfH) + " kJ/kg*K, sg = " +
                                     str(sgH) + " kJ/kg*K\nvf = " + str(vfH) + " m^3/kg, vg = " + str(vgH) + " m^3/kg")

        # P_low interpolation formatted
        PbarL = cycle.p_low / 100
        TsatL = '%.2f' % float(griddata((ps), ts, (PbarL)))
        hfL = '%.2f' % float(griddata((ps), hfs, (PbarL)))
        hgL = '%.2f' % float(griddata((ps), hgs, (PbarL)))
        sfL = '%.2f' % float(griddata((ps), sfs, (PbarL)))
        sgL = '%.2f' % float(griddata((ps), sgs, (PbarL)))
        vfL = '%.4f' % float(griddata((ps), vfs, (PbarL)))
        vgL = '%.2f' % float(griddata((ps), vgs, (PbarL)))
        # Set text label with the above values and units
        self.lbl_SatPropLow.setText("PSat = " + str(PbarL) + " bar, TSat = " + str(TsatL) + " C\nhf = " + str(hfL) +
                                     " kJ/kg, hg = " + str(hgL) + " kJ/kg\nsf = " + str(sfL) + " kJ/kg*K, sg = " +
                                     str(sgL) + " kJ/kg*K\nvf = " + str(vfL) + " m^3/kg, vg = " + str(vgL) + " m^3/kg")
        return

    def ExitApp(self):
        app.exit()


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()
    sys.exit(app.exec_())