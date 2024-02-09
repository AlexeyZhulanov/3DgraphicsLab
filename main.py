import matplotlib.pyplot as plt
import wx
import matplotlib.figure
import mplcursors as mpc
import math
import string
import json
from pathlib import Path
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from mpl_toolkits.mplot3d import Axes3D


class Line2D(wx.App):
    def __init__(self, *args, **kwds):
        wx.App.__init__(self, *args, **kwds)

    def OnInit(self) -> bool:
        wx.InitAllImageHandlers()
        mainWnd = MainWindow(None, -1, '')
        mainWnd.Show()
        self.SetTopWindow(mainWnd)
        return True


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwds) -> None:
        kwds['style'] = wx.DEFAULT_FRAME_STYLE
        super(MainWindow, self).__init__(*args, **kwds)
        self.SetTitle('ComputerGraphicsLab1')
        #Дискрет, с которым будет строиться график(прерывистость)
        self._graphStep = 0.01
        #Размер главного окна
        self.SetSize((880, 550))
        self.SetMinSize((880, 550))
        #Заполнить главное окно элементами управления
        self._createGui()
        #Нарисовать 2D линии
        self._drawGraph()

    def _createGui(self) -> None:
        self.dat = 0.0
        self.ldatx = 0.0
        self.daty = 0.0
        self.ldaty = 0.0
        self.flg = False
        #copy for group
        self.gdat = [0.0] * 20
        self.gldatx = [0.0] * 20
        self.gdaty = [0.0] * 20
        self.gldaty = [0.0] * 20
        self.gflg = [False] * 20

        self.list_points = []
        self.list_lines = []
        self.flag_create = False
        self.flag_edit = False
        self.flag_T = False
        self.flag_R = False
        self.flag_M = False
        self.flag_S = False
        self.flag_mselect = False
        self.line_widths = [1.5] * 100
        self.selected_lines = []
        self.lines = []
        self.colors = ["blue", "red", "green", "orange", "lime", "purple", "teal", "gold", "darkgreen", "darkred",
                  "cyan", "darkblue", "pink", "indigo", "crimson", "olive", "dimgrey", "palegreen", "khaki", "tan"]
        self.flag3d = False
        self.first3d = True
        self.idx1 = 0
        self.idx2 = 1
        self.drop_idx = -1

        #Создание кнопок listbox
        hboxSizer = wx.FlexGridSizer(cols=2)
        self.listbox = wx.ListBox(self)
        hboxSizer.Add(self.listbox, flag=wx.LEFT | wx.TOP | wx.ALL, border=2)
        vboxSizer = wx.BoxSizer(wx.VERTICAL)
        self.newBtn = wx.Button(self, wx.ID_ANY, 'New')
        self.edtBtn = wx.Button(self, wx.ID_ANY, 'Edit')
        self.delBtn = wx.Button(self, wx.ID_ANY, 'Delete')
        self.clrBtn = wx.Button(self, wx.ID_ANY, 'Clear')

        #Привязка кнопок listbox к функциям
        self.Bind(wx.EVT_BUTTON, self.NewItem, id=self.newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.EditItem, id=self.edtBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=self.delBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=self.clrBtn.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.EditItem)

        vboxSizer.Add(self.newBtn, flag=wx.ALL, proportion=1, border=2)
        vboxSizer.Add(self.edtBtn, flag=wx.ALL, proportion=1, border=2)
        vboxSizer.Add(self.delBtn, flag=wx.ALL, proportion=1, border=2)
        vboxSizer.Add(self.clrBtn, flag=wx.ALL, proportion=1, border=2)

        hboxSizer.Add(vboxSizer, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=2)

        self.cursorBtn = wx.Button(self, wx.ID_ANY, 'cursor')
        self.plus_scaleBtn = wx.Button(self, wx.ID_ANY, '+')
        self.minus_scaleBtn = wx.Button(self, wx.ID_ANY, '-')
        self.operation_MultiSelect = wx.Button(self, wx.ID_ANY, '*Group*')
        self.go_2d = wx.Button(self, wx.ID_ANY, 'Mode 2D')
        self.Bind(wx.EVT_BUTTON, self.Enable_Cursor, id=self.cursorBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.Scale_Plus, id=self.plus_scaleBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.Scale_Minus, id=self.minus_scaleBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.oper_mselect, id=self.operation_MultiSelect.GetId())
        self.Bind(wx.EVT_BUTTON, self.goto2d, id=self.go_2d.GetId())
        oboxSizer = wx.FlexGridSizer(cols=2)
        sboxSizer = wx.BoxSizer(wx.VERTICAL)
        sboxSizer.Add(self.cursorBtn, flag=wx.ALL, proportion=1, border=2)
        sboxSizer.Add(self.plus_scaleBtn, flag=wx.ALL, proportion=1, border=2)
        sboxSizer.Add(self.minus_scaleBtn, flag=wx.ALL, proportion=1, border=2)
        sboxSizer.Add(self.operation_MultiSelect, flag=wx.ALL, proportion=1, border=2)
        sboxSizer.Add(self.go_2d, flag=wx.ALL, proportion=1, border=2)
        oboxSizer.Add(sboxSizer, flag=wx.ALL | wx.TOP | wx.LEFT, border=2)

        self.operation_T = wx.Button(self, wx.ID_ANY, 'T')
        self.operation_S = wx.Button(self, wx.ID_ANY, 'S')
        self.operation_R = wx.Button(self, wx.ID_ANY, 'R')
        self.operation_M = wx.Button(self, wx.ID_ANY, 'M')
        self.go_3d = wx.Button(self, wx.ID_ANY, 'Mode 3D')
        self.Bind(wx.EVT_BUTTON, self.oper_T, id=self.operation_T.GetId())
        self.Bind(wx.EVT_BUTTON, self.oper_S, id=self.operation_S.GetId())
        self.Bind(wx.EVT_BUTTON, self.oper_R, id=self.operation_R.GetId())
        self.Bind(wx.EVT_BUTTON, self.oper_M, id=self.operation_M.GetId())
        self.Bind(wx.EVT_BUTTON, self.goto3d, id=self.go_3d.GetId())
        self.rb1 = wx.RadioButton(self, label='XY', style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, label='XZ')
        self.rb3 = wx.RadioButton(self, label='YZ')
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButtons)
        opSizer = wx.BoxSizer(wx.VERTICAL)
        opSizer.Add(self.operation_T, flag=wx.ALL, proportion=1, border=2)
        opSizer.Add(self.operation_S, flag=wx.ALL, proportion=1, border=2)
        opSizer.Add(self.operation_R, flag=wx.ALL, proportion=1, border=2)
        opSizer.Add(self.operation_M, flag=wx.ALL, proportion=1, border=2)
        opSizer.Add(self.go_3d, flag=wx.ALL, proportion=1, border=2)
        oboxSizer.Add(opSizer, flag=wx.ALL | wx.TOP | wx.LEFT, border=2)
        hboxSizer.Add(oboxSizer, flag=wx.ALL | wx.LEFT, border=2)
        rSizer = wx.BoxSizer(wx.VERTICAL)
        rSizer.Add(self.rb1, flag=wx.UP, proportion=1, border=25)
        rSizer.Add(self.rb2, flag=wx.UP, proportion=1, border=15)
        rSizer.Add(self.rb3, flag=wx.UP, proportion=1, border=5)
        hboxSizer.Add(rSizer, flag=wx.ALL | wx.LEFT, border=2)
        self.listbox2 = wx.ListBox(self)
        self.listbox2.SetMinSize((200, 150))
        hboxSizer.Add(self.listbox2, flag=wx.LEFT | wx.BOTTOM | wx.ALL, border=2)
        self.saveJs = wx.Button(self, wx.ID_ANY, 'Save')
        self.loadJs = wx.Button(self, wx.ID_ANY, 'Load')
        self.delJs = wx.Button(self, wx.ID_ANY, 'Delete')

        # Привязка кнопок listbox к функциям
        self.Bind(wx.EVT_BUTTON, self.saveJson, id=self.saveJs.GetId())
        self.Bind(wx.EVT_BUTTON, self.loadJson, id=self.loadJs.GetId())
        self.Bind(wx.EVT_BUTTON, self.delJson, id=self.delJs.GetId())
        jsSizer = wx.BoxSizer(wx.VERTICAL)
        jsSizer.Add(self.saveJs, flag=wx.ALL, proportion=1, border=2)
        jsSizer.Add(self.loadJs, flag=wx.ALL, proportion=1, border=2)
        jsSizer.Add(self.delJs, flag=wx.ALL, proportion=1, border=2)
        hboxSizer.Add(jsSizer, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=2)
        self.lim_list = [[-1., 1.], [-10., 10.], [-25., 25.], [-50., 50.], [-100., 100.], [-250., 250.], [-500., 500.],
                         [-1000., 1000.]]
        self.temp_ind_list = 4

        self.go_2d.SetForegroundColour("red")

        # Создание фигуры
        self.figure = matplotlib.figure.Figure()
        self.figure, self.axes = plt.subplots()

        #Создание панели для рисования с помощью Matplotlib
        self.canvas = FigureCanvasWxAgg(self, wx.ID_ANY, self.figure)
        self.canvas.SetMinSize((400, 400))
        self.listbox.SetMinSize((200, 200))

        #Размещение элементов управления в окне
        mainSizer = wx.FlexGridSizer(cols=2)
        mainSizer.Add(hboxSizer, flag=wx.ALL | wx.EXPAND, border=2)
        mainSizer.Add(self.canvas, flag=wx.ALL | wx.EXPAND, border=2)
        mainSizer.AddGrowableRow(0)
        mainSizer.AddGrowableCol(1)
        self.SetSizer(mainSizer)
        self.Layout()

    def _drawGraph(self) -> None:
        # Удаление предыдущих прямых, если они есть
        self.axes.clear()
        mpc.cursor().remove()
        self.listbox.Clear()
        self.lines.clear()
        color_ind = 0
        w_index = 0
        list_ind = 0
        # Корректировка линий(если точки очень близко друг к другу, то они сливаются в одну, образуя цельную фигуру)
        self.list_points, self.list_lines = correct_points(self.list_points, self.list_lines, self.lim_list[self.temp_ind_list][1], self.idx1, self.idx2)
        # Отрисовка всех прямых
        for lin in self.list_lines:
            if color_ind == len(self.colors):
                color_ind = 0
            lbl = calculate_line(self.list_points[list_ind][self.idx1], self.list_points[list_ind][self.idx2],
                                 self.list_points[list_ind + 1][self.idx1], self.list_points[list_ind + 1][self.idx2],
                                 self.lim_list[self.temp_ind_list][1], self.idx1, self.idx2)
            lbl = str(color_ind + 1) + ". " + lbl
            self.line, = self.axes.plot(lin[self.idx1], lin[self.idx2], 'X', linestyle="-", linewidth=self.line_widths[w_index],
                                        color=self.colors[color_ind], label=lbl, picker=True, pickradius=5)
            self.lines.append(self.line)
            self.axes.legend(*[*zip(*{l: h for h, l in zip(*self.axes.get_legend_handles_labels())}.items())][::-1], loc=0)
            color_ind += 1
            w_index += 1
            list_ind += 2
            self.listbox.Append(lbl)

        # Установка пределов по осям
        self.axes.set_xlim(self.lim_list[self.temp_ind_list])
        self.axes.set_ylim(self.lim_list[self.temp_ind_list])
        if self.idx1 == 0:
            self.axes.set_xlabel('x')
        elif self.idx1 == 1:
            self.axes.set_xlabel('y')
        else:
            self.axes.set_xlabel('z')
        if self.idx2 == 0:
            self.axes.set_ylabel('x')
        elif self.idx2 == 1:
            self.axes.set_ylabel('y')
        else:
            self.axes.set_ylabel('z')
        # Включение сетки
        self.axes.grid(visible=True, animated=True)
        # Обновление окна
        self.canvas.draw()
        self.fill_listbox()
        if self.flag3d:
            self.draw3DGraph()

    # тот же drawgraph, только в 3D
    def draw3DGraph(self) -> None:
        # Удаление предыдущих прямых, если они есть
        self.ax.clear()
        color_ind = 0
        w_index = 0
        # Отрисовка всех прямых
        list_ind = 0
        for lin in self.list_lines:
            if color_ind == len(self.colors):
                color_ind = 0
            self.li, = self.ax.plot(lin[0], lin[1], lin[2], 'X', linestyle="-", linewidth=self.line_widths[w_index],
                                        color=self.colors[color_ind], picker=True, pickradius=5)
            color_ind += 1
            w_index += 1
            list_ind += 2
        self.ax.set_xlim(self.lim_list[self.temp_ind_list])
        self.ax.set_ylim(self.lim_list[self.temp_ind_list])
        self.ax.set_zlim(self.lim_list[self.temp_ind_list])
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        # Включение сетки
        self.ax.grid(visible=True, animated=True)
        self.ax.set_proj_type('persp', focal_length=0.2)
        plt.show()

    def drawpoint(self, event) -> None:
        if event.xdata is not None and event.ydata is not None:
            x = event.xdata
            y = event.ydata
            if self.idx1 == 0 and self.idx2 == 1:
                self.list_points.append([x, y, 0])
            elif self.idx1 == 0 and self.idx2 == 2:
                self.list_points.append([x, 0, y])
            else:
                self.list_points.append([0, x, y])
            if len(self.list_points) > 0 and len(self.list_points) % 2 == 0:
                self.figure.canvas.mpl_disconnect(self.follower2)
                point1 = self.list_points[len(self.list_points)-2]
                point2 = self.list_points[len(self.list_points)-1]
                x_values = [point1[self.idx1], point2[self.idx1]]
                y_values = [point1[self.idx2], point2[self.idx2]]
                z_values = [0, 0]
                if self.idx1 == 0 and self.idx2 == 1:
                    self.list_lines.append([x_values, y_values, z_values])
                elif self.idx1 == 0 and self.idx2 == 2:
                    self.list_lines.append([x_values, z_values, y_values])
                else:
                    self.list_lines.append([z_values, x_values, y_values])
                self._drawGraph()
            else:
                self.follow_flag = False
                self.follower2 = self.figure.canvas.mpl_connect("motion_notify_event", self.followmouse2)

    def followmouse2(self, event) -> None:
        point1 = self.list_points[len(self.list_points) - 1]
        x = event.xdata
        y = event.ydata
        point2 = x, y
        x_values = [point1[self.idx1], point2[0]]
        y_values = [point1[self.idx2], point2[1]]
        if not self.follow_flag:
            self.line, = self.axes.plot(x_values, y_values, 'X', linestyle="--")
            self.follow_flag = True
        else:
            self.line.set_xdata(x_values)
            self.line.set_ydata(y_values)
        self.canvas.draw_idle()

    # Выполнение действий при движении мышки после drag
    def followmouse(self, event) -> None:
        if len(self.selected_lines) <= 1:
            if not self.flg:
                self.drop_idx = self.listbox.GetSelection()
                self.dat = event.xdata
                self.ldatx = self.line.get_xdata()
                self.daty = event.ydata
                self.ldaty = self.line.get_ydata()
                self.flg = True
            if isinstance(event.xdata, float) and isinstance(event.ydata, float):
                self.line.set_xdata(self.ldatx + (event.xdata - self.dat))
                self.line.set_ydata(self.ldaty + (event.ydata - self.daty))
                self.canvas.draw_idle()
        else:
            for i in self.selected_lines:
                if not self.gflg[i]:
                    self.gdat[i] = event.xdata
                    self.gldatx[i] = self.lines[i].get_xdata()
                    self.gdaty[i] = event.ydata
                    self.gldaty[i] = self.lines[i].get_ydata()
                    self.gflg[i] = True
                if isinstance(event.xdata, float) and isinstance(event.ydata, float):
                    self.lines[i].set_xdata(self.gldatx[i] + (event.xdata - self.gdat[i]))
                    self.lines[i].set_ydata(self.gldaty[i] + (event.ydata - self.gdaty[i]))
                    self.canvas.draw_idle()

    # функция drop
    def releaseonclick(self, event) -> None:
        self.figure.canvas.mpl_disconnect(self.releaser)
        self.figure.canvas.mpl_disconnect(self.follower)
        if len(self.selected_lines) <= 1:
            st_idx = self.drop_idx
            p_idx = st_idx * 2
            if self.idx1 == 0 and self.idx2 == 1:
                self.list_lines[st_idx] = [list(self.line.get_xdata()), list(self.line.get_ydata()), self.list_lines[st_idx][2]]
                self.list_points[p_idx] = [self.list_lines[st_idx][self.idx1][0], self.list_lines[st_idx][self.idx2][0], self.list_points[p_idx][2]]
                self.list_points[p_idx + 1] = [self.list_lines[st_idx][self.idx1][1], self.list_lines[st_idx][self.idx2][1], self.list_points[p_idx+1][2]]
            elif self.idx1 == 0 and self.idx2 == 2:
                self.list_lines[st_idx] = [list(self.line.get_xdata()), self.list_lines[st_idx][1], list(self.line.get_ydata())]
                self.list_points[p_idx] = [self.list_lines[st_idx][self.idx1][0], self.list_points[p_idx][1], self.list_lines[st_idx][self.idx2][0]]
                self.list_points[p_idx + 1] = [self.list_lines[st_idx][self.idx1][1], self.list_points[p_idx + 1][1], self.list_lines[st_idx][self.idx2][1]]
            else:
                self.list_lines[st_idx] = [self.list_lines[st_idx][0], list(self.line.get_xdata()), list(self.line.get_ydata())]
                self.list_points[p_idx] = [self.list_points[p_idx][0], self.list_lines[st_idx][self.idx1][0], self.list_lines[st_idx][self.idx2][0]]
                self.list_points[p_idx + 1] = [self.list_points[p_idx + 1][0], self.list_lines[st_idx][self.idx1][1], self.list_lines[st_idx][self.idx2][1]]
            self.flg = False
            self.dat = 0.0
            self.ldatx = 0.0
            self.daty = 0.0
            self.ldaty = 0.0
        else:
            for i in self.selected_lines:
                st = self.lines[i].get_label()
                st_idx = self.listbox.FindString(st)
                p_idx = st_idx * 2
                if self.idx1 == 0 and self.idx2 == 1:
                    self.list_lines[st_idx] = [list(self.lines[i].get_xdata()), list(self.lines[i].get_ydata()), self.list_lines[st_idx][2]]
                    self.list_points[p_idx] = [self.list_lines[st_idx][self.idx1][0], self.list_lines[st_idx][self.idx2][0], self.list_points[p_idx][2]]
                    self.list_points[p_idx + 1] = [self.list_lines[st_idx][self.idx1][1], self.list_lines[st_idx][self.idx2][1], self.list_points[p_idx + 1][2]]
                elif self.idx1 == 0 and self.idx2 == 2:
                    self.list_lines[st_idx] = [list(self.lines[i].get_xdata()), self.list_lines[st_idx][1], list(self.lines[i].get_ydata())]
                    self.list_points[p_idx] = [self.list_lines[st_idx][self.idx1][0], self.list_points[p_idx][1], self.list_lines[st_idx][self.idx2][0]]
                    self.list_points[p_idx + 1] = [self.list_lines[st_idx][self.idx1][1], self.list_points[p_idx + 1][1], self.list_lines[st_idx][self.idx2][1]]
                else:
                    self.list_lines[st_idx] = [self.list_lines[st_idx][0], list(self.lines[i].get_xdata()), list(self.lines[i].get_ydata())]
                    self.list_points[p_idx] = [self.list_points[p_idx][0], self.list_lines[st_idx][self.idx1][0], self.list_lines[st_idx][self.idx2][0]]
                    self.list_points[p_idx + 1] = [self.list_points[p_idx + 1][0], self.list_lines[st_idx][self.idx1][1], self.list_lines[st_idx][self.idx2][1]]
                self.gflg = [False] * 20
                self.gdat = [0.0] * 20
                self.gldatx = [0.0] * 20
                self.gdaty = [0.0] * 20
                self.gldaty = [0.0] * 20
        self.canvas.draw_idle()
        if self.flag3d:
            self.draw3DGraph()

    def pressbutton(self, event):
        if event.key == 'left':
            if len(self.selected_lines) <= 1:
                sel = self.listbox.GetSelection()
                if sel != -1:
                    if self.line_widths[sel] > 0:
                        self.line_widths[sel] -= 0.5
                        self.line.set_linewidth(self.line_widths[sel])
            else:
                for i in self.selected_lines:
                    if self.line_widths[i] > 0:
                        self.line_widths[i] -= 0.5
                        self.lines[i].set_linewidth(self.line_widths[i])

            self.canvas.draw_idle()
        if event.key == 'right':
            if len(self.selected_lines) <= 1:
                sel = self.listbox.GetSelection()
                if sel != -1:
                    self.line_widths[sel] += 0.5
                    self.line.set_linewidth(self.line_widths[sel])
            else:
                for i in self.selected_lines:
                    self.line_widths[i] += 0.5
                    self.lines[i].set_linewidth(self.line_widths[i])
            self.canvas.draw_idle()
        if event.key == 'up' or event.key == 'down':
            if len(self.selected_lines) <= 1:
                sel = self.listbox.GetSelection()
                if sel != -1:
                    if event.key == 'up':
                        ls = calculate_next_points(self.list_points[sel*2][self.idx1], self.list_points[sel*2][self.idx2], self.list_points[sel*2+1][self.idx1], self.list_points[sel*2+1][self.idx2], True, self.idx1, self.idx2)
                    else:
                        ls = calculate_next_points(self.list_points[sel*2][self.idx1], self.list_points[sel*2][self.idx2], self.list_points[sel*2+1][self.idx1], self.list_points[sel*2+1][self.idx2], False, self.idx1, self.idx2)
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[sel*2] = ls[0], ls[1], self.list_points[sel*2][2]
                        self.list_points[sel*2+1] = ls[2], ls[3], self.list_points[sel*2+1][2]
                        self.list_lines[sel] = [ls[0], ls[2]], [ls[1], ls[3]], self.list_lines[sel][2]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[sel * 2] = ls[0], self.list_points[sel*2][1], ls[1]
                        self.list_points[sel * 2 + 1] = ls[2], self.list_points[sel*2+1][1], ls[3]
                        self.list_lines[sel] = [ls[0], ls[2]], self.list_lines[sel][1], [ls[1], ls[3]]
                    else:
                        self.list_points[sel * 2] = self.list_points[sel*2][0], ls[0], ls[1]
                        self.list_points[sel * 2 + 1] = self.list_points[sel*2+1][0], ls[2], ls[3]
                        self.list_lines[sel] = self.list_lines[sel][0], [ls[0], ls[2]], [ls[1], ls[3]]
                    self.line.set_xdata(self.list_lines[sel][self.idx1])
                    self.line.set_ydata(self.list_lines[sel][self.idx2])
            else:
                for i in self.selected_lines:
                    if event.key == 'up':
                        ls = calculate_next_points(self.list_points[i*2][self.idx1], self.list_points[i*2][self.idx2], self.list_points[i*2+1][self.idx1], self.list_points[i*2+1][self.idx2], True, self.idx1, self.idx2)
                    else:
                        ls = calculate_next_points(self.list_points[i*2][self.idx1], self.list_points[i*2][self.idx2], self.list_points[i*2+1][self.idx1], self.list_points[i*2+1][self.idx2], False, self.idx1, self.idx2)
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[i * 2] = ls[0], ls[1], self.list_points[i*2][2]
                        self.list_points[i * 2 + 1] = ls[2], ls[3], self.list_points[i*2+1][2]
                        self.list_lines[i] = [ls[0], ls[2]], [ls[1], ls[3]], self.list_lines[i][2]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[i * 2] = ls[0], self.list_points[i*2][1], ls[1]
                        self.list_points[i * 2 + 1] = ls[2], self.list_points[i*2+1][1], ls[3]
                        self.list_lines[i] = [ls[0], ls[2]], self.list_lines[i][1], [ls[1], ls[3]]
                    else:
                        self.list_points[i * 2] = self.list_points[i*2][0], ls[0], ls[1]
                        self.list_points[i * 2 + 1] = self.list_points[i*2+1][0], ls[2], ls[3]
                        self.list_lines[i] = self.list_lines[i][0], [ls[0], ls[2]], [ls[1], ls[3]]
                    self.lines[i].set_xdata(self.list_lines[i][self.idx1])
                    self.lines[i].set_ydata(self.list_lines[i][self.idx2])
            self.canvas.draw_idle()

    def rpressbutton(self, event):
        if event.key == 'q' or event.key == 'e':
            if len(self.selected_lines) <= 1:
                sel = self.listbox.GetSelection()
                if sel != -1:
                    if event.key == 'q':
                        theta = math.radians(15)
                    else:
                        theta = math.radians(-15)
                    ox, px = self.list_lines[sel][self.idx1]
                    oy, py = self.list_lines[sel][self.idx2]
                    p_prime = [round(px*math.cos(theta)-py*math.sin(theta), 2), round(px*math.sin(theta)+py*math.cos(theta), 2)]
                    p_oprime = [round(ox*math.cos(theta)-oy*math.sin(theta), 2), round(ox*math.sin(theta)+oy*math.cos(theta), 2)]
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[sel*2+1] = p_prime[0], p_prime[1], self.list_points[sel*2+1][2]
                        self.list_points[sel * 2] = p_oprime[0], p_oprime[1], self.list_points[sel*2][2]
                        self.list_lines[sel] = [p_oprime[0], p_prime[0]], [p_oprime[1], p_prime[1]], self.list_lines[sel][2]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[sel * 2 + 1] = p_prime[0], self.list_points[sel * 2 + 1][1], p_prime[1]
                        self.list_points[sel * 2] = p_oprime[0], self.list_points[sel * 2][1], p_oprime[1]
                        self.list_lines[sel] = [p_oprime[0], p_prime[0]], self.list_lines[sel][1], [p_oprime[1], p_prime[1]]
                    else:
                        self.list_points[sel * 2 + 1] = self.list_points[sel * 2 + 1][0], p_prime[0], p_prime[1]
                        self.list_points[sel * 2] = self.list_points[sel * 2][0], p_oprime[0], p_oprime[1]
                        self.list_lines[sel] = self.list_lines[sel][0], [p_oprime[0], p_prime[0]], [p_oprime[1], p_prime[1]]
                    self.line.set_xdata(self.list_lines[sel][self.idx1])
                    self.line.set_ydata(self.list_lines[sel][self.idx2])
            else:
                for i in self.selected_lines:
                    if event.key == 'q':
                        theta = math.radians(15)
                    else:
                        theta = math.radians(-15)
                    ox, px = self.list_lines[i][self.idx1]
                    oy, py = self.list_lines[i][self.idx2]
                    p_prime = [round(px*math.cos(theta)-py*math.sin(theta), 2), round(px*math.sin(theta)+py*math.cos(theta), 2)]
                    p_oprime = [round(ox*math.cos(theta)-oy*math.sin(theta), 2), round(ox*math.sin(theta)+oy*math.cos(theta), 2)]
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[i*2+1] = p_prime[0], p_prime[1], self.list_points[i*2+1][2]
                        self.list_points[i * 2] = p_oprime[0], p_oprime[1], self.list_points[i*2][2]
                        self.list_lines[i] = [p_oprime[0], p_prime[0]], [p_oprime[1], p_prime[1]], self.list_lines[i][2]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[i * 2 + 1] = p_prime[0], self.list_points[i * 2 + 1][1], p_prime[1]
                        self.list_points[i * 2] = p_oprime[0], self.list_points[i * 2][1], p_oprime[1]
                        self.list_lines[i] = [p_oprime[0], p_prime[0]], self.list_lines[i][1], [p_oprime[1], p_prime[1]]
                    else:
                        self.list_points[i * 2 + 1] = self.list_points[i * 2 + 1][0], p_prime[0], p_prime[1]
                        self.list_points[i * 2] = self.list_points[i * 2][0], p_oprime[0], p_oprime[1]
                        self.list_lines[i] = self.list_lines[i][0], [p_oprime[0], p_prime[0]], [p_oprime[1], p_prime[1]]
                    self.lines[i].set_xdata(self.list_lines[i][self.idx1])
                    self.lines[i].set_ydata(self.list_lines[i][self.idx2])
            self.canvas.draw_idle()

    def mpressbutton(self, event):
        if event.key == '1' or event.key == '2' or event.key == '3':
            if len(self.selected_lines) <= 1:
                sel = self.listbox.GetSelection()
                if sel != -1:
                    x1, x2 = self.list_lines[sel][self.idx1]
                    y1, y2 = self.list_lines[sel][self.idx2]
                    #Зеркалирование по X
                    if event.key == '1':
                        y1 *= -1
                        y2 *= -1
                    #Зеркалирование по Y
                    elif event.key == '2':
                        x1 *= -1
                        x2 *= -1
                    #Зеркалирование по XY
                    else:
                        x1 *= -1
                        y1 *= -1
                        x2 *= -1
                        y2 *= -1
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[sel * 2 + 1] = x2, y2, self.list_points[sel*2+1][2]
                        self.list_points[sel * 2] = x1, y1, self.list_points[sel*2][2]
                        self.list_lines[sel] = [[x1, x2], [y1, y2], self.list_lines[sel][2]]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[sel * 2 + 1] = x2, self.list_points[sel * 2 + 1][1], y2
                        self.list_points[sel * 2] = x1, self.list_points[sel * 2][1], y1
                        self.list_lines[sel] = [[x1, x2], self.list_lines[sel][1], [y1, y2]]
                    else:
                        self.list_points[sel * 2 + 1] = self.list_points[sel * 2 + 1][0], x2, y2
                        self.list_points[sel * 2] = self.list_points[sel * 2][0], x1, y1
                        self.list_lines[sel] = [self.list_lines[sel][0], [x1, x2], [y1, y2]]
                    self.line.set_xdata(self.list_lines[sel][self.idx1])
                    self.line.set_ydata(self.list_lines[sel][self.idx2])
            else:
                for i in self.selected_lines:
                    x1, x2 = self.list_lines[i][self.idx1]
                    y1, y2 = self.list_lines[i][self.idx2]
                    # Зеркалирование по X
                    if event.key == '1':
                        y1 *= -1
                        y2 *= -1
                    # Зеркалирование по Y
                    elif event.key == '2':
                        x1 *= -1
                        x2 *= -1
                    # Зеркалирование по XY
                    else:
                        x1 *= -1
                        y1 *= -1
                        x2 *= -1
                        y2 *= -1
                    if self.idx1 == 0 and self.idx2 == 1:
                        self.list_points[i * 2 + 1] = x2, y2, self.list_points[i * 2 + 1][2]
                        self.list_points[i * 2] = x1, y1, self.list_points[i * 2][2]
                        self.list_lines[i] = [[x1, x2], [y1, y2], self.list_lines[i][2]]
                    elif self.idx1 == 0 and self.idx2 == 2:
                        self.list_points[i * 2 + 1] = x2, self.list_points[i * 2 + 1][1], y2
                        self.list_points[i * 2] = x1, self.list_points[i * 2][1], y1
                        self.list_lines[i] = [[x1, x2], self.list_lines[i][1], [y1, y2]]
                    else:
                        self.list_points[i * 2 + 1] = self.list_points[i * 2 + 1][0], x2, y2
                        self.list_points[i * 2] = self.list_points[i * 2][0], x1, y1
                        self.list_lines[i] = [self.list_lines[i][0], [x1, x2], [y1, y2]]
                    self.lines[i].set_xdata(self.list_lines[i][self.idx1])
                    self.lines[i].set_ydata(self.list_lines[i][self.idx2])
            self.canvas.draw_idle()

    def followmouse3(self, event) -> None:
        counter = 0
        if event.inaxes == self.axes:
            for line in self.lines:
                cont, d = line.contains(event)
                if cont:
                    line.set_color('black')
                    self.selected_lines.append(counter)
                    self.canvas.draw_idle()
                counter += 1
        elif len(self.selected_lines) > 0:
            self.figure.canvas.mpl_disconnect(self.follower3)
            self.selected_lines = list(set(self.selected_lines))
            print("selected lines indexes: " + str(self.selected_lines))

    # Функция drag
    def on_pick(self, event) -> None:
        self.line = event.artist
        st = self.line.get_label()
        st_idx = self.listbox.FindString(st)
        self.listbox.SetSelection(st_idx)
        if self.flag_T:
            self.follower = self.figure.canvas.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser = self.figure.canvas.mpl_connect("button_press_event", self.releaseonclick)
        if self.flag_S:
            self.presser = self.figure.canvas.mpl_connect("key_press_event", self.pressbutton)
        if self.flag_R:
            self.rpresser = self.figure.canvas.mpl_connect("key_press_event", self.rpressbutton)
        if self.flag_M:
            self.mpresser = self.figure.canvas.mpl_connect("key_press_event", self.mpressbutton)

    def NewItem(self, event) -> None:
        if not self.flag_create:
            self.ni = self.figure.canvas.mpl_connect("button_press_event", self.drawpoint)
            self.flag_create = True
            self.newBtn.SetBackgroundColour("orange")
            if self.flag_edit:
                self.edtBtn.SetBackgroundColour(None)
                self.flag_edit = False
                self.figure.canvas.mpl_disconnect(self.ei)
                self.flag_T = False
                self.flag_M = False
                self.flag_R = False
                self.flag_S = False
                self.flag_mselect = False
                self.operation_T.SetForegroundColour(None)
                self.operation_S.SetForegroundColour(None)
                self.operation_R.SetForegroundColour(None)
                self.operation_M.SetForegroundColour(None)
                self.operation_MultiSelect.SetBackgroundColour(None)
                self.selected_lines.clear()
                self._drawGraph()
        else:
            self.figure.canvas.mpl_disconnect(self.ni)
            self.flag_create = False
            if self.flag_S:
                self.figure.canvas.mpl_disconnect(self.presser)
            self.newBtn.SetBackgroundColour(None)

    def EditItem(self, event) -> None:
        if not self.flag_edit:
            self.ei = self.figure.canvas.mpl_connect('pick_event', self.on_pick)
            self.flag_edit = True
            self.edtBtn.SetBackgroundColour("orange")
            if self.flag_create:
                self.newBtn.SetBackgroundColour(None)
                self.flag_create = False
                self.figure.canvas.mpl_disconnect(self.ni)
        else:
            self.figure.canvas.mpl_disconnect(self.ei)
            self.flag_edit = False
            self.edtBtn.SetBackgroundColour(None)
            self.flag_T = False
            self.flag_M = False
            self.flag_R = False
            self.flag_S = False
            self.operation_T.SetForegroundColour(None)
            self.operation_S.SetForegroundColour(None)
            self.operation_R.SetForegroundColour(None)
            self.operation_M.SetForegroundColour(None)
            self.selected_lines.clear()
            self.figure.canvas.mpl_disconnect(self.presser)
            self.figure.canvas.mpl_disconnect(self.rpresser)
            self.figure.canvas.mpl_disconnect(self.mpresser)

    def OnDelete(self, event) -> None:
        sel = self.listbox.GetSelection()
        if sel != -1:
            self.listbox.Delete(sel)
            self.list_lines.pop(sel)
            self.list_points.pop(sel*2+1)
            self.list_points.pop(sel*2)
            tmp = self.colors[sel]
            self.colors.pop(sel)
            self.colors.append(tmp)
            self._drawGraph()

    def OnClear(self, event) -> None:
        self.listbox.Clear()
        self.list_points.clear()
        self.list_lines.clear()
        self._drawGraph()

    def Scale_Plus(self, event) -> None:
        if self.temp_ind_list < 7:
            self.temp_ind_list += 1
            sel = self.listbox.GetSelection()
            self._drawGraph()
            self.listbox.SetSelection(sel)

    def Scale_Minus(self, event) -> None:
        if self.temp_ind_list > 0:
            self.temp_ind_list -= 1
            sel = self.listbox.GetSelection()
            self._drawGraph()
            self.listbox.SetSelection(sel)

    def Enable_Cursor(self, event) -> None:
        mpc.cursor(hover=False)

    def oper_T(self, event) -> None:
        if self.flag_edit:
            if not self.flag_T:
                self.flag_T = True
                self.operation_T.SetForegroundColour('red')
            else:
                self.flag_T = False
                self.operation_T.SetForegroundColour(None)

    def oper_S(self, event) -> None:
        if self.flag_edit:
            if not self.flag_S:
                self.flag_S = True
                self.operation_S.SetForegroundColour('red')
            else:
                self.flag_S = False
                self.operation_S.SetForegroundColour(None)
                self.figure.canvas.mpl_disconnect(self.presser)

    def oper_R(self, event) -> None:
        if self.flag_edit:
            if not self.flag_R:
                self.flag_R = True
                self.operation_R.SetForegroundColour('red')
            else:
                self.flag_R = False
                self.operation_R.SetForegroundColour(None)
                self.figure.canvas.mpl_disconnect(self.rpresser)

    def oper_M(self, event) -> None:
        if self.flag_edit:
            if not self.flag_M:
                self.flag_M = True
                self.operation_M.SetForegroundColour('red')
            else:
                self.flag_M = False
                self.operation_M.SetForegroundColour(None)
                self.figure.canvas.mpl_disconnect(self.mpresser)

    def oper_mselect(self, event) -> None:
        if self.flag_edit:
            if not self.flag_mselect:
                self.flag_mselect = True
                self.operation_MultiSelect.SetBackgroundColour('red')
                self.selected_lines.clear()
                self.follower3 = self.figure.canvas.mpl_connect("motion_notify_event", self.followmouse3)
            else:
                self.flag_mselect = False
                self.operation_MultiSelect.SetBackgroundColour(None)
                self.figure.canvas.mpl_disconnect(self.follower3)
                self.selected_lines.clear()
                self._drawGraph()

    def goto2d(self, event) -> None:
        if self.flag3d:
            self.flag3d = False
            self.go_3d.SetForegroundColour(None)
            self.go_2d.SetForegroundColour('red')
            matplotlib.pyplot.close(2)
            self._drawGraph()

    def goto3d(self, event) -> None:
        if not self.flag3d:
            self.flag3d = True
            self.go_3d.SetForegroundColour('red')
            self.go_2d.SetForegroundColour(None)
            self.ax = plt.figure().add_subplot(projection=Axes3D.name)
            # Установка пределов по осям
            self.ax.set_xlim(self.lim_list[self.temp_ind_list])
            self.ax.set_ylim(self.lim_list[self.temp_ind_list])
            self.ax.set_zlim(self.lim_list[self.temp_ind_list])
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_zlabel('z')
            if self.first3d:
                matplotlib.pyplot.close(1)
                self.first3d = False
            plt.show()
            self.draw3DGraph()

    def onRadioButtons(self, e):
        rb = e.GetEventObject()
        if rb.GetLabel() == 'XY':
            self.idx1 = 0
            self.idx2 = 1
        elif rb.GetLabel() == 'XZ':
            self.idx1 = 0
            self.idx2 = 2
        elif rb.GetLabel() == 'YZ':
            self.idx1 = 1
            self.idx2 = 2
        self._drawGraph()

    def fill_listbox(self):
        path = Path('D:/data.json')
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            mas = []
            for p in data:
                mas.append(p)
            self.listbox2.Clear()
            [self.listbox2.Append(i) for i in mas]
        except json.JSONDecodeError:
            data = {}
            path.write_text(json.dumps(data), encoding='utf-8')

    def saveJson(self, event) -> None:
        filters = string.ascii_uppercase + string.ascii_lowercase + '0123456789'
        inAlf = True
        name = wx.GetTextFromUser('Введите название сохранения', 'Insert dialog')
        if name != '':
            for w in name:
                if w not in filters:
                    inAlf = False
            if inAlf:
                path = Path('D:/data.json')
                try:
                    data = json.loads(path.read_text(encoding='utf-8'))
                    data[name] = [{
                        'points': self.list_points,
                        'lines': self.list_lines
                    }]
                    path.write_text(json.dumps(data), encoding='utf-8')
                    self.fill_listbox()
                except json.JSONDecodeError:
                    data = {}
                    path.write_text(json.dumps(data), encoding='utf-8')

    def loadJson(self, event) -> None:
        sel = self.listbox2.GetSelection()
        if sel != -1:
            path = Path('D:/data.json')
            data = json.loads(path.read_text(encoding='utf-8'))
            mas = []
            for p in data:
                mas.append(p)
            for p in data[mas[sel]]:
                self.list_points = p['points']
                self.list_lines = p['lines']
            self._drawGraph()

    def delJson(self, event) -> None:
        sel = self.listbox2.GetSelection()
        if sel != -1:
            path = Path('D:/data.json')
            data = json.loads(path.read_text(encoding='utf-8'))
            mas = []
            for p in data:
                mas.append(p)
            data.pop(mas[sel])
            path.write_text(json.dumps(data), encoding='utf-8')
            self.fill_listbox()


if __name__ == '__main__':
    # Вычисление уравнения прямой по двум точкам
    def calculate_line(xd1, yd1, xd2, yd2, lim, type1, type2) -> str:
        if type1 == 0 and type2 == 1:
            arg1 = "x"
            arg2 = "y"
        elif type1 == 0 and type2 == 2:
            arg1 = "x"
            arg2 = "z"
        else:
            arg1 = "y"
            arg2 = "z"
        rd = 1
        if lim <= 10:
            rd = 2
        r1 = xd2 - xd1
        if abs(r1) < lim/100:
            r1 = round(xd1, rd)
            res = str(arg1) + "=" + str(r1)
            return res
        r2 = yd2 - yd1
        if abs(r2) < lim/100:
            r2 = round(yd1, rd)
            res = str(arg2) + "=" + str(r2)
            return res
        r3 = -1 * yd1 * r1
        r4 = -1 * xd1 * r2 - r3
        if r1 != 0:
            xx = round(r2 / r1, rd)
            numb = round(r4 / r1, rd)
        else:
            xx = round(r2, rd)
            numb = round(r4, rd)
        if xx.is_integer():
            xx = int(xx)
        if numb.is_integer():
            numb = int(numb)
        if xx != 0:
            if numb >= 0:
                res = str(arg2) + "=" + str(xx) + str(arg1) + "+" + str(numb)
            else:
                res = str(arg2) + "=" + str(xx) + str(arg1) + str(numb)
        else:
            res = str(arg2) + "=" + str(numb)
        return res

    def calculate_next_points(x1, y1, x2, y2, is_plus, type1, type2) -> list[int]:
        ur = calculate_line(x1, y1, x2, y2, 1, type1, type2)
        if type1 == 0 and type2 == 1:
            arg1 = "x"
            arg2 = "y"
        elif type1 == 0 and type2 == 2:
            arg1 = "x"
            arg2 = "z"
        else:
            arg1 = "y"
            arg2 = "z"
        if arg1 + '=' in ur:
            a = 0
            b = float(ur[2:])
        elif arg2 + '=' in ur and arg1 not in ur:
            a = 0
            b = float(ur[2:])
        else:
            s = ur.find(arg1)
            a = float(ur[2:s])
            if '+' in ur:
                b = float(ur[s+2:])
            else:
                b = float(ur[s+1:])
        if arg2 + '=' in ur:
            step = abs((x2-x1) / 50)
            if x2 < x1:
                step = step * -1
            if not is_plus:
                step = step * -1
            ry1 = a*(x1-step) + b
            rx1 = x1-step
            ry2 = a*(x2+step) + b
            rx2 = x2+step
        else:
            step = abs((y2-y1) / 50)
            if y2 < y1:
                step = step * -1
            if not is_plus:
                step = step * -1
            rx1 = x1
            rx2 = x2
            ry1 = y1-step
            ry2 = y2+step
        ls: list[int] = [rx1, ry1, rx2, ry2]
        return ls


    def correct_points(lst, lns, lim, type1, type2):
        flag = False
        lm = lim / 20
        if type1 == 0 and type2 == 1:
            type3 = 2
        elif type1 == 0 and type2 == 2:
            type3 = 1
        else:
            type3 = 0
        st3 = [ls[type3] for ls in lst]
        lst2d = [[ls[type1], ls[type2]] for ls in lst]
        for i in range(len(lst2d)):
            for j in range(i + 1, len(lst2d)):
                if (abs(lst2d[i][0] - lst2d[j][0])) < lm:
                    if ((abs(lst2d[i][1] - lst2d[j][1])) < lm) and (
                            ((abs(lst2d[i][1] - lst2d[j][1])) != 0) or ((abs(lst2d[i][0] - lst2d[j][0])) != 0)):
                        lst2d[j] = lst2d[i]
                        flag = True

        if not flag:
            return lst, lns
        else:
            lns2d = [[ll[type1], ll[type2]] for ll in lns]
            l3d = [ll[type3] for ll in lns]
            lns2d = correct_lines(lst2d, lns2d)
            if type1 == 0 and type2 == 1:
                lst = [[lst2d[i][0], lst2d[i][1], st3[i]] for i in range(len(lst))]
                lns = [[lns2d[i][0], lns2d[i][1], l3d[i]] for i in range(len(lns))]
            elif type1 == 0 and type2 == 2:
                lst = [[lst2d[i][0], st3[i], lst2d[i][1]] for i in range(len(lst))]
                lns = [[lns2d[i][0], l3d[i], lns2d[i][1]] for i in range(len(lns))]
            else:
                lst = [[st3[i], lst2d[i][0], lst2d[i][1]] for i in range(len(lst))]
                lns = [[l3d[i], lns2d[i][0], lns2d[i][1]] for i in range(len(lns))]
            return lst, lns


    def correct_lines(lst2d, lns2d) -> list:
        for i in range(0, len(lst2d), 2):
            point1 = lst2d[i]
            point2 = lst2d[i + 1]
            x_values = [point1[0], point2[0]]
            y_values = [point1[1], point2[1]]
            lns2d[i // 2] = [x_values, y_values]
        return lns2d

    application = Line2D(False)
    application.MainLoop()
