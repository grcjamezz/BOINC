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
// $Log$
// Revision 1.2  2004/09/24 22:19:00  rwalton
// *** empty log message ***
//
// Revision 1.1  2004/09/21 01:26:25  rwalton
// *** empty log message ***
//
//

#ifndef _VIEWRESOURCES_H_
#define _VIEWRESOURCES_H_

#if defined(__GNUG__) && !defined(__APPLE__)
#pragma interface "ViewResources.cpp"
#endif


#include "BOINCBaseView.h"

class CViewResources : public CBOINCBaseView
{
    DECLARE_DYNAMIC_CLASS( CViewResources )

public:
    CViewResources();
    CViewResources(wxNotebook* pNotebook);

    ~CViewResources();

    virtual wxString        GetViewName();
    virtual char**          GetViewIcon();

    virtual void            OnRender( wxTimerEvent& event );

    virtual void            OnListSelected( wxListEvent& event );
    virtual void            OnListDeselected( wxListEvent& event );
    virtual wxString        OnListGetItemText( long item, long column ) const;

    virtual void            OnTaskLinkClicked( const wxHtmlLinkInfo& link );
    virtual void            OnTaskCellMouseHover( wxHtmlCell* cell, wxCoord x, wxCoord y );

private:

    bool                    m_bTaskHeaderHidden;

    bool                    m_bTipsHeaderHidden;

    bool                    m_bItemSelected;

    virtual void            UpdateSelection();
    virtual void            UpdateTaskPane();

};


#endif

