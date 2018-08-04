import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pandas as pd
import csv
import re
import glob
import os
import numpy as np
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle("Dynamic Bus Scheduler")
        self.setWindowIcon(QtGui.QIcon('Bus-icon.png'))
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
        self.months = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'June', '07': 'July',
                  '08': 'Aug', '09': 'Sept', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

        self.home()

    def home(self):
        btn = QtGui.QPushButton("Quit", self)
        choosefile=QtGui.QPushButton("Choose File", self)
        upload_btn=QtGui.QPushButton("Upload", self)
        generate_trips_btn=QtGui.QPushButton("Generate Trips", self)
        view_btn=QtGui.QPushButton("View Bus Trips", self)
        generate_schedule_btn=QtGui.QPushButton("Generate Schedule ", self)
        reset_btn = QtGui.QPushButton("Reset", self)
        view_schedule_btn = QtGui.QPushButton("View Schedule ", self)

        #quit button
        btn.clicked.connect(self.close_application)
        btn.resize(btn.minimumSizeHint())
        btn.move(630, 415)

        #browsefiles button
        choosefile.resize(btn.sizeHint())
        choosefile.clicked.connect(lambda: self.singlebrowse())
        choosefile.move(200, 27)

        #Upload button
        upload_btn.clicked.connect(lambda: self.processfile())
        upload_btn.resize(btn.minimumSizeHint())
        upload_btn.move(600, 170)

        # Generate trips button
        generate_trips_btn.clicked.connect(lambda: self.generate_trips())
        generate_trips_btn.resize(btn.minimumSizeHint())
        generate_trips_btn.move(305, 355)

        # view files button
        view_btn.clicked.connect(lambda: self.view_trips())
        view_btn.resize(btn.minimumSizeHint())
        view_btn.move(415, 355)

        # generate schedule button
        generate_schedule_btn.clicked.connect(lambda: self.generate_schedule())
        generate_schedule_btn.resize(100,23)
        generate_schedule_btn.move(525, 355)

        #route dropdown
        self.styleChoice = QtGui.QLabel("Choose Route No:", self)      #Dropdown label
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItem(" ")
        self.comboBox.addItem("0071")
        self.comboBox.addItem("3310")
        self.comboBox.addItem("3400")
        self.comboBox.addItem("3860")
        self.comboBox.addItem("3870")
        self.comboBox.addItem("4100")
        self.comboBox.addItem("4180")
        self.comboBox.addItem("4781")
        self.comboBox.addItem("6020")
        self.comboBox.addItem("6034")
        self.comboBox.addItem("6040")
        self.comboBox.addItem("6050")
        self.comboBox.addItem("6064")
        self.comboBox.addItem("6074")
        self.comboBox.addItem("6080")
        self.comboBox.addItem("6120")
        self.comboBox.move(500, 25)
        self.styleChoice.move(400, 25)
        self.comboBox.activated[str].connect(self.route_choice)
        #selected_route=str(comboBox.currentText())

        # method dropdown
        self.styleChoice = QtGui.QLabel("Choose Method:", self)  # Dropdown label
        self.MethodBox = QtGui.QComboBox(self)
        self.MethodBox.addItem(" ")
        self.MethodBox.addItem("Polynomial Regression")
        self.MethodBox.addItem("LSTM")
        self.MethodBox.addItem("Arimax")
        self.MethodBox.addItem("Sarimax")
        self.MethodBox.addItem("SVM")
        self.MethodBox.addItem("NN Categorical")
        self.MethodBox.move(170, 352)
        self.styleChoice.move(80, 352)
        self.MethodBox.activated[str].connect(self.method_choice)

        #progressBar
        self.progress = QtGui.QProgressBar(self)
        self.progress.setGeometry(155, 417, 460, 20)
        self.ProgressLabel = QtGui.QLabel("Progress:", self)  # StatusBox label
        self.ProgressLabel.move(95, 412)

        #date1
        self.dayChoice = QtGui.QLabel("Choose Day:", self)  # Dropdown label
        self.daySelect = QtGui.QComboBox(self)
        self.daySelect.addItem(" ")
        self.daySelect.addItem("Monday")
        self.daySelect.addItem("Tuesday")
        self.daySelect.addItem("Wednesday")
        self.daySelect.addItem("Thursday")
        self.daySelect.addItem("Friday")
        self.daySelect.addItem("Saturday")
        self.daySelect.addItem("Sunday")
        self.daySelect.move(150, 170)
        self.dayChoice.move(80, 170)
        self.daySelect.activated[str].connect(self.day_choice)

        #date2
        cal2 = QtGui.QCalendarWidget(self)
        cal2.setGridVisible(True)
        cal2.move(320, 90)
        cal2.resize(210, 200)
        cal2.clicked[QtCore.QDate].connect(self.showPredictionDate)

        self.lbl = QtGui.QLabel(self)
        date = cal2.selectedDate()
        self.lbl.setText(date.toString())
        self.lbl.move(387, 295)

        # reset button
        reset_btn.clicked.connect(lambda: self.reset())
        reset_btn.resize(btn.minimumSizeHint())
        reset_btn.resize(100, 23)
        reset_btn.move(345, 563)

        # view schedule button
        view_schedule_btn.resize(btn.minimumSizeHint())
        view_schedule_btn.clicked.connect(lambda: self.view_schedule())
        view_schedule_btn.move(655, 355)

        #Status Box
        self.log=QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.move(80, 485)
        self.log.resize(650, 60)
        self.StatusBox = QtGui.QLabel("Current Status:", self)  # StatusBox label
        self.StatusBox.move(80, 455)

        self.show()

    def reset(self):
        self.bus_schedule_path=''
        self.month=''
        self.date=''
        self.route=''
        self.method=''
        self.trip_path=''
        self.day=''
        self.filePath=''
        self.daySelect.setCurrentIndex(0)
        self.MethodBox.setCurrentIndex(0)
        self.comboBox.setCurrentIndex(0)
        self.progress.setValue(0)
        self.fillLog('Application system has been reset successfully!')


    def view_schedule(self):
        import subprocess
        p = subprocess.Popen(str(self.bus_schedule_path), shell=True)

    def fillLog(self,str):
        if(len(str)>60):
            first,second=str.split("/",1)
            self.log.setText(first+'\n'+second)

        self.log.setText(str)


    def view_trips(self):
        import subprocess
        p = subprocess.Popen(str(self.trip_path), shell=True)

    def generate_schedule(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Trip data')
        self.fetch_trips()
        self.progress.setValue(33)
        self.fillLog('Scheduling buses on route: '+str(self.route)+' for '+str(self.date)+'-'+str(self.month))
        self.generate_timetable()
        self.progress.setValue(100)
        self.fillLog('Bus Schedule and Allocation generated successfully at: '+ self.bus_schedule_path)
        print self.df_trips

    def generate_timetable(self):
        def gen_time(hours, minutes, trip_time):
            if (minutes + trip_time >= 60):
                minutes = minutes + trip_time - 60
                hours += 1
            else:
                minutes = minutes + trip_time
            if (hours >= 24):
                hours = 0
            return [hours, minutes]

        def gen_hourly_schedule(start_hour, end_hour, num_trips):
            step = round((end_hour - start_hour) * 60 / (num_trips + 1))
            schedule = []
            minutes = 0
            for i in range(int(num_trips)):
                schedule.append([start_hour, minutes])
                minutes += step
            return schedule

        def gen_minute_schedule(start_hour, curr_min, num_trips):
            step = round((60 - curr_min) / (num_trips + 1))
            schedule = []
            minutes = curr_min + step
            for i in range(int(num_trips)):
                schedule.append([start_hour, minutes])
                minutes += step
                if (minutes >= 60):
                    minutes -= round(step / 2)
            return schedule

        up_trips = []
        down_trips = []
        trip_time = 20
        for i in range(0, 20):
            up_trips.append(self.df_trips['Trips'][i])
            down_trips.append(self.df_trips['Trips_Down'][i])

        up_bus = np.zeros(20)
        down_bus = np.zeros(20)

        up_schedule = pd.DataFrame(columns=['Hour', 'Minutes', 'Bus Tag'])
        down_schedule = pd.DataFrame(columns=['Hour', 'Minutes', 'Bus Tag'])

        up_arrival = pd.DataFrame(columns=['Hour', 'Minutes', 'Bus Tag'])
        down_arrival = pd.DataFrame(columns=['Hour', 'Minutes', 'Bus Tag'])

        curr_hour = 4
        next_hour = 5
        curr_min = 0
        Bus_tag = 0

        up_bus[0] += 1
        schedule = gen_hourly_schedule(curr_hour, next_hour, 1)
        for i in range(len(schedule)):
            Bus_tag += 1
            up_schedule = up_schedule.append(pd.Series([schedule[i][0], schedule[i][1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
            arrival_time = gen_time(curr_hour, schedule[i][1], trip_time)
            # print arrival_time
            curr_min = schedule[i][1]
            down_arrival = down_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)

        down_bus[0] += 1
        schedule = gen_hourly_schedule(curr_hour, next_hour, 1)
        for i in range(len(schedule)):
            Bus_tag += 1
            down_schedule = down_schedule.append(pd.Series([schedule[i][0], schedule[i][1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
            arrival_time = gen_time(curr_hour, schedule[i][1], trip_time)
            curr_min = max(schedule[i][1], curr_min)
            up_arrival = up_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)

        up_trips[0] -= 1
        down_trips[0] -= 1
        for i in range(0, 20):
            while (up_trips[i] > 0 or down_trips[i] > 0):
                while (len(up_arrival) > 0 and up_trips[i] > 0):
                    up_arrival.sort_values(['Hour', 'Minutes'], ascending=[True, True], inplace=True)
                    if (up_arrival['Hour'].iloc[0] <= curr_hour):
                        rows = up_arrival.loc[up_arrival.index[[0]], :]
                        if (rows['Hour'].iloc[0] < curr_hour):
                            rows['Hour'].iloc[0] = curr_hour
                            rows['Minutes'].iloc[0] = curr_min
                            temp = gen_minute_schedule(curr_hour, curr_min, 1)
                            curr_min = temp[len(temp) - 1][1]
                        up_schedule = up_schedule.append(rows, ignore_index=True)
                        arrival_time = gen_time(curr_hour, rows['Minutes'].iloc[0], trip_time)
                        down_arrival = down_arrival.append(pd.Series([arrival_time[0], arrival_time[1], rows['Bus Tag'].iloc[0]],index=['Hour', 'Minutes', 'Bus Tag']), ignore_index=True)
                        up_arrival.drop(up_arrival.index[[0]], inplace=True)
                        up_trips[i] -= 1
                    else:
                        schedule = gen_minute_schedule(curr_hour, curr_min, up_trips[i])
                        for j in range(len(schedule)):
                            Bus_tag += 1
                            up_bus[i] += 1
                            up_schedule = up_schedule.append(pd.Series([schedule[j][0], schedule[j][1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                            arrival_time = gen_time(schedule[j][0], schedule[j][1], trip_time)
                            curr_min = schedule[j][1]
                            down_arrival = down_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                            up_trips[i] -= 1
                if (len(up_arrival) == 0 and up_trips[i] > 0):
                    schedule = gen_minute_schedule(curr_hour, curr_min, up_trips[i])
                    for j in range(len(schedule)):
                        Bus_tag += 1
                        up_bus[i] += 1
                        up_schedule = up_schedule.append(pd.Series([schedule[j][0], schedule[j][1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                        arrival_time = gen_time(schedule[j][0], schedule[j][1], trip_time)
                        curr_min = schedule[j][1]
                        down_arrival = down_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                        up_trips[i] -= 1

                while (len(down_arrival) > 0 and down_trips[i] > 0):
                    down_arrival.sort_values(['Hour', 'Minutes'], ascending=[True, True], inplace=True)
                    if (down_arrival['Hour'].iloc[0] <= curr_hour):
                        rows = down_arrival.loc[down_arrival.index[[0]], :]
                        if (rows['Hour'].iloc[0] < curr_hour):
                            rows['Hour'].iloc[0] = curr_hour
                            rows['Minutes'].iloc[0] = curr_min
                            temp = gen_minute_schedule(curr_hour, curr_min, 1)
                            curr_min = temp[len(temp) - 1][1]
                        down_schedule = down_schedule.append(rows, ignore_index=True)
                        arrival_time = gen_time(curr_hour, rows['Minutes'].iloc[0], trip_time)
                        up_arrival = up_arrival.append(pd.Series([arrival_time[0], arrival_time[1], rows['Bus Tag'].iloc[0]],index=['Hour', 'Minutes', 'Bus Tag']), ignore_index=True)
                        down_arrival.drop(down_arrival.index[[0]], inplace=True)
                        down_trips[i] -= 1
                    else:
                        schedule = gen_minute_schedule(curr_hour, curr_min, down_trips[i])
                        for j in range(len(schedule)):
                            Bus_tag += 1
                            down_bus[i] += 1
                            down_schedule = down_schedule.append(pd.Series([schedule[j][0], schedule[j][1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                            arrival_time = gen_time(schedule[j][0], schedule[j][1], trip_time)
                            curr_min = schedule[j][1]
                            up_arrival = up_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                            down_trips[i] -= 1
                if (len(down_arrival) == 0 and down_trips[i] > 0):
                    schedule = gen_minute_schedule(curr_hour, curr_min, down_trips[i])
                    for j in range(len(schedule)):
                        Bus_tag += 1
                        down_bus[i] += 1
                        down_schedule = down_schedule.append(pd.Series([schedule[j][0], schedule[j][1], Bus_tag], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                        arrival_time = gen_time(schedule[j][0], schedule[j][1], trip_time)
                        curr_min = schedule[j][1]
                        up_arrival = up_arrival.append(pd.Series([arrival_time[0], arrival_time[1], Bus_tag],index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
                        down_trips[i] -= 1
            curr_hour += 1
            next_hour += 1
            curr_min = 0

        total_bus = sum(up_bus) + sum(down_bus)
        down_schedule.sort_values(['Hour', 'Minutes'], ascending=[True, True], inplace=True)
        up_schedule.sort_values(['Hour', 'Minutes'], ascending=[True, True], inplace=True)
        up_schedule = up_schedule.append(pd.Series(['', 'Total Buses required:', sum(up_bus)], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
        down_schedule = down_schedule.append(pd.Series(['', 'Total Buses required:', sum(down_bus)], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)
        final_row = pd.DataFrame(columns=['Hour', 'Minutes', 'Bus Tag'])
        final_row = final_row.append(pd.Series(['', 'Total Buses required on route:', total_bus], index=['Hour', 'Minutes', 'Bus Tag']),ignore_index=True)

        schedule_file_name = "Bus Schedule_" + str(self.method)+'_'+str(self.route)+'_'+str(self.month)+'_'+str(self.date)+'_'+str(self.day)
        frames = [up_schedule, down_schedule, final_row]
        result = pd.concat(frames, keys=['Up', 'Down', 'Summary'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/'+str(self.route)+'/Bus schedule and allocation/'
        result.to_csv(save_path + schedule_file_name + '.csv')
        self.bus_schedule_path=save_path + schedule_file_name + '.csv'

    def fetch_trips(self):
        self.df_trips = pd.DataFrame(columns=['Time Slot', 'Trips', 'Trips_Down'])
        with open(self.trip_path, 'rb') as f:
            reader = csv.reader(f, delimiter=",")
            rows = [r for r in reader]
            for x in rows[1:]:
                self.df_trips = self.df_trips.append(pd.Series([x[1],x[2], x[3]],index=['Time Slot', 'Trips', 'Trips_Down']),ignore_index=True)
                self.df_trips.replace('', 0)
                self.df_trips[['Trips','Trips_Down']] = self.df_trips[['Trips', 'Trips_Down']].apply(pd.to_numeric)


    def processfile(self):
        opened_file = open(self.filePath, 'rb')
        selected_route = str(self.comboBox.currentText())
        self.route=selected_route
        udf = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers'])
        ddf = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers'])
        self.progress.setValue(25)
        reader = csv.reader(opened_file, delimiter=",")
        timeslot = []
        up_trips = []
        down_trips = []
        up_passengers = []
        down_passengers = []
        rows = [r for r in reader]
        # print selected_route
        route = ''.join(re.findall(r'\d+', rows[0][0]))
        if(selected_route!=route):
            self.fillLog('Wrong File Uploaded. Please upload file for route:'+ selected_route)
            self.progress.setValue(0)
            return
        month = self.months[''.join(re.findall(r'\d+', rows[0][1][:9]))]
        date = ''.join(re.findall(r'\d+', rows[0][1][10:12]))
        day = rows[0][9][6:]
        self.progress.setValue(50)
        for x in rows[4:-1]:
            timeslot.append(x[0])
            up_trips.append(x[1])
            up_passengers.append(x[3])
            down_trips.append(x[9])
            down_passengers.append(x[11])

        for j in xrange(len(timeslot)):
            udf = udf.append(
                pd.Series([timeslot[j], up_trips[j], up_passengers[j]], index=['Time Slot', 'Trips', 'Passengers']),
                ignore_index=True)
            ddf = ddf.append(
                pd.Series([timeslot[j], down_trips[j], down_passengers[j]], index=['Time Slot', 'Trips', 'Passengers']),
                ignore_index=True)
        self.progress.setValue(75)
        filename = route + '_Up_' + date + '_' + month + '_' + day
        self.up_path='C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route + '/Up/'
        self.down_path='C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route + '/Down/'
        udf.to_csv('C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route + '/Up/Clean data' + filename + '.csv')
        filename = route + '_Down_' + date + '_' + month + '_' + day
        ddf.to_csv('C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route + '/Down/Clean data' + filename + '.csv')
        self.progress.setValue(100)
        self.fillLog('File Uploaded and cleaned. File placed at: ' + 'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route)
        print(str(self.filePath))

    def day_choice(self,selected_day):
        Days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        self.day = Days[str(selected_day)]
        print self.day

    def singlebrowse(self):
        import shutil
        self.filePath = QtGui.QFileDialog.getOpenFileName(self, 'Select File', "", '*.csv')
        opened_file = open(self.filePath, 'rb')
        reader = csv.reader(opened_file, delimiter=",")
        rows = [r for r in reader]
        month = self.months[''.join(re.findall(r'\d+', rows[0][1][:9]))]
        date = ''.join(re.findall(r'\d+', rows[0][1][10:12]))
        day = rows[0][9][6:]
        route = ''.join(re.findall(r'\d+', rows[0][0]))
        opened_file.close()
        dstpath= 'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + route + '/Uncleaned data/Uncleaned_file_'+month+'_'+date+'_'+day+'.csv'
        shutil.copyfile(self.filePath,dstpath)
        self.progress.setValue(100)
        self.fillLog('File Selected successfully:'+ str(self.filePath))
        self.progress.setValue(0)
        print self.filePath

    def showDate(self, date):
        date_selected=date.toString()
        self.lbl.setText(date.toString())
        print date_selected

    def showPredictionDate(self, date):
        prediction_date=date
        var_date = str(prediction_date.toPyDate())
        self.month = var_date[5:7]
        self.date = var_date[8:]
        self.lbl.setText(date.toString())

    def route_choice(self, selected_route):
       self.route = selected_route

    def method_choice(self, method):
        self.method = method
        self.fillLog('Selected method: '+method)

    def generate_trips(self):
        if (self.method == 'Polynomial Regression'):
            self.polynomial_reg()
        elif (self.method == 'LSTM'):
            self.lstm_RNN()
        elif (self.method == 'Arimax'):
            self.arimax()
        elif (self.method == 'Sarimax'):
            self.sarimax()
        elif (self.method == 'SVM'):
            self.svm()
        elif (self.method == 'NN Categorical'):
            self.nn_cat()

    def polynomial_reg(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing regression for up trips')
        self.reg_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing regression for down trips')
        self.reg_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                           '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                           '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                           '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                           '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot', 'Poly_Trips', 'Poly_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/'+str(self.route)+'/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],
                          index=['Time Slot', 'Poly_Trips', 'Poly_Trips_Down']),ignore_index=True)
        filename = 'Forecasted_trips_'+str(self.method)+'_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path =save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('Regression Successful. Forecasted trips file at: '+self.trip_path)

    def lstm_RNN(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing LSTM for up trips')
        self.lstm_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing LSTM for down trips')
        self.lstm_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot', 'LSTM_Trips', 'LSTM_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + str(self.route) + '/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],index=['Time Slot', 'LSTM_Trips','LSTM_Trips_Down']), ignore_index=True)
        filename = 'Forecasted_trips_' + str(self.method) + '_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path = save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('LSTM Successful. Forecasted trips file at: ' + self.trip_path)

    def arimax(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing Arimax for up trips')
        self.arimax_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing Arimax for down trips')
        self.arimax_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot','Arima_Trips','Arima_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/'+str(self.route)+'/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],
                          index=['Time Slot','Arima_Trips','Arima_Trips_Down']),ignore_index=True)
        filename = 'Forecasted_trips_' + str(self.method) + '_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path = save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('Arimax Successful. Forecasted trips file at: ' + self.trip_path)

    def sarimax(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing Sarimax for up trips')
        self.sarimax_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing Sarimax for down trips')
        self.sarimax_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot', 'Sarimax_Trips', 'Sarimax_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + str(self.route) + '/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],index=['Time Slot', 'Sarimax_Trips','Sarimax_Trips_Down']), ignore_index=True)
        filename = 'Forecasted_trips_' + str(self.method) + '_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path = save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('Sarimax Successful. Forecasted trips file at: ' + self.trip_path)

    def svm(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing SVM for up trips')
        self.svm_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing SVM for down trips')
        self.svm_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot', 'SVM_Trips', 'SVM_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + str(self.route) + '/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],index=['Time Slot','SVM_Trips','SVM_Trips_Down']), ignore_index=True)
        filename = 'Forecasted_trips_' + str(self.method) + '_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path = save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('SVM Successful. Forecasted trips file at: ' + self.trip_path)

    def nn_cat(self):
        self.progress.setValue(0)
        self.fillLog('Fetching Up data')
        self.fetch_data_up()
        self.progress.setValue(25)
        self.fillLog('Performing NN Categorical for up trips')
        self.nn_cat_predict_up()
        self.progress.setValue(50)
        self.fillLog('Fetching Down data')
        self.fetch_data_down()
        self.progress.setValue(75)
        self.fillLog('Performing NN Categorical for down trips')
        self.nn_cat_predict_down()
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        forecasted_trips = pd.DataFrame(columns=['Time Slot', 'NN_Trips', 'NN_Trips_Down'])
        save_path = r'C:/Users/Rushabh-L/Desktop/FYP/GUI Folders/' + str(self.route) + '/Forecasted Trips/'
        for j in xrange(len(timeslot)):
            forecasted_trips = forecasted_trips.append(pd.Series([timeslot[j], self.up_trips[j], self.down_trips[j]],index=['Time Slot', 'NN_Trips','NN_Trips_Down']), ignore_index=True)
        filename = 'Forecasted_trips_' + str(self.method) + '_' + str(self.route) + '_' + str(self.month) + '_' + str(self.date) + '_' + str(self.day)
        forecasted_trips.to_csv(save_path + filename + '.csv')
        self.trip_path = save_path + filename + '.csv'
        self.progress.setValue(100)
        self.fillLog('NN Categorical Successful. Forecasted trips file at: ' + self.trip_path)

    def fetch_data_up(self):
        allfiles = glob.glob(self.up_path + "*.csv")
        down_allfiles = glob.glob(self.down_path + "*.csv")
        Holiday_colnames = ['Holiday', 'Date', 'Day', 'Month']
        Holiday_data = pd.read_csv('C:\Users\Rushabh-L\Desktop\FYP\List of holidays.csv', names=Holiday_colnames)
        Days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}

        # Making separate dataframes for each separate timeslot over many days
        self.df1 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df2 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df3 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df4 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df5 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df6 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df7 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df8 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df9 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df10 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df11 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df12 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df13 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df14 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df15 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df16 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df17 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df18 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df19 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df20 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df = [self.df1, self.df2, self.df3, self.df4, self.df5, self.df6, self.df7, self.df8, self.df9, self.df10, self.df11, self.df12, self.df13, self.df14, self.df15, self.df16, self.df17, self.df18, self.df19,
                   self.df20]
        # Dicing only requird data from list of holidays
        holiday_day = Holiday_data['Day']
        holiday_month = Holiday_data['Month']

        self.isCurrDay_holiday = 0
        for i in range(1, 24):  # checking if there is holiday today
            if (holiday_day[i] == self.date and self.month == holiday_month[i]):
                self.isCurrDay_holiday = 1

        for files in allfiles:
            # Obtaining Day and date details from filename
            base = os.path.basename(files)
            day = os.path.splitext(base)[0][25:]
            date = os.path.splitext(base)[0][18:20]
            month = os.path.splitext(base)[0][21:24]

            # Determining whether holiday or not
            holiday = 0
            for i in range(1, 24):
                if (holiday_day[i] == date and month == holiday_month[i]):
                    holiday = 1

            # Pre-processing data into required format
            day = Days[day]  # Mapping day to numeric value
            with open(files, 'rb') as f:
                timeslot = []
                trips = []
                passengers = []
                reader = csv.reader(f, delimiter=",")
                rows = [r for r in reader]
                for x in rows[1:]:
                    timeslot.append(x[1])
                    trips.append(x[2])
                    if (x[3] == ''):
                        x[3] = 0
                    passengers.append(x[3])

            # Adding data into the dataframes created previously according to time slots
            for j in xrange(len(timeslot)):
                self.df[j] = self.df[j].append(pd.Series([timeslot[j], trips[j], int(passengers[j]), day, holiday],
                                               index=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday']),ignore_index=True)
                self.df[j] = self.df[j].replace('', 0)  # Replacing NAN values by 0

    def fetch_data_down(self):
        down_allfiles = glob.glob(self.down_path + "*.csv")
        Holiday_colnames = ['Holiday', 'Date', 'Day', 'Month']
        Holiday_data = pd.read_csv('C:\Users\Rushabh-L\Desktop\FYP\List of holidays.csv', names=Holiday_colnames)
        Days = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}

        # Making separate dataframes for each separate timeslot over many days
        self.df1 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df2 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df3 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df4 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df5 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df6 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df7 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df8 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df9 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df10 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df11 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df12 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df13 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df14 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df15 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df16 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df17 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df18 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df19 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df20 = pd.DataFrame(columns=['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday'])
        self.df = [self.df1, self.df2, self.df3, self.df4, self.df5, self.df6, self.df7, self.df8, self.df9,
                   self.df10, self.df11, self.df12, self.df13, self.df14, self.df15, self.df16, self.df17,
                   self.df18, self.df19,
                   self.df20]
        # Dicing only requird data from list of holidays
        holiday_day = Holiday_data['Day']
        holiday_month = Holiday_data['Month']

        self.isCurrDay_holiday = 0
        for i in range(1, 24):  # checking if there is holiday today
            if (holiday_day[i] == self.date and self.month == holiday_month[i]):
                self.isCurrDay_holiday = 1

        for files in down_allfiles:
            # Obtaining Day and date details from filename
            base = os.path.basename(files)
            day = os.path.splitext(base)[0][27:]
            date = os.path.splitext(base)[0][18:20]
            month = os.path.splitext(base)[0][21:24]

            # Determining whether holiday or not
            holiday = 0
            for i in range(1, 24):
                if (holiday_day[i] == date and month == holiday_month[i]):
                    holiday = 1

            # Pre-processing data into required format
            day = Days[day]  # Mapping day to numeric value
            with open(files, 'rb') as f:
                timeslot = []
                trips = []
                passengers = []
                reader = csv.reader(f, delimiter=",")
                rows = [r for r in reader]
                for x in rows[1:]:
                    timeslot.append(x[1])
                    trips.append(x[2])
                    if (x[3] == ''):
                        x[3] = 0
                    passengers.append(x[3])

            # Adding data into the dataframes created previously according to time slots
            for j in xrange(len(timeslot)):
                self.df[j] = self.df[j].append(pd.Series([timeslot[j], trips[j], int(passengers[j]), day, holiday],
                                                         index=['Time Slot', 'Trips', 'Passengers', 'Day',
                                                                'isHoliday']), ignore_index=True)
                self.df[j] = self.df[j].replace('', 0)  # Replacing NAN values by 0

    def reg_predict_up(self):
        import numpy as np
        from sklearn.preprocessing import PolynomialFeatures
        Timeslot_values = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                           '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                           '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                           '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                           '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']
        self.up_trips = []
        self.up_pass = []
        # To obtain average error measure across all dataframes
        for j in xrange(len(Timeslot_values)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging

            passenger_predictor = LinearRegression(
                normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.up_pass.append(round(pass_pred))
            target = np.append(target, round(pass_pred))
            print target  # Target features for predicting number of trips

            trip_data = np.asarray(self.df[j][['Day', 'isHoliday', 'Passengers']])
            trip_labels = np.asarray(self.df[j]['Trips'])

            # generate a model of polynomial features
            poly = PolynomialFeatures(5)
            target = [target]

            # transform the x data for proper fitting (for single variable type it returns,[1,x,x**2])
            trip_data_ = poly.fit_transform(trip_data)

            # transform the prediction to fit the model type
            target_ = poly.fit_transform(target)

            # here we can remove polynomial orders we don't want
            # for instance I'm removing the `x` component
            trip_data_ = np.delete(trip_data_, [7, 10, 13], axis=1)
            target_ = np.delete(target_, [7, 10, 13], axis=1)

            # generate the regression object
            clf = linear_model.LinearRegression()
            # preform the actual regression
            clf.fit(trip_data_, trip_labels)
            pred = round(clf.predict(target_))
            if pred <= 0 or pred == '' or pred > 20:
                pred = 0
            self.up_trips.append(pred)
            print "Prediction =", pred

        for i in range(len(self.up_trips)):
            if self.up_trips[i] == '':
                self.up_trips[i] = 0
        self.up_trips = [0 if x is None else x for x in self.up_trips]

    def reg_predict_down(self):
        import numpy as np
        from sklearn.preprocessing import PolynomialFeatures
        Timeslot_values = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                           '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                           '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                           '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                           '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        self.down_trips = []
        self.down_pass = []
        for j in xrange(len(Timeslot_values)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging

            passenger_predictor = LinearRegression(
                normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.down_pass.append(round(pass_pred))
            target = np.append(target, round(pass_pred))
            print target  # Target features for predicting number of trips

            trip_data = np.asarray(self.df[j][['Day', 'isHoliday', 'Passengers']])
            trip_labels = np.asarray(self.df[j]['Trips'])

            # generate a model of polynomial features
            poly = PolynomialFeatures(5)
            target = [target]

            # transform the x data for proper fitting (for single variable type it returns,[1,x,x**2])
            trip_data_ = poly.fit_transform(trip_data)

            # transform the prediction to fit the model type
            target_ = poly.fit_transform(target)

            # here we can remove polynomial orders we don't want
            # for instance I'm removing the `x` component
            trip_data_ = np.delete(trip_data_, [7, 10, 13], axis=1)
            target_ = np.delete(target_, [7, 10, 13], axis=1)

            # generate the regression object
            clf = linear_model.LinearRegression()
            # preform the actual regression
            clf.fit(trip_data_, trip_labels)
            pred = round(clf.predict(target_))
            if pred <= 0 or pred == '' or pred > 20:
                pred = 0
            self.down_trips.append(pred)
            print "Prediction =", pred

        for i in range(len(self.down_trips)):
            if self.down_trips[i] == '':
                self.down_trips[i] = 0
        self.down_trips = [0 if x is None else x for x in self.down_trips]

    def arimax_predict_up(self):
        from statsmodels.tsa.arima_model import ARIMA
        import numpy

        # create a differenced series
        def difference(dataset, interval=1):
            diff = list()
            for i in range(interval, len(dataset)):
                value = dataset[i] - dataset[i - interval]
                diff.append(value)
            return numpy.array(diff)

        # invert differenced value
        def inverse_difference(history, yhat, interval=1):
            return yhat + history[-interval]

        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                           '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                           '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                           '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                           '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        pass_forecast = []
        for j in xrange(len(timeslot)):
            # load dataset
            series = self.df[j].copy()
            # print series
            series.drop(['Time Slot', 'Trips', 'isHoliday', 'Day'], axis=1, inplace=True)
            # seasonal difference
            X = series.values
            days_in_week = 7  # Change name
            differenced = difference(X, days_in_week)
            # fit model
            differenced = differenced.astype('float64')
            model = ARIMA(differenced, order=(1, 0, 0))
            model_fit = model.fit(disp=0)
            # multi-step out-of-sample forecast
            forecast = model_fit.forecast(steps=1)[0]
            history = [x for x in X]
            day = 1
            for yhat in forecast:
                inverted = inverse_difference(history, yhat, days_in_week)
                print('Day %d: %f' % (day, inverted))
                pass_forecast.append(round(inverted[0]))
                history.append(inverted)
                day += 1

        self.up_trips = []
        for j in range(len(timeslot)):
            target = pd.Series([self.day, self.isCurrDay_holiday], index=['Day', 'isHoliday'])
            target['Passengers'] = pass_forecast[j]
            df_try = self.df[j][['Day', 'isHoliday', 'Passengers']]
            labels = self.df[j]['Trips']
            print target
            print df_try
            labels = np.asarray(labels, dtype=float)
            df_try = np.asarray(df_try, dtype=float)
            model1 = ARIMA(endog=labels, exog=df_try, order=(1, 0, 0)).fit()
            trip_forecast = model1.forecast(steps=1, exog=target)
            if (trip_forecast[0] < 0.0001):
                trips = 0
            else:
                trips = round(trip_forecast[0])
            self.up_trips.append(trips)
            print trip_forecast

    def arimax_predict_down(self):
        from statsmodels.tsa.arima_model import ARIMA
        import numpy
        # create a differenced series
        def difference(dataset, interval=1):
            diff = list()
            for i in range(interval, len(dataset)):
                value = dataset[i] - dataset[i - interval]
                diff.append(value)
            return numpy.array(diff)

        # invert differenced value
        def inverse_difference(history, yhat, interval=1):
            return yhat + history[-interval]

        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        pass_down = []
        for j in xrange(len(timeslot)):
            # load dataset
            series = self.df[j].copy()
            # print series
            series.drop(['Time Slot', 'Trips', 'isHoliday', 'Day'], axis=1, inplace=True)
            # seasonal difference
            X = series.values
            days_in_week = 7  # Change name
            differenced = difference(X, days_in_week)
            # fit model
            differenced = differenced.astype('float64')
            model = ARIMA(differenced, order=(1, 0, 0))
            model_fit = model.fit(disp=0)
            # multi-step out-of-sample forecast
            forecast = model_fit.forecast(steps=1)[0]
            history = [x for x in X]
            day = 1
            for yhat in forecast:
                inverted = inverse_difference(history, yhat, days_in_week)
                print('Day %d: %f' % (day, inverted))
                pass_down.append(round(inverted[0]))
                history.append(inverted)
                day += 1

        self.down_trips = []
        def is_invertible(a):
            return a.shape[0] == a.shape[1] and np.linalg.matrix_rank(a) == a.shape[0]

        for j in range(len(timeslot)):
            target = pd.Series([self.day, self.isCurrDay_holiday], index=['Day', 'isHoliday'])
            target['Passengers'] = pass_down[j]
            df_try = self.df[j][['Day', 'isHoliday', 'Passengers']]
            df_try = df_try.as_matrix()
            labels = self.df[j]['Trips']
            #print target
            labels = np.asarray(labels, dtype=float)
            df_try = np.asarray(df_try, dtype=float)
            #print df_try
            if (is_invertible(df_try) or df_try.sum() == 0 or j >= 19):
                trips = 0
            else:
                model = ARIMA(endog=labels, exog=df_try, order=(1, 0, 0)).fit(trend='nc')
                trip_forecast = model.forecast(steps=1, exog=target)
                if (trip_forecast[0] <= 0):
                    trips = 0
                else:
                    trips = round(trip_forecast[0])
            self.down_trips.append(trips)
            #print trip_forecast

    def sarimax_predict_up(self):
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        for j in xrange(len(timeslot)):
            self.df[j]['Trips'] = self.df[j]['Trips'].apply(pd.to_numeric)

        up_pass = []
        for j in range(len(timeslot)):
            self.df[j].index = pd.DatetimeIndex(freq="d", start=0, periods=self.df[j].shape[0])
            series = self.df[j].copy()
            series.drop(['Time Slot', 'Trips', 'isHoliday', 'Day'], axis=1, inplace=True)
            # seasonal difference
            X = series.values
            model = sm.tsa.statespace.SARIMAX(series.Passengers, trend='n', order=(1, 0, 0),seasonal_order=(0, 1, 1, 7), enforce_invertibility=False)
            model_fit = model.fit()
            # print model_fit.summary()
            forecast_values = model_fit.forecast(steps=1)
            if forecast_values[0] <= 0:
                up_pass.append(0)
            else:
                up_pass.append(round(forecast_values[0]))

        self.up_trips = []
        for j in range(len(timeslot)):
            target = pd.Series([self.day, self.isCurrDay_holiday, ], index=['Day', 'isHoliday'])
            target['Passengers'] = up_pass[j]
            df_try = self.df[j][['Day', 'isHoliday', 'Passengers']].copy()
            labels = self.df[j]['Trips'].copy()

            labels = np.asarray(labels, dtype=float)
            df_try = np.asarray(df_try, dtype=float)
            target = np.asarray(target, dtype=float)
            target = [target]
            #print target
            model_trips = sm.tsa.statespace.SARIMAX(endog=labels, exog=df_try, trend='n', order=(1, 0, 0),seasonal_order=(0, 1, 1, 7), enforce_stationarity=True,
                                                    enforce_invertibility=False)
            model_trips = model_trips.fit()
            trip_forecast = model_trips.forecast(steps=1, exog=target)
            #print trip_forecast
            if trip_forecast[0] <= 0:
                trip = 0
            else:
                trip = round(trip_forecast[0])
            self.up_trips.append(trip)

    def sarimax_predict_down(self):
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        for j in xrange(len(timeslot)):
            self.df[j]['Trips'] = self.df[j]['Trips'].apply(pd.to_numeric)

        self.down_trips = []
        self.down_pass = []

        for j in range(len(timeslot)):
            self.df[j].index = pd.DatetimeIndex(freq="d", start=0, periods=self.df[j].shape[0])
            series = self.df[j].copy()
            series.drop(['Time Slot', 'Trips', 'isHoliday', 'Day'], axis=1, inplace=True)
            # seasonal difference
            X = series.values
            model = sm.tsa.statespace.SARIMAX(series.Passengers, trend='n', order=(1, 0, 0),seasonal_order=(0, 1, 1, 7), enforce_invertibility=False)
            model_fit = model.fit()
            # print model_fit.summary()
            forecast_values = model_fit.forecast(steps=1)
            if forecast_values[0] <= 0:
                self.down_pass.append(0)
            else:
                self.down_pass.append(round(forecast_values[0]))

        for j in range(len(timeslot)):
            target = pd.Series([self.day, self.isCurrDay_holiday, ], index=['Day', 'isHoliday'])
            target['Passengers'] = self.down_pass[j]
            df_try = self.df[j][['Day', 'isHoliday', 'Passengers']].copy()
            labels = self.df[j]['Trips'].copy()

            labels = np.asarray(labels, dtype=float)
            df_try = np.asarray(df_try, dtype=float)
            target = np.asarray(target, dtype=float)
            target = [target]
            #print target
            if (j < 19):
                model_trips = sm.tsa.statespace.SARIMAX(endog=labels, exog=df_try, trend='n', order=(1, 0, 0),seasonal_order=(1, 1, 1, 7), enforce_stationarity=True,
                                                        enforce_invertibility=False)
                model_trips = model_trips.fit()
                trip_forecast = model_trips.forecast(steps=1, exog=target)
                #print trip_forecast
                if trip_forecast[0] <= 0:
                    trip = 0
                else:
                    trip = round(trip_forecast[0])
            else:
                trip = 0
            self.down_trips.append(trip)

    def lstm_predict_up(self):
        from sklearn.preprocessing import MinMaxScaler
        from keras.models import Sequential
        from keras.layers import Dense
        from keras.layers import LSTM
        from numpy import concatenate
        from pandas import DataFrame
        from pandas import concat

        # convert series to supervised learning
        def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
            n_vars = 1 if type(data) is list else data.shape[1]
            df = DataFrame(data)
            cols, names = list(), list()
            # input sequence (t-n, ... t-1)
            for i in range(n_in, 0, -1):
                cols.append(df.shift(i))
                names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
            # forecast sequence (t, t+1, ... t+n)
            for i in range(0, n_out):
                cols.append(df.shift(-i))
                if i == 0:
                    names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
                else:
                    names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
            # put it all together
            agg = concat(cols, axis=1)
            agg.columns = names
            # drop rows with NaN values
            if dropnan:
                agg.dropna(inplace=True)
            return agg

        self.up_trips = []
        # load dataset
        for i in range(0, 20):
            dataset = self.df[i].copy()
            dataset.drop('Time Slot', axis=1, inplace=True)
            values = dataset.values
            # ensure all data is float
            values = values.astype('float32')
            # normalize features
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled = scaler.fit_transform(values)
            # frame as supervised learning
            reframed = series_to_supervised(scaled, 1, 1)
            # drop columns we don't want to predict
            reframed.drop(reframed.columns[[5, 6, 7]], axis=1, inplace=True)
            # print(reframed.head())             #To debug

            # Divide Data into Training and test set
            values = reframed.values
            # n_train_steps = 30                  #Training set size
            train_set = values[:, :]
            test_set = values[:, :]
            # split into input and outputs
            train_X, train_y = train_set[:-1, :-1], train_set[:-1, -1]
            test_X, test_y = test_set[-1:, :-1], test_set[-1:, -1]

            # reshape input to be 3D [samples, timesteps, features]
            train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

            # design network
            model = Sequential()
            model.add(LSTM(5, input_shape=(train_X.shape[1], train_X.shape[2])))  # Adding LSTM units into the RNN
            model.add(Dense(1))
            model.compile(loss='mae', optimizer='adam')  # mae-Mean Absolute error, Adam optimization rule
            # fit network
            history = model.fit(train_X, train_y, epochs=20, batch_size=3, validation_data=(test_X, test_y), verbose=1,shuffle=False)

            # obtaining predictions
            test_prediction = model.predict(test_X)
            test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))

            # invert scaling for forecast
            actual_prediction = concatenate((test_prediction, test_X[:, 1:]), axis=1)
            actual_prediction = scaler.inverse_transform(actual_prediction)
            actual_prediction = actual_prediction[:, 0]
            for x in actual_prediction:
                print round(x)
                if round(x) <= 0:
                    self.up_trips.append(0)
                else:
                    self.up_trips.append(round(x))

            # invert scaling for actual ie. already available predictions(teacher signal)
            test_y = test_y.reshape((len(test_y), 1))
            inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
            inv_y = scaler.inverse_transform(inv_y)
            inv_y = inv_y[:, 0]
            print inv_y
            # print df[i]['Trips']

    def lstm_predict_down(self):
        from sklearn.preprocessing import MinMaxScaler
        from keras.models import Sequential
        from keras.layers import Dense
        from keras.layers import LSTM
        from numpy import concatenate
        from pandas import DataFrame
        from pandas import concat


        # convert series to supervised learning
        def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
            n_vars = 1 if type(data) is list else data.shape[1]
            df = DataFrame(data)
            cols, names = list(), list()
            # input sequence (t-n, ... t-1)
            for i in range(n_in, 0, -1):
                cols.append(df.shift(i))
                names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
            # forecast sequence (t, t+1, ... t+n)
            for i in range(0, n_out):
                cols.append(df.shift(-i))
                if i == 0:
                    names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
                else:
                    names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
            # put it all together
            agg = concat(cols, axis=1)
            agg.columns = names
            # drop rows with NaN values
            if dropnan:
                agg.dropna(inplace=True)
            return agg

        self.down_trips = []
        # load dataset
        for i in range(0, 20):
            dataset = self.df[i].copy()
            dataset.drop('Time Slot', axis=1, inplace=True)
            values = dataset.values
            # ensure all data is float
            values = values.astype('float32')
            # normalize features
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled = scaler.fit_transform(values)
            # frame as supervised learning
            reframed = series_to_supervised(scaled, 1, 1)
            # drop columns we don't want to predict
            reframed.drop(reframed.columns[[5, 6, 7]], axis=1, inplace=True)
            # print(reframed.head())             #To debug

            # Divide Data into Training and test set
            values = reframed.values
            # n_train_steps = 30                  #Training set size
            train_set = values[:, :]
            test_set = values[:, :]
            # split into input and outputs
            train_X, train_y = train_set[:-1, :-1], train_set[:-1, -1]
            test_X, test_y = test_set[-1:, :-1], test_set[-1:, -1]

            # reshape input to be 3D [samples, timesteps, features]
            train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

            # design network
            model = Sequential()
            model.add(LSTM(5, input_shape=(train_X.shape[1], train_X.shape[2])))  # Adding LSTM units into the RNN
            model.add(Dense(1))
            model.compile(loss='mae', optimizer='adam')  # mae-Mean Absolute error, Adam optimization rule
            # fit network
            history = model.fit(train_X, train_y, epochs=20, batch_size=3, validation_data=(test_X, test_y), verbose=1,
                                shuffle=False)

            # obtaining predictions
            test_prediction = model.predict(test_X)
            test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))

            # invert scaling for forecast
            print test_prediction
            actual_prediction = concatenate((test_prediction, test_X[:, 1:]), axis=1)
            actual_prediction = scaler.inverse_transform(actual_prediction)
            actual_prediction = actual_prediction[:, 0]
            for x in actual_prediction:
                print round(x)
                if round(x) <= 0:
                    self.down_trips.append(0)
                else:
                    self.down_trips.append(round(x))

            # invert scaling for actual ie. already available predictions(teacher signal)
            test_y = test_y.reshape((len(test_y), 1))
            inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
            inv_y = scaler.inverse_transform(inv_y)
            inv_y = inv_y[:, 0]
            print inv_y
            print 'For df',i
            # print df[i]['Trips']

    def svm_predict_up(self):
        from sklearn.linear_model import LinearRegression
        from sklearn import svm

        for i in xrange(20):
            for j in xrange(len(self.df[i]['Time Slot'])):
                self.df[i]['Time Slot'][j] = int(self.df[i]['Time Slot'][j][:2])

        feature_names = ['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday']
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        C = 1.0
        self.up_trips = []
        self.up_pass = []
        for j in xrange(len(timeslot)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging

            passenger_predictor = LinearRegression(normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.up_pass.append(round(pass_pred))
            target = np.append(round(pass_pred), target)
            print target

            X = self.df[j][feature_names].drop(['Trips', 'Time Slot'], axis=1).values
            y = self.df[j]['Trips'].values
            y = y.astype('int')
            if (j == 19 and len(np.unique(y)) < 2):
                predicted_trips = 0
            else:
                svc = svm.SVC(kernel='rbf', degree=3, C=C, ).fit(X, y)
                target = target.reshape(1, 3)
                predicted_trips = svc.predict(target)

            self.up_trips.append(int(predicted_trips))
            print('Predicted trips for timeslot: %d is: %d' % (j + 1, predicted_trips))

        for i in range(len(self.up_trips)):
            if self.up_trips[i] == '':
                self.up_trips[i] = 0
        self.up_trips = [0 if x is None else x for x in self.up_trips]

    def svm_predict_down(self):
        from sklearn.linear_model import LinearRegression
        from sklearn import svm

        for i in xrange(20):
            for j in xrange(len(self.df[i]['Time Slot'])):
                self.df[i]['Time Slot'][j] = int(self.df[i]['Time Slot'][j][:2])

        feature_names = ['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday']
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        C = 1.0
        self.down_trips = []
        self.down_pass = []
        for j in xrange(len(timeslot)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging
            passenger_predictor = LinearRegression(normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.down_pass.append(round(pass_pred))
            target = np.append(round(pass_pred), target)
            print target

            X = self.df[j][feature_names].drop(['Trips', 'Time Slot'], axis=1).values
            y = self.df[j]['Trips'].values
            y = y.astype('int')
            if (j == 19 and len(np.unique(y)) < 2):
                predicted_trips = 0
            else:
                svc = svm.SVC(kernel='rbf', degree=3, C=C, ).fit(X, y)
                target = target.reshape(1, 3)
                predicted_trips = int(svc.predict(target))
            self.down_trips.append(predicted_trips)
            print('Predicted trips for timeslot: %d is: %d' % (j + 1, predicted_trips))

        for i in range(len(self.down_trips)):
            if self.down_trips[i] == '':
                self.down_trips[i] = 0
        self.down_trips = [0 if x is None else x for x in self.down_trips]

    def nn_cat_predict_up(self):
        from sklearn.linear_model import LinearRegression
        import keras
        from keras.models import Sequential
        from keras.layers import Dense, Dropout
        from keras.optimizers import RMSprop
        from theano import ifelse

        for i in xrange(20):
            for j in xrange(len(self.df[i]['Time Slot'])):
                self.df[i]['Time Slot'][j] = int(self.df[i]['Time Slot'][j][:2])

        feature_names = ['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday']
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        self.up_trips = []
        self.up_pass = []
        # To obtain average error measure across all dataframes
        for j in xrange(len(timeslot)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging
            passenger_predictor = LinearRegression(normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.up_pass.append(round(pass_pred))
            target = np.append(round(pass_pred), target)
            print target  # Target features for predicting number of trips
            train_all_features = self.df[j][feature_names][:36].drop(['Trips', 'Time Slot'],axis=1).values  # create training data with trips and time slot dropped
            test_all_features = self.df[j][feature_names][36:].drop(['Trips', 'Time Slot'],axis=1).values  # create testing data with trips and time slot dropped
            # print train_all_features,all_classes
            train_labels = keras.utils.to_categorical(self.df[j]['Trips'][:36],8)  # create categorical data df[i]['Trips'][:32].argmax()
            test_labels = keras.utils.to_categorical(self.df[j]['Trips'][36:], 8)  # create categorical data
            # model creation
            model = Sequential()
            # input layer
            model.add(Dense(4, activation='relu', input_shape=(3,)))
            # hidden layer
            model.add(Dense(2, activation='relu'))
            # drop 20% nodes
            model.add(Dropout(0.2))
            # output layer
            model.add(Dense(8, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])
            history = model.fit(train_all_features, train_labels, batch_size=30, epochs=10, verbose=2,validation_data=(test_all_features, test_labels))
            predicted_trips = 0
            target = target.reshape(1, 3)
            predicted_trips += model.predict(target).argmax()
            self.up_trips.append(predicted_trips)
            print('Predicted trips for timeslot: %d is: %d' % (j + 1, predicted_trips))

        for i in range(len(self.up_trips)):
            if self.up_trips[i] == '':
                self.up_trips[i] = 0
        self.up_trips = [0 if x is None else x for x in self.up_trips]

    def nn_cat_predict_down(self):
        from sklearn.linear_model import LinearRegression
        import keras
        from keras.models import Sequential
        from keras.layers import Dense, Dropout
        from keras.optimizers import RMSprop
        from theano import ifelse

        for i in xrange(20):
            for j in xrange(len(self.df[i]['Time Slot'])):
                self.df[i]['Time Slot'][j] = int(self.df[i]['Time Slot'][j][:2])

        feature_names = ['Time Slot', 'Trips', 'Passengers', 'Day', 'isHoliday']
        timeslot = ['00:00:01-05:00:00', '05:00:01-06:00:00', '06:00:01-07:00:00', '07:00:01-08:00:00',
                    '08:00:01-09:00:00', '09:00:01-10:00:00', '10:00:01-11:00:00', '11:00:01-12:00:00',
                    '12:00:01-13:00:00', '13:00:01-14:00:00', '14:00:01-15:00:00', '15:00:01-16:00:00',
                    '16:00:01-17:00:00', '17:00:01-18:00:00', '18:00:01-19:00:00', '19:00:01-20:00:00',
                    '20:00:01-21:00:00', '21:00:01-22:00:00', '22:00:01-23:00:00', '23:00:01-24:00:00']

        self.down_trips = []
        self.down_pass = []

        # To obtain average error measure across all dataframes
        for j in xrange(len(timeslot)):
            print 'Timeslot', j + 1, ':'
            pass_data = np.asarray(self.df[j][['Day', 'isHoliday']])
            pass_labels = np.asarray(self.df[j]['Passengers'])
            target = [[self.day, self.isCurrDay_holiday]]  # Example target list to check output format and debugging
            passenger_predictor = LinearRegression(normalize=True)  # Linear regression model to predict passenger frequency
            passenger_predictor.fit(pass_data, pass_labels)
            pass_pred = passenger_predictor.predict(target)
            self.down_pass.append(round(pass_pred))
            target = np.append(round(pass_pred), target)
            print target  # Target features for predicting number of trips
            train_all_features = self.df[j][feature_names][:36].drop(['Trips', 'Time Slot'],axis=1).values  # create training data with trips and time slot dropped
            test_all_features = self.df[j][feature_names][36:].drop(['Trips', 'Time Slot'],axis=1).values  # create testing data with trips and time slot dropped
            train_labels = keras.utils.to_categorical(self.df[j]['Trips'][:36],8)  # create categorical data
            test_labels = keras.utils.to_categorical(self.df[j]['Trips'][36:],8)  # create categorical data
            # model creation
            model = Sequential()
            # input layer
            model.add(Dense(4, activation='relu', input_shape=(3,)))
            # hidden layer
            model.add(Dense(2, activation='relu'))
            # drop 20% nodes
            model.add(Dropout(0.2))
            # output layer
            model.add(Dense(8, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer=RMSprop(), metrics=['accuracy'])

            history = model.fit(train_all_features, train_labels, batch_size=30, epochs=10, verbose=2,validation_data=(test_all_features, test_labels))
            predicted_trips = 0
            target = target.reshape(1, 3)
            predicted_trips += model.predict(target).argmax()
            self.down_trips.append(predicted_trips)
            print('Predicted trips for timeslot: %d is: %d' % (j + 1, predicted_trips))

        for i in range(len(self.down_trips)):
            if self.down_trips[i] == '':
                self.down_trips[i] = 0
        self.down_trips = [0 if x is None else x for x in self.down_trips]

    def close_application(self):
        sys.exit()


def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


run()