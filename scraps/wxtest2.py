#!/usr/bin/env python

import wx

class wxHelloFrame(wx.Frame):
    """This is the frame for our application, it is derived from
    the wx.Frame element."""

    def __init__(self, *args, **kwargs):
        """Initialize, and let the user set any Frame settings"""
        wx.Frame.__init__(self, *args, **kwargs)
        self.create_controls()

    def create_controls(self):
        """Called when the controls on Window are to be created"""

        #Horizontal sizer
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #Vertical sizer
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)

        #Widget Creation
        #Create the static text widget and set the text
        self.text = wx.StaticText(self, label="Enter some text:")
        #Create the Edit Field (or TextCtrl)
        self.edit = wx.TextCtrl(self, size=wx.Size(250, -1))
        #Create the button
        self.button = wx.Button(self, label="Press me!")
        #bind the button click to our press function
        self.button.Bind(wx.EVT_BUTTON, self.on_button_pressed)

        #Add to horizontal sizer
        #add the static text to the sizer, tell it not to resize
        self.h_sizer.Add(self.text, 0,)
        #Add 5 pixels between the static text and the edit
        self.h_sizer.AddSpacer((5,0))
        #Add Edit
        self.h_sizer.Add(self.edit, 1)

        #Add to the vertical sizer to create two rows
        self.v_sizer.Add(self.h_sizer, 0, wx.EXPAND)
        #Add button underneath
        self.v_sizer.Add(self.button, 0)

        #Set the sizer
        self.SetSizer(self.v_sizer)
        #Fit ourselves to the sizer
        self.v_sizer.Fit(self)
        #Set the Minumum size
        self.SetMinSize(self.v_sizer.GetMinSize())

    def on_button_pressed(self, event):
        """Called when the button is clicked.  It will
        show a simple dialog with the text from the
        edit feld."""
        #Get the message text
        message_text = "You typed: %s" % (self.edit.GetValue())
        msg_box = wx.MessageDialog(self
            , message_text
            , "Hello!"
            , wx.OK | wx.CENTRE | wx.ICON_EXCLAMATION)
        #Show the Dialog
        msg_box.ShowModal()

class wxHelloApp(wx.App):
    """The wx.App for the wxHello application"""

    def OnInit(self):
        """Override OnInit to create our Frame"""
        frame = wxHelloFrame(None, title="wxHello")
        frame.Show()
        self.SetTopWindow(frame)

        return True

if __name__ == "__main__":
    app = wxHelloApp()
    app.MainLoop()