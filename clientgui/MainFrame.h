// $Id$
//
// The contents of this file are subject to the BOINC Public License
// Version 1.0 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://boinc.berkeley.edu/license_1.0.txt
// 
// Software distributed under the License is distributed on an "AS IS"
// basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
// License for the specific language governing rights and limitations
// under the License. 
// 
// The Original Code is the Berkeley Open Infrastructure for Network Computing. 
// 
// The Initial Developer of the Original Code is the SETI@home project.
// Portions created by the SETI@home project are Copyright (C) 2002
// University of California at Berkeley. All Rights Reserved. 
// 
// Contributor(s):
//
// Revision History:
//


#ifndef _MAINFRAME_H_
#define _MAINFRAME_H_

#if defined(__GNUG__) && !defined(__APPLE__)
#pragma interface "MainFrame.cpp"
#endif


class CMainFrame : public wxFrame
{
    DECLARE_DYNAMIC_CLASS(CMainFrame)

public:
    CMainFrame();
    CMainFrame(wxString strTitle);

    ~CMainFrame(void);

    bool UpdateStatusbar( const wxString& strStatusbarText );

    void OnHide( wxCommandEvent& event );
    void OnActivitySelection( wxCommandEvent& event );
    void OnNetworkSelection( wxCommandEvent& event );
    void OnRunBenchmarks( wxCommandEvent& event );
    void OnSelectComputer( wxCommandEvent& event );
    void OnExit( wxCommandEvent& event );

    void OnToolsOptions( wxCommandEvent& event );
    void OnAbout( wxCommandEvent& event );

    void OnUpdateActivitySelection( wxUpdateUIEvent& event );
    void OnUpdateNetworkSelection( wxUpdateUIEvent& event );

    void OnIdle ( wxIdleEvent& event );
    void OnClose( wxCloseEvent& event );
    void OnSize( wxSizeEvent& event );
    void OnChar( wxKeyEvent& event );


    void OnNotebookSelectionChanged( wxNotebookEvent& event );

    void OnListSelected( wxListEvent& event );
    void OnListDeselected( wxListEvent& event );

    void OnFrameRender( wxTimerEvent& event );
    void OnListPanelRender( wxTimerEvent& event );
    void OnTaskPanelRender( wxTimerEvent& event );

private:

    wxMenuBar*      m_pMenubar;
    wxNotebook*     m_pNotebook;
    wxStatusBar*    m_pStatusbar;
    wxTimer*        m_pFrameRenderTimer;
    wxTimer*        m_pFrameTaskPanelRenderTimer;
    wxTimer*        m_pFrameListPanelRenderTimer;

    wxStaticBitmap* m_pbmpConnected;
    wxStaticBitmap* m_pbmpDisconnect;

    wxString        m_strBaseTitle;


    bool            CreateMenu();
    bool            DeleteMenu();

    bool            CreateNotebook();
    template < class T >
        bool        CreateNotebookPage( T pwndNewNotebookPage );
    bool            DeleteNotebook();

    bool            CreateStatusbar();
    bool            DeleteStatusbar();

    bool            SaveState();
    bool            RestoreState();


    DECLARE_EVENT_TABLE()

};


#endif

